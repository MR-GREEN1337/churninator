# forge/train/train.py
import yaml
import os
from pathlib import Path
import torch
from transformers import (
    AutoProcessor,
    Idefics2ForConditionalGeneration,
    TrainingArguments,
    Trainer,
    BitsAndBytesConfig,
)
from peft import LoraConfig, get_peft_model, PeftModel
import wandb

from forge.train.datasets import FinetuneDataset
from forge.train.collator import FinetuneDataCollator


def main(config_path: str):
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    # --- W&B Setup ---
    wandb.init(
        project="TheChurninatorForge",
        name=Path(config["output_dir"]).name,
        config=config,
    )

    # --- Model & Processor Loading ---
    print(f"Loading base model config from: {config['base_model']}")
    quantization_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
    )
    base_model_id = "HuggingFaceTB/SmolLM-1.7B-32k-instruct"
    processor = AutoProcessor.from_pretrained(base_model_id)

    model = Idefics2ForConditionalGeneration.from_pretrained(
        base_model_id, quantization_config=quantization_config, device_map="auto"
    )

    # --- DYNAMIC MODEL SETUP for Stage 1 vs Stage 2 ---
    if os.path.isdir(config["base_model"]):
        print("--- STAGE 2 RUN DETECTED ---")
        print(f"Loading Stage 1 LoRA adapters from: {config['base_model']}")
        model = PeftModel.from_pretrained(model, config["base_model"])
        print("Successfully loaded Stage 1 adapters.")
    else:
        print("--- STAGE 1 RUN DETECTED ---")

    # --- LoRA Configuration ---
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

    # --- Dataset Loading ---
    stage_num = 2 if "reasoning" in config["data_file"] else 1
    print(f"Configuring dataset for training Stage {stage_num}.")

    data_file = Path("forge/data/processed") / config["data_file"]
    raw_data_root = Path("forge/data/raw")
    train_dataset = FinetuneDataset(
        str(data_file), processor, str(raw_data_root), stage=stage_num
    )

    # --- Data Collator ---
    data_collator = FinetuneDataCollator(processor)

    # --- Training Arguments ---
    training_args = TrainingArguments(
        output_dir=config["output_dir"],
        num_train_epochs=config["num_train_epochs"],
        per_device_train_batch_size=config["per_device_train_batch_size"],
        gradient_accumulation_steps=config["gradient_accumulation_steps"],
        gradient_checkpointing=config["gradient_checkpointing"],
        learning_rate=config["learning_rate"],
        optim=config["optim"],
        logging_steps=config["logging_steps"],
        save_strategy="epoch",
        report_to="wandb",
        bf16=config.get("bf16", False),
        fp16=config.get("fp16", False),
        remove_unused_columns=False,
    )

    # --- Initialize Trainer ---
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        data_collator=data_collator,
    )

    # --- START TRAINING ---
    print("🔥🔥🔥 The Forge is lit. Fine-tuning has begun. 🔥🔥🔥")
    trainer.train()
    print("✅ Training complete!")

    # --- Save Final Model ---
    final_path = Path(config["output_dir"]) / "final"
    trainer.save_model(str(final_path))
    print(f"✅ Final model adapters saved to {final_path}")
    wandb.finish()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to training config YAML.")
    args = parser.parse_args()
    main(args.config)
