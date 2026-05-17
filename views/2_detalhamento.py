import streamlit as st
import plotly.express as px
import pandas as pd

st.title("📅 Análise Temporal Detalhada")

if "dados_shopee" not in st.session_state:
    st.warning("⚠️ Por favor, envie sua planilha na aba 'Visão Geral' para liberar as análises.")
    st.stop()

df = st.session_state["dados_shopee"].copy()

# --- EXTRAÇÃO DE COLUNAS DE TEMPO COMPLEMENTARES ---
df['Ano'] = df['Data de criação do pedido'].dt.year
df['Nome_Mes'] = df['Data de criação do pedido'].dt.strftime('%m - %B') # Ex: 05 - May
df['Data_Dia'] = df['Data de criação do pedido'].dt.date
df['Trimestre'] = df['Data de criação do pedido'].dt.to_period('Q').astype(str)

# --- BARRA LATERAL DE FILTROS DINÂMICOS ---
st.sidebar.header("Filtros Temporais")

# 1. Filtro de Ano
anos_disponiveis = sorted(df['Ano'].unique())
anos_selecionados = st.sidebar.multiselect("Selecione o Ano", options=anos_disponiveis, default=anos_disponiveis)
df_filtrado = df[df['Ano'].isin(anos_selecionados)]

# 2. Filtro de Mês (Baseado no ano escolhido acima)
meses_disponiveis = sorted(df_filtrado['Nome_Mes'].unique())
meses_selecionados = st.sidebar.multiselect("Selecione o Mês", options=meses_disponiveis, default=meses_disponiveis)
df_filtrado = df_filtrado[df_filtrado['Nome_Mes'].isin(meses_selecionados)]

# 3. Filtro Regional por Estado
st.sidebar.markdown("---")
ufs_selecionadas = st.sidebar.multiselect("Estados (UF)", options=sorted(df_filtrado["UF"].unique()), default=df_filtrado["UF"].unique())
df_filtrado = df_filtrado[df_filtrado["UF"].isin(ufs_selecionadas)]

if df_filtrado.empty:
    st.warning("Nenhum dado encontrado para os filtros selecionados.")
    st.stop()

# --- SISTEMA DE ABAS ---
aba_mensal, aba_trimestral, aba_anual = st.tabs(["📉 Visão Diária/Mensal", "📊 Visão Trimestral", "2026 Visão Anual"])

# 1. ABA MENSAL (AGORA COM FOCO EM VENDAS DIÁRIAS)
with aba_mensal:
    st.subheader("Performance Evolutiva por Dia")
    
    # 1.1 KPIs do intervalo selecionado nos filtros
    col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
    faturamento_mensal = df_filtrado['Valor Total'].sum()
    ticket_medio_m = faturamento_mensal / len(df_filtrado) if len(df_filtrado) > 0 else 0
    total_frete_m = df_filtrado['Taxa de envio pagas pelo comprador'].sum()
    
    col_kpi1.metric("Faturamento Filtrado", f"R$ {faturamento_mensal:,.2f}")
    col_kpi2.metric("Ticket Médio", f"R$ {ticket_medio_m:,.2f}")
    col_kpi3.metric("Frete do Período", f"R$ {total_frete_m:,.2f}")
    
    st.divider()
    
    # 1.2 Gráfico Principal: Vendas por Dia baseado no mês/ano filtrado
    vendas_por_dia = df_filtrado.groupby('Data_Dia')['Valor Total'].sum().reset_index()
    fig_dia = px.bar(
        vendas_por_dia, x='Data_Dia', y='Valor Total', 
        title='Faturamento Detalhado Dia a Dia',
        labels={'Valor Total': 'Faturamento (R$)', 'Data_Dia': 'Dias com Vendas'},
        text_auto='.2f'
    )
    st.plotly_chart(fig_dia, use_container_width=True)
    
    st.divider()
    
    # 1.3 Top 5 Produtos
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        top_qtd = df_filtrado.groupby('Nome do Produto')['Quantidade'].sum().sort_values(ascending=False).head(5).reset_index()
        fig_qtd = px.bar(top_qtd, x='Quantidade', y='Nome do Produto', orientation='h', title='Produtos mais Vendidos (Qtd)')
        fig_qtd.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_qtd, use_container_width=True)
    with col_g2:
        top_valor = df_filtrado.groupby('Nome do Produto')['Valor Total'].sum().sort_values(ascending=False).head(5).reset_index()
        fig_val = px.bar(top_valor, x='Valor Total', y='Nome do Produto', orientation='h', title='Produtos que mais Faturaram (R$)')
        fig_val.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_val, use_container_width=True)

# 2. ABA TRIMESTRAL
with aba_trimestral:
    st.subheader("Análise por Trimestre")
    
    col_kpi_t1, col_kpi_t2 = st.columns(2)
    col_kpi_t1.metric("Faturamento Acumulado", f"R$ {df_filtrado['Valor Total'].sum():,.2f}")
    col_kpi_t2.metric("Volume de Trimestres Ativos", df_filtrado['Trimestre'].nunique())
    
    st.divider()
    
    vendas_tri = df_filtrado.groupby('Trimestre')['Valor Total'].sum().reset_index()
    vendas_tri['Trimestre'] = vendas_tri['Trimestre'].str.replace('Q', ' - Trimestre ')
    fig_tri = px.bar(
        vendas_tri, x='Trimestre', y='Valor Total', 
        title='Faturamento por Trimestre Comercial', color='Trimestre', text_auto='.2f'
    )
    st.plotly_chart(fig_tri, use_container_width=True)

# 3. ABA ANUAL
with aba_anual:
    st.subheader("Fechamento Anual")
    
    col_kpi_a1, col_kpi_a2 = st.columns(2)
    col_kpi_a1.metric("Faturamento Histórico", f"R$ {df_filtrado['Valor Total'].sum():,.2f}")
    col_kpi_a2.metric("Anos Analisados", df_filtrado['Ano'].nunique())
    
    st.divider()
    
    vendas_ano = df_filtrado.groupby('Ano')['Valor Total'].sum().reset_index()
    vendas_ano['Ano'] = vendas_ano['Ano'].astype(str)
    fig_ano = px.line(vendas_ano, x='Ano', y='Valor Total', title='Evolução de Faturamento Anual', markers=True)
    st.plotly_chart(fig_ano, use_container_width=True)