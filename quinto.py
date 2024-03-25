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
def plot_stock_chart(stock_data):
  # Cria um objeto sympy para o tempo
  t = Symbol('t')

  # Cria uma função sympy para o preço da ação
  price = sin(2*pi*t) + 50

  # Plota o gráfico
  plot(price, (t, 0, 10), title='Preço da Ação')

# Obtendo a lista de empresas da Ibovespa
empresas_ibovespa = obter_empresas_ibovespa()

# Criando o aplicativo Streamlit
st.title("Empresas Listadas na Ibovespa")

# Adicionando checkboxes para cada empresa
selected_companies = st.multiselect( "Selecione as empresas", empresas_ibovespa)

# Mostrando as empresas selecionadas
st.write("Empresas selecionadas:")
st.write(selected_companies)

# Exibindo os dados da ação para as empresas selecionadas
for company in selected_companies:
  st.subheader(f"Dados da ação para {company}")
  stock_data = get_stock_data(company + ".SA") # Adicionando ".SA" para o símbolo da empresa
  st.write(stock_data)

  # Chatbot para inserir o valor a ser investido
  valor_investido = st.number_input("Valor a ser investido:", min_value=0.01)

  # Determinar a quantidade de ações que podem ser compradas
  quantidade_acoes = valor_investido / stock_data['Close'][-1]

  # Mostrar a quantidade de ações que podem ser compradas
  st.write(f"Quantidade de ações que podem ser compradas: {quantidade_acoes:.2f}")

  # Determinar a tendência da ação
  trend = determinar_tendencia(stock_data)
  st.write(f"Tendência: {trend}")

  # Determinar a volatilidade da ação
  volatilidade = determinar_volatilidade(stock_data)
  st.write(f"Volatilidade: {volatilidade:.2f}%")

  # Cálculo do índice P/L
