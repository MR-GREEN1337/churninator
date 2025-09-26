# backend/src/inference/server.py
import os
import base64
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager
from vllm import LLM, SamplingParams


# --- Pydantic Models for API ---
class InferenceRequest(BaseModel):
    image_base64: str
    prompt: str


class InferenceResponse(BaseModel):
    generated_text: str


# --- Global variable for the model ---
llm: LLM | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles the startup and shutdown of the model.
    On startup, it loads the specified model from the Hugging Face Hub.
    """
    global llm

    # CRITICAL: We point this to the pre-trained SmolOperator model on the Hub.
    # A user could override this with an environment variable to use their own model.
    model_id = os.environ.get(
        "MODEL_ID", "smolagents/SmolVLM2-2.2B-Instruct-Agentic-GUI"
    )
    print(f"🚀 Loading model '{model_id}' for inference using vLLM...")

    # vLLM is the industry standard for high-performance inference.
    llm = LLM(
        model=model_id,
        tensor_parallel_size=1,
        trust_remote_code=True,  # SmolLM requires this
        gpu_memory_utilization=0.90,
    )
    print(f"✅ Model '{model_id}' loaded and ready for inference.")
    yield
    # --- On Shutdown ---
    print("🔌 Shutting down inference server.")
    llm = None


app = FastAPI(title="Churninator Inference Server", lifespan=lifespan)


@app.post("/predict", response_model=InferenceResponse)
async def predict(request: InferenceRequest):
    """
    Receives an image and a prompt, runs inference with the loaded VLM,
    and returns the raw generated text.
    """
    if not llm:
        raise HTTPException(
            status_code=503, detail="Model is not loaded or is warming up."
        )

    try:
        # 1. Decode the image from base64
        # vLLM's multimodal support expects a PIL Image.
        from PIL import Image
        from io import BytesIO

        image_bytes = base64.b64decode(request.image_base64)
        image = Image.open(BytesIO(image_bytes))

        # 2. Format the prompt using the model's chat template
        # The SmolLM model uses the Llama 3 Instruct template.
        prompt_text = f"<|user|>\n{request.prompt}<|end|>\n<|assistant|>"

        # 3. Configure sampling parameters for deterministic output
        sampling_params = SamplingParams(
            temperature=0.0,  # Set to 0 for deterministic, predictable actions
            max_tokens=256,  # Increase max tokens to allow for longer thoughts
        )

        # 4. Run inference using vLLM
        # The `llm.generate` method handles batching requests for high throughput.
        # For multimodal, we pass the image via the `multi_modal_data` argument.
        outputs = await llm.generate(
            prompts=prompt_text,
            sampling_params=sampling_params,
            multi_modal_data={"image": image},
        )

        # Extract the generated text from the first (and only) output
        generated_text = outputs[0].outputs[0].text

        return InferenceResponse(generated_text=generated_text)

    except Exception as e:
        print(f"❌ Inference Error: {e}")
        raise HTTPException(
            status_code=500, detail=f"An error occurred during inference: {e}"
        )
