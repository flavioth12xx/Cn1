import pandas as pd
import requests
from bs4 import BeautifulSoup
import streamlit as st
import yfinance as yf
from sympy import *

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

# Função para obter os dados da ação selecionada
def get_stock_data(symbol):
    stock_data = yf.download(symbol, start="2024-01-01", end="2024-03-06")
    return stock_data

# Função para determinar a tendência da ação com base no preço atual e média móvel
def determinar_tendencia(stock_data):
    current_price = stock_data['Close'][-1]
    short_term_avg = stock_data['Close'][-10:].mean()
    long_term_avg = stock_data['Close'][-50:].mean()

    if current_price > short_term_avg > long_term_avg:
        return "Tendência de alta"
    elif current_price < short_term_avg < long_term_avg:
        return "Tendência de baixa"
    else:
        return "Sem tendência clara"

# Função para determinar a volatilidade da ação
def determinar_volatilidade(stock_data):
    return stock_data['Close'].pct_change().std() * 100

# Função para plotar o gráfico da ação
def plot_stock_chart(stock_data, symbol):

    # Cria um objeto sympy para o tempo
    t = Symbol('t')

    # Cria uma função sympy para o preço da ação
    # Fechando o preço com a média móvel exponencial de 10 dias
    close_prices = stock_data['Close']
    ema_10 = close_prices.ewm(span=10, min_periods=10).mean()
    price = ema_10

    # Plota o gráfico
    plt.plot(price, label='Preço da Ação')
    plt.plot(ema_10, label='Média Móvel de 10 dias', linestyle='dashed')
    plt.title(f'Preço da Ação {symbol}')
    plt.xlabel('Tempo (dias)')
    plt.ylabel('Preço (R$)')
    plt.legend()
    st.pyplot()

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

    # Cálculo da volatilidade da ação
    volatilidade = stock_data['Close'].pct_change().std() * 100

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

# Exemplo de uso das funções
if __name__ == "__main__":
    st.title("Análise de Ações")

    # Obter lista de empresas da Ibovespa
    empresas = obter_empresas_ibovespa()

    # Selecionar ação para análise
    selected_symbol = st.selectbox("Selecione uma empresa da lista:", empresas)

    # Obter dados da ação selecionada
    stock_data = get_stock_data(selected_symbol)

    # Plotar gráfico da ação
    plot_stock_chart(stock_data, selected_symbol)

    # Determinar porcentagem ideal de investimento
    perfil_investidor = st.radio("Selecione o perfil do investidor:", ("Conservador", "Moderado", "Agressivo"))
    porcentagem_investimento = determinar_porcentagem_investimento(stock_data, perfil_investidor.lower())

    st.write(f"Porcentagem ideal de investimento: {porcentagem_investimento}%")
