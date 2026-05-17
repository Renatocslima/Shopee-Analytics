import streamlit as st
import streamlit_authenticator as stauth
from streamlit_gsheets import GSheetsConnection

# 1. Configuração Inicial do Dashboard
st.set_page_config(page_title="Shopee Analytics MVP", layout="wide")

# 2. Conexão Base de Usuários (Google Sheets)
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
    st.error(f"Erro de conexão com o banco de usuários: {e}")
    st.stop()

# 3. Inicialização do Autenticador
authenticator = stauth.Authenticate(
    credentials=credentials,
    cookie_name="shopee_dashboard_cookie",
    key="chave_secreta_configurada_123",
    cookie_expiry_days=30
)

# Renderiza Tela de Login
authenticator.login()

# 4. Estrutura de Navegação Multi-Páginas se Estiver Logado
if st.session_state.get("authentication_status"):
    
    # Criando os links para os arquivos das subpastas
    pg_visao_geral = st.Page("views/1_visao_geral.py", title="Visão Geral", icon="📊", default=True)
    pg_detalhes = st.Page("views/2_detalhamento.py", title="Análise Temporal", icon="📅")
    pg_config = st.Page("views/3_configuracoes.py", title="Configurações de Conta", icon="⚙️")
    pg_feedback = st.Page("views/4_feedback.py", title="Enviar Feedback", icon="💬")

    # Inicializa o menu dinâmico na lateral esquerda organizando por seções
    navegacao = st.navigation(
        {
            "Dashboards": [pg_visao_geral, pg_detalhes],
            "Gerenciamento": [pg_config, pg_feedback]
        }
    )
    
    # Botão de Logout fixo no topo da barra lateral esquerda
    authenticator.logout("Desconectar do Painel", "sidebar")
    
    # Executa a visualização do arquivo selecionado no menu
    navegacao.run()

elif st.session_state.get("authentication_status") is False:
    st.error("Usuário ou senha incorretos.")
elif st.session_state.get("authentication_status") is None:
    st.warning("Por favor, insira suas credenciais de acesso.")