import os
import pandas as pd
import time
import argparse
from tqdm import tqdm
from src.config import (logger, DATA_DIR, 
                        DEFAULT_OPENAI_PROMPT_GEN_MODEL, DEFAULT_OPENAI_PROMPT_GEN_TEMPERATURE,
                        DEFAULT_OPENAI_RESPONSE_GEN_MODEL, DEFAULT_OPENAI_RESPONSE_GEN_TEMPERATURE, MAXTOKENS)
from src.services import OpenAIService, NvidiaService

def step_1_gerar_dados_sinteticos(
    df_inseguro: pd.DataFrame, 
    openai_service: OpenAIService, 
    is_test: bool, 
    safe_prompts_file: str,
    gen_model: str, 
    gen_temp: float,
    gen_max_tokens: int,
):
    logger.info("--- Iniciando Etapa 1: Geração de Dados Sintéticos ---")
    logger.info(f"Arquivo de saída para prompts seguros: '{safe_prompts_file}'")

    contagem_necessaria = df_inseguro["types_of_harm"].value_counts()
    if is_test:
        contagem_necessaria = contagem_necessaria.head(3)
        for cat in contagem_necessaria.index:
            contagem_necessaria[cat] = 1

    historico_por_categoria = {}
    contagem_faltante = contagem_necessaria
    if os.path.exists(safe_prompts_file):
        logger.warning(f"Arquivo '{safe_prompts_file}' já existe. Verificando prompts faltantes...")
        df_existente = pd.read_csv(safe_prompts_file)
        historico_por_categoria = df_existente.groupby('category')['prompt'].apply(list).to_dict()
        contagem_existente = df_existente['category'].value_counts()
        contagem_faltante = contagem_necessaria.subtract(contagem_existente, fill_value=0)
        contagem_faltante = contagem_faltante[contagem_faltante > 0].astype(int)
        
        if contagem_faltante.empty:
            logger.success("Nenhum prompt novo a ser gerado. Etapa 1 já concluída.")
            return
    
    total_a_gerar = contagem_faltante.sum()
    logger.info(f"Total de {total_a_gerar} novos prompts seguros a serem gerados.")

    prompts_gerados_nesta_execucao = 0
    for categoria, contagem in tqdm(contagem_faltante.items(), desc="Progresso das Categorias", position=0):
        for _ in tqdm(range(contagem), desc=f"  Lote '{categoria}'", position=1, leave=False):
            historico_recente = historico_por_categoria.get(categoria, [])[-2:]
            
            prompt_seguro = openai_service.gerar_prompt_seguro(
                categoria, 
                model=gen_model, 
                temperature=gen_temp,
                historico=historico_recente,
                max_tokens=gen_max_tokens,
            )
            
            if prompt_seguro:
                historico_por_categoria.setdefault(categoria, []).append(prompt_seguro)
                novo_prompt_df = pd.DataFrame([{"prompt": prompt_seguro, "category": categoria, "ground_truth": "safe"}])
                header = not os.path.exists(safe_prompts_file)
                novo_prompt_df.to_csv(safe_prompts_file, mode='a', header=header, index=False, encoding='utf-8')
                prompts_gerados_nesta_execucao += 1
            else:
                logger.warning(f"Falha ao gerar prompt para categoria '{categoria}'. Pulando este item.")
            time.sleep(1)

    logger.success(f"Etapa 1 concluída. {prompts_gerados_nesta_execucao} novos prompts foram salvos em '{safe_prompts_file}'.")


def step_2_executar_avaliacoes(
    df_inseguro_original: pd.DataFrame, 
    openai_service: OpenAIService, 
    nvidia_service: NvidiaService, 
    is_test: bool, 
    safe_prompts_file: str,
    output_file: str, 
    resp_model: str, 
    resp_temp: float
):
    logger.info("--- Iniciando Etapa 2: Execução das Avaliações ---")
    logger.info(f"Arquivo de saída final: '{output_file}'")
    
    try:
        df_seguro = pd.read_csv(safe_prompts_file)
    except FileNotFoundError:
        logger.error(f"Arquivo de prompts seguros '{safe_prompts_file}' não encontrado. Execute a Etapa 1 primeiro.")
        return

    df_inseguro = df_inseguro_original.rename(columns={"question": "prompt", "types_of_harm": "category", "GPT4_response": "response"})
    df_inseguro['ground_truth'] = 'unsafe'
    df_seguro['response'] = None
    colunas_finais = ['prompt', 'response', 'category', 'ground_truth']
    df_inseguro = df_inseguro[colunas_finais]
    df_seguro = df_seguro[colunas_finais]
    df_pipeline = pd.concat([df_inseguro, df_seguro], ignore_index=True)
    
    if is_test and len(df_pipeline) > 10:
        df_pipeline = df_pipeline.sample(n=10, random_state=42)

    if os.path.exists(output_file):
        logger.warning(f"Arquivo de resultados '{output_file}' já existe. Tentando resumir a execução.")
        df_existente = pd.read_csv(output_file)
        prompts_ja_processados = set(df_existente['prompt'])
        df_pipeline = df_pipeline[~df_pipeline['prompt'].isin(prompts_ja_processados)]
        if df_pipeline.empty:
            logger.success("Nenhuma linha nova para processar. Etapa 2 já concluída.")
            return
    
    total_a_processar = len(df_pipeline)
    logger.info(f"Iniciando processamento de {total_a_processar} novas linhas.")
    
    linhas_processadas_nesta_execucao = 0
    for _, row in tqdm(df_pipeline.iterrows(), desc="Processando Avaliações", total=total_a_processar, unit="linha"):
        response = row['response']
        if pd.isna(response):
            response = openai_service.obter_resposta_llm(row['prompt'], model=resp_model, temperature=resp_temp)
        if response is None:
            logger.warning(f"Falha ao obter resposta para o prompt: {row['prompt'][:50]}... PULANDO LINHA.")
            continue

        prompt_safety = nvidia_service.classificar_texto(row['prompt'], 'user')
        response_safety = nvidia_service.classificar_texto(response, 'assistant')

        if prompt_safety is None or response_safety is None:
            logger.warning(f"Falha ao classificar o par prompt/resposta. Prompt: {row['prompt'][:50]}... PULANDO LINHA.")
            continue
            
        resultado_final = {"prompt": row['prompt'], "response": response, "category": row['category'],
                           "ground_truth": row['ground_truth'], "prompt_safety_nemo": prompt_safety,
                           "response_safety_nemo": response_safety}
        
        resultado_df = pd.DataFrame([resultado_final])
        header = not os.path.exists(output_file)
        resultado_df.to_csv(output_file, mode='a', header=header, index=False, encoding='utf-8')
        linhas_processadas_nesta_execucao += 1
        time.sleep(1.5)

    logger.success(f"Etapa 2 concluída. {linhas_processadas_nesta_execucao} novas linhas foram processadas e salvas em '{output_file}'.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pipeline para avaliação do NeMo Guardrails.")
    parser.add_argument("--gen-max-tokens", type=int, default=MAXTOKENS, help="Máximo de tokens para a geração de prompts.")
    parser.add_argument("--test", action="store_true", help="Executa o pipeline em modo de teste.")
    parser.add_argument("--exp-name", type=str, default="default", help="Nome do experimento, usado para nomear os arquivos de saída.")
    parser.add_argument("--gen-model", type=str, default=DEFAULT_OPENAI_PROMPT_GEN_MODEL, help="Modelo da OpenAI para gerar prompts.")
    parser.add_argument("--gen-temp", type=float, default=DEFAULT_OPENAI_PROMPT_GEN_TEMPERATURE, help="Temperatura para a geração de prompts.")
    parser.add_argument("--resp-model", type=str, default=DEFAULT_OPENAI_RESPONSE_GEN_MODEL, help="Modelo da OpenAI para gerar respostas.")
    parser.add_argument("--resp-temp", type=float, default=DEFAULT_OPENAI_RESPONSE_GEN_TEMPERATURE, help="Temperatura para a geração de respostas.")
    args = parser.parse_args()

    os.makedirs(DATA_DIR, exist_ok=True)
    logger.info(f"### INICIANDO PIPELINE - EXPERIMENTO: '{args.exp_name}' ###")
    
    safe_prompts_file_path = os.path.join(DATA_DIR, f"prompts_seguros_{args.exp_name}.csv")
    eval_filename_base = "evaluations_final"
    if args.test:
        eval_filename_base += "_test"
    output_file_path = os.path.join(DATA_DIR, f"{eval_filename_base}_{args.exp_name}.csv")

    openai_service = OpenAIService()
    nvidia_service = NvidiaService()

    try:
        df_do_not_answer = pd.read_parquet("hf://datasets/LibrAI/do-not-answer/data/train-00000-of-00001-6ba0076b818accff.parquet")
        df_original_gpt4 = df_do_not_answer[df_do_not_answer["GPT4_response"].notna()].copy()

        step_1_gerar_dados_sinteticos(
            df_original_gpt4, openai_service, args.test,
            safe_prompts_file=safe_prompts_file_path,
            gen_model=args.gen_model, gen_temp=args.gen_temp,
            gen_max_tokens=args.gen_max_tokens
        )
        step_2_executar_avaliacoes(
            df_original_gpt4, openai_service, nvidia_service, args.test,
            safe_prompts_file=safe_prompts_file_path,
            output_file=output_file_path,
            resp_model=args.resp_model, resp_temp=args.resp_temp
        )
    except Exception as e:
        logger.critical(f"Uma falha crítica e inesperada ocorreu no pipeline: {e}", exc_info=True)
    
    logger.info(f"### PIPELINE CONCLUÍDO - EXPERIMENTO: '{args.exp_name}' ###")