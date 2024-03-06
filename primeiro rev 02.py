# Salve este código em um arquivo chamado "app.py"

import streamlit as st
import matplotlib.pyplot as plt
import yfinance as yf
from bs4 import BeautifulSoup
import requests

# Função para obter a lista de empresas da Ibovespa
def obter_empresas_ibovespa():
    url = "https://pt.wikipedia.org/wiki/Lista_de_companhias_citadas_no_Ibovespa"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table", {"class": "wikitable"})

    empresas = []
    for row in table.find_all("tr")[1:]:
        cols = row.find_all("td")
        empresas.append(cols[0].text.strip())

    return empresas

# Função para inverter texto
def inverte_texto(texto):
    return texto[::-1]

st.title('Meu primeiro programa de web')
st.text('Nome')
nome = st.text_input('Digite seu nome')
st.write('Olá', nome)

# Botão para inverter o texto
b1 = st.button("Inverter")
if b1:
    texto_invertido = inverte_texto(nome)
    st.write(f"Texto Invertido: {texto_invertido}")

b2 = st.button("Gráfico")
if b2:
    fig, ax = plt.subplots()
    ax.scatter([1, 2, 3], [1, 2, 3])
    st.pyplot(fig)

# Pegar ticker de uma ação da Ibovespa e baixar os dados e plotar o gráfico
st.header('Dados da Ação na Ibovespa')

# Obtendo a lista de empresas da Ibovespa
empresas_ibovespa = obter_empresas_ibovespa()

# Adicionando selectbox para selecionar uma empresa
ticker = st.selectbox('Selecione o ticker da ação', empresas_ibovespa)

data_inicio = st.date_input('Data Início')
data_fim = st.date_input('Data Fim')

b3 = st.button('Buscar')
if b3:
    # Loading
    st.write('Carregando...')

    # Baixar dados da ação
    acao = yf.download(ticker + '.SA', start=data_inicio, end=data_fim)
    st.line_chart(acao['Close'])
    st.write(acao)
    st.write(acao.describe())
