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
df['Nome_Mes'] = df['Data de criação do pedido'].dt.strftime('%m - %B')
df['Data_Dia'] = df['Data de criação do pedido'].dt.date
df['Trimestre'] = df['Data de criação do pedido'].dt.to_period('Q').astype(str)

# --- BARRA LATERAL DE FILTROS DINÂMICOS ---
st.sidebar.header("Filtros Temporais")

# 1. Filtro de Ano
anos_disponiveis = sorted(df['Ano'].dropna().unique())
anos_selecionados = st.sidebar.multiselect("Selecione o Ano", options=anos_disponiveis, default=anos_disponiveis)
df_filtrado = df[df['Ano'].isin(anos_selecionados)]

# 2. Filtro de Mês
meses_disponiveis = sorted(df_filtrado['Nome_Mes'].dropna().unique())
meses_selecionados = st.sidebar.multiselect("Selecione o Mês", options=meses_disponiveis, default=meses_disponiveis)
df_filtrado = df_filtrado[df_filtrado['Nome_Mes'].isin(meses_selecionados)]

# 3. Filtro de Status do Pedido
st.sidebar.markdown("---")
st.sidebar.header("Filtros de Operação")
status_disponiveis = sorted(df_filtrado['Status do pedido'].dropna().unique())
status_selecionados = st.sidebar.multiselect("Status do Pedido", options=status_disponiveis, default=status_disponiveis)
df_filtrado = df_filtrado[df_filtrado['Status do pedido'].isin(status_selecionados)]

# 4. Filtro Regional por Estado
ufs_selecionadas = st.sidebar.multiselect("Estados (UF)", options=sorted(df_filtrado["UF"].dropna().unique()), default=df_filtrado["UF"].unique())
df_filtrado = df_filtrado[df_filtrado["UF"].isin(ufs_selecionadas)]

if df_filtrado.empty:
    st.warning("Nenhum dado encontrado para os filtros selecionados.")
    st.stop()

# --- SISTEMA DE ABAS ---
aba_mensal, aba_trimestral, aba_anual = st.tabs(["📉 Visão Diária/Mensal", "📊 Visão Trimestral", "📆 Visão Anual"])

# 1. ABA MENSAL
with aba_mensal:
    st.subheader("Métricas Financeiras de Sucesso")
    
    # --- REGRAS DE NEGÓCIO PARA OS KPIs ---
    faturamento_bruto = df_filtrado['Valor Total'].sum()
    
    # Filtrando valores por status real de mercado (Correção feita aqui)
    vendas_reais = df_filtrado[df_filtrado['Status do pedido'] == 'Concluído']['Valor Total'].sum()
    vendas_perdidas = df_filtrado[df_filtrado['Status do pedido'] == 'Cancelado']['Valor Total'].sum()
    vendas_aguardando = df_filtrado[df_filtrado['Status do pedido'].isin(['A enviar', 'Processando', 'Pendente'])]['Valor Total'].sum()
    
    # Índice de Sucesso: O quanto do bruto realmente se converteu em Concluído
    indice_sucesso = (vendas_reais / faturamento_bruto * 100) if faturamento_bruto > 0 else 0
    
    # Renderização dos KPIs
    col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
    col_kpi1.metric("💰 Faturamento Real (Concluído)", f"R$ {vendas_reais:,.2f}")
    col_kpi2.metric("❌ Faturamento Perdido (Cancelado)", f"R$ {vendas_perdidas:,.2f}")
    col_kpi3.metric("⏳ Aguardando Envio", f"R$ {vendas_aguardando:,.2f}")
    col_kpi4.metric("🏆 Índice de Sucesso", f"{indice_sucesso:.1f}%")
    
    st.divider()
    
    # 1.2 Gráfico Principal: Vendas por Dia Dividido por Status coloridos
    st.subheader("Evolução Diária de Faturamento por Status")
    vendas_por_dia_status = df_filtrado.groupby(['Data_Dia', 'Status do pedido'])['Valor Total'].sum().reset_index()
    
    fig_dia = px.bar(
        vendas_por_dia_status, 
        x='Data_Dia', 
        y='Valor Total', 
        color='Status do pedido',
        title='Faturamento Detalhado Dia a Dia (Separado por Status)',
        labels={'Valor Total': 'Faturamento (R$)', 'Data_Dia': 'Dias com Vendas', 'Status do pedido': 'Status'},
        barmode='stack'
    )
    st.plotly_chart(fig_dia, use_container_width=True)
    
    st.divider()
    
    # 1.3 Top 5 Produtos Baseado Apenas em Vendas Reais (Concluídas)
    st.subheader("Análise de Mix (Apenas Vendas Concluídas)")
    df_concluidos = df_filtrado[df_filtrado['Status do pedido'] == 'Concluído']
    
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        top_qtd = df_concluidos.groupby('Nome do Produto')['Quantidade'].sum().sort_values(ascending=False).head(5).reset_index()
        fig_qtd = px.bar(top_qtd, x='Quantidade', y='Nome do Produto', orientation='h', title='Top 5 Produtos mais Entregues (Qtd)')
        fig_qtd.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_qtd, use_container_width=True)
    with col_g2:
        top_valor = df_concluidos.groupby('Nome do Produto')['Valor Total'].sum().sort_values(ascending=False).head(5).reset_index()
        fig_val = px.bar(top_valor, x='Valor Total', y='Nome do Produto', orientation='h', title='Top 5 Produtos Faturamento Líquido (R$)')
        fig_val.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_val, use_container_width=True)

# 2. ABA TRIMESTRAL
with aba_trimestral:
    st.subheader("Análise por Trimestre Comercial")
    
    vendas_tri_status = df_filtrado.groupby(['Trimestre', 'Status do pedido'])['Valor Total'].sum().reset_index()
    vendas_tri_status['Trimestre'] = vendas_tri_status['Trimestre'].str.replace('Q', ' - Trimestre ')
    
    fig_tri = px.bar(
        vendas_tri_status, 
        x='Trimestre', 
        y='Valor Total', 
        color='Status do pedido',
        title='Faturamento por Trimestre Comercial e Saúde de Entrega', 
        barmode='group' 
    )
    st.plotly_chart(fig_tri, use_container_width=True)

# 3. ABA ANUAL
with aba_anual:
    st.subheader("Fechamento Histórico Anual")
    
    vendas_ano_status = df_filtrado.groupby(['Ano', 'Status do pedido'])['Valor Total'].sum().reset_index()
    vendas_ano_status['Ano'] = vendas_ano_status['Ano'].astype(str)
    
    fig_ano = px.bar(
        vendas_ano_status, 
        x='Ano', 
        y='Valor Total', 
        color='Status do pedido',
        title='Evolução de Faturamento Anual por Status',
        barmode='stack'
    )
    st.plotly_chart(fig_ano, use_container_width=True)