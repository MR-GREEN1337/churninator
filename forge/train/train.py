# forge/train/train.py
import yaml
import os
from pathlib import Path
import torch
import wandb
from transformers import (
    AutoProcessor,
    Idefics2ForConditionalGeneration,
    TrainingArguments,
    Trainer,
    BitsAndBytesConfig,
)
from peft import LoraConfig, get_peft_model, PeftModel
import argparse

# --- Local Project Imports ---
from forge.train.datasets import FinetuneDataset
from forge.train.collator import FinetuneDataCollator


def main(config_path: str):
    """
    The main training function for the Churninator Forge.
    Orchestrates the entire fine-tuning process based on hierarchical YAML configs.
    """
    # --- 1. Load Hierarchical Configurations ---
    print("--- Loading Configurations ---")
    with open("forge/config.yaml", "r") as f:
        master_config = yaml.safe_load(f)

    with open(config_path, "r") as f:
        run_config = yaml.safe_load(f)

    # Merge configs: run_config overrides defaults in master_config['defaults']
    config = {**master_config.get("defaults", {}), **run_config}

    # Add non-default, essential keys from master_config
    for key in [
        "hf_token",
        "wandb_project",
        "wandb_entity",
        "output_dir",
        "base_model",
    ]:
        if key in master_config and key not in config:
            config[key] = master_config[key]

    # Crucially, allow the run_config to override the master `base_model` for Stage 2
    if "base_model" in run_config:
        config["base_model"] = run_config["base_model"]

    print("--- Effective Run Configuration ---")
    print(yaml.dump(config))
    print("---------------------------------")

    # --- 2. Initialize W&B ---
    wandb.init(
        project=config["wandb_project"],
        entity=config["wandb_entity"],
        name=config["output_dir"],
        config=config,
        resume="allow",  # Allows resuming a previous run
    )

    # --- 3. Model & Processor Loading ---
    print(f"Loading base model config from: {config['base_model']}")
    quantization_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
    )

    # The `base_model_id` is always the original model from the Hub.
    # For Stage 2, we load this first, then apply our Stage 1 adapters.
    base_model_id = master_config["base_model"]
    processor = AutoProcessor.from_pretrained(base_model_id, token=config["hf_token"])

    model = Idefics2ForConditionalGeneration.from_pretrained(
        base_model_id,
        quantization_config=quantization_config,
        device_map="auto",
        token=config["hf_token"],
    )

    # --- 4. DYNAMIC MODEL SETUP (Stage 1 vs Stage 2) ---
    is_stage_2 = os.path.isdir(config["base_model"])
    if is_stage_2:
        print("--- STAGE 2 RUN DETECTED ---")
        print(f"Loading Stage 1 LoRA adapters from: {config['base_model']}")
        model = PeftModel.from_pretrained(model, config["base_model"])
        print("Successfully loaded Stage 1 adapters.")
    else:
        print("--- STAGE 1 RUN DETECTED ---")

    # --- 5. LoRA Configuration ---
    lora_config = LoraConfig(
        r=config["lora_r"],
        lora_alpha=config["lora_alpha"],
        lora_dropout=config["lora_dropout"],
        target_modules=[
            "q_proj",
            "k_proj",
            "v_proj",
            "o_proj",
            "gate_proj",
            "up_proj",
            "down_proj",
        ],
        use_rslora=True,
        bias="none",
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    # --- 6. Dataset Loading ---
    stage_num = 2 if "reasoning" in config["data_file"] else 1
    print(f"Configuring dataset for training Stage {stage_num}.")

    data_file = Path(master_config["data_dir"]) / "processed" / config["data_file"]
    raw_data_root = Path(master_config["data_dir"]) / "raw"

    train_dataset = FinetuneDataset(
        str(data_file), processor, str(raw_data_root), stage=stage_num
    )
    data_collator = FinetuneDataCollator(processor)

    # --- 7. Training Arguments ---
    output_dir_final = Path(master_config["output_dir"]) / config["output_dir"]
    training_args = TrainingArguments(
        output_dir=str(output_dir_final),
        num_train_epochs=config["num_train_epochs"],
        per_device_train_batch_size=config["per_device_train_batch_size"],
        gradient_accumulation_steps=config["gradient_accumulation_steps"],
        gradient_checkpointing=config["gradient_checkpointing"],
        learning_rate=config["learning_rate"],
        optim=config["optim"],
        logging_steps=config["logging_steps"],
        save_strategy=config["save_strategy"],
        save_steps=config.get("save_steps", 500),  # Use get for optional keys
        save_total_limit=config.get("save_total_limit", 2),
        report_to=config["report_to"],
        bf16=config.get("bf16", False),
        fp16=config.get("fp16", False),
        remove_unused_columns=False,
    )

    # --- 8. Initialize Trainer ---
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        data_collator=data_collator,
    )

    # --- 9. START or RESUME TRAINING ---
    print("🔥🔥🔥 The Forge is lit. Fine-tuning will now begin or resume. 🔥🔥🔥")

    # The Trainer will automatically look for the latest checkpoint in `output_dir`.
    # Passing `True` is the most explicit way to enable this behavior.
    trainer.train(resume_from_checkpoint=True)

    print("✅ Training complete!")

    # --- 10. Save Final Model ---
    final_path = output_dir_final / "final"
    trainer.save_model(str(final_path))
    print(f"✅ Final model adapters saved to {final_path}")
    wandb.finish()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="The Churninator Forge Training Script"
    )
    parser.add_argument(
        "--config",
        required=True,
        help="Path to the RUN-SPECIFIC config YAML (e.g., forge/train/configs/stage1_grounding.yaml).",
    )
    args = parser.parse_args()
    main(args.config)
