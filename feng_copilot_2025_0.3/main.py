import streamlit as st
from dotenv import load_dotenv
from functions import criar_assistente_personalizado, realizar_consulta_assistente, executar_query, gerar_excel_download

load_dotenv()

st.set_page_config(page_title="Consultas com LLM + DW", page_icon="🤖")
st.title("🔍FENG - Assistente IA")
st.write("Faça uma pergunta para gerar a query!")

# Inicializar assistente apenas uma vez
if "assistant_id" not in st.session_state:
    assistant_id = criar_assistente_personalizado()
    st.session_state.assistant_id = assistant_id
    st.success(f"🧠 Assistente criado com ID: {assistant_id}")

# Inicializar thread apenas uma vez por sessão
if "thread_id" not in st.session_state:
    st.session_state.thread_id = None

# Botão para reiniciar a sessão
if st.button("🔁 Nova sessão"):
    st.session_state.thread_id = None
    st.success("🆕 Sessão reiniciada.")

# Campo de pergunta
prompt_usuario = st.text_input("🗣️ Escreva sua pergunta:", placeholder="Ex: Quantos sócios temos no sistema?")

if st.button("Enviar Consulta"):
    if not prompt_usuario.strip():
        st.warning("Por favor, insira uma pergunta válida.")
    else:
        with st.spinner("⚙️ Processando..."):
            try:
                resposta, thread_id = realizar_consulta_assistente(prompt_usuario, st.session_state.assistant_id)
                st.session_state.thread_id = thread_id
                st.subheader("📜 Query gerada pelo assistente:")
                st.code(resposta, language="sql")

                df_resultado = executar_query(resposta)
                if df_resultado.empty:
                    st.info("⚠️ Nenhum dado retornado.")
                else:
                    st.subheader("📊 Resultado:")
                    st.dataframe(df_resultado)
                    
                    excel_data = gerar_excel_download(df_resultado)
                    st.download_button(
                        label="📥 Baixar em Excel",
                        data=excel_data,
                        file_name="resultado_query.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

            except Exception as e:
                st.error(f"❌ Erro: {e}")
