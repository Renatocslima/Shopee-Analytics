import streamlit as st
import streamlit_authenticator as stauth
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px

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
    st.markdown("### Envie o relatório da Shopee")
    uploaded_file = st.file_uploader("Selecione o arquivo .xlsx gerado na Central do Vendedor", type="xlsx")
    
    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file)
            st.success("Arquivo carregado com sucesso!")
            
            # --- TRATAMENTO DE DADOS ---
            # Converte a coluna de data
            df['Data de criação do pedido'] = pd.to_datetime(df['Data de criação do pedido'], errors='coerce')
            
            # Limpa e converte a coluna de Valor Total (remove R$, pontos e ajusta vírgula)
            if df['Valor Total'].dtype == 'object':
                df['Valor Total'] = df['Valor Total'].astype(str).str.replace('R$', '', regex=False).str.replace('.', '', regex=False).str.replace(',', '.').astype(float)
            
            # --- KPIs PRINCIPAIS ---
            st.markdown("### 2. Resumo da Operação")
            col1, col2, col3 = st.columns(3)
            col1.metric("Faturamento Bruto", f"R$ {df['Valor Total'].sum():,.2f}")
            col2.metric("Total de Pedidos", df['ID do pedido'].nunique())
            col3.metric("Itens Vendidos", df['Quantidade'].sum())
            
            # --- GRÁFICOS ---
            st.markdown("### 3. Análises Detalhadas")
            
            # Gráfico 1: Vendas por Dia
            vendas_dia = df.groupby(df['Data de criação do pedido'].dt.date)['Valor Total'].sum().reset_index()
            fig_dia = px.line(vendas_dia, x='Data de criação do pedido', y='Valor Total', title='Faturamento por Dia')
            st.plotly_chart(fig_dia, use_container_width=True)
            
            col_graf1, col_graf2 = st.columns(2)
            
            # Gráfico 2: Top Produtos
            top_produtos = df.groupby('Nome do Produto')['Quantidade'].sum().sort_values(ascending=False).head(5).reset_index()
            fig_prod = px.bar(top_produtos, x='Quantidade', y='Nome do Produto', orientation='h', title='Top 5 Produtos mais Vendidos')
            fig_prod.update_layout(yaxis={'categoryorder':'total ascending'})
            col_graf1.plotly_chart(fig_prod, use_container_width=True)
            
            # Gráfico 3: Status dos Pedidos
            fig_status = px.pie(df, names='Status do pedido', title='Distribuição por Status')
            col_graf2.plotly_chart(fig_status, use_container_width=True)

        except Exception as e:
            st.error(f"Erro ao processar o arquivo Excel: {e}")
            
elif st.session_state.get("authentication_status") is False:
    st.error("Usuário ou senha incorretos")
elif st.session_state.get("authentication_status") is None:
    st.warning("Por favor, insira seu usuário e senha")