"""
Pipeline principal para o projeto de avaliação do NeMo Guardrails.
Orquestra a geração de dados sintéticos e a execução das avaliações.
"""
import os
import pandas as pd
from loguru import logger
import time
import argparse  # Para adicionar o modo de teste

# Importa as funções dos nossos módulos
from scripts.prompt_gen import gerar_prompt_seguro
from scripts.llm_prompt_response import obter_resposta_llm
from scripts.nemo_eval import classificar_com_nemo

# --- CONFIGURAÇÃO DE ARQUIVOS ---
DATA_DIR = "data"
SAFE_PROMPTS_FILE = os.path.join(DATA_DIR, "prompts_seguros_sinteticos.csv")
FINAL_EVALUATION_FILE = os.path.join(DATA_DIR, "evaluations_final.csv")
FINAL_EVALUATION_FILE_TEST = os.path.join(DATA_DIR, "evaluations_final_test.csv")

def step_1_gerar_dados_sinteticos(df_inseguro_original: pd.DataFrame, is_test: bool):
    """Etapa 1: Gera prompts seguros espelhando a distribuição de categorias."""
    logger.info("--- Iniciando Etapa 1: Geração de Dados Sintéticos ---")
    
    if os.path.exists(SAFE_PROMPTS_FILE):
        logger.warning(f"'{SAFE_PROMPTS_FILE}' já existe. Pulando Etapa 1.")
        return

    contagem_categorias = df_inseguro_original["types_of_harm"].value_counts()
    
    if is_test:
        # Em modo teste, gera apenas 1 prompt para as 3 primeiras categorias
        contagem_categorias = contagem_categorias.head(3)
        for cat in contagem_categorias.index:
            contagem_categorias[cat] = 1

    total_prompts_a_gerar = contagem_categorias.sum()
    logger.info(f"Total de {total_prompts_a_gerar} prompts seguros a serem gerados.")
    
    prompts_gerados = []
    for categoria, contagem in contagem_categorias.items():
        logger.info(f"Gerando {contagem} prompts para a categoria: '{categoria}'...")
        # CORREÇÃO: Removido o 'contagem = 2' hardcodado.
        for i in range(contagem):
            logger.debug(f"Gerando prompt {i+1}/{contagem} para '{categoria}'...")
            prompt_seguro = gerar_prompt_seguro(categoria)
            if prompt_seguro:
                prompts_gerados.append({
                    "prompt": prompt_seguro, "category": categoria, "ground_truth": "safe"
                })
            time.sleep(1)

    df_sintetico = pd.DataFrame(prompts_gerados)
    df_sintetico.to_csv(SAFE_PROMPTS_FILE, index=False, encoding='utf-8')
    logger.success(f"Etapa 1 concluída. Salvo em '{SAFE_PROMPTS_FILE}'.")


def step_2_executar_avaliacoes(df_inseguro_original: pd.DataFrame, is_test: bool):
    """Etapa 2: Executa as avaliações com GPT-4 e NeMo."""
    logger.info("--- Iniciando Etapa 2: Execução das Avaliações ---")
    
    output_file = FINAL_EVALUATION_FILE_TEST if is_test else FINAL_EVALUATION_FILE
    if os.path.exists(output_file):
        logger.warning(f"Arquivo final '{output_file}' já existe. Pipeline concluído.")
        return

    df_seguro = pd.read_csv(SAFE_PROMPTS_FILE)
    
    # CORREÇÃO: Sintaxe do rename corrigida (espera um dicionário)
    df_inseguro = df_inseguro_original.rename(columns={
        "question": "prompt",
        "types_of_harm": "category",
        "GPT4_response": "response"
    })
    df_inseguro['ground_truth'] = 'unsafe'
    df_seguro['response'] = None

    colunas_finais = ['prompt', 'response', 'category', 'ground_truth']
    df_inseguro = df_inseguro[colunas_finais]
    df_seguro = df_seguro[colunas_finais]

    df_pipeline = pd.concat([df_inseguro, df_seguro], ignore_index=True)
    
    if is_test:
        df_pipeline = df_pipeline.sample(n=10, random_state=42)

    logger.info("Obtendo respostas do GPT-4 para prompts novos...")
    for index, row in df_pipeline.iterrows():
        if pd.isna(row['response']):
            resposta = obter_resposta_llm(row['prompt'])
            df_pipeline.at[index, 'response'] = resposta
            time.sleep(1.5)
            
    logger.info("Classificando prompts com NeMo Guardrails...")
    # CORREÇÃO: Removido o slice '[:3]' para processar todo o DataFrame
    df_pipeline['prompt_safety_nemo'] = df_pipeline['prompt'].apply(lambda txt: classificar_com_nemo(txt, 'user'))
    logger.info("Classificando respostas com NeMo Guardrails...")
    df_pipeline['response_safety_nemo'] = df_pipeline['response'].apply(lambda txt: classificar_com_nemo(txt, 'assistant'))

    df_pipeline.to_csv(output_file, index=False, encoding='utf-8')
    logger.success(f"Etapa 2 concluída. Avaliação final salva em '{output_file}'.")
    logger.info(f"Visualização do resultado final:\n{df_pipeline.head().to_string()}")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Pipeline para avaliação do NeMo Guardrails.")
    parser.add_argument("--test", action="store_true", help="Executa o pipeline em modo de teste com uma pequena amostra de dados.")
    args = parser.parse_args()

    # Cria diretórios se não existirem
    os.makedirs(DATA_DIR, exist_ok=True)

    log_file = "pipeline_test.log" if args.test else "pipeline_full.log"
    logger.add(log_file, rotation="10 MB", level="INFO")
    logger.info("### INICIANDO PIPELINE DE GERAÇÃO E AVALIAÇÃO DE DADOS ###")
    
    try:
        df_do_not_answer = pd.read_parquet("hf://datasets/LibrAI/do-not-answer/data/train-00000-of-00001-6ba0076b818accff.parquet")
        df_original_gpt4 = df_do_not_answer[df_do_not_answer['GPT4_response'].notna()].copy()
        
        step_1_gerar_dados_sinteticos(df_original_gpt4, args.test)
        step_2_executar_avaliacoes(df_original_gpt4, args.test)
    except FileNotFoundError as e:
        logger.critical(f"Erro fatal: Arquivo de dataset não pôde ser carregado. {e}")
    except Exception as e:
        logger.critical(f"Uma falha crítica ocorreu no pipeline: {e}")
    
    logger.info("### PIPELINE CONCLUÍDO ###")