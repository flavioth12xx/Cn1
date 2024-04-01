import pandas as pd
import matplotlib.pyplot as plt
import requests
from bs4 import BeautifulSoup
import streamlit as st
import yfinance as yf
from sympy import *

# Definir configuração para evitar o aviso de uso global do Pyplot
st.set_option('deprecation.showPyplotGlobalUse', False)

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

# Função para obter os dados das ações selecionadas
def get_stock_data(symbols):
    stock_data = pd.DataFrame()
    for symbol in symbols:
        data = yf.download(symbol, start="2024-01-01", end="2024-03-06")['Close']
        stock_data = pd.concat([stock_data, data], axis=1)
    return stock_data

# Função para determinar a tendência da ação com base no preço atual e média móvel
def determinar_tendencia(stock_data):
    if not stock_data.empty:
        current_price = stock_data[-1]
        short_term_avg = stock_data[-10:].mean()
        long_term_avg = stock_data[-50:].mean()

        if current_price > short_term_avg > long_term_avg:
            return "Tendência de alta"
        elif current_price < short_term_avg < long_term_avg:
            return "Tendência de baixa"
        else:
            return "Sem tendência clara"
    else:
        return "Sem dados disponíveis"

# Função para determinar a porcentagem ideal de investimento em uma ação
def determinar_porcentagem_investimento(stock_data, perfil_investidor):
    """
    Função para determinar a porcentagem ideal de investimento em uma ação.

    Args:
        stock_data: DataFrame com os dados da ação.
        perfil_investidor: String que indica o perfil do investidor ("conservador", "moderado" ou "agressivo").

    Returns:
        Float que representa a porcentagem ideal de investimento.
    """
    if not stock_data.empty:
        # Cálculo da volatilidade da ação
        volatilidade = stock_data.pct_change().std() * 100

        # Tendência da ação
        trend = determinar_tendencia(stock_data)

        # Fator de ajuste para o perfil do investidor
        fator_ajuste = 0.5 if perfil_investidor == "conservador" else 1.0 if perfil_investidor == "moderado" else 1.5

        # Cálculo da porcentagem de investimento
        porcentagem_investimento = (100 - volatilidade) * fator_ajuste

        # Se a ação estiver em tendência de baixa, ajusta a porcentagem
        if trend == "Tendência de baixa":
            porcentagem_investimento *= 0.5

        # Retorna a porcentagem de investimento
        return porcentagem_investimento
    else:
        return 0  # Retorna 0 se o DataFrame estiver vazio

# Função para plotar o gráfico da ação
def plot_stock_chart(stock_data, symbols):

    # Plota o gráfico
    fig, ax = plt.subplots()
    for symbol in symbols:
        if symbol in stock_data.columns:
            ax.plot(stock_data[symbol], label=f'Preço da Ação {symbol}')
    ax.set_title(f'Preços das Ações {", ".join(symbols)}')
    ax.set_xlabel('Tempo (dias)')
    ax.set_ylabel('Preço (R$)')
    ax.legend()
    st.pyplot(fig)

# Exemplo de uso das funções
if __name__ == "__main__":
    st.title("Análise de Ações")

    # Obter lista de empresas da Ibovespa
    empresas = obter_empresas_ibovespa()

    # Selecionar ações para análise
    selected_symbols = st.multiselect("Selecione as empresas da lista:", empresas)

    if selected_symbols:
        # Obter dados das ações selecionadas
        stock_data = get_stock_data(selected_symbols)

        # Plotar gráfico das ações
        plot_stock_chart(stock_data, selected_symbols)

        # Determinar porcentagem ideal de investimento
        perfil_investidor = st.radio("Selecione o perfil do investidor:", ("Conservador", "Moderado", "Agressivo"))
        porcentagem_investimento = determinar_porcentagem_investimento(stock_data, perfil_investidor.lower())

        st.write(f"Porcentagem ideal de investimento: {porcentagem_investimento}%")

        # Chatbox para inserir o valor do investimento
        valor_investimento = st.number_input("Insira o valor que deseja investir:", min_value=0.0)

        # Cálculo do lucro esperado
        lucro_esperado = (porcentagem_investimento / 100) * valor_investimento
        st.write(f"Lucro esperado: R$ {lucro_esperado:.2f}")
    else:
        st.warning("Selecione pelo menos uma empresa para análise.")
