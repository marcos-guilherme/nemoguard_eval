import os
from openai import OpenAI
from dotenv import load_dotenv


# --- CONFIGURAÇÃO ---
load_dotenv()

api_key_openai = os.getenv("OPENAI_API_KEY")
if not api_key_openai:
    raise ValueError("A variável de ambiente OPENAI_API_KEY não foi definida.")
client_openai = OpenAI(api_key=api_key_openai)


def obter_resposta_llm(prompt: str, modelo_gpt: str = "gpt-4o-mini") -> str:
    """Obtém uma resposta de um modelo GPT para um determinado prompt."""
    try:
        response = client_openai.chat.completions.create(
            model=modelo_gpt,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Erro ao obter resposta do GPT-4 para o prompt '{prompt[:50]}...': {e}")
        return "Error generating response"