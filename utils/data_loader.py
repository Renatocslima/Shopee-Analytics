import pandas as pd

def limpar_moeda(valor):
    if isinstance(valor, str):
        valor = valor.replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.')
    try:
        return float(valor)
    except ValueError:
        return 0.0

def processar_dataframe_shopee(uploaded_file):
    """Lê o Excel e retorna o DataFrame já higienizado."""
    df = pd.read_excel(uploaded_file)
    
    # Padronização de Datas
    df['Data de criação do pedido'] = pd.to_datetime(df['Data de criação do pedido'], errors='coerce')
    
    # Padronização de Valores Monetários
    df['Valor Total'] = df['Valor Total'].apply(limpar_moeda)
    df['Taxa de envio pagas pelo comprador'] = df['Taxa de envio pagas pelo comprador'].apply(limpar_moeda)
    
    return df