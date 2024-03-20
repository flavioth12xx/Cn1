import pandas as pd
import requests
from bs4 import BeautifulSoup
import streamlit as st
import yfinance as yf
from sympy import Symbol, solve

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
def get_stock_data(symbol, start_date, end_date):
  stock_data = yf.download(symbol, start=start_date, end=end_date)
  return stock_data

# Função para calcular o lucro em relação ao dinheiro investido
def calcular_lucro(valor_investido, preco_compra, preco_venda):
  lucro = (preco_venda - preco_compra) * valor_investido
  return lucro

# Função para calcular o lucro utilizando Sympy
def calcular_lucro_sympy(valor_investido, preco_compra, preco_venda):
  x = Symbol('x')  # Variavel para o lucro
  equacao = lucro == valor_investido * (preco_venda - preco_compra)
  solucao = solve(equacao, x)
  return solucao[0]

# Obtendo a lista de empresas da Ibovespa
empresas_ibovespa = obter_empresas_ibovespa()

# Criando o aplicativo Streamlit
st.title("Análise de Lucro em Ações")

# Adicionando caixa de texto para inserir o valor a ser investido
valor_investido = st.number_input("Digite o valor a ser investido:", min_value=0.01, step=0.01)

# Adicionando caixas de texto para inserir as datas de compra e venda
data_compra = st.date_input("Data de compra:", value="2023-01-01")
data_venda = st.date_input("Data de venda:", value="2023-12-31")

# Adicionando checkboxes para cada empresa
selected_companies = st.multiselect(
  "Selecione as empresas",
  empresas_ibovespa
)

# Mostrando as empresas selecionadas
st.write("Empresas selecionadas:")
st.write(selected_companies)

# Exibindo os dados da ação para as empresas selecionadas
for company in selected_companies:
  st.subheader(f"Dados da ação para {company}")
  stock_data = get_stock_data(company + ".SA", data_compra, data_venda)
  st.write(stock_data)

  # Calcular o lucro
  preco_compra = stock_data['Close'][0]
  preco_venda = stock_data['Close'][-1]
  lucro = calcular_lucro(valor_investido, preco_compra, preco_venda)

  # Calcular o lucro utilizando Sympy
  lucro_sympy = calcular_lucro_sympy(valor_investido, preco_compra, preco_venda)

  # Exibir o lucro
  st.write(f"Lucro: {lucro:.2f}")
  st.write(f"Lucro (Sympy): {lucro_sympy}")
