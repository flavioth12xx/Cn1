import requests
from bs4 import BeautifulSoup
import yfinance as yf
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from scipy.optimize import minimize

# Definindo a URL da página da Wikipedia
url = "https://pt.wikipedia.org/wiki/Lista_de_companhias_citadas_no_Ibovespa"

# Função para obter a lista de nomes de ações a partir da tabela HTML
def get_company_names():
    """
    Obtém a lista de nomes de companhias do Ibovespa a partir da tabela HTML.

    Retorna:
        Lista de strings contendo os nomes das companhias.
    """
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
            company_names = []
            for row in table.find_all("tr")[1:]:
                cells = row.find_all("td")
                if len(cells) >= 2:
                    company_names.append(cells[0].text.strip())
            return company_names
        else:
            st.error("Tabela não encontrada.")
    else:
        st.error(f"Erro ao acessar a página: {response.status_code}")

# Função para obter os preços ajustados de fechamento das ações
def get_adj_close_prices(tickers, start_date, end_date):
    """
    Obtém os preços ajustados de fechamento de ações para os tickers especificados no intervalo de datas.

    Args:
        tickers (list): Lista de strings contendo os tickers das ações.
        start_date (str): Data inicial no formato YYYY-MM-DD.
        end_date (str): Data final no formato YYYY-MM-DD.

    Returns:
        pandas.DataFrame: DataFrame contendo os preços ajustados de fechamento para cada ticker.
    """
    # Cria um DataFrame vazio para armazenar os preços ajustados de fechamento
    df_prices = pd.DataFrame()

    # Itera sobre os tickers para obter os preços de cada empresa
    for ticker in tickers:
        # Obtém os dados do ticker no intervalo de datas especificado
        data = yf.download(ticker + ".SA", start=start_date, end=end_date)
        # Adiciona os preços ajustados de fechamento ao DataFrame
        df_prices[ticker] = data["Adj Close"]

    return df_prices

# Função para calcular o Índice de Sharpe
def calculate_sharpe_ratio(df_prices, weights):
    """
    Calcula o Índice de Sharpe de uma carteira de ações.

    Args:
        df_prices (pandas.DataFrame): DataFrame contendo os preços ajustados de fechamento.
        weights (dict): Dicionário contendo os pesos de cada ação na carteira.

    Returns:
        float: Índice de Sharpe da carteira.
    """
    # Calcula os retornos diários das ações
    daily_returns = df_prices.pct_change()

    # Calcula o retorno diário da carteira
    portfolio_return = (daily_returns * weights).sum(axis=1)

    # Calcula o retorno anualizado da carteira
    annual_return = portfolio_return.mean() * 252

    # Calcula o risco da carteira (desvio padrão dos retornos diários)
    portfolio_std_dev = daily_returns.dot(weights).std() * np.sqrt(252)

    # Calcula o Índice de Sharpe
    sharpe_ratio = annual_return / portfolio_std_dev

    return sharpe_ratio

# Função para otimizar os pesos da carteira
def maximize_sharpe_ratio(df_prices, initial_weights):
    """
    Otimiza os pesos da carteira para maximizar o Índice de Sharpe.

    Args:
        df_prices (pandas.DataFrame): DataFrame contendo os preços ajustados de fechamento.
        initial_weights (dict): Dicionário contendo os pesos iniciais de cada ação na carteira.

    Returns:
        dict: Dicionário contendo os pesos ótimos de cada ação na carteira.
    """
    # Define a função de minimização (negativo do Índice de Sharpe)
    def negative_sharpe(weights):
        return -calculate_sharpe_ratio(df_prices, dict(zip(selected_tickers, weights)))

    # Define as restrições (soma dos pesos deve ser igual a 1)
    constraints = ({'type': 'eq', 'fun': lambda w: np.sum(w) - 1})

    # Define os limites dos pesos (entre 0 e 1)
    bounds = tuple((0, 1) for _ in range(len(selected_tickers)))

    # Otimiza os pesos utilizando o método SLSQP
    result = minimize(negative_sharpe, list(initial_weights.values()), method='SLSQP', bounds=bounds, constraints=constraints)

    # Retorna os pesos ótimos como um dicionário
    optimal_weights = dict(zip(selected_tickers, result.x))

    return optimal_weights

# Título da aplicação
st.title("Análise de Carteira com Índice de Sharpe")

# Seleção de tickers
selected_tickers = st.multiselect("Selecione os tickers:", ["PETR4", "VALE3", "ITUB4", "BOVA11", "GGPL3"], default=["PETR4", "VALE3"])

# Seleção de data de início
start_date_str = st.date_input("Data inicial:", min_value=pd.to_datetime("2020-01-01"), max_value=pd.to_datetime("2024-04-24"))
start_date = start_date_str.strftime("%Y-%m-%d")

# Seleção de data final
end_date_str = st.date_input("Data final:", min_value=start_date_str, max_value=pd.to_datetime("2024-04-24"))
end_date = end_date_str.strftime("%Y-%m-%d")

# Obtem os preços ajustados de fechamento
df_adj_close_prices = get_adj_close_prices(selected_tickers, start_date, end_date)

# Seção para definir os pesos iniciais das ações
st.header("Definição dos Pesos Iniciais das Ações")
initial_weights_input = st.number_input("Peso inicial (0-1)", min_value=0.0, max_value=1.0, step=0.01, value=0.2)
initial_weights = {ticker: initial_weights_input for ticker in selected_tickers}

# Otimização dos pesos da carteira
optimal_weights = maximize_sharpe_ratio(df_adj_close_prices, initial_weights)

# Exibe os pesos ótimos e o Índice de Sharpe da carteira otimizada
st.header("Pesos Ótimos e Índice de Sharpe")
st.write(f"Pesos ótimos: {optimal_weights}")
sharpe_ratio_optimized = calculate_sharpe_ratio(df_adj_close_prices, optimal_weights)
st.write(f"Índice de Sharpe da carteira otimizada: {sharpe_ratio_optimized:.3f}")

# Gráfico de alocação de ativos otimizada
fig, ax = plt.subplots()
ax.pie(optimal_weights.values(), labels=optimal_weights.keys(), autopct="%1.1f%%")
plt.title("Alocação de Ativos Otimizada")
st.pyplot(fig)
