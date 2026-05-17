import streamlit as st
import requests
from datetime import datetime

st.title("💬 Central de Feedback")
st.write("Deixe sua sugestão de melhoria ou reporte um bug do sistema.")

with st.form("form_feedback", clear_on_submit=True):
    tipo = st.selectbox("Tipo de Feedback", ["Sugestão de Gráfico", "Bug/Erro na Planilha", "Outro"])
    mensagem = st.text_area("Descreva o que você precisa ou o erro que aconteceu")
    submetido = st.form_submit_button("Enviar Feedback Oficial")
    
    if submetido:
        if not mensagem:
            st.warning("Por favor, digite uma mensagem antes de enviar.")
        else:
            webhook_url = st.secrets.get("DISCORD_WEBHOOK_URL")
            
            if webhook_url:
                # Monta a notificação formatada para o seu canal
                payload = {
                    "embeds": [{
                        "title": f"📝 Novo Feedback - {tipo}",
                        "color": 15418782, # Cor personalizada
                        "fields": [
                            {"name": "👤 Usuário", "value": f"`{st.session_state.get('username', 'Desconhecido')}`", "inline": True},
                            {"name": "📅 Data", "value": datetime.now().strftime("%d/%m/%Y %H:%M"), "inline": True},
                            {"name": "💬 Mensagem", "value": mensagem, "inline": False}
                        ]
                    }]
                }
                
                try:
                    response = requests.post(webhook_url, json=payload)
                    if response.status_code in [200, 204]:
                        st.success("🚀 Feedback enviado com sucesso diretamente para o desenvolvedor!")
                    else:
                        st.error(f"Erro ao processar envio (Status {response.status_code})")
                except Exception as e:
                    st.error(f"Falha na comunicação segura: {e}")
            else:
                st.error("Erro de configuração: O webhook de destino não foi cadastrado nos Secrets.")