# forge/train/datasets.py
import json
from pathlib import Path
from torch.utils.data import Dataset
from PIL import Image


class FinetuneDataset(Dataset):
    """
    Loads and processes data for both Stage 1 (Grounding) and Stage 2 (Reasoning)
    of the Churninator fine-tuning process.
    """

    def __init__(self, jsonl_file: str, processor, raw_data_root: str, stage: int):
        """
        Initializes the dataset.

        Args:
            jsonl_file (str): Path to the processed .jsonl data file.
            processor: The Hugging Face model processor.
            raw_data_root (str): Path to the root of the raw data directory (for resolving image paths).
            stage (int): The training stage (1 or 2) to configure the prompt format.
        """
        self.data = [json.loads(line) for line in open(jsonl_file)]
        self.processor = processor
        self.raw_data_root = Path(raw_data_root)
        self.stage = stage

        if self.stage not in [1, 2]:
            raise ValueError(f"Invalid stage specified: {self.stage}. Must be 1 or 2.")

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx: int):
        item = self.data[idx]

        # Resolve the full image path
        image_path = self.raw_data_root / item["image_path"]
        try:
            image = Image.open(image_path).convert("RGB")
        except Exception as e:
            print(
                f"Warning: Could not load image at {image_path}. Error: {e}. Skipping."
            )
            # Recursively try the next item if the current one is broken
            return self.__getitem__((idx + 1) % len(self))

        # --- DYNAMIC PROMPT FORMATTING based on stage ---
        if self.stage == 1:
            # Stage 1: Simple Instruction -> Action for Grounding
            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful GUI agent. You will be given an instruction and a screenshot. Respond with the single pyautogui-style action to complete the instruction.",
                },
                {"role": "user", "content": f"Instruction: {item['instruction']}"},
                {"role": "assistant", "content": f"Action: {item['action']}"},
            ]

        elif self.stage == 2:
            # Stage 2: Instruction -> Thought & Action for Reasoning
            # This format teaches the model the "inner monologue" structure.
            # Assumes the preprocessed data for stage 2 has 'thought' and 'action' keys.
            thought = item.get(
                "thought", "I need to analyze the screen and decide the next step."
            )  # Default thought
            action = item.get("action", "TERMINATE('missing action')")

            assistant_response = f"<think>{thought}</think>\n<code>{action}</code>"
            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful GUI agent. First, think step-by-step about your plan inside <think> tags. Then, provide the single action to perform inside <code> tags.",
                },
                {"role": "user", "content": f"Instruction: {item['instruction']}"},
                {"role": "assistant", "content": assistant_response},
            ]

        # Return the raw image and messages; the collator will handle tokenization.
        return {"image": image, "messages": messages}
