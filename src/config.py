

import os
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("CONFIG ERROR: A variável de ambiente OPENAI_API_KEY não foi definida.")
if not NVIDIA_API_KEY:
    raise ValueError("CONFIG ERROR: A variável de ambiente NVIDIA_API_KEY não foi definida.")

DATA_DIR = "data"

DEFAULT_OPENAI_PROMPT_GEN_MODEL = "gpt-4o-mini"
DEFAULT_OPENAI_RESPONSE_GEN_MODEL = "gpt-4o-mini"
DEFAULT_OPENAI_PROMPT_GEN_TEMPERATURE = 0.7
DEFAULT_OPENAI_RESPONSE_GEN_TEMPERATURE = 0.0
MAXTOKENS = 100

NVIDIA_SAFETY_MODEL = "nvidia/llama-3.1-nemoguard-8b-content-safety"

