# forge/eval/eval.py
import argparse
import torch
from transformers import AutoProcessor, Idefics2ForConditionalGeneration
from peft import PeftModel
from PIL import Image
import requests
from pathlib import Path
from tqdm import tqdm
import sys
import re

# Add project root to path for imports
sys.path.append(str(Path(__file__).resolve().parents[2]))

from forge.eval.eval_prompt import (
    SCREENSPOT_V2_USER_PROMPT_PHASE_1,
    STAGE_2_SYSTEM_PROMPT,
    STAGE_2_USER_PROMPT,
)
from forge.utils.function_parser import extract_function_calls_from_text
from forge.eval.eval_dataset import ScreenSpotDataset


def load_model_for_eval(model_path: str):
    """Loads a fine-tuned PEFT model and merges it for fast inference."""
    print(f"--- Loading model from: {model_path} ---")
    base_model_id = "HuggingFaceTB/SmolLM-1.7B-32k-instruct"

    dtype = torch.float16 if torch.backends.mps.is_available() else torch.bfloat16

    # Load the base model first, in 4-bit for memory efficiency on the host
    # When we merge the adapter, it will be upcasted.
    model = Idefics2ForConditionalGeneration.from_pretrained(
        base_model_id, torch_dtype=dtype
    )

    # Apply the LoRA adapters from your fine-tuning run
    model = PeftModel.from_pretrained(model, model_path)
    model = model.merge_and_unload()  # Merge adapters for fast inference

    device = (
        "mps"
        if torch.backends.mps.is_available()
        else "cuda"
        if torch.cuda.is_available()
        else "cpu"
    )
    model.to(device)

    processor = AutoProcessor.from_pretrained(base_model_id)
    print(f"✅ Model loaded to {device}.")
    return model, processor


def parse_action_from_stage2_output(text: str) -> list:
    """Extracts the action from the <code> block of a Stage 2 model output."""
    code_match = re.search(r"<code>(.*?)</code>", text, re.DOTALL)
    if code_match:
        code_content = code_match.group(1).strip()
        return extract_function_calls_from_text(code_content)
    return []


def run_evaluation(model, processor, stage, eval_type, **kwargs):
    """Unified evaluation runner."""
    if eval_type == "qualitative":
        run_qualitative_test(model, processor, stage, **kwargs)
    elif eval_type == "quantitative":
        run_quantitative_benchmark(model, processor, stage, **kwargs)


def run_qualitative_test(model, processor, stage, image_url, instruction):
    """Runs a single, qualitative spot-check on the model."""
    print("\n--- Running Qualitative Spot-Check ---")
    print(f"Fetching image from: {image_url}")
    image = Image.open(requests.get(image_url, stream=True).raw).convert("RGB")

    # --- DYNAMIC PROMPT SELECTION ---
    if stage == 1:
        prompt_text = SCREENSPOT_V2_USER_PROMPT_PHASE_1.format(instruction=instruction)
        messages = [
            {
                "role": "user",
                "content": [{"type": "image"}, {"type": "text", "text": prompt_text}],
            }
        ]
    else:  # Stage 2
        messages = [
            {"role": "system", "content": STAGE_2_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {"type": "image"},
                    {
                        "type": "text",
                        "text": STAGE_2_USER_PROMPT.format(instruction=instruction),
                    },
                ],
            },
        ]

    inputs = processor(messages, image=image, return_tensors="pt").to(model.device)

    print("🤖 Generating prediction...")
    generated_ids = model.generate(**inputs, max_new_tokens=100)
    generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

    print("\n--- RESULTS ---")
    print(f"Instruction: {instruction}")
    print(f"Full Model Output:\n{generated_text}")

    # --- DYNAMIC PARSING ---
    parsed_actions = (
        parse_action_from_stage2_output(generated_text)
        if stage == 2
        else extract_function_calls_from_text(generated_text)
    )

    if parsed_actions:
        print(f"\n✅ Parsed Action: {parsed_actions[0].to_string()}")
    else:
        print("\n⚠️ Could not parse an action from the model's output.")


def check_click_accuracy(pred_x, pred_y, gt_bbox_norm):
    """Checks if a predicted click (normalized) is within a ground truth bbox (normalized)."""
    return (
        gt_bbox_norm[0] <= pred_x <= gt_bbox_norm[2]
        and gt_bbox_norm[1] <= pred_y <= gt_bbox_norm[3]
    )


def run_quantitative_benchmark(model, processor, stage, data_root, limit):
    """Runs a quantitative benchmark on the ScreenSpot dataset."""
    print(f"\n--- Running Quantitative Benchmark (Stage {stage}) on ScreenSpot ---")
    dataset = ScreenSpotDataset(data_root=data_root)
    dataset_subset = torch.utils.data.Subset(dataset, range(min(limit, len(dataset))))

    correct_predictions = 0
    for item in tqdm(dataset_subset, desc="Benchmarking"):
        image, instruction, gt_bbox_pixels = (
            item["image"],
            item["instruction"],
            item["ground_truth_bbox"],
        )
        img_width, img_height = image.size
        gt_bbox_norm = [
            gt_bbox_pixels[0] / img_width,
            gt_bbox_pixels[1] / img_height,
            gt_bbox_pixels[2] / img_width,
            gt_bbox_pixels[3] / img_height,
        ]

        if stage == 1:
            prompt_text = SCREENSPOT_V2_USER_PROMPT_PHASE_1.format(
                instruction=instruction
            )
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "image"},
                        {"type": "text", "text": prompt_text},
                    ],
                }
            ]
        else:  # Stage 2
            messages = [
                {"role": "system", "content": STAGE_2_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {"type": "image"},
                        {
                            "type": "text",
                            "text": STAGE_2_USER_PROMPT.format(instruction=instruction),
                        },
                    ],
                },
            ]

        inputs = processor(messages, image=image, return_tensors="pt").to(model.device)
        generated_ids = model.generate(**inputs, max_new_tokens=100)
        generated_text = processor.batch_decode(
            generated_ids, skip_special_tokens=True
        )[0]

        parsed_actions = (
            parse_action_from_stage2_output(generated_text)
            if stage == 2
            else extract_function_calls_from_text(generated_text)
        )

        if parsed_actions and parsed_actions[0].function_name == "click":
            params = parsed_actions[0].parameters
            if "x" in params and "y" in params:
                if check_click_accuracy(params["x"], params["y"], gt_bbox_norm):
                    correct_predictions += 1

    accuracy = (correct_predictions / limit) * 100
    print("\n--- BENCHMARK COMPLETE ---")
    print(f"Total Samples: {limit}")
    print(f"Correct Predictions: {correct_predictions}")
    print(f"Accuracy: {accuracy:.2f}%")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Churninator Model Evaluation Suite")
    parser.add_argument(
        "--model-path",
        required=True,
        help="Path to the fine-tuned PEFT model checkpoint directory.",
    )
    parser.add_argument(
        "--stage",
        required=True,
        type=int,
        choices=[1, 2],
        help="Which fine-tuning stage is this model from (1 or 2).",
    )
    parser.add_argument(
        "--eval-type",
        required=True,
        choices=["qualitative", "quantitative"],
        help="Type of evaluation to run.",
    )
    parser.add_argument("--image-url", help="URL of the image for qualitative test.")
    parser.add_argument("--instruction", help="Instruction for qualitative test.")
    parser.add_argument(
        "--data-root",
        default="forge/data/eval_data/ScreenSpot_v2",
        help="Root directory of the ScreenSpot evaluation data.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=100,
        help="Number of samples for quantitative benchmark.",
    )

    args = parser.parse_args()

    model, processor = load_model_for_eval(args.model_path)

    kwargs = {
        "image_url": args.image_url,
        "instruction": args.instruction,
        "data_root": args.data_root,
        "limit": args.limit,
    }

    run_evaluation(model, processor, args.stage, args.eval_type, **kwargs)
