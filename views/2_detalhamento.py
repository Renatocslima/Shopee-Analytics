import streamlit as st
import plotly.express as px

st.title("📅 Análise Temporal Detalhada")

if "dados_shopee" not in st.session_state:
    st.warning("⚠️ Por favor, envie sua planilha na aba 'Visão Geral' para liberar as análises.")
    st.stop()

df = st.session_state["dados_shopee"]

# Filtros avançados exclusivos desta página na Sidebar
st.sidebar.header("Filtros Avançados")
ufs_selecionadas = st.sidebar.multiselect("Estados (UF)", options=sorted(df["UF"].unique()), default=df["UF"].unique())
df_filtrado = df[df["UF"].isin(ufs_selecionadas)]

# Sistema de Sub-páginas em Abas (Tabs)
aba_mensal, aba_trimestral, aba_anual = st.tabs(["📉 Visão Mensal", "📊 Visão Trimestral", "📆 Visão Anual"])

with aba_mensal:
    st.subheader("Performance Mensal")
    col1, col2 = st.columns(2)
    
    # Custo de Frete aproximado
    total_frete = df_filtrado['Taxa de envio pagas pelo comprador'].sum()
    col1.metric("Custo Total de Frete", f"R$ {total_frete:,.2f}")
    
    # Cálculo simples de Ticket Médio
    ticket_medio = df_filtrado['Valor Total'].sum() / len(df_filtrado) if len(df_filtrado) > 0 else 0
    col2.metric("Ticket Médio por Venda", f"R$ {ticket_medio:,.2f}")

    # Top Produtos
    top_produtos = df_filtrado.groupby('Nome do Produto')['Quantidade'].sum().sort_values(ascending=False).head(5).reset_index()
    fig_prod = px.bar(top_produtos, x='Quantidade', y='Nome do Produto', orientation='h', title='Top 5 Produtos')
    st.plotly_chart(fig_prod, use_container_width=True)

with aba_trimestral:
    st.subheader("Análise Trimestral de Crescimento")
    st.info("Espaço reservado para agrupamentos por períodos sazonais (Q1, Q2, Q3, Q4).")

with aba_anual:
    st.subheader("Fechamento Consolidado do Ano")
    st.info("Espaço reservado para análise macro anual.")