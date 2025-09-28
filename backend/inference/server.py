import os
import base64
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager
from PIL import Image
from io import BytesIO
from loguru import logger
from backend.src.core.settings import get_settings

try:
    VLLM_AVAILABLE = False
    raise ImportError
except ImportError:
    VLLM_AVAILABLE = False
    print("✅ Using standard Transformers pipeline for Mac/CPU.")
    import torch
    from transformers import AutoProcessor, AutoModelForImageTextToText


class InferenceRequest(BaseModel):
    image_base64: str
    prompt: str


class InferenceResponse(BaseModel):
    generated_text: str


model = None
processor = None
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    global model, processor
    model_id = os.environ.get(
        "MODEL_ID", "smolagents/SmolVLM2-2.2B-Instruct-Agentic-GUI"
    )
    print(f"🚀 Loading model '{model_id}' for inference...")

    device = "mps" if torch.backends.mps.is_available() else "cpu"
    dtype = torch.float16 if device == "mps" else torch.bfloat16

    processor = AutoProcessor.from_pretrained(model_id, trust_remote_code=True)
    model = AutoModelForImageTextToText.from_pretrained(
        model_id, torch_dtype=dtype, trust_remote_code=True
    )
    model.to(device)

    print(f"✅ Model '{model_id}' loaded and ready on {device}.")
    yield
    model, processor = None, None


app = FastAPI(title="Churninator Inference Server", lifespan=lifespan)


@app.post("/predict", response_model=InferenceResponse)
async def predict(request: InferenceRequest):
    if not model or not processor:
        raise HTTPException(status_code=503, detail="Model or processor is not loaded.")

    # Decode the base64 image
    image = Image.open(BytesIO(base64.b64decode(request.image_base64))).convert("RGB")

    # CRITICAL FIX: SmolVLM requires <image> token in the prompt to match the number of images
    # The model expects the image token to be present in the text
    prompt_with_image = f"<image>\nUser: {request.prompt}\nAssistant:"

    try:
        # Process the inputs with the correct format
        inputs = processor(
            text=prompt_with_image,
            images=[image],
            return_tensors="pt",
        ).to(model.device)

        # Generate response
        with torch.no_grad():
            generated_ids = model.generate(
                **inputs,
                max_new_tokens=256,
                do_sample=False,
                pad_token_id=processor.tokenizer.eos_token_id,
            )

        # Decode the response
        generated_text = processor.batch_decode(
            generated_ids, skip_special_tokens=True
        )[0]

        # Clean the response to only get the assistant's response
        if "Assistant:" in generated_text:
            cleaned_text = generated_text.split("Assistant:")[-1].strip()
        else:
            # Fallback: remove the original prompt
            cleaned_text = generated_text.replace(prompt_with_image, "").strip()

        response = InferenceResponse(generated_text=cleaned_text)
        logger.info(f"Generated response: {response}")
        return response

    except Exception as e:
        print(f"Error during inference: {e}")
        raise HTTPException(status_code=500, detail=f"Inference failed: {str(e)}")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "model_loaded": model is not None}
