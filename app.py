import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1 import Client
import os
from dotenv import load_dotenv

import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Obter o caminho para o arquivo de credenciais
firebase_credentials_path = os.getenv('FIREBASE_CREDENTIALS_PATH')

# Inicializar o Firebase se não estiver inicializado
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_credentials_path)
    firebase_admin.initialize_app(cred)

# Conectar ao Firestore
db = firestore.client()

# Função para buscar dados de status do Firestore
def get_project_status():
    statuses = db.collection('Status').stream()
    status_list = []
    total_setup = 0
    total_mrr = 0
    latest_date = None

    # Itera sobre os documentos e acumula os dados
    for status in statuses:
        data = status.to_dict()
        # Calcular a soma de Setup e MRR
        total_setup += data.get('Setup', 0)
        total_mrr += data.get('MRR', 0)

        # Verificar a data mais recente
        current_date = data.get('Data')
        if latest_date is None or current_date > latest_date:
            latest_date = current_date

        # Adiciona cada status à lista
        status_list.append({
            'Projeto': data.get('Projeto'),
            'Status': data.get('Status'),
            'Previsão de término': data.get('Previsão de término projeto'),
            'Setup': data.get('Setup'),
            'MRR': data.get('MRR'),
            'Último status report': data.get('Último status report')
        })
    
    return latest_date, total_setup, total_mrr, status_list

# Função para transformar status em farol
def get_status_color(status):
    if status == "verde":
        return "🟢"
    elif status == "amarelo":
        return "🟡"
    elif status == "vermelho":
        return "🔴"
    else:
        return "⚪"

# Exibe a aplicação no Streamlit
def main():
    st.title("Dashboard de Status do Portfólio de Projetos")

    # Obter dados do Firestore
    latest_date, total_setup, total_mrr, status_list = get_project_status()

    # Primeira linha com o resumo
    st.subheader("Resumo do Portfólio")
    st.write(f"Data mais recente: {latest_date}")
    st.write(f"Total Setup: R$ {total_setup:.2f}")
    st.write(f"Total MRR: R$ {total_mrr:.2f}")

    # Tabela de status dos projetos
    st.subheader("Detalhes dos Projetos")
    for status in status_list:
        st.markdown(f"**Projeto**: {status['Projeto']}")
        st.markdown(f"**Status**: {get_status_color(status['Status'])}")
        st.markdown(f"**Previsão de término**: {status['Previsão de término']}")
        st.markdown(f"**Setup**: R$ {status['Setup']:.2f}")
        st.markdown(f"**MRR**: R$ {status['MRR']:.2f}")
        if st.button(f"Ver último status report ({status['Projeto']})"):
            st.write(f"[Último status report]({status['Último status report']})")
        st.write("---")

if __name__ == "__main__":
    main()
