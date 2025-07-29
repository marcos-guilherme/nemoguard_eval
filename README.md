# Avaliação do NeMo Guardrails como um Firewall para a Interação Usuário-LLM

## Resumo

Este repositório contém o artefato para o artigo **"Avaliação do NeMo Guardrails como um Firewall para a Interação Usuário-LLM"**. O objetivo deste artefato é fornecer todo o código, dados e instruções para reproduzir os experimentos do artigo, permitindo a validação dos resultados apresentados.

**Resumo do Artigo:**
> Neste artigo é analisado o NeMo Guardrails, Modelo de Linguagem em Larga Escala (LLM) que tem como papel atuar como um firewall durante interações usuário-LLM. O objetivo é avaliar seu desempenho na identificação de tentativas maliciosas dentro do contexto dessas interações, como jailbreaking e prompt injection. Foi utilizado o Do Not Answer dataset para a tarefa de classificação do modelo dentre as classes Seguro ou Inseguro. A avaliação consistiu em uma análise por categoria de risco e do cálculo de métricas de classificação binária; e da Taxa de Compensação, uma nova métrica proposta neste trabalho. O F1 Score apresenta um possível trade-off entre Precisão e Sensibilidade.

---

## Estrutura do Repositório


-   `main.py`: O script principal (orquestrador) que executa todo o pipeline de ponta a ponta.
-   `analise_resultados.ipynb`: **(A ser anexado)** Um Notebook no Collab para carregar o dataset final e reproduzir os do artigo.
-   `requirements.txt`: Lista de todas as dependências Python necessárias.
-   `.env`: Arquivo local (não versionado) para armazenar as chaves de API. (Você deve criá-lo localmente)
-   `scripts/`: Diretório contendo os módulos com a lógica de negócio.
    -   `prompt_gen.py`: Responsável por gerar os prompts seguros sintéticos via API do GPT-4.
    -   `llm_prompt_response.py`: Responsável por obter as respostas do GPT-4 para um dado prompt.
    -   `nemo_eval.py`: Responsável por classificar a segurança de um texto com o NeMo Guardrails via API da NVIDIA.
-   `data/`: Diretório onde os dados gerados pelo pipeline são salvos.



## Selos Reivindicados

Este artefato foi preparado para atender aos critérios dos seguintes selos de avaliação:

-   [x] **Artefatos Disponíveis (SeloD)**
-   [x] **Artefatos Funcionais (SeloF)**
-   [x] **Artefatos Sustentáveis (SeloS)**
-   [x] **Artefatos Reprodutíveis (SeloR)**

---


---

## Configuração do Ambiente

### Informações Básicas
-   **Ambiente de Execução:** Testado em Windows 11 e Ubuntu 22.04.
-   **Requisitos de Hardware:**
    -   RAM: Mínimo de 4 GB.
    -   Disco: ~5 GB de espaço livre.
    -   Conexão estável com a internet (essencial para as APIs).
-   **Requisitos de Software:**
    -   Python 3.9+
    -   Recomenda-se o uso de um ambiente virtual (`venv`).

### Dependências
-   **Python:** Todas as bibliotecas estão em `requirements.txt`. A versão de cada uma está fixada para garantir a reprodutibilidade.
-   **Recursos de Terceiros:** A execução requer chaves de API para os serviços da **OpenAI (GPT-4)** e da **NVIDIA (NeMo Guardrails)**.

### Preocupações com Segurança
As chaves de API são informações sensíveis. O código foi projetado para carregá-las de um arquivo local `.env`, que não deve ser compartilhado. Os scripts não armazenam ou transmitem as chaves para nenhum outro lugar.

---

## Instalação

Siga os passos abaixo para configurar o ambiente.

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/seu-usuario/nemoguard_eval.git](https://github.com/seu-usuario/nemoguard_eval.git)
    cd nemoguard_eval
    ```

2.  **Crie e ative um ambiente virtual:**
    ```bash
    # Windows
    python -m venv venv
    .\venv\Scripts\activate

    # Linux/macOS
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure as chaves de API:**
    -   Crie um arquivo `.env` na raiz do projeto.
    -   Adicione suas chaves ao arquivo, seguindo este formato:
        ```
        OPENAI_API_KEY="sk-..."
        NVIDIA_API_KEY="nvapi-..."
        ```

---

## Fluxo de Reprodução dos Experimentos 

O fluxo para reproduzir os resultados do artigo é dividido em três passos claros: um teste mínimo para garantir que a instalação funcionou, a execução completa para gerar os dados, e a análise final em um notebook para validar as reivindicações.

### Passo 1: Teste Mínimo (Verificação da Instalação)

Este teste executa o pipeline em uma pequena amostra de dados para uma verificação rápida do ambiente e das chaves de API.

-   **Comando:**
    ```bash
    python main.py --test
    ```
-   **Tempo Esperado:** 1-3 minutos.
-   **Resultado Esperado:** Um arquivo `evaluations_final_test.csv` será criado na pasta `data/`. A ausência de erros críticos no log indica sucesso.

### Passo 2: Execução Completa do Pipeline (Geração dos Dados)

Esta etapa reproduz o dataset completo utilizado no artigo.

-   **Comando:**
    ```bash
    python main.py
    ```
-   Isso deve demorar um pouco, pois muitas requisicões serão executadas.
-   **Resultado Esperado:** O arquivo `data/evaluations_final.csv` será criado, contendo ~1878 linhas com os prompts, respostas e as classificações do NeMo. Este arquivo é o principal resultado do pipeline.

### Passo 3: Análise e Validação das Reivindicações (Reprodução dos Resultados)

Com o dataset final gerado, a análise para reproduzir as métricas do artigo pode ser feita livremente, como num notebook no collab ou o que preferir dado que neste momento o dataset está em mãos.

Os Plots presentes no notebook disponibilizado não estão esteticamente 100% fiéis aos que estão no artigo, pois problemas técnicos impediram o uso do código criado originalmente.

---

## LICENSE

