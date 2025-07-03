# 🍺 Breweries Medallion ETL

Projeto de pipeline ETL usando Apache Airflow, PySpark e o padrão Medallion Architecture (**Bronze, Silver, Gold**), extraindo e processando dados da [Open Brewery DB API](https://www.openbrewerydb.org/).  
Inclui orquestração de tarefas, particionamento eficiente dos dados e sistema de alertas por e-mail em caso de falha.

---

## 📋 Sumário

- [Visão Geral](#visão-geral)
- [Arquitetura](#arquitetura)
- [Como Rodar Localmente (Docker)](#como-rodar-localmente-docker)
- [Parâmetros & Customização](#parâmetros--customização)
- [Alertas por E-mail (Airflow)](#alertas-por-e-mail-airflow)
- [Estrutura de Pastas](#estrutura-de-pastas)
- [Exemplo de Execução Manual](#exemplo-de-execução-manual)
- [FAQ e Troubleshooting](#faq-e-troubleshooting)
- [Créditos](#créditos)

---

## Visão Geral

Este pipeline realiza:

1. **Extração** de dados públicos da Open Brewery DB (API REST)
2. **Armazenamento bruto** (Bronze), **limpeza e normalização** (Silver) e **agregação** (Gold) dos dados
3. **Orquestração** das etapas via Apache Airflow
4. **Particionamento** eficiente por `state` e `data`
5. **Alertas automáticos** por e-mail em caso de falha na DAG

---

## Arquitetura

- **Bronze:** Dados brutos extraídos da API, salvos como JSON, particionados por estado e data (`state`, `dt`)
- **Silver:** Dados limpos e normalizados com PySpark, persistidos como Parquet, com deduplicação, timestamp de ingestão e tipagem correta
- **Gold:** Tabelas agregadas por estado e tipo de cervejaria (`brewery_type`), com contagem e datas envolvidas, prontas para análise e visualização

API -> Airflow (extract.py) -> Bronze (JSON)
|
transform.py
↓
Silver (Parquet normalizado)
|
load.py
↓
Gold (Parquet agregado)

yaml
Copiar
Editar

---

## Como Rodar Localmente (Docker)

**Pré-requisitos:**  
- [Docker](https://www.docker.com/) e [Docker Compose](https://docs.docker.com/compose/)

**Passos:**

1. **Clone o repositório:**
    ```bash
    git clone https://github.com/seuusuario/breweries-medallion-etl.git
    cd breweries-medallion-etl
    ```

2. **Configure o e-mail de alerta** (opcional, mas recomendado!)  
   Edite o `docker-compose.yml` com seu e-mail e senha de app:

    ```yaml
    environment:
      AIRFLOW__SMTP__SMTP_HOST: "smtp.gmail.com"
      AIRFLOW__SMTP__SMTP_STARTTLS: "True"
      AIRFLOW__SMTP__SMTP_SSL: "False"
      AIRFLOW__SMTP__SMTP_PORT: "587"
      AIRFLOW__SMTP__SMTP_MAIL_FROM: "seu_email@gmail.com"
      AIRFLOW__SMTP__SMTP_USER: "seu_email@gmail.com"
      AIRFLOW__SMTP__SMTP_PASSWORD: "sua_senha_app"
    ```

    > Para Gmail, gere uma [senha de app](https://support.google.com/accounts/answer/185833).

3. **Suba os containers:**
    ```bash
    docker compose up --build
    ```

4. **Acesse o Airflow:**  
    Abra [http://localhost:8080](http://localhost:8080) (usuário/senha padrão: `airflow` / `airflow`)

5. **Ative a DAG `breweries_medallion_etl` e execute**.

---

## Parâmetros & Customização

O pipeline permite processar **intervalos de datas**:

- Para rodar manualmente um intervalo de datas pelo Airflow UI:
    - Clique em "**Trigger DAG w/ config**"  
    - Exemplo de payload:
      ```json
      {
        "start_date": "2025-07-01",
        "end_date": "2025-07-03"
      }
      ```
- Se rodar sem parâmetros, o pipeline processa o dia corrente.

---

## Alertas por E-mail (Airflow)

O projeto já está configurado para enviar alertas de falha por e-mail:

- **Alterar destinatário:** Edite o campo `email` no bloco `default_args` da DAG.
- **Customização de mensagem:** Personalize a função de callback, se desejar um corpo de e-mail customizado.

---

## Estrutura de Pastas

.
├── dags/
│ └── breweries_etl.py # DAG Airflow principal
├── src/
│ ├── extract.py # Extração Bronze
│ ├── transform.py # Normalização Silver
│ └── load.py # Agregação Gold
├── data/
│ ├── bronze/ # Dados brutos
│ ├── silver/ # Dados tratados
│ └── gold/ # Dados agregados
├── logs/
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md

yaml
Copiar
Editar

---

## Exemplo de Execução Manual

Via terminal, dentro do container:

```bash
# Para extrair um intervalo específico de datas
docker exec -it breweries_airflow bash
python src/extract.py --start_date 2025-07-01 --end_date 2025-07-03

# Para transformar apenas um range:
spark-submit src/transform.py --start_date 2025-07-01 --end_date 2025-07-03

# Para gerar o gold apenas para um intervalo:
spark-submit src/load.py 2025-07-01 2025-07-03
FAQ e Troubleshooting
Não recebo e-mails de erro:

Confira variáveis SMTP (host, porta, senha, e-mail).

Verifique o log do Airflow e o spam da sua caixa.

Erro de permissão nos diretórios /data:

Verifique se a pasta está criada no host e tem permissão de escrita.

Faltam pacotes no container:

Adicione ao requirements.txt e reinicie com docker compose up --build.

Problemas ao rodar Spark com datasets grandes:

Ajuste o parâmetro N_PARTITIONS no extract.py ou aumente recursos do container.

Créditos
Desenvolvido por Seu Nome
Inspirado no modelo Medallion do Databricks e boas práticas de Engenharia de Dados.

Pull requests e sugestões são bem-vindas!

yaml
Copiar
Editar

---

Se quiser, posso adaptar ainda mais para o padrão de README da sua empresa, incluir GIFs/screenshots, instruções para rodar no cloud, etc.  
Só pedir!