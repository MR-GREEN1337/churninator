# backend/src/inference/server.py
import os
import base64
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager
from PIL import Image
from io import BytesIO

# --- Environment Detection ---
# A simple way to check if we're in a CUDA-enabled (NVIDIA) environment.
# vLLM will fail to import if CUDA is not available.
try:
    from vllm import LLM, SamplingParams
    from vllm.multimodal import ImagePixelData  # noqa: F401

    VLLM_AVAILABLE = True
except ImportError:
    VLLM_AVAILABLE = False
    print(
        "⚠️ vLLM not found. Falling back to standard Transformers pipeline. This will be slower."
    )
    import torch
    from transformers import AutoProcessor, Idefics2ForConditionalGeneration
    from peft import PeftModel


# --- Pydantic Models & Global State ---
class InferenceRequest(BaseModel):
    image_base64: str
    prompt: str


class InferenceResponse(BaseModel):
    generated_text: str


# Global variable for the model
model = None
processor = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global model, processor
    model_id = os.environ.get(
        "MODEL_ID", "smolagents/SmolVLM2-2.2B-Instruct-Agentic-GUI"
    )
    print(f"🚀 Loading model '{model_id}' for inference...")

    if VLLM_AVAILABLE:
        print("✅ vLLM is available. Using high-performance engine.")
        model = LLM(
            model=model_id,
            tensor_parallel_size=1,
            trust_remote_code=True,
            gpu_memory_utilization=0.90,
        )
    else:
        print(
            "✅ vLLM not available. Using standard Transformers pipeline for Mac/CPU."
        )
        device = "mps" if torch.backends.mps.is_available() else "cpu"
        dtype = torch.float16 if device == "mps" else torch.bfloat16

        processor = AutoProcessor.from_pretrained(model_id)

        # In a real local setup, you might point this to your fine-tuned adapters
        if os.path.isdir(model_id):  # If MODEL_ID is a local path to adapters
            base_model_id = os.environ.get(
                "BASE_MODEL_ID", "HuggingFaceTB/SmolLM-1.7B-32k-instruct"
            )
            base_model = Idefics2ForConditionalGeneration.from_pretrained(
                base_model_id, torch_dtype=dtype
            )
            model = PeftModel.from_pretrained(base_model, model_id)
            model = model.merge_and_unload()
        else:  # Load directly from Hub
            model = Idefics2ForConditionalGeneration.from_pretrained(
                model_id, torch_dtype=dtype, trust_remote_code=True
            )

        model.to(device)

    print(f"✅ Model '{model_id}' loaded and ready.")
    yield
    model, processor = None, None


app = FastAPI(title="Churninator Inference Server", lifespan=lifespan)


@app.post("/predict", response_model=InferenceResponse)
async def predict(request: InferenceRequest):
    if not model:
        raise HTTPException(status_code=503, detail="Model is not loaded.")

    image = Image.open(BytesIO(base64.b64decode(request.image_base64)))
    prompt_text = f"<|user|>\n{request.prompt}<|end|>\n<|assistant|>"

    if VLLM_AVAILABLE:
        sampling_params = SamplingParams(temperature=0.0, max_tokens=256)
        outputs = await model.generate(
            prompts=prompt_text,
            sampling_params=sampling_params,
            multi_modal_data={"image": image},
        )
        generated_text = outputs[0].outputs[0].text
    else:
        # Standard Transformers pipeline for Mac/CPU
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image"},
                    {"type": "text", "text": request.prompt},
                ],
            }
        ]

        if not model or not processor:
            raise HTTPException(
                status_code=503, detail="Model or processor is not loaded."
            )

        inputs = processor(messages, image=image, return_tensors="pt").to(model.device)
        generated_ids = model.generate(**inputs, max_new_tokens=256)
        generated_text = processor.batch_decode(
            generated_ids, skip_special_tokens=True
        )[0]

    return InferenceResponse(generated_text=generated_text)
