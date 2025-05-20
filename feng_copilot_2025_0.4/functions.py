import os
import pandas as pd
import io

from sqlalchemy import create_engine, text
from openai import OpenAI
from dotenv import load_dotenv
from instructions import instrucoes_assistente


load_dotenv()


client = OpenAI(
    organization=os.getenv("OPENAI_ORGANIZATION"),
    project=os.getenv("OPENAI_PROJECT")
)


def connect_dw():
    return create_engine(
        f"snowflake://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}?warehouse={os.getenv('DB_WAREHOUSE')}"
    )


def executar_query(query):
    conn = connect_dw()
    with conn.connect() as sql:
        try:
            result = sql.execute(text(query))
            columns = result.keys()
            data = result.fetchall()
            return pd.DataFrame(data, columns=columns) if data else pd.DataFrame()
        except Exception as e:
            raise Exception(f"Erro ao executar a query: {e}")


def criar_assistente_personalizado():
    assistant = client.beta.assistants.create(
        name="Analista de Dados da Feng",
        instructions=instrucoes_assistente,
        tools=[{"type": "code_interpreter"}],
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
    )
    return assistant.id


def realizar_consulta_assistente(prompt_usuario, assistant_id):
    thread = client.beta.threads.create()
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=prompt_usuario
    )

    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id,
    )

    while run.status != "completed":
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

    messages = client.beta.threads.messages.list(thread_id=thread.id)
    return messages.data[0].content[0].text.value, thread.id


def gerar_excel_download(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Resultado')
    output.seek(0)
    return output