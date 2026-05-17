import streamlit as st
import streamlit_authenticator as stauth
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configuração da página
st.set_page_config(page_title="Dashboard Shopee Analytics", layout="wide")

# 1. Conexão com o Google Sheets (Base de Usuários)
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_usuarios = conn.read()
    
    credentials = {"usernames": {}}
    for _, row in df_usuarios.iterrows():
        credentials["usernames"][str(row['username'])] = {
            "name": row['name'],
            "password": str(row['password']),
            "email": row['email']
        }
except Exception as e:
    st.error(f"Erro ao conectar à base de usuários: {e}")
    st.stop()

# 2. Configuração do Autenticador (Versão Atualizada)
authenticator = stauth.Authenticate(
    credentials=credentials,
    cookie_name="shopee_dashboard_cookie",
    key="chave_secreta_configurada_123",
    cookie_expiry_days=30
)

# 3. Renderiza a tela de login
authenticator.login()

# 4. Controle de Acesso via Session State
if st.session_state.get("authentication_status"):
    authenticator.logout("Sair", "sidebar")
    st.title(f"📊 Dashboard de Vendas — Bem-vindo, {st.session_state.get('name')}")
    
    # --- ÁREA DE UPLOAD DO ARQUIVO SHOPEE ---
    st.markdown("### 1. Envie o relatório da Shopee")
    uploaded_file = st.file_uploader("Selecione o arquivo .xlsx gerado na Central do Vendedor", type="xlsx")
    
    if uploaded_file:
        try:
            # Lendo o arquivo Excel da Shopee
            df = pd.read_excel(uploaded_file)
            
            st.success("Arquivo carregado com sucesso!")
            
            st.markdown("### 2. Visão Geral dos Dados")
            st.dataframe(df.head())
            
        except Exception as e:
            st.error(f"Erro ao processar o arquivo Excel: {e}")
            
elif st.session_state.get("authentication_status") is False:
    st.error("Usuário ou senha incorretos")
elif st.session_state.get("authentication_status") is None:
    st.warning("Por favor, insira seu usuário e senha")