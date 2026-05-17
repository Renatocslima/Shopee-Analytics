import streamlit as st
import streamlit_authenticator as stauth
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Shopee Analytics MVP", layout="wide")

# Conexão Segura usando os Secrets privados
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # Lendo a aba de forma explícita. O conector cuidará da segurança.
    df_usuarios = conn.read(worksheet=0)
    
    credentials = {"usernames": {}}
    for _, row in df_usuarios.iterrows():
        credentials["usernames"][str(row['username']).strip()] = {
            "name": row['name'],
            "password": str(row['password']).strip(),
            "email": row['email']
        }
except Exception as e:
    st.error(f"Erro seguro de conexão: {e}")
    st.stop()

authenticator = stauth.Authenticate(
    credentials=credentials,
    cookie_name="shopee_dashboard_cookie",
    key="chave_secreta_configurada_123",
    cookie_expiry_days=30
)

authenticator.login()

if st.session_state.get("authentication_status"):
    pg_visao_geral = st.Page("views/1_visao_geral.py", title="Visão Geral", icon="📊", default=True)
    pg_detalhes = st.Page("views/2_detalhamento.py", title="Análise Temporal", icon="📅")
    pg_feedback = st.Page("views/4_feedback.py", title="Enviar Feedback", icon="💬")

    navegacao = st.navigation({
        "Dashboards": [pg_visao_geral, pg_detalhes],
        "Suporte": [pg_feedback]
    })
    
    authenticator.logout("Desconectar do Painel", "sidebar")
    navegacao.run()
elif st.session_state.get("authentication_status") is False:
    st.error("Usuário ou senha incorretos.")
elif st.session_state.get("authentication_status") is None:
    st.warning("Por favor, insira suas credenciais de acesso.")