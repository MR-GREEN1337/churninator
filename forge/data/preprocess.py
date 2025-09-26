# forge/data/preprocess.py
import json
from pathlib import Path
from datasets import load_dataset
from tqdm import tqdm
import logging

from forge.utils.function_parser import parse_function_call
from forge.utils.action_conversion import action_conversion

# Setup basic logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def process_stage(stage_name, stage_num, raw_data_dir, output_dir):
    """Processes a single stage of the AGUVIS dataset, now with action conversion."""
    raw_stage_path = raw_data_dir / f"aguvis-stage{stage_num}"
    if not raw_stage_path.exists():
        logging.error(f"Raw data path not found: {raw_stage_path}")
        return

    logging.info(f"--- Starting processing for {stage_name} ---")

    dataset = load_dataset(str(raw_stage_path), name="default", split="train")
    output_file = output_dir / f"stage{stage_num}_{stage_name.lower()}.jsonl"
    logging.info(f"Processing and saving to {output_file}...")

    count = 0
    conversion_errors = 0
    with open(output_file, "w") as f:
        for item in tqdm(dataset, desc=f"Processing {stage_name}"):
            try:
                # --- ACTION CONVERSION LOGIC ---
                # 1. Parse the raw action string using our universal translator
                original_action_str = item["action"]
                parsed_calls = parse_function_call(original_action_str)

                if not parsed_calls:
                    continue  # Skip if the action is malformed

                # 2. Convert to our clean, unified action space using the AGUVIS specialist
                # We assume a dummy resolution for now, as the model will learn normalized coords.
                # The actual pixel values don't matter during this conversion step.
                converted_calls = action_conversion(parsed_calls, resolution=(1, 1))

                # 3. Reconstruct the clean action string
                clean_action_str = " ".join(
                    [call.to_string() for call in converted_calls]
                )
                # --- END ACTION CONVERSION ---

                portable_image_path = str(
                    Path(f"aguvis-stage{stage_num}") / item["image"]
                )

                processed_item = {
                    "image_path": portable_image_path,
                    "instruction": item["instruction"],
                    "action": clean_action_str,  # Use the clean, converted action
                }
                f.write(json.dumps(processed_item) + "\n")
                count += 1
            except Exception as e:
                conversion_errors += 1
                logging.warning(
                    f"Skipping record due to conversion error: {e} on action '{item.get('action', 'N/A')}'"
                )

    logging.info(
        f"✅ {stage_name} processing complete. Wrote {count} records to {output_file}"
    )
    if conversion_errors > 0:
        logging.warning(f"⚠️ Encountered {conversion_errors} action conversion errors.")


def main():
    raw_data_dir = Path("forge/data/raw")
    output_dir = Path("forge/data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)

    process_stage("grounding", 1, raw_data_dir, output_dir)
    # You can uncomment this later when you're ready for Stage 2
    # process_stage("reasoning", 2, raw_data_dir, output_dir)


if __name__ == "__main__":
    main()
