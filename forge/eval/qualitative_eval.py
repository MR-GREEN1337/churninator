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

# Add project root to path for imports
sys.path.append(str(Path(__file__).resolve().parents[2]))

from forge.eval.eval_prompt import SCREENSPOT_V2_USER_PROMPT_PHASE_1
from forge.utils.function_parser import extract_function_calls_from_text
from forge.eval.eval_dataset import ScreenSpotDataset


def load_model_for_eval(model_path: str):
    """Loads a fine-tuned PEFT model and merges it for fast inference."""
    print(f"--- Loading model from: {model_path} ---")
    base_model_id = "HuggingFaceTB/SmolLM-1.7B-32k-instruct"

    # Use float16 for Mac, bfloat16 for CUDA
    dtype = torch.float16 if torch.backends.mps.is_available() else torch.bfloat16

    model = Idefics2ForConditionalGeneration.from_pretrained(
        base_model_id, torch_dtype=dtype
    )
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


def run_qualitative_test(model, processor, image_url, instruction):
    """Runs a single, qualitative spot-check on the model."""
    print("\n--- Running Qualitative Spot-Check ---")
    print(f"Fetching image from: {image_url}")
    try:
        image = Image.open(requests.get(image_url, stream=True).raw).convert("RGB")
    except Exception as e:
        print(f"❌ Failed to load image: {e}")
        return

    prompt_text = SCREENSPOT_V2_USER_PROMPT_PHASE_1.format(instruction=instruction)
    messages = [
        {
            "role": "user",
            "content": [{"type": "image"}, {"type": "text", "text": prompt_text}],
        }
    ]
    inputs = processor(messages, image=image, return_tensors="pt").to(model.device)

    print("🤖 Generating prediction...")
    generated_ids = model.generate(**inputs, max_new_tokens=50)
    generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

    print("\n--- RESULTS ---")
    print(f"Instruction: {instruction}")
    print(f"Full Model Output:\n{generated_text}")

    parsed_actions = extract_function_calls_from_text(generated_text)
    if parsed_actions:
        print(f"\n✅ Parsed Action: {parsed_actions[0].to_string()}")
    else:
        print("\n⚠️ Could not parse an action from the model's output.")


def check_click_accuracy(pred_x, pred_y, gt_bbox):
    """Checks if a predicted click (normalized) is within a ground truth bbox (pixels)."""
    # The bbox is [x_min, y_min, x_max, y_max] in pixels.
    # The prediction is normalized. We assume image size 1x1 for simplicity.
    return gt_bbox[0] <= pred_x <= gt_bbox[2] and gt_bbox[1] <= pred_y <= gt_bbox[3]


def run_quantitative_benchmark(model, processor, data_root, limit=100):
    """Runs a quantitative benchmark on the ScreenSpot dataset."""
    print("\n--- Running Quantitative Benchmark on ScreenSpot ---")
    dataset = ScreenSpotDataset(data_root=data_root)

    correct_predictions = 0
    total_predictions = 0

    # Limit the number of samples for a quick benchmark
    dataset_subset = torch.utils.data.Subset(dataset, range(min(limit, len(dataset))))

    for item in tqdm(dataset_subset, desc="Benchmarking"):
        image = item["image"]
        instruction = item["instruction"]
        gt_bbox_pixels = item["ground_truth_bbox"]

        # We need to normalize the ground truth bbox to compare with model output
        img_width, img_height = image.size
        gt_bbox_norm = [
            gt_bbox_pixels[0] / img_width,
            gt_bbox_pixels[1] / img_height,
            gt_bbox_pixels[2] / img_width,
            gt_bbox_pixels[3] / img_height,
        ]

        prompt_text = SCREENSPOT_V2_USER_PROMPT_PHASE_1.format(instruction=instruction)
        messages = [
            {
                "role": "user",
                "content": [{"type": "image"}, {"type": "text", "text": prompt_text}],
            }
        ]
        inputs = processor(messages, image=image, return_tensors="pt").to(model.device)

        generated_ids = model.generate(**inputs, max_new_tokens=50)
        generated_text = processor.batch_decode(
            generated_ids, skip_special_tokens=True
        )[0]

        parsed_actions = extract_function_calls_from_text(generated_text)
        total_predictions += 1

        if parsed_actions and parsed_actions[0].function_name == "click":
            params = parsed_actions[0].parameters
            if "x" in params and "y" in params:
                pred_x, pred_y = params["x"], params["y"]
                if check_click_accuracy(pred_x, pred_y, gt_bbox_norm):
                    correct_predictions += 1

    accuracy = (
        (correct_predictions / total_predictions) * 100 if total_predictions > 0 else 0
    )
    print("\n--- BENCHMARK COMPLETE ---")
    print(f"Total Samples: {total_predictions}")
    print(f"Correct Predictions: {correct_predictions}")
    print(f"Accuracy: {accuracy:.2f}%")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Churninator Model Evaluation Suite")
    parser.add_argument(
        "--model-path",
        required=True,
        help="Path to the fine-tuned PEFT model checkpoint directory (e.g., forge/checkpoints/run/final).",
    )
    parser.add_argument(
        "--eval-type",
        required=True,
        choices=["qualitative", "quantitative"],
        help="Type of evaluation to run.",
    )

    # Args for qualitative eval
    parser.add_argument("--image-url", help="URL of the image for qualitative test.")
    parser.add_argument("--instruction", help="Instruction for qualitative test.")

    # Args for quantitative eval
    parser.add_argument(
        "--data-root",
        default="forge/data/eval_data/ScreenSpot_v2",
        help="Root directory of the ScreenSpot evaluation data.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=100,
        help="Number of samples to run for quantitative benchmark.",
    )

    args = parser.parse_args()

    model, processor = load_model_for_eval(args.model_path)

    if args.eval - type == "qualitative":
        if not args.image_url or not args.instruction:
            raise ValueError(
                "--image-url and --instruction are required for qualitative evaluation."
            )
        run_qualitative_test(model, processor, args.image_url, args.instruction)
    elif args.eval - type == "quantitative":
        run_quantitative_benchmark(model, processor, args.data_root, args.limit)
