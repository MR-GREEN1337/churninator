## In command center, implement prompt instruction alongside url

<p align="center">
  <img src="web/src/app/favicon.ico" alt="Churninator Logo" width="128">
</p>

<h1 align="center">The Churninator</h1>

<p align="center">
  <strong>The Autonomous AI Mystery Shopper for SaaS.</strong>
  <br />
  Find your competitor's fatal flaw before they do.
</p>

<p align="center">
  <a href="https://github.com/MR-GREEN1337/churninator/stargazers"><img src="https://img.shields.io/github/stars/MR-GREEN1337/churninator?style=social" alt="GitHub Stars"></a>
  <a href="https://github.com/MR-GREEN1337/churninator/blob/main/LICENSE"><img src="https://img.shields.io/github/license/MR-GREEN1337/churninator" alt="License"></a>
  <a href="https://x.com/MR_GREEN1337"><img src="https://img.shields.io/twitter/follow/MR_GREEN1337?style=social&logo=twitter" alt="Follow on Twitter"></a>
</p>

---

![Churninator Live Agent View](/assets/agent.png)

**Churninator** is an open-source AI platform that autonomously analyzes the signup and onboarding experience of any web application. It acts as a tireless "mystery shopper," navigating complex user flows to identify friction points, conversion killers, and usability issues that cause users to churn.

The output isn't just a log; it's a **premium, AI-generated UX audit**, complete with visual "before and after" mockups, providing product teams with the actionable intelligence they need to win their market.

## ✨ Key Features

*   **🤖 Autonomous Agent:** Powered by a fine-tuned multimodal AI that understands and interacts with modern web apps like a human.
*   **📺 Live Observatory:** Watch the agent's browser view and "inner monologue" in real-time as it executes its mission.
*   **📄 AI-Powered Friction Reports:** Receive detailed, shareable PDF reports that don't just identify problems—they propose and visualize solutions with AI-generated design mockups.
*   **🔧 The Forge:** A complete, open-source ML pipeline to fine-tune your own specialized agents for any task.
*   **☁️ SaaS & Self-Hosted:** Use our upcoming managed platform, Churninator Cloud, or self-host the entire system for maximum control.

## 🏗️ Architecture Overview

Churninator is a production-grade, multi-component system designed for scale and reliability.

![Architecture Diagram](/assets/architecture.png)

1.  **Frontend (`web/`):** A Next.js dashboard for creating and observing agent runs. It features real-time log streaming (SSE) and video (MJPEG).
2.  **Backend (`backend/`):** A high-performance FastAPI application that serves the API, manages the database, and queues jobs with Redis.
3.  **Worker (`backend/worker/`):** Scalable Dramatiq workers that run Playwright in a headless environment to perform the browser automation.
4.  **Inference Server (`backend/inference/`):** A dedicated server that hosts the fine-tuned `SmolVLM` model, acting as the remote "brain" for the workers.
5.  **The Forge (`forge/`):** A suite of Python scripts for our two-stage model fine-tuning process, enabling the creation of new, powerful agents.

## 🚀 Getting Started

You can run the entire Churninator platform locally for development and testing.

### Prerequisites

*   Python 3.11+
*   Node.js 18+ & npm
*   [Postgres.app](https://postgresapp.com/) (or another local PostgreSQL server)
*   A Google Gemini API Key

### Local Development Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/MR-GREEN1337/churninator.git
    cd churninator
    ```

2.  **Configure Environment:**
    *   Copy the example environment file: `cp .env.example .env`
    *   Set up a local PostgreSQL database (see instructions [here](#part-1-setting-up-a-local-postgresql-database-on-macos)).
    *   Fill in your `DATABASE_URL` and `GOOGLE_API_KEY` in the `.env` file.

3.  **Run the automated setup script:**
    This will create a Python virtual environment, install all dependencies for the backend and frontend, and download the necessary Playwright browser.
    ```bash
    make -f Makefile.local setup
    ```

4.  **Run the application:**
    This will start all four services (frontend, API, worker, inference) concurrently using `honcho`.
    ```bash
    make -f Makefile.local run
    ```
    You can now access the dashboard at `http://localhost:3000`.

## ☁️ Churninator Cloud

While the entire Churninator platform is open-source and free to self-host, we are building a managed **Churninator Cloud** platform that provides:
*   One-click agent deployment without any setup.
*   Team collaboration features and shared reports.
*   Access to our continuously improved, state-of-the-art AI models.
*   Enterprise-grade security and support.

**[➡️ Sign up for the private beta](https://your-saas-website.com)**

---

## 🤝 Contributing

We are building Churninator in the open and welcome contributions of all kinds! Whether you're a developer, a designer, or a UX enthusiast, we'd love your help.

*   Check out our [Contribution Guide](CONTRIBUTING.md) to get started.
*   View our [public roadmap](https://github.com/users/your-username/projects/1) to see what's next.
*   Submit bug reports and feature requests on the [Issues](https://github.com/your-username/churninator/issues) page.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
