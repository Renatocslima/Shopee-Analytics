import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

st.title("💬 Central de Feedback")
st.write("Ajude-nos a melhorar o produto MVP. Deixe sua sugestão ou reporte um problema abaixo.")

with st.form("form_feedback", clear_on_submit=True):
    tipo = st.selectbox("Tipo de Feedback", ["Sugestão de Gráfico", "Bug/Erro na Planilha", "Outro"])
    mensagem = st.text_area("Descreva detalhadamente o que você precisa")
    submetido = st.form_submit_button("Enviar Sugestão")
    
    if submetido:
        try:
            # Conecta na aba específica de Feedbacks
            conn = st.connection("gsheets", type=GSheetsConnection)
            df_feedbacks = conn.read(worksheet="Feedbacks")
            
            # Monta a nova linha de dados
            novo_feedback = pd.DataFrame([{
                "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "Usuario": st.session_state.get("username", "Desconhecido"),
                "Tipo": tipo,
                "Mensagem": mensagem
            }])
            
            # Adiciona a nova linha e atualiza a planilha
            df_atualizado = pd.concat([df_feedbacks, novo_feedback], ignore_index=True)
            conn.update(worksheet="Feedbacks", data=df_atualizado)
            
            st.success("Obrigado! Seu feedback foi enviado diretamente para a equipe de produto.")
        except Exception as e:
            st.error(f"Erro ao salvar feedback. Verifique se a aba 'Feedbacks' existe na planilha. Detalhe: {e}")