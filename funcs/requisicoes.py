from datetime import datetime
import requests

from funcs.storage import store_access_token, get_access_token

API_PRFX = "https://oceanstream-8b3329b99e40.herokuapp.com/"

def verifica_formato_data(data):
    """Verifica se a data está no formato YYYY-MM-DD."""
    try:
        datetime.strptime(data, "%Y-%m-%d")
        return True
    except ValueError:
        return False

# POST /dados
def api_dados(nome_tabela, start_date, end_date):
    # Verifica o formato das datas
    if not (verifica_formato_data(start_date) and verifica_formato_data(end_date)):
        return

    # Adiciona o horário ao final da data final
    end_date = f"{end_date} 23:59:59"

    # Corpo da requisição
    corpo = {
        "tabela": nome_tabela,
        "dt_inicial": start_date,
        "dt_final": end_date
    }

    # Cabeçalhos da requisição
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {get_access_token()}"
    }

    # URL da API
    url = API_PRFX+"dados"

    # Faz a requisição POST
    try:
        response = requests.post(url, headers=headers, json=corpo)

        # Verifica se a requisição foi bem-sucedida
        if response.status_code != 200:
            raise Exception(f"Erro na requisição: {response.status_code} - {response.text}")

        # Converte a resposta para JSON
        data = response.json()

        return data

    except Exception as error:
        print(f"Erro: {error}")

# GET /ultimosDados
def api_ultimosDados():
    # Cabeçalhos da requisição
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {get_access_token()}"
    }

    # URL da API
    url = API_PRFX+"ultimosDados"

    # Faz a requisição POST
    try:
        response = requests.get(url, headers=headers)

        # Verifica se a requisição foi bem-sucedida
        if response.status_code != 200:
            raise Exception(f"Erro na requisição: {response.status_code} - {response.text}")

        # Converte a resposta para JSON
        data = response.json()

        return data

    except Exception as error:
        print(f"Erro: {error}")

# POST /login
def login(email, senha):
    url = API_PRFX+'login'
    headers = {'Content-Type': 'application/json'}
    corpo = {"email": email, "senha": senha}
    try:
        response = requests.post(url, json=corpo, headers=headers)
        if response.status_code == 200:
            data = response.json()
            access_token = data.get('accessToken')
            store_access_token(access_token)
            return [True, '']
        else:
            msg = f"Falha no login: {response.status_code} - {response.text}"
            print(msg)
    except Exception as e:
        msg = f"Erro ao tentar fazer login: {str(e)}"
        print(msg)
    
    return [False, msg]
