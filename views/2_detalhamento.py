import streamlit as st
import plotly.express as px
import pandas as pd

st.title("📅 Análise Temporal Detalhada")

if "dados_shopee" not in st.session_state:
    st.warning("⚠️ Por favor, envie sua planilha na aba 'Visão Geral' para liberar as análises.")
    st.stop()

df = st.session_state["dados_shopee"].copy()

# --- CRIAÇÃO DAS COLUNAS TEMPORAIS ---
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
    
    # 1.1 KPIs Primeiro
    col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
    faturamento_mensal = df_filtrado['Valor Total'].sum()
    ticket_medio_m = faturamento_mensal / len(df_filtrado) if len(df_filtrado) > 0 else 0
    total_frete_m = df_filtrado['Taxa de envio pagas pelo comprador'].sum()
    
    col_kpi1.metric("Faturamento do Período", f"R$ {faturamento_mensal:,.2f}")
    col_kpi2.metric("Ticket Médio por Venda", f"R$ {ticket_medio_m:,.2f}")
    col_kpi3.metric("Total de Frete Pago", f"R$ {total_frete_m:,.2f}")
    
    st.divider()
    
    # 1.2 Gráfico Principal
    vendas_mes = df_filtrado.groupby('Mês/Ano')['Valor Total'].sum().reset_index()
    fig_mes = px.bar(
        vendas_mes, x='Mês/Ano', y='Valor Total', 
        title='Faturamento Consolidado por Mês',
        labels={'Valor Total': 'Faturamento (R$)', 'Mês/Ano': 'Período'},
        text_auto='.2f'
    )
    st.plotly_chart(fig_mes, use_container_width=True)
    
    st.divider()
    
    # 1.3 Gráficos de Top 5 por Qtd e Valor
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        top_qtd = df_filtrado.groupby('Nome do Produto')['Quantidade'].sum().sort_values(ascending=False).head(5).reset_index()
        fig_qtd = px.bar(top_qtd, x='Quantidade', y='Nome do Produto', orientation='h', title='Top 5 Produtos (Por Quantidade)')
        fig_qtd.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_qtd, use_container_width=True)
    with col_g2:
        top_valor = df_filtrado.groupby('Nome do Produto')['Valor Total'].sum().sort_values(ascending=False).head(5).reset_index()
        fig_val = px.bar(top_valor, x='Valor Total', y='Nome do Produto', orientation='h', title='Top 5 Produtos (Por Faturamento)')
        fig_val.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_val, use_container_width=True)

# 2. ABA TRIMESTRAL
with aba_trimestral:
    st.subheader("Análise por Trimestre")
    
    # 2.1 KPIs Primeiro
    col_kpi_t1, col_kpi_t2 = st.columns(2)
    col_kpi_t1.metric("Faturamento Acumulado", f"R$ {df_filtrado['Valor Total'].sum():,.2f}")
    col_kpi_t2.metric("Volume de Trimestres Ativos", df_filtrado['Trimestre'].nunique())
    
    st.divider()
    
    # 2.2 Gráfico Principal
    vendas_tri = df_filtrado.groupby('Trimestre')['Valor Total'].sum().reset_index()
    vendas_tri['Trimestre'] = vendas_tri['Trimestre'].str.replace('Q', ' - Trimestre ')
    fig_tri = px.bar(
        vendas_tri, x='Trimestre', y='Valor Total', 
        title='Faturamento por Trimestre Comercial', color='Trimestre', text_auto='.2f'
    )
    st.plotly_chart(fig_tri, use_container_width=True)
    
    st.divider()
    
    # 2.3 Top 5 do Trimestre
    col_gt1, col_gt2 = st.columns(2)
    with col_gt1:
        top_qtd_t = df_filtrado.groupby('Nome do Produto')['Quantidade'].sum().sort_values(ascending=False).head(5).reset_index()
        fig_qtd_t = px.bar(top_qtd_t, x='Quantidade', y='Nome do Produto', orientation='h', title='Top 5 Trimestral (Por Qtd)')
        fig_qtd_t.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_qtd_t, use_container_width=True)
    with col_gt2:
        top_val_t = df_filtrado.groupby('Nome do Produto')['Valor Total'].sum().sort_values(ascending=False).head(5).reset_index()
        fig_val_t = px.bar(top_val_t, x='Valor Total', y='Nome do Produto', orientation='h', title='Top 5 Trimestral (Por Valor)')
        fig_val_t.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_val_t, use_container_width=True)

# 3. ABA ANUAL
with aba_anual:
    st.subheader("Fechamento Anual")
    
    # 3.1 KPIs Primeiro
    col_kpi_a1, col_kpi_a2 = st.columns(2)
    col_kpi_a1.metric("Faturamento Histórico Total", f"R$ {df_filtrado['Valor Total'].sum():,.2f}")
    col_kpi_a2.metric("Média de Faturamento Anual", f"R$ {(df_filtrado['Valor Total'].sum() / df_filtrado['Ano'].nunique()):,.2f}")
    
    st.divider()
    
    # 3.2 Gráfico Principal
    vendas_ano = df_filtrado.groupby('Ano')['Valor Total'].sum().reset_index()
    vendas_ano['Ano'] = vendas_ano['Ano'].astype(str)
    fig_ano = px.line(vendas_ano, x='Ano', y='Valor Total', title='Evolução de Faturamento Anual', markers=True)
    st.plotly_chart(fig_ano, use_container_width=True)
    
    st.divider()
    
    # 3.3 Top 5 do Ano
    col_ga1, col_ga2 = st.columns(2)
    with col_ga1:
        top_qtd_a = df_filtrado.groupby('Nome do Produto')['Quantidade'].sum().sort_values(ascending=False).head(5).reset_index()
        fig_qtd_a = px.bar(top_qtd_a, x='Quantidade', y='Nome do Produto', orientation='h', title='Top 5 Anual (Por Qtd)')
        fig_qtd_a.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_qtd_a, use_container_width=True)
    with col_ga2:
        top_val_a = df_filtrado.groupby('Nome do Produto')['Valor Total'].sum().sort_values(ascending=False).head(5).reset_index()
        fig_val_a = px.bar(top_val_a, x='Valor Total', y='Nome do Produto', orientation='h', title='Top 5 Anual (Por Valor)')
        fig_val_a.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_val_a, use_container_width=True)