# import kivy
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty
from kivy.uix.label import Label
from kivy.lang import Builder
from kivy.clock import Clock
from plyer import storagepath
from datetime import datetime
import requests
import json
import os
import jwt

###
'''
    Json Web Token [JWT]
'''
###
JWT_FILE = "oceanstream.jwt"

def store_access_token(token):
    # Salvar o token em um arquivo persistente
    app_storage_dir = storagepath.get_home_dir()  # Diretório de armazenamento do app
    token_file_path = os.path.join(app_storage_dir, JWT_FILE)

    with open(token_file_path, 'w') as token_file:
        token_file.write(token)
    print(f"Token salvo em {token_file_path}")

def get_access_token():
    # Recuperar o token armazenado
    app_storage_dir = storagepath.get_home_dir()
    token_file_path = os.path.join(app_storage_dir, JWT_FILE)

    if os.path.exists(token_file_path):
        with open(token_file_path, 'r') as token_file:
            token = token_file.read()
            print(f"Token recuperado: {token}")
            return token
    else:
        print("Nenhum token encontrado.")
        return ""

def delete_access_token():
    # Deletar o token armazenado
    app_storage_dir = storagepath.get_home_dir()
    token_file_path = os.path.join(app_storage_dir, JWT_FILE)

    if os.path.exists(token_file_path):
        os.remove(token_file_path)
        print("Token deletado.")
    else:
        print("Nenhum token para deletar.")

def is_token_valid(token):
    try:
        # Decodificar o token JWT para verificar a validade
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        exp_timestamp = decoded_token.get('exp')
        if exp_timestamp:
            exp_date = datetime.fromtimestamp(exp_timestamp)
            if exp_date > datetime.now():
                return True
        return False
    except Exception as e:
        print(f"Erro ao verificar token: {str(e)}")
        return False

###
'''
    telas
'''
###

Builder.load_file('paginas/overview.kv')
class Overview(Screen):
    pass
    # def __init__(self, **kwargs):
    #     super(Tela1, self).__init__(**kwargs)
    #     self.add_widget(Label(text="Esta é a Tela 1"))

Builder.load_file('paginas/login.kv')
class TelaLogin(Screen):
    email = ObjectProperty(None)
    senha = ObjectProperty(None)

    def on_enter(self):
        token = get_access_token()
        if token:
            if is_token_valid(token):
                print("Token válido, redirecionando...")
                self.manager.current = 'overview'
            else:
                print("Token expirado, deletando...")
                delete_access_token()

    def submit(self):
        email = self.ids.email.text
        senha = self.ids.senha.text

        # Montar o payload JSON
        payload = {
            "email": email,
            "senha": senha
        }

        # Fazer a requisição POST
        url = 'https://oceanstream-8b3329b99e40.herokuapp.com/login'
        headers = {'Content-Type': 'application/json'}

        try:
            response = requests.post(url, data=json.dumps(payload), headers=headers)

            if response.status_code == 200:
                # Obter a resposta
                data = response.json()
                access_token = data.get('accessToken')

                # Armazenar o accessToken de forma persistente
                store_access_token(access_token)
                self.manager.current = 'overview'
            else:
                print(f"Falha no login: {response.status_code} - {response.text}")
        
        except Exception as e:
            print(f"Erro ao tentar fazer login: {str(e)}")
        
        # Limpar o campo de senha
        self.ids.senha.text = ""

# Tela de carregamento
class TelaCarregamento(Screen):
    def __init__(self, **kwargs):
        super(TelaCarregamento, self).__init__(**kwargs)
        self.add_widget(Label(text="OceanStream"))
        Clock.schedule_once(self.verificar_token, 2.5)  # Aguarda 2 segundos para simular o carregamento

    def verificar_token(self, dt):
        try:
            if is_token_valid(token = get_access_token()):
                self.manager.current = 'overview'
            else:
                delete_access_token()
                self.manager.current = 'login'
        except FileNotFoundError:
            print("Arquivo não encontrado.")

# Gerenciador de Telas
class GerenciadorTelas(ScreenManager):
    pass

class OceanStream(MDApp):
    def build(self):
        gerenciador = GerenciadorTelas()
        
        # Adiciona as telas ao ScreenManager
        gerenciador.add_widget(TelaCarregamento(name='load'))
        gerenciador.add_widget(Overview(name='overview'))
        gerenciador.add_widget(TelaLogin(name='login'))

        # Define a tela inicial como a tela de carregamento
        gerenciador.current = 'load'

        return gerenciador

if __name__ == '__main__':
    OceanStream().run()
