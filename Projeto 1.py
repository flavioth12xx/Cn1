import requests
from bs4 import BeautifulSoup
import streamlit as st

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

# Título da aplicação
st.title("Lista de Companhias do Ibovespa")

# Obtendo a lista de nomes de ações
company_names = get_company_names()

# Verificando se a lista foi obtida com sucesso
if company_names:
    # Exibindo a lista de companhias
    st.write(company_names)
