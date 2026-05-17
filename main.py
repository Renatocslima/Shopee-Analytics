import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURAÇÃO DA PÁGINA (Deve ser o primeiro comando Streamlit) ---
st.set_page_config(
    page_title="Shopee Analytics",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- INICIALIZAÇÃO DO ESTADO DE SESSÃO ---
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
if "usuario_atual" not in st.session_state:
    st.session_state["usuario_atual"] = None

# --- FUNÇÃO PARA CARREGAR USUÁRIOS (COM TRATAMENTO DE ERRO 400) ---
def carregar_usuarios():
    try:
        # Criamos a conexão pura
        conn = st.connection("gsheets", type=GSheetsConnection)
        
        # Lemos a aba 'Usuarios' zerando o TTL (Time-To-Live) para ignorar o cache local
        df = conn.read(worksheet="Usuarios", ttl=0)
        
        # Limpeza preventiva de dados: remove linhas vazias e espaços invisíveis
        df = df.dropna(subset=["usuario", "senha"])
        df["usuario"] = df["usuario"].astype(str).str.strip()
        df["senha"] = df["senha"].astype(str).str.strip()
        
        return df
    except Exception as e:
        # Se der erro 400 ou qualquer outro, exibe o aviso mas não trava o app completamente
        st.error(f"⚠️ Erro de comunicação com o banco de dados (Google Sheets). Detalhes: {e}")
        st.info("💡 Dica: Verifique se o nome da aba na planilha é exatamente 'Usuarios' e se não há colunas corrompidas.")
        return pd.DataFrame(columns=["usuario", "senha"])

# --- TELA DE LOGIN ---
def tela_login():
    st.markdown("<h2 style='text-align: center;'>🔑 Acesso ao Painel Shopee</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.form("form_login", clear_on_submit=False):
            usuario_input = st.text_input("Usuário").strip()
            senha_input = st.text_input("Senha", type="password").strip()
            botao_entrar = st.form_submit_button("Entrar no Painel")
            
            if botao_entrar:
                if not usuario_input or not senha_input:
                    st.warning("Por favor, preencha todos os campos.")
                else:
                    # Busca a base de dados atualizada em tempo real
                    df_usuarios = carregar_usuarios()
                    
                    if not df_usuarios.empty:
                        # Validação de credenciais
                        usuario_valido = df_usuarios[
                            (df_usuarios["usuario"] == usuario_input) & 
                            (df_usuarios["senha"] == senha_input)
                        ]
                        
                        if not usuario_valido.empty:
                            st.session_state["autenticado"] = True
                            st.session_state["usuario_atual"] = usuario_input
                            st.success("Login efetuado com sucesso! Redirecionando...")
                            st.rerun()
                        else:
                            st.error("❌ Usuário ou senha incorretos. Se acabou de criar o usuário, verifique espaços extras na planilha.")
                    else:
                        st.error("Não foi possível validar as credenciais pois a tabela de usuários está inacessível.")

# --- FLUXO PRINCIPAL DE NAVEGAÇÃO ---
if not st.session_state["autenticado"]:
    tela_login()
else:
    # Barra lateral de navegação interna e Logout
    st.sidebar.markdown(f"👤 **Usuário:** `{st.session_state['usuario_atual']}`")
    if st.sidebar.button("🚪 Sair / Logoff"):
        st.session_state["autenticado"] = False
        st.session_state["usuario_atual"] = None
        st.rerun()
    
    st.sidebar.markdown("---")
    
    # Definição das páginas usando o novo sistema de navegação do Streamlit
    paginas = {
        "Análises Operacionais": [
            st.Page("views/1_visao_geral.py", title="📊 Visão Geral", icon="📈"),
            st.Page("views/2_detalhamento.py", title="📅 Análise Detalhada", icon="📅"),
        ],
        "Suporte e Opinião": [
            st.Page("views/4_feedback.py", title="💬 Enviar Feedback", icon="💬"),
        ]
    }
    
    # Inicializa e executa o roteador de páginas do Streamlit
    navegacao = st.navigation(paginas)
    navegacao.run()