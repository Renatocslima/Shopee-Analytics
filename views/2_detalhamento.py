import streamlit as st
import plotly.express as px
import pandas as pd

# === VARIÁVEIS DE CORES (FÁCIL EDIÇÃO) ===
# Altere os códigos Hex para mudar as cores dos gráficos em todas as telas
CORES_STATUS = {
    "Concluído": "#2ecc71",    # Verde
    "Cancelado": "#e74c3c",    # Vermelho
    "A enviar": "#f39c12",     # Laranja
    "Processando": "#3498db",  # Azul
    "Pendente": "#95a5a6"      # Cinza
}

st.title("📅 Análise Temporal Detalhada")

if "dados_shopee" not in st.session_state:
    st.warning("⚠️ Por favor, envie sua planilha na aba 'Visão Geral'.")
    st.stop()

df = st.session_state["dados_shopee"].copy()

# --- EXTRAÇÃO DE COLUNAS DE TEMPO ---
df['Ano'] = df['Data de criação do pedido'].dt.year.astype(str) # Transformado em texto para os gráficos
df['Ano_Mes'] = df['Data de criação do pedido'].dt.to_period('M').astype(str)
df['Data_Dia'] = df['Data de criação do pedido'].dt.date

# --- BARRA LATERAL DE FILTROS ---
st.sidebar.header("Filtros Temporais")
anos_disponiveis = sorted(df['Ano'].dropna().unique())
anos_selecionados = st.sidebar.multiselect("Selecione o Ano", options=anos_disponiveis, default=anos_disponiveis)
df_filtrado = df[df['Ano'].isin(anos_selecionados)]

meses_disponiveis = sorted(df_filtrado['Ano_Mes'].dropna().unique())
meses_selecionados = st.sidebar.multiselect("Selecione o Período (Ano-Mês)", options=meses_disponiveis, default=meses_disponiveis)
df_filtrado = df_filtrado[df_filtrado['Ano_Mes'].isin(meses_selecionados)]

st.sidebar.markdown("---")
st.sidebar.header("Filtros de Operação")
status_disponiveis = sorted(df_filtrado['Status do pedido'].dropna().unique())
status_selecionados = st.sidebar.multiselect("Status do Pedido", options=status_disponiveis, default=status_disponiveis)
df_filtrado = df_filtrado[df_filtrado['Status do pedido'].isin(status_selecionados)]

ufs_selecionadas = st.sidebar.multiselect("Estados (UF)", options=sorted(df_filtrado["UF"].dropna().unique()), default=df_filtrado["UF"].dropna().unique())
df_filtrado = df_filtrado[df_filtrado["UF"].isin(ufs_selecionadas)]

if df_filtrado.empty:
    st.warning("Nenhum dado encontrado para os filtros selecionados.")
    st.stop()

# --- FUNÇÃO MESTRA DE RENDERIZAÇÃO (REUTILIZADA NAS 3 ABAS) ---
# Adicionamos o parâmetro 'chave_unica'
def renderizar_painel(df_escopo, coluna_agrupamento, label_eixo_x, chave_unica):
    # 1. KPIs
    faturamento_bruto = df_escopo['Valor Total'].sum()
    vendas_reais = df_escopo[df_escopo['Status do pedido'] == 'Concluído']['Valor Total'].sum()
    vendas_perdidas = df_escopo[df_escopo['Status do pedido'] == 'Cancelado']['Valor Total'].sum()
    vendas_aguardando = df_escopo[df_escopo['Status do pedido'].isin(['A enviar', 'Processando', 'Pendente'])]['Valor Total'].sum()
    
    indice_sucesso = (vendas_reais / faturamento_bruto * 100) if faturamento_bruto > 0 else 0
    numero_pedidos = df_escopo['ID do pedido'].nunique()

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("💰 Real (Concluído)", f"R$ {vendas_reais:,.2f}")
    col2.metric("❌ Perdido", f"R$ {vendas_perdidas:,.2f}")
    col3.metric("⏳ Aguardando", f"R$ {vendas_aguardando:,.2f}")
    col4.metric("🏆 Sucesso", f"{indice_sucesso:.1f}%")
    col5.metric("📦 Pedidos", f"{numero_pedidos}")
    st.divider()

    # 2. Gráfico Principal Empilhado por Status
    vendas_tempo_status = df_escopo.groupby([coluna_agrupamento, 'Status do pedido'])['Valor Total'].sum().reset_index()
    fig_tempo = px.bar(
        vendas_tempo_status, x=coluna_agrupamento, y='Valor Total', color='Status do pedido',
        title=f'Faturamento por {label_eixo_x} e Status',
        labels={'Valor Total': 'Faturamento (R$)', coluna_agrupamento: label_eixo_x, 'Status do pedido': 'Status'},
        barmode='stack',
        color_discrete_map=CORES_STATUS 
    )
    # Adicionando o 'key' exclusivo para não dar erro de ID duplicado
    st.plotly_chart(fig_tempo, use_container_width=True, key=f"graf_tempo_{chave_unica}")

    # 3. Top 5 Produtos (Apenas Vendas Concluídas)
    st.markdown("### Top 5 Produtos mais Entregues (Apenas Concluídos)")
    df_concluidos = df_escopo[df_escopo['Status do pedido'] == 'Concluído']
    
    if df_concluidos.empty:
        st.info("Nenhuma venda concluída neste período para ranquear os produtos.")
    else:
        cor_concluido = CORES_STATUS.get("Concluído", "#2ecc71") 
        col_g1, col_g2 = st.columns(2)
        
        with col_g1:
            top_qtd = df_concluidos.groupby('Nome do Produto')['Quantidade'].sum().sort_values(ascending=False).head(5).reset_index()
            fig_qtd = px.bar(top_qtd, x='Quantidade', y='Nome do Produto', orientation='h', title='Volume por Quantidade', color_discrete_sequence=[cor_concluido])
            fig_qtd.update_layout(yaxis={'categoryorder':'total ascending'})
            
            # Adicionando o 'key' exclusivo
            st.plotly_chart(fig_qtd, use_container_width=True, key=f"graf_qtd_{chave_unica}")
            
        with col_g2:
            top_valor = df_concluidos.groupby('Nome do Produto')['Valor Total'].sum().sort_values(ascending=False).head(5).reset_index()
            fig_val = px.bar(top_valor, x='Valor Total', y='Nome do Produto', orientation='h', title='Volume por Faturamento (R$)', color_discrete_sequence=[cor_concluido])
            fig_val.update_layout(yaxis={'categoryorder':'total ascending'})
            
            # Adicionando o 'key' exclusivo
            st.plotly_chart(fig_val, use_container_width=True, key=f"graf_val_{chave_unica}")

# --- SISTEMA DE ABAS ---
aba_diaria, aba_mensal, aba_anual = st.tabs(["📉 Visão Diária", "📊 Visão Mensal", "📆 Visão Anual"])

# Passamos um texto único no último parâmetro ('diaria', 'mensal', 'anual') para o Streamlit diferenciar os gráficos
with aba_diaria:
    st.subheader("Performance Detalhada Dia a Dia")
    renderizar_painel(df_filtrado, 'Data_Dia', 'Dias', 'diaria')

with aba_mensal:
    st.subheader("Performance Consolidada por Mês")
    renderizar_painel(df_filtrado, 'Ano_Mes', 'Meses', 'mensal')

with aba_anual:
    st.subheader("Performance Histórica Anual")
    renderizar_painel(df_filtrado, 'Ano', 'Anos', 'anual')