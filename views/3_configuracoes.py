import streamlit as st

st.title("⚙️ Configurações da Conta")
st.subheader("Dados do Perfil")
st.write(f"**Usuário Conectado:** {st.session_state.get('username')}")
st.write(f"**Nome do Titular:** {st.session_state.get('name')}")

st.divider()
st.info("Nas próximas fases, aqui o cliente gerenciará tokens de API e chaves de integração automática da Shopee.")