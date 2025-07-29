import os
import json
from openai import OpenAI


api_key_nvidia = os.getenv("NVIDIA_API_KEY")
if not api_key_nvidia:
    raise ValueError("A variável de ambiente NVIDIA_API_KEY não foi definida.")

client_nvidia = OpenAI(
  base_url = "https://integrate.api.nvidia.com/v1",
  api_key = api_key_nvidia
)

def classificar_com_nemo(texto: str, role: str) -> str:
    """
    Classifica um texto como 'safe' ou 'unsafe' usando NeMo Guardrails,
    analisando a resposta JSON.
    """
    if not isinstance(texto, str) or not texto.strip():
        return "not_applicable"

    try:
        completion = client_nvidia.chat.completions.create(
          model="nvidia/llama-3.1-nemoguard-8b-content-safety",
          messages=[{"role": role, "content": texto}],
          stream=False
        )
        
        resultado_json_str = completion.choices[0].message.content

        dados_json = json.loads(resultado_json_str)
        
        if role == 'user':

            return dados_json.get("User Safety", "parsing_failed")
        elif role == 'assistant':
            return dados_json.get("Response Safety", "parsing_failed")
        else:
            return "invalid_role"

    except json.JSONDecodeError:
        print(f"Erro: Não foi possível decodificar o JSON da resposta da API NeMo: {resultado_json_str}")
        return "json_decode_error"
    except Exception as e:
        print(f"Erro ao classificar texto com NeMo para '{texto[:50]}...': {e}")
        return "api_error"
