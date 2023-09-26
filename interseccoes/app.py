import streamlit as st
import pandas as pd

st.header("Interseccionador")

st.caption('Esta ferramenta permite entender as intersecções entre conjuntos de dados')

st.subheader('#1 Arquivos.')

st.caption('Escolhas os arquivos csv que contém os campos chaves')
st.caption('Atenção, não envie informações sensiveis, como emails, telefone, numero de documentos. Anonimize seus dados antes.')

arquivos = st.file_uploader("Escolha os arquivos CSV", type=['csv'], accept_multiple_files=True)


st.subheader('#1 Dados.')
st.caption('Aponte a coluna, em cada arquivo, onde há as chaves a serem comparadas')

dataframes = dict()
dados = dict()

if arquivos:
    for i, arquivo in enumerate(arquivos):
        df = pd.read_csv(arquivo)
        dataframes[f'{i+1}_{arquivo.name}'] = df


for chave, valor in dataframes.items():
    coluna_selecionada = st.selectbox(chave, valor.columns, key=hash(id(valor)))

    dados[chave] = valor[coluna_selecionada].astype(str).to_list()
    st.write(f'Coluna {coluna_selecionada}')

print(dados.keys())



