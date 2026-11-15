# NeMo Guardrails as a Firewall for User-LLM Interaction

[![Future Internet 2026](https://img.shields.io/badge/MDPI_Future_Internet-2026-1E293B?style=flat-square)](https://www.mdpi.com/1999-5903/18/5/252)
[![SBSeg 2025](https://img.shields.io/badge/SBSeg-2025-0A66C2?style=flat-square)](https://sol.sbc.org.br/index.php/sbseg/article/view/36622)
[![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat-square&logo=docker&logoColor=white)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

Official reproducible artifact for the paper **"NeMo Guardrails as a Firewall for User-LLM Interaction"**, published at **SBSeg 2025** and extended in **Future Internet (MDPI, 2026)**.

> **Abstract:**
> This work evaluates NVIDIA NeMo Guardrails acting as a firewall during interactions between users and Large Language Models (LLMs). We benchmark its effectiveness at detecting adversarial inputs such as *jailbreaking* and *prompt injection* using the *Do Not Answer* dataset formulated as a binary classification task ("Safe" vs. "Unsafe"). The evaluation covers risk-category breakdowns, standard binary classification metrics, and the **Compensation Rate** (*Taxa de Compensação*), a metric proposed in this study to measure its effectiveness as a second line of defense.

---

## Repository Structure

```text
.
├── data/                   # Stores generated CSV outputs (empty by default)
├── src/
│   ├── __init__.py
│   ├── config.py           # Configuration and logger initialization
│   └── services.py         # OpenAIService and NvidiaService API wrappers
├── .dockerignore
├── .env.example            # Environment variable template
├── Dockerfile
├── main.py                 # End-to-end pipeline entrypoint and orchestrator
└── requirements.txt        # Pinned Python dependencies
```

---

## Requirements

- **Hardware:** Minimum 4 GB RAM, ~1 GB free disk space, stable internet connection.
- **Software:** Python 3.11, Docker (recommended for reproducibility).
- **API Keys:** Active keys for **OpenAI** and **NVIDIA AI Foundation Models**, loaded via environment variables or a local `.env` file (never baked into the Docker image).

---

## Reproducing the Experiments

### Option 1: Prebuilt Docker Hub Image (Recommended)

1. Create a working directory and `data/` folder:

   ```bash
   mkdir nemoguard-eval-run && cd nemoguard-eval-run
   mkdir data
   ```

2. Create a `.env` file with your API keys:

   ```env
   OPENAI_API_KEY="sk-..."
   NVIDIA_API_KEY="nvapi-..."
   ```

3. Pull the image and run:

   ```bash
   docker pull octequ/nemoguard-eval:latest

   # Quick verification run
   docker run --rm --env-file .env -v ./data:/app/data octequ/nemoguard-eval:latest --test

   # Full paper benchmark (resumable)
   docker run --rm --env-file .env -v ./data:/app/data octequ/nemoguard-eval:latest
   ```

---

### Option 2: Build Docker Image Locally

```bash
docker build -t nemoguard-eval .

# Quick verification run (2-5 minutes)
docker run --rm \
  -e OPENAI_API_KEY="your_openai_key" \
  -e NVIDIA_API_KEY="your_nvidia_key" \
  -v ./data:/app/data \
  nemoguard-eval \
  --exp-name "default" --test

# Full benchmark run
docker run --rm \
  -e OPENAI_API_KEY="your_openai_key" \
  -e NVIDIA_API_KEY="your_nvidia_key" \
  -v ./data:/app/data \
  nemoguard-eval \
  --exp-name "default"
```

---

### Option 3: Local Python Environment

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env      # Fill in your API keys

# Quick verification
python main.py --test

# Full benchmark
python main.py
```

---

## Custom Experiments & CLI Options

Example running shorter generated prompts with `gpt-4o`:

```bash
python main.py --exp-name "short_prompts_gpt4o" --gen-max-tokens 50 --resp-model "gpt-4o"
```

| Flag | Default | Description |
|---|---|---|
| `--test` | `false` | Runs on a small sample to verify setup and API keys. |
| `--exp-name` | `"default"` | Experiment identifier used in output CSV filenames. |
| `--gen-model` | `"gpt-4o-mini"` | OpenAI model used to generate safe prompts (Stage 1). |
| `--gen-temp` | `0.7` | Sampling temperature for prompt generation (Stage 1). |
| `--gen-max-tokens` | `100` | Max tokens for prompt generation (Stage 1). |
| `--resp-model` | `"gpt-4o-mini"` | OpenAI model used to generate responses (Stage 2). |
| `--resp-temp` | `0.0` | Sampling temperature for response generation (Stage 2). |

---

## Results Analysis

Once `data/evaluations_final_default.csv` is generated, metrics and plots from the study can be reproduced using `analise_resultados.ipynb`.

---

## License

This project is licensed under the [MIT License](LICENSE).
