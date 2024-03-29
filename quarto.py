import streamlit as st
import matplotlib.pyplot as plt
import yfinance as yf
from bs4 import BeautifulSoup
import requests

# Classe para representar uma ação
class Acao:
    def __init__(self, ticker, data_inicio, data_fim):
        self.ticker = ticker
        self.data_inicio = data_inicio
        self.data_fim = data_fim
        self.data = None

    # Método para baixar os dados da ação
    def download_data(self):
        try:
            self.data = yf.download(self.ticker + '.SA', start=self.data_inicio, end=self.data_fim)
            return True
        except Exception as e:
            st.error(f"Erro ao baixar dados da ação {self.ticker}: {str(e)}")
            return False

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

st.title('Meu primeiro programa de web')
st.text('Nome')
nome = st.text_input('Digite seu nome')
st.write('Olá', nome)


def inverte_texto(texto):
    return texto[::-1]

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

    # Criando objeto de ação e baixando dados
    acao = Acao(ticker, data_inicio, data_fim)
    if acao.download_data():
        # Plotando gráfico em tempo real
        st.line_chart(acao.data['Close'])
