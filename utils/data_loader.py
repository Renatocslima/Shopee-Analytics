import streamlit as st
import streamlit_authenticator as stauth
from streamlit_gsheets import GSheetsConnection

# 1. Configuração da Página
st.set_page_config(page_title="Shopee Analytics MVP", layout="wide")

# 2. Conexão Base de Usuários (Google Sheets) com colunas corretas
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # Lendo com ttl=0 para pegar o usuário 'teste' na hora
    df_usuarios = conn.read(worksheet="Usuarios", ttl=0)
    
    # Mapeando os nomes exatos das colunas da sua imagem (username, password, name, email)
    credentials = {"usernames": {}}
    for _, row in df_usuarios.iterrows():
        credentials["usernames"][str(row['username']).strip()] = {
            "name": row['name'],
            "password": str(row['password']).strip(),
            "email": row['email']
        }
except Exception as e:
    st.error(f"Erro de conexão com o banco de usuários: {e}")
    st.stop()

# 3. Inicialização do Autenticador Oficial (Trata senhas criptografadas $2b$12$)
authenticator = stauth.Authenticate(
    credentials=credentials,
    cookie_name="shopee_dashboard_cookie",
    key="chave_secreta_configurada_123",
    cookie_expiry_days=30
)

# Renderiza a interface padrão de Login
authenticator.login()

# 4. Controle de Rotas se Estiver Logado
if st.session_state.get("authentication_status"):
    
    # Define os caminhos modulares das suas views
    pg_visao_geral = st.Page("views/1_visao_geral.py", title="Visão Geral", icon="📊", default=True)
    pg_detalhes = st.Page("views/2_detalhamento.py", title="Análise Temporal", icon="📅")
    pg_feedback = st.Page("views/4_feedback.py", title="Enviar Feedback", icon="💬")

    # Inicializa o menu lateral integrado
    navegacao = st.navigation(
        {
            "Dashboards": [pg_visao_geral, pg_detalhes],
            "Suporte": [pg_feedback]
        }
    )
    
    # Botão de deslogar na barra lateral
    authenticator.logout("Desconectar do Painel", "sidebar")
    
    # Executa a view selecionada
    navegacao.run()

elif st.session_state.get("authentication_status") is False:
    st.error("Usuário ou senha incorretos.")
elif st.session_state.get("authentication_status") is None:
    st.warning("Por favor, insira suas credenciais de acesso.")