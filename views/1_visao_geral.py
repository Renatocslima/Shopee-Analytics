import streamlit as st
from utils.data_loader import processar_dataframe_shopee
import plotly.express as px

st.title("📊 Visão Geral da Operação")

st.markdown("### Envie o relatório da Shopee")
uploaded_file = st.file_uploader("Selecione o arquivo .xlsx gerado na Central do Vendedor", type="xlsx")

if uploaded_file:
    try:
        # Processa e armazena no Session State (Memória Global do App)
        if "dados_shopee" not in st.session_state or st.button("🔄 Atualizar Dados"):
            st.session_state["dados_shopee"] = processar_dataframe_shopee(uploaded_file)
            st.success("Dados carregados com sucesso!")

        df = st.session_state["dados_shopee"]

        # Filtros Globais Rápidos (Barra Lateral)
        st.sidebar.header("Filtros Rápidos")
        status_global = st.sidebar.multiselect("Status do Pedido", df["Status do pedido"].unique(), default=df["Status do pedido"].unique())
        df_filtrado = df[df["Status do pedido"].isin(status_global)]

        # KPIs Principais
        col1, col2, col3 = st.columns(3)
        col1.metric("Faturamento Bruto", f"R$ {df_filtrado['Valor Total'].sum():,.2f}")
        col2.metric("Total de Pedidos", df_filtrado['ID do pedido'].nunique())
        col3.metric("Itens Vendidos", df_filtrado['Quantidade'].sum())

        # Gráficos de Linha de Venda Diária
        vendas_dia = df_filtrado.groupby(df_filtrado['Data de criação do pedido'].dt.date)['Valor Total'].sum().reset_index()
        fig_dia = px.line(vendas_dia, x='Data de criação do pedido', y='Valor Total', title='Curva de Faturamento Diário')
        st.plotly_chart(fig_dia, use_container_width=True)

    except Exception as e:
        st.error(f"Erro ao renderizar painel: {e}")