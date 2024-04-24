import streamlit as st
import requests
from bs4 import BeautifulSoup
import yfinance as yf
import pandas as pd
import numpy as np
from scipy.optimize import minimize

def obter_lista_acoes_ibovespa():
    # URL da página da Wikipedia
    url = "https://pt.wikipedia.org/wiki/Lista_de_companhias_citadas_no_Ibovespa"

    # Fazendo a requisição para obter o conteúdo da página
    response = requests.get(url)

    # Verificando se a requisição foi bem-sucedida
    if response.status_code == 200:
        # Criando o objeto BeautifulSoup
        soup = BeautifulSoup(response.content, "html.parser")

        # Encontrando a tabela que contém a lista de ações
        table = soup.find("table", {"class": "wikitable sortable"})

        # Verificando se a tabela foi encontrada
        if table:
            # Iterando pelas linhas da tabela para obter os nomes das ações
            companies = []
            for row in table.find_all("tr")[1:]:
                cells = row.find_all("td")
                if len(cells) >= 2:  # Verifica se há pelo menos duas células na linha
                    nome_acao = cells[0].text.strip()  # Obtém o nome da ação
                    companies.append(nome_acao)
            return companies
        else:
            st.error("Tabela não encontrada.")
            return None
    else:
        st.error("Erro ao acessar a página.")
        return None

def get_adj_close_prices(tickers, start_date, end_date):
    # Cria um DataFrame vazio para armazenar os preços ajustados de fechamento
    df_prices = pd.DataFrame()

    # Itera sobre os tickers para obter os preços de cada empresa
    for ticker in tickers:
        # Obtém os dados do ticker no intervalo de datas especificado
        data = yf.download(ticker + ".SA", start=start_date, end=end_date)
        # Adiciona os preços ajustados de fechamento ao DataFrame
        df_prices[ticker] = data["Adj Close"]

    return df_prices

def calculate_sharpe_ratio(df_prices, weights):
    if isinstance(weights, list):
        weights = np.array(weights)
    # Calcula os retornos diários das ações
    daily_returns = df_prices.pct_change()

    # Calcula o retorno anualizado médio das ações
    annual_returns = daily_returns.mean() * 252  # 252 dias úteis em um ano

    # Calcula a matriz de covariância dos retornos diários das ações
    cov_matrix = daily_returns.cov()

    # Calcula o retorno e a volatilidade da carteira
    portfolio_return = np.dot(annual_returns, weights)
    portfolio_std_dev = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights))) * np.sqrt(252)

    # Define a taxa livre de risco (geralmente usa-se a taxa de juros de títulos do governo)
    risk_free_rate = 0.05  # Exemplo: 5% ao ano

    # Calcula o índice de Sharpe
    sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_std_dev

    return sharpe_ratio

def maximize_sharpe_ratio(df_prices):
    # Função objetivo a ser minimizada
    def negative_sharpe_ratio(weights):
        return -calculate_sharpe_ratio(df_prices, weights)

    # Restrição: a soma dos pesos deve ser igual a 1
    constraints = ({'type': 'eq', 'fun': lambda weights: np.sum(weights) - 1})

    # Limites dos pesos (0 <= peso <= 1)
    bounds = [(0, 1) for _ in range(len(df_prices.columns))]

    # Chute inicial para os pesos
    initial_guess = np.ones(len(df_prices.columns)) / len(df_prices.columns)

    # Minimiza a função objetivo negativa para maximizar o índice de Sharpe
    result = minimize(negative_sharpe_ratio, initial_guess, method='SLSQP', bounds=bounds, constraints=constraints)

    # Retorna os pesos ótimos que maximizam o índice de Sharpe
    return result.x

# Função para calcular o lucro com base no índice de Sharpe e no valor investido
def calculate_profit(investment_amount, sharpe_ratio):
    return investment_amount * sharpe_ratio

# Título da página
st.title('Análise de Investimentos')

# Obtém a lista de ações da Ibovespa
tickers_ibovespa = obter_lista_acoes_ibovespa()
if tickers_ibovespa:
    st.write("Lista de ações da Ibovespa:", tickers_ibovespa)

    # Define as datas de início e fim para obter os preços
    start_date = st.date_input("Data de início", value=pd.to_datetime('2022-01-01'))
    end_date = st.date_input("Data de fim", value=pd.to_datetime('2022-12-31'))

    # Obtém os preços ajustados de fechamento das empresas
    df_adj_close_prices = get_adj_close_prices(tickers_ibovespa, start_date, end_date)
    st.write("Preços ajustados de fechamento das empresas:")
    st.write(df_adj_close_prices)

    # Calcula os pesos ótimos que maximizam o índice de Sharpe da carteira
    optimal_weights = maximize_sharpe_ratio(df_adj_close_prices)
    st.write("Pesos ótimos para maximizar o índice de Sharpe:", optimal_weights)

    # Calcula o índice de Sharpe da carteira com os pesos ótimos
    sharpe_ratio_optimal = calculate_sharpe_ratio(df_adj_close_prices, optimal_weights)
    st.write("Índice de Sharpe da carteira com pesos ótimos:", sharpe_ratio_optimal)

    # Solicita ao usuário o valor a ser investido
    investment_amount = st.number_input("Valor a ser investido", min_value=0.0, step=100.0, value=1000.0)

    # Calcula o lucro com base no índice de Sharpe e no valor investido
    profit = calculate_profit(investment_amount, sharpe_ratio_optimal)
    st.write("Lucro estimado com base no índice de Sharpe:", profit)
