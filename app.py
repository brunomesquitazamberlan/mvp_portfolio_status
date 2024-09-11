import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
from datetime import datetime

# Inicializar o Firebase
cred = credentials.Certificate('path/to/your/firebase_config.json')
firebase_admin.initialize_app(cred)

# Conectar ao Firestore
db = firestore.client()

def fetch_data():
    # Consultar a subcoleção "Status" dentro da coleção "Projetos"
    statuses_ref = db.collection('Projetos').document('status').collection('Status')
    docs = statuses_ref.stream()
   
    data = []
    for doc in docs:
        data.append(doc.to_dict())
   
    return pd.DataFrame(data)

def process_data(df):
    # Processar os dados
    df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y')
    df['Previsão de término fase'] = pd.to_datetime(df['Previsão de término fase'], format='%d/%m/%Y')
    df['Previsão de término projeto'] = pd.to_datetime(df['Previsão de término projeto'], format='%d/%m/%Y')
   
    latest_date = df['Data'].max()
    total_setup = df['Setup'].sum()
    total_mrr = df['MRR'].sum()
   
    # Criar um resumo
    summary = {
        'Data': latest_date.strftime('%d/%m/%Y'),
        'Setup': f'R$ {total_setup:,.2f}',
        'MRR': f'R$ {total_mrr:,.2f}'
    }
   
    # Adicionar coluna de status como farol
    def status_color(status):
        if status == 'Concluído':
            return 'green'
        elif status == 'Em andamento':
            return 'yellow'
        else:
            return 'red'
   
    df['Status Color'] = df['Status'].apply(status_color)
   
    return summary, df

# Streamlit Interface
def main():
    st.title('Dashboard de Projetos')

    data = fetch_data()
    if data.empty:
        st.write('Nenhum dado disponível.')
        return
   
    summary, processed_data = process_data(data)

    # Exibir resumo do portfólio
    st.header('Resumo do Portfólio')
    st.write(f"**Data mais recente:** {summary['Data']}")
    st.write(f"**Total Setup:** {summary['Setup']}")
    st.write(f"**Total MRR:** {summary['MRR']}")
   
    # Exibir tabela de status
    st.header('Status dos Projetos')
   
    def render_status_color(val):
        return f'<span style="color: {val};">●</span>'
   
    processed_data['Status Color'] = processed_data['Status Color'].apply(render_status_color)
   
    # Exibir a tabela com links clicáveis
    def link_html(url):
        if pd.notna(url):
            return f'<a href="{url}" target="_blank">Último Status Report</a>'
        return 'N/A'

    processed_data['Último Status Report Link'] = processed_data['Último status report'].apply(link_html)
   
    # Criar uma tabela para visualização
    st.write(processed_data[['Projeto', 'Status Color', 'Previsão de término projeto', 'Setup', 'MRR', 'Último Status Report Link']]
             .rename(columns={'Status Color': 'Status'}).to_html(escape=False, index=False), unsafe_allow_html=True)

if __name__ == '__main__':
    main()