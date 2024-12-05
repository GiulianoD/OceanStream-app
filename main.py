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
from kivy.config import Config
Config.set('graphics', 'multisamples', '0')

from navigation_bar import NavigationBar  # Importando a barra de navegação

### JWT
JWT_FILE = "oceanstream.jwt"

def store_access_token(token):
    app_storage_dir = storagepath.get_home_dir()
    token_file_path = os.path.join(app_storage_dir, JWT_FILE)
    with open(token_file_path, 'w') as token_file:
        token_file.write(token)
    print(f"Token salvo em {token_file_path}")

def get_access_token():
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
    app_storage_dir = storagepath.get_home_dir()
    token_file_path = os.path.join(app_storage_dir, JWT_FILE)
    if os.path.exists(token_file_path):
        os.remove(token_file_path)
        print("Token deletado.")
    else:
        print("Nenhum token para deletar.")

def is_token_valid(token):
    try:
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

### Telas

Builder.load_file('paginas/overview.kv')
Builder.load_file('paginas/alertas.kv')
Builder.load_file('paginas/login.kv')
Builder.load_file('paginas/configuracao.kv')

class Overview(Screen):
    pass

class Alertas(Screen):
    pass

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
        payload = {"email": email, "senha": senha}
        url = 'https://oceanstream-8b3329b99e40.herokuapp.com/login'
        headers = {'Content-Type': 'application/json'}

        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                data = response.json()
                access_token = data.get('accessToken')
                store_access_token(access_token)
                self.manager.current = 'overview'
            else:
                print(f"Falha no login: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Erro ao tentar fazer login: {str(e)}")
        
        self.ids.senha.text = ""

class Configuracao(Screen):
    pass

# Tela de carregamento
class TelaCarregamento(Screen):
    def __init__(self, **kwargs):
        super(TelaCarregamento, self).__init__(**kwargs)
        self.add_widget(Label(text="OceanStream"))
        Clock.schedule_once(self.verificar_token, 2.5)

    def verificar_token(self, dt):
        try:
            if is_token_valid(get_access_token()):
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
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_parameters = {}  # Dicionário para armazenar parâmetros selecionados por equipamento

    def build(self):
        self.gerenciador = GerenciadorTelas()
        
        # Adiciona as telas ao ScreenManager
        self.gerenciador.add_widget(TelaCarregamento(name='load'))
        self.gerenciador.add_widget(Overview(name='overview'))
        self.gerenciador.add_widget(Alertas(name='alertas'))
        self.gerenciador.add_widget(TelaLogin(name='login'))
        self.gerenciador.add_widget(Configuracao(name='configuracao'))

        # Define a tela inicial como a tela de carregamento
        self.gerenciador.current = 'load'

        # Passa delete_access_token como função de logout para NavigationBar
        self.navigation_bar = NavigationBar(screen_manager=self.gerenciador, logout_callback=self.logout)

        # Observa as mudanças de tela para controlar a visibilidade da toolbar
        self.gerenciador.bind(current=self.on_screen_change)

        return self.navigation_bar

    def toggle_parameter(self, equipment, parameter, state):
        # Inicializa o equipamento se não estiver no dicionário
        if equipment not in self.selected_parameters:
            self.selected_parameters[equipment] = set()

        if state == 'down':  # Adiciona parâmetro ao conjunto se marcado
            self.selected_parameters[equipment].add(parameter)
        else:  # Remove o parâmetro se desmarcado
            self.selected_parameters[equipment].discard(parameter)

        # Verifica os parâmetros selecionados
        print(f"Parâmetros selecionados para {equipment}: {self.selected_parameters[equipment]}")

    def on_screen_change(self, instance, value):
        # Oculta a toolbar se a tela atual for 'login' ou 'configuracao'
        if value in ['login', 'configuracao']:
            self.navigation_bar.toolbar.opacity = 0
            self.navigation_bar.toolbar.disabled = True
        else:
            self.navigation_bar.toolbar.opacity = 1
            self.navigation_bar.toolbar.disabled = False

    def logout(self):
        delete_access_token()
        self.gerenciador.current = 'login'

if __name__ == '__main__':
    OceanStream().run()