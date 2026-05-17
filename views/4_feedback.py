import streamlit as st

st.title("💬 Central de Feedback")
st.write("Ajude-nos a melhorar o produto MVP. Deixe sua sugestão ou reporte um problema abaixo.")

with st.form("form_feedback", clear_on_submit=True):
    tipo = st.selectbox("Tipo de Feedback", ["Sugestão de Gráfico", "Bug/Erro na Planilha", "Outro"])
    mensagem = st.text_area("Descreva detalhadamente o que você precisa")
    submetido = st.form_submit_button("Enviar Sugestão")
    
    if submetido:
        st.success("Obrigado! Seu feedback foi registrado e será analisado para as próximas atualizações.")