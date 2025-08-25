

# Avaliação do NeMo Guardrails como um Firewall para a Interação Usuário-LLM

## Resumo

Este repositório contém o artefato para o artigo **"Avaliação do NeMo Guardrails como um Firewall para a Interação Usuário-LLM"**. O objetivo deste artefato é fornecer todo o código, dados e instruções para reproduzir os experimentos do artigo, permitindo a validação dos resultados apresentados.

> **Resumo do Artigo:**
> Neste artigo é analisado o NeMo Guardrails, um framework que atua como um firewall durante interações entre usuário e Modelos de Linguagem em Larga Escala (LLM). O objetivo é avaliar seu desempenho na identificação de tentativas maliciosas, como *jailbreaking* e *prompt injection*. Foi utilizado o *Do Not Answer dataset* para a tarefa de classificação do modelo dentre as classes "Seguro" ou "Inseguro". A avaliação consistiu em uma análise por categoria de risco, no cálculo de métricas de classificação binária e na aplicação da Taxa de Compensação, uma nova métrica proposta neste trabalho. O F1 Score sugere um possível *trade-off* entre Precisão e Sensibilidade.

-----

## Estrutura do Repositório

O projeto foi refatorado para seguir práticas de engenharia de software que promovem sustentabilidade e clareza.

```
.
├── data/
│   └── (Vazio por padrão, armazena os CSVs gerados)
├── src/
│   ├── __init__.py
│   ├── config.py           # Carrega configurações e variáveis de ambiente
│   └── services.py         # Abstrai a lógica de comunicação com as APIs (OpenAI, NVIDIA)
├── .dockerignore           # Especifica arquivos a serem ignorados pelo Docker
├── .env.example            # Template para as variáveis de ambiente
├── Dockerfile              # Define a imagem Docker para o projeto
├── main.py                 # Ponto de entrada e orquestrador do pipeline
└── requirements.txt        # Lista de dependências Python
```

  - `main.py`: O script principal (orquestrador) que executa todo o pipeline de ponta a ponta.
  - `requirements.txt`: Lista de todas as dependências Python necessárias, com versões fixadas para garantir a reprodutibilidade.
  - `.env.example`: Um arquivo de exemplo para as chaves de API. Você deve copiá-lo para `.env` para a execução local.
  - `src/`: Diretório contendo os módulos com a lógica de negócio desacoplada.
      - `config.py`: Centraliza o carregamento de configurações e a inicialização do *logger*.
      - `services.py`: Contém as classes `OpenAIService` e `NvidiaService`, que encapsulam todas as interações com as APIs externas.
  - `data/`: Diretório onde os dados gerados pelo pipeline (arquivos `.csv`) são salvos.
  - `Dockerfile`: Define o ambiente de execução containerizado para garantir a reprodutibilidade.

## Selos Reivindicados

Este artefato foi preparado para atender aos critérios dos seguintes selos de avaliação:

  - [x] **Artefatos Disponíveis (SeloD)**
  - [x] **Artefatos Funcionais (SeloF)**
  - [x] **Artefatos Sustentáveis (SeloS)**
  - [x] **Artefatos Reprodutíveis (SeloR)**

-----

## Configuração do Ambiente

### Informações Básicas

  - **Requisitos de Hardware:**
      - **RAM:** Mínimo de 4 GB.
      - **Disco:** \~1 GB de espaço livre.
      - **Conexão estável com a internet** (essencial para as APIs).
  - **Requisitos de Software:**
      - **Python 3.11**
      - **Docker** (recomendado para a execução principal).

### Dependências

  - **Python:** Todas as bibliotecas estão listadas em `requirements.txt`. A versão de cada uma está fixada para garantir a reprodutibilidade.
  - **Recursos de Terceiros:** A execução requer chaves de API para os serviços da **OpenAI** e da **NVIDIA AI Foundation Models**.

### Preocupações com Segurança

As chaves de API são informações sensíveis. O código foi projetado para carregá-las de variáveis de ambiente. Para a execução local, utiliza-se um arquivo `.env` (ignorado pelo Git). Para a execução com Docker, as chaves são injetadas de forma segura no momento da execução, sem nunca serem armazenadas na imagem.

-----

## Fluxo de Reprodução dos Experimentos

Recomendamos fortemente o uso do **Docker** para a reprodução, pois ele garante um ambiente idêntico ao de desenvolvimento e validação.

### Método 1: Executando com Imagem do Docker Hub (Recomendado)

Esta abordagem é a mais rápida e simples. A imagem está disponível no **Docker Hub**.

#### Pré-requisitos

  - **Docker** instalado ([docker.com](https://www.docker.com/products/docker-desktop/))
  - Conta no Docker Hub (para fazer o `pull`)

#### Passos

1.  **Crie a pasta de trabalho e o diretório `data`:**

    ```bash
    mkdir experimento_nemoguard && cd experimento_nemoguard
    mkdir data
    ```

2.  **Crie o arquivo `.env`** dentro de `experimento_nemoguard` com suas chaves de API:

    ```env
    OPENAI_API_KEY="sk-..."
    NVIDIA_API_KEY="nvapi-..."
    ```

    > **Atenção:** Substitua pelos valores reais das suas chaves.

3.  **Faça login e baixe a imagem do Docker Hub:**

    ```bash
    docker login
    docker pull octequ/nemoguard-eval:latest
    ```

4.  **Execute o contêiner:**

      - **Teste Rápido (Verificação):**

        ```bash
        docker run --rm --env-file .env -v ./data:/app/data octequ/nemoguard-eval:latest --test
        ```

      - **Execução Completa (Reprodução do artigo):**

        ```bash
        docker run --rm --env-file .env -v ./data:/app/data octequ/nemoguard-eval:latest
        ```

> **Notas sobre os comandos:**
>
>   - `--rm`: Remove o contêiner após a execução para evitar acúmulo de lixo.
>   - `--env-file .env`: Carrega as variáveis de ambiente (suas chaves de API) de forma segura.
>   - `-v ./data:/app/data`: Mapeia a pasta `data` local para a pasta `data` dentro do contêiner, garantindo que os resultados sejam salvos na sua máquina.

Após a execução, os arquivos `.csv` com os resultados estarão na sua pasta `data/`.

-----

### Método 2: Construindo a Imagem Docker Localmente

Se preferir construir a imagem a partir do código-fonte.

**1. Construa a Imagem Docker:**
Na raiz do projeto, execute o seguinte comando. Isso precisa ser feito apenas uma vez.

```bash
docker build -t nemoguard-eval .
```

**2. Execute o Teste Rápido (Verificação):**
Este teste valida seu ambiente e suas chaves de API em uma pequena amostra.

```bash
docker run --rm \
    -e OPENAI_API_KEY="sua_chave_openai_aqui" \
    -e NVIDIA_API_KEY="sua_chave_nvidia_aqui" \
    -v ./data:/app/data \
    nemoguard-eval \
    --exp-name "default" --test
```

> **Nota:** A flag `-e` permite passar variáveis de ambiente diretamente. Use este método se não quiser criar um arquivo `.env`.
>
>   - **Tempo Esperado:** 2-5 minutos.
>   - **Resultado Esperado:** Arquivos `prompts_seguros_default.csv` e `evaluations_final_test_default.csv` serão criados na sua pasta `data/`.

**3. Execute o Pipeline Completo:**
Este comando gera o dataset completo usado no artigo. O pipeline é resumível e pode ser interrompido e reiniciado sem perda de progresso.

```bash
docker run --rm \
    -e OPENAI_API_KEY="sua_chave_openai_aqui" \
    -e NVIDIA_API_KEY="sua_chave_nvidia_aqui" \
    -v ./data:/app/data \
    nemoguard-eval \
    --exp-name "default"
```

>   - **Tempo Esperado:** Várias horas, dependendo da latência da API e dos limites de taxa.
>   - **Resultado Esperado:** O arquivo `data/evaluations_final_default.csv` será criado (ou completado), contendo o dataset final da avaliação.

### Método 3: Execução Local (Sem Docker)

Se preferir não usar Docker, siga os passos abaixo.

**1. Prepare o Ambiente:**
Clone o repositório, crie um ambiente virtual, instale as dependências e crie seu arquivo `.env` com as chaves de API.

```bash
git clone <URL_DO_REPOSITORIO>
cd <NOME_DO_REPOSITORIO>
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Agora, edite o arquivo .env com suas chaves
```

**2. Execute o Teste Rápido:**

```bash
python main.py --test
```

**3. Execute o Pipeline Completo:**

```bash
python main.py
```

> O tempo e os resultados esperados são idênticos aos da execução com Docker.

### Executando Experimentos Customizados

O pipeline permite total controle sobre os parâmetros para facilitar a experimentação.

**Exemplo:** Para gerar prompts mais curtos e usar o `gpt-4o` para as respostas:

```bash
# Via Docker
docker run --rm -e ... -v ... nemoguard-eval --exp-name "prompts_curtos_gpt4o" --gen-max-tokens 50 --resp-model "gpt-4o"

# Localmente
python main.py --exp-name "prompts_curtos_gpt4o" --gen-max-tokens 50 --resp-model "gpt-4o"
```

**Argumentos da Linha de Comando:**

| Argumento          | Padrão (Default) | Descrição                                                       |
| ------------------ | ---------------- | --------------------------------------------------------------- |
| `--test`           | (Nenhum)         | Ativa o modo de teste com uma pequena amostra de dados.           |
| `--exp-name`       | `"default"`      | Nome do experimento, usado para nomear os arquivos de saída.      |
| `--gen-model`      | `"gpt-4o-mini"`  | Modelo da OpenAI para **gerar** os prompts seguros (Etapa 1).   |
| `--gen-temp`       | `0.7`            | Temperatura para a geração de prompts (Etapa 1).                  |
| `--gen-max-tokens` | `100`            | Máximo de tokens para a geração de prompts (Etapa 1).             |
| `--resp-model`     | `"gpt-4o-mini"`  | Modelo da OpenAI para **gerar** as respostas (Etapa 2).         |
| `--resp-temp`      | `0.0`            | Temperatura para a geração de respostas (Etapa 2).                |

### Passo Final: Análise e Validação das Reivindicações

Com o dataset final gerado (`evaluations_final_default.csv`), a análise para reproduzir as métricas e gráficos do artigo pode ser feita usando o notebook `analise_resultados.ipynb`.

> **Nota Importante:** Os plots gerados pelo notebook podem não ser esteticamente 100% idênticos aos do artigo, pois problemas técnicos impediram o uso do código de plotagem original. No entanto, os dados e as conclusões métricas são os mesmos.

-----

## License

Este projeto está licenciado sob a [Licença MIT](https://www.google.com/search?q=LICENSE).
