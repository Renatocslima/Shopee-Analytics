import streamlit as st
import plotly.express as px
import pandas as pd

st.title("📅 Análise Temporal Detalhada")

if "dados_shopee" not in st.session_state:
    st.warning("⚠️ Por favor, envie sua planilha na aba 'Visão Geral' para liberar as análises.")
    st.stop()

df = st.session_state["dados_shopee"].copy()

# --- CRIAÇÃO DAS COLUNAS TEMPORAIS ---
# Garante que as datas sejam lidas como datas e extrai os períodos
df['Ano'] = df['Data de criação do pedido'].dt.year
df['Mês/Ano'] = df['Data de criação do pedido'].dt.strftime('%m/%Y')
df['Trimestre'] = df['Data de criação do pedido'].dt.to_period('Q').astype(str)

# --- BARRA LATERAL DE FILTROS ---
st.sidebar.header("Filtros Avançados")
ufs_selecionadas = st.sidebar.multiselect("Estados (UF)", options=sorted(df["UF"].unique()), default=df["UF"].unique())
df_filtrado = df[df["UF"].isin(ufs_selecionadas)]

if df_filtrado.empty:
    st.warning("Nenhum dado encontrado para os filtros selecionados.")
    st.stop()

# --- SISTEMA DE ABAS ---
aba_mensal, aba_trimestral, aba_anual = st.tabs(["📉 Visão Mensal", "📊 Visão Trimestral", "📆 Visão Anual"])

# 1. ABA MENSAL
with aba_mensal:
    st.subheader("Performance por Mês")
    
    # Agrupa faturamento por Mês/Ano
    vendas_mes = df_filtrado.groupby('Mês/Ano')['Valor Total'].sum().reset_index()
    
    fig_mes = px.bar(
        vendas_mes, 
        x='Mês/Ano', 
        y='Valor Total', 
        title='Faturamento Consolidado por Mês',
        labels={'Valor Total': 'Faturamento (R$)', 'Mês/Ano': 'Período'},
        text_auto='.2f'
    )
    st.plotly_chart(fig_mes, use_container_width=True)
    
    # Detalhe de produtos no mês
    col1, col2 = st.columns(2)
    with col1:
        top_produtos = df_filtrado.groupby('Nome do Produto')['Quantidade'].sum().sort_values(ascending=False).head(5).reset_index()
        fig_prod = px.bar(top_produtos, x='Quantidade', y='Nome do Produto', orientation='h', title='Top 5 Produtos do Período')
        st.plotly_chart(fig_prod, use_container_width=True)
    with col2:
        ticket_medio = df_filtrado['Valor Total'].sum() / len(df_filtrado) if len(df_filtrado) > 0 else 0
        st.metric("Ticket Médio Geral", f"R$ {ticket_medio:,.2f}")
        st.metric("Total de Frete Pago", f"R$ {df_filtrado['Taxa de envio pagas pelo comprador'].sum():,.2f}")

# 2. ABA TRIMESTRAL
with aba_trimestral:
    st.subheader("Análise por Trimestre (Sazonalidade)")
    
    # Agrupa faturamento por Trimestre (Ex: 2026Q1, 2026Q2)
    vendas_tri = df_filtrado.groupby('Trimestre')['Valor Total'].sum().reset_index()
    
    # Organiza a nomenclatura para ficar mais amigável (Ex: 2026-Q1)
    vendas_tri['Trimestre'] = vendas_tri['Trimestre'].str.replace('Q', ' - Trimestre ')
    
    fig_tri = px.bar(
        vendas_tri, 
        x='Trimestre', 
        y='Valor Total', 
        title='Faturamento por Trimestre Comercial',
        color='Trimestre',
        text_auto='.2f'
    )
    st.plotly_chart(fig_tri, use_container_width=True)

# 3. ABA ANUAL
with aba_anual:
    st.subheader("Fechamento Macroeconômico Anual")
    
    # Agrupa faturamento por Ano
    vendas_ano = df_filtrado.groupby('Ano')['Valor Total'].sum().reset_index()
    vendas_ano['Ano'] = vendas_ano['Ano'].astype(str) # Evita que o gráfico mostre 2025.5
    
    fig_ano = px.line(
        vendas_ano, 
        x='Ano', 
        y='Valor Total', 
        title='Evolução de Faturamento Anual',
        markers=True
    )
    fig_ano.update_traces(textposition="top center")
    st.plotly_chart(fig_ano, use_container_width=True)