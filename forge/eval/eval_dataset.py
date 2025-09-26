# forge/eval/eval_dataset.py
import json
from pathlib import Path
from torch.utils.data import Dataset
from PIL import Image


class ScreenSpotDataset(Dataset):
    """Loads the ScreenSpot benchmark dataset for quantitative evaluation."""

    def __init__(self, data_root: str, split: str = "all"):
        self.data_root = Path(data_root)
        self.split = split
        self.data = self._load_data()

    def _load_data(self):
        all_data = []
        # ScreenSpot has web, mobile, desktop splits
        splits_to_load = (
            ["web", "mobile", "desktop"] if self.split == "all" else [self.split]
        )
        for s in splits_to_load:
            json_path = self.data_root / f"annotations/{s}.json"
            with open(json_path, "r") as f:
                data = json.load(f)
                for item in data:
                    item["split"] = s
                    all_data.append(item)
        return all_data

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]
        image_path = self.data_root / f"screenshot/{item['split']}/{item['image']}"
        try:
            image = Image.open(image_path).convert("RGB")
        except Exception:
            # Fallback for corrupted data
            return self.__getitem__((idx + 1) % len(self))

        # Ground truth bounding box (left, top, right, bottom)
        bbox = [
            item["bbox"][0],
            item["bbox"][1],
            item["bbox"][0] + item["bbox"][2],
            item["bbox"][1] + item["bbox"][3],
        ]

        return {
            "image": image,
            "instruction": item["instruction"],
            "ground_truth_bbox": bbox,
        }
