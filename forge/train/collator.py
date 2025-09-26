# forge/training/collator.py
from typing import List, Dict, Any
import torch
from transformers import AutoProcessor


class FinetuneDataCollator:
    """
    A specialized data collator for the Churninator fine-tuning process.

    This collator takes a batch of data items from the FinetuneDataset and
    formats them into the precise structure expected by modern Vision-Language
    Models for training. It handles dynamic batching of images and text,
    padding, tokenization, and the crucial task of masking labels.
    """

    def __init__(self, processor: AutoProcessor, max_length: int = 4096):
        """
        Initializes the collator.

        Args:
            processor: The Hugging Face AutoProcessor for the model (e.g., for SmolLM/Idefics2).
            max_length (int): The maximum sequence length for the model input.
        """
        self.processor = processor
        self.max_length = max_length

    def __call__(self, examples: List[Dict[str, Any]]) -> Dict[str, torch.Tensor]:
        """
        The main collating function that transforms a list of dataset items into a batch.

        Args:
            examples (List[Dict[str, Any]]): A list of dictionaries from our
                FinetuneDataset. Each item has 'image' (a PIL Image) and 'messages'
                (a list of conversation turn dictionaries).

        Returns:
            Dict[str, torch.Tensor]: A dictionary of batched and padded tensors
                ready for the model, including 'input_ids', 'attention_mask',
                pixel_values, and 'labels'.
        """

        # Extract images and message lists from the batch
        images = [example["image"] for example in examples]
        batch_messages = [example["messages"] for example in examples]

        # Use the processor's chat template to convert the structured message lists
        # into a single, correctly formatted prompt string for each example.
        # This handles all the special tokens (e.g., <|user|>, <|assistant|>) automatically.
        full_texts = [
            self.processor.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=False
            )
            for messages in batch_messages
        ]

        # Tokenize the text and process the images all at once.
        # This is the most efficient method and correctly handles multimodal inputs.
        batch = self.processor(
            text=full_texts,
            images=images,
            padding="longest",  # Pad to the longest sequence in the batch
            truncation=True,
            max_length=self.max_length,
            return_tensors="pt",
        )

        # --- LABEL MASKING ---
        # Our goal is to train the model *only* on the assistant's responses.
        # We do this by creating a 'labels' tensor where all tokens belonging to
        # the user or system prompts are masked with -100.

        labels = batch["input_ids"].clone()

        # To find where the assistant's part begins, we can process the prompts
        # again, but this time *without* the assistant's final response.
        prompts_without_assistant = []
        for messages in batch_messages:
            # Create a version of the conversation with the last (assistant) message removed
            prompt_only_messages = messages[:-1]
            prompt_text = self.processor.apply_chat_template(
                prompt_only_messages, tokenize=False, add_generation_prompt=False
            )
            prompts_without_assistant.append(prompt_text)

        # Tokenize these "prompt-only" texts to find their length
        prompt_lengths = self.processor(
            text=prompts_without_assistant,
            padding=False,  # We only need the length, not padding
            truncation=True,
            max_length=self.max_length,
            return_tensors="pt",
        )["input_ids"].shape[1]

        # For each item in the batch, mask the prompt part
        for i in range(len(examples)):
            prompt_len = prompt_lengths[i]
            # Set all tokens up to the end of the prompt to -100
            labels[i, :prompt_len] = -100
            # Also mask any padding tokens at the end
            # The attention mask is 1 for real tokens and 0 for padding.
            labels[i][batch["attention_mask"][i] == 0] = -100

        batch["labels"] = labels
        return batch
