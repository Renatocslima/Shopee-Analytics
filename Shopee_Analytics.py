import streamlit as st
import streamlit_authenticator as stauth
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px

# Configuração da página
st.set_page_config(page_title="Dashboard Shopee MVP", layout="wide")

# 1. Conexão com o Google Sheets (Usuários)
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
    st.error("Erro ao conectar à base de usuários.")
    st.stop()

# 2. Configura o Autenticador
authenticator = stauth.Authenticate(
    credentials,
    "shopee_dashboard_cookie",
    "chave_secreta_configurada_123",
    cookie_expiry_days=30
)

name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status:
    authenticator.logout("Sair", "sidebar")
    st.title(f"📊 Dashboard de Vendas — Bem-vindo, {name}")
    
    # --- ÁREA DE UPLOAD DO ARQUIVO SHOPEE ---
    st.markdown("### 1. Envie o relatório da Shopee")
    uploaded_file = st.file_uploader("Arraste ou selecione o arquivo .xlsx gerado na Central do Vendedor", type="xlsx")
    
    if uploaded_file:
        try:
            # Lendo o arquivo Excel da Shopee
            df = pd.read_excel(uploaded_file)
            
            st.success("Arquivo carregado com sucesso!")
            
            # TODO: Ajustar os nomes exatos das colunas conforme o arquivo real da Shopee
            st.markdown("### 2. Análise de Dados (Exemplo)")
            st.dataframe(df.head())
            
        except Exception as e:
            st.error(f"Erro ao processar o arquivo Excel: {e}")
            
elif authentication_status == False:
    st.error("Usuário ou senha incorretos")
elif authentication_status == None:
    st.warning("Por favor, insira seu usuário e senha")