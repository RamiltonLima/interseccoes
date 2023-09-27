import streamlit as st
import pandas as pd
from audiencia import Interseccoes


st.set_page_config(page_title='Interseccionador', layout='wide', initial_sidebar_state='auto')

st.session_state['contador_arquivos'] = 0
st.session_state['colunas_selecionadas'] = dict()
st.session_state['sequencia_para_interseccionar'] = dict()
# st.error('This is a warning', icon="🚨")
@st.cache_data
def processa_arquivos(arquivos):
    dataframes = dict()
    if arquivos:
        for i, arquivo in enumerate(arquivos):
            df = pd.read_csv(arquivo)
            id_arquivo = st.session_state['contador_arquivos'] + 1
            dataframes[id_arquivo] = {'dataframe':df, 'nome_arquivo': arquivo.name, 'sequencia_arquivo': i}

            st.session_state['contador_arquivos'] += 1
    return dataframes


def seta_colunas_selecionadas(id, coluna_selecionada):
    st.session_state['colunas_selecionadas'][id] = coluna_selecionada

st.header("Interseccionador")
st.caption('Esta ferramenta permite entender as intersecções entre conjuntos de dados')
col1, col2 = st.columns(2)
with st.container():

    with col1:
        st.subheader('Etapa #1: Arquivos.')
        st.caption('Escolhas os arquivos csv que contém os campos chaves')
        st.caption('Atenção, não envie informações sensiveis, como emails, telefone, numero de documentos. Anonimize seus dados antes.')

        arquivos = st.file_uploader("Escolha os arquivos CSV", type=['csv'], accept_multiple_files=True)

    with col2:
        st.subheader('Etapa #2: Dados.')
        st.caption('Aponte a coluna, em cada arquivo, onde há as chaves a serem comparadas')

        arquivos = processa_arquivos(arquivos=arquivos)

        if arquivos:
            for id, arquivo in arquivos.items():
                coluna_selecionada = st.selectbox('Selecione a coluna', arquivo['dataframe'].columns, key=id, index=None, placeholder='Escolha uma das colunas')
                seta_colunas_selecionadas(id,coluna_selecionada)


            
    

with st.container():
    st.subheader('Etapa #3: Resumo.')

    colunas_nao_selecionadas = 0
    if st.button('Interseccionar', use_container_width=True):
        for id_df, coluna_selecionada in st.session_state['colunas_selecionadas'].items():
            if not coluna_selecionada:
                colunas_nao_selecionadas += 1
                st.toast(f'Escolha a coluna do arquivo {id_df}', icon='🚨')

        dados = dict()
        if colunas_nao_selecionadas == 0:
            for id, coluna in st.session_state['colunas_selecionadas'].items():
                dados[f'{str(id)}_{arquivos[id]["nome_arquivo"]}'] = arquivos[id]["dataframe"][coluna].astype(str).to_list()

            st.session_state['sequencia_para_interseccionar'] = dados


        iscc = Interseccoes(dados=dados)
        iscc.dados_dataframe

        col1, col2 = st.columns(2)
        with col1:
            st.download_button('Download JSON', iscc.dados_json, 'interseccionador.json', "application/json")
            st.download_button('Download CSV', iscc.dados_dataframe.to_csv(index=False).encode('utf-8'), 'interseccionador.csv', "text/csv")