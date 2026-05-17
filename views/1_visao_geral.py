import streamlit as st
from utils.data_loader import processar_dataframe_shopee
import plotly.express as px

st.title("📊 Visão Geral da Operação")

st.markdown("### 1. Envie o relatório da Shopee")
uploaded_file = st.file_uploader("Selecione o arquivo .xlsx gerado na Central do Vendedor", type="xlsx")

if uploaded_file is not None:
    try:
        st.session_state["dados_shopee"] = processar_dataframe_shopee(uploaded_file)
        st.success("Dados carregados com sucesso!")
    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")

if "dados_shopee" in st.session_state:
    df = st.session_state["dados_shopee"]

    # Filtros Globais Rápidos (Barra Lateral)
    st.sidebar.header("Filtros Rápidos")
    status_global = st.sidebar.multiselect("Status do Pedido", df["Status do pedido"].unique(), default=df["Status do pedido"].unique())
    df_filtrado = df[df["Status do pedido"].isin(status_global)]

    # --- FUNÇÕES DE FORMATAÇÃO PT-BR EXPLÍCITAS ---
    def fmt_moeda(valor):
        txt_us = f"{valor:,.2f}"  # Ex: 9,359.40
        inteiro, decimal = txt_us.split('.')
        inteiro_br = inteiro.replace(',', '.')
        return f"R$ {inteiro_br},{decimal}"

    def fmt_int(valor):
        txt_us = f"{valor:,}"
        return txt_us.replace(',', '.')

    # KPIs Principais Formatados no Padrão Brasileiro
    col1, col2, col3 = st.columns(3)
    col1.metric("Faturamento Bruto", fmt_moeda(df_filtrado['Valor Total'].sum()))
    col2.metric("Total de Pedidos", fmt_int(df_filtrado['ID do pedido'].nunique()))
    col3.metric("Itens Vendidos", fmt_int(df_filtrado['Quantidade'].sum()))

    # Gráficos de Linha de Venda Diária
    vendas_dia = df_filtrado.groupby(df_filtrado['Data de criação do pedido'].dt.date)['Valor Total'].sum().reset_index()
    fig_dia = px.line(vendas_dia, x='Data de criação do pedido', y='Valor Total', title='Curva de Faturamento Diário')
    
    # Aplica o padrão de separadores do Brasil no gráfico
    fig_dia.update_layout(separators=',.')
    
    st.plotly_chart(fig_dia, use_container_width=True)
else:
    st.info("💡 Aguardando o envio da planilha para exibir os dados do painel.")