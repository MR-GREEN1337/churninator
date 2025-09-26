# 🔥 The Churninator Forge

Welcome to the Forge. This is the heart of the Churninator project—a complete, open-source ML engineering pipeline for creating powerful, vision-based GUI agents.

This isn't just a collection of scripts; it's a factory. It takes in efficient, open-source Vision-Language Models (VLMs) like **SmolLM** and forges them into specialized **Churninators**: autonomous agents capable of navigating web applications and identifying user experience issues.

The entire process is based on the state-of-the-art methodology presented in the **AGUVIS** paper, focusing on a sequential, two-stage fine-tuning process:
1.  **Stage 1: Grounding:** Teaching the model the fundamental vocabulary of GUI interaction (linking text instructions to coordinates and actions).
2.  **Stage 2: Reasoning:** Taking the "grounded" model and further training it to plan, reason, and form an "inner monologue" to execute multi-step tasks.

This Forge is designed to be run on powerful cloud GPUs (like those from **Vast.ai**) to handle the massive datasets required for serious fine-tuning.

## ⚙️ What's Inside?

The Forge is a self-contained ML pipeline with several key components:

*   **Data Pipeline (`/data`):** Contains scripts to download the massive AGUVIS datasets, process them into a clean and unified format, and download the ScreenSpot benchmark dataset for evaluation.
*   **Training Pipeline (`/train`):** The core engine. A modular and configurable training system built with Hugging Face `transformers`, `accelerate`, and `peft` for efficient QLoRA fine-tuning.
*   **Evaluation Suite (`/eval`):** A unified script for running both qualitative spot-checks and rigorous, quantitative benchmarks on your newly forged models to measure their performance.
*   **Utility Library (`/utils`):** The toolbox of the Forge, containing robust parsers and converters for handling the complex "action space" of GUI agents.

---

## 🚀 Running the Forge on Vast.ai (End-to-End Workflow)

This guide will walk you through the entire process of fine-tuning your first two-stage Churninator using a remote cloud GPU from Vast.ai.

### Step 1: Prepare Your Local Machine

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/your-username/the-churninator.git
    cd the-churninator
    ```
2.  **Create Sync Scripts:** Create `sync_to_vast.sh` and `sync_from_vast.sh` scripts in your project root to easily manage code and model checkpoints. (Templates are available in the main project `README.md`).

### Step 2: Launch Your Vast.ai Instance

1.  **Create an account** on [Vast.ai](https://vast.ai).
2.  **Select a Docker Image:** On the "Create" page, use a pre-built PyTorch image. This saves a lot of setup time.
    *   **Recommended Image:** `pytorch/pytorch:2.3.0-cuda12.1-cudnn8-runtime`
3.  **Choose a GPU:** Fine-tuning even a ~1.7B model benefits from VRAM. Aim for a GPU with at least **16GB of VRAM**.
    *   **Good choices:** RTX 3080, RTX 4070, A10g.
4.  **Launch:** Configure your storage (at least 200GB to be safe for the full AGUVIS dataset) and launch the instance. Once it's running, copy the **SSH command** from your "Instances" dashboard.

### Step 3: Setup the Remote Machine

1.  **Sync Your Code:** From your **local machine**, run your sync script.
    ```bash
    ./sync_to_vast.sh
    ```
2.  **SSH into the Instance:** Use the SSH command you copied from Vast.ai.
    ```bash
    ssh -p <PORT> root@<IP_ADDRESS>
    ```
3.  **Navigate and Install Dependencies:**
    ```bash
    # Navigate to the project root you synced
    cd /path/to/your/project/

    # Create a virtual environment
    python -m venv .venv
    source .venv/bin/activate

    # Install all project dependencies
    pip install -r requirements.txt

    # Set up the Forge as an editable package to resolve all imports
    pip install -e .
    ```

### Step 4: Data Preparation (on Vast.ai)

Now, from inside your SSH session on the powerful remote machine, you'll prepare all necessary data.

1.  **Download Training Data:** This will download the full, multi-gigabyte AGUVIS datasets.
    ```bash
    bash forge/data/download_aguvis.sh
    ```
2.  **Download Evaluation Data:** This downloads the much smaller ScreenSpot benchmark.
    ```bash
    bash forge/data/download_eval_data.sh
    ```
3.  **Process the Training Data:** Run the preprocessing script to convert the raw AGUVIS data into clean `jsonl` files for both stages.
    ```bash
    python forge/data/preprocess.py
    ```

### Step 5: The Two-Stage Fine-Tuning Run

This is the main event. We'll use `tmux` to ensure the process keeps running even if your SSH connection drops.

1.  **Start a `tmux` Session:**
    ```bash
    tmux new -s training
    ```
2.  **Set Up Authentication:** Inside the `tmux` session, log in to your services.
    ```bash
    export WANDB_API_KEY='your_wandb_api_key' # pragma: allowlist secret
    huggingface-cli login
    ```
3.  **Launch Stage 1 (Grounding):**
    ```bash
    echo "--- LAUNCHING STAGE 1: GROUNDING ---"
    accelerate launch forge/train/train.py --config forge/train/configs/stage1_grounding.yaml
    ```
4.  **Monitor Stage 1:**
    *   Press **`Ctrl+b`**, then **`d`** to safely detach.
    *   Open the **Weights & Biases** link from your terminal to monitor the run. Wait for it to complete.

5.  **Launch Stage 2 (Reasoning):**
    *   Once Stage 1 is done, re-attach to your session: `tmux attach -t training`.
    *   The Stage 2 config is pre-configured to look for the output of the Stage 1 run. Launch it:
    ```bash
    echo "--- LAUNCHING STAGE 2: REASONING ---"
    accelerate launch forge/train/train.py --config forge/train/configs/stage2_reasoning.yaml
    ```
6.  **Detach and Monitor Stage 2** just as you did before.

### Step 6: Evaluate Your Forged Models

After both stages are complete, you need to test your creations.

1.  **Re-attach** to your `tmux` session (`tmux attach -t training`).
2.  **Evaluate the Stage 1 Model:** Run the quantitative benchmark on your first model.
    ```bash
    echo "--- EVALUATING STAGE 1 MODEL ---"
    python forge/eval/eval.py \
      --model-path "forge/checkpoints/churninator-smollm-1.7b-grounded-v1/final" \
      --stage 1 \
      --eval-type quantitative \
      --limit 250
    ```
3.  **Evaluate the Stage 2 Model:** Now test your final, reasoning-capable model.
    ```bash
    echo "--- EVALUATING STAGE 2 MODEL ---"
    python forge/eval/eval.py \
      --model-path "forge/checkpoints/churninator-smollm-1.7b-reasoning-v1/final" \
      --stage 2 \
      --eval-type quantitative \
      --limit 250
    ```
    *(Compare the accuracy scores in your terminal and on W&B. Did the reasoning training improve the model's grounding ability?)*

### Step 7: Retrieve Your Final Model & Shut Down

1.  From your **local machine**, run your `sync_from_vast.sh` script to download the final model adapters from the remote `forge/checkpoints` directory.
2.  **IMPORTANT:** Go to your Vast.ai dashboard and **DESTROY** the instance to stop being billed.

You have now successfully used the Forge to create and validate a complete, two-stage AI agent. The resulting model adapters are on your local machine, ready for deployment or to be pushed to the Hugging Face Hub.
