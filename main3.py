from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.storage.jsonstore import JsonStore
import requests

# URL da API para autenticação
API_URL = 'https://oceanstream-8b3329b99e40.herokuapp.com/login'

# Gerenciador de telas
class LoginScreen(Screen):
    def login(self):
        email = self.ids.email.text
        senha = self.ids.senha.text
        
        # Dados a serem enviados para a API
        data = {
            'email': email,
            'senha': senha
        }
        
        try:
            # Requisição POST para a API
            response = requests.post(API_URL, json=data)
            response.raise_for_status()
            result = response.json()
            
            # Armazena o token em um arquivo JSON local
            store = JsonStore('user_data.json')
            store.put('accessToken', token=result['accessToken'])
            
            # Redireciona para a tela principal
            self.manager.current = 'main'
        except requests.exceptions.HTTPError as err:
            print(f"Erro no login: {err}")
            self.ids.error_message.text = "Erro no login. Verifique suas credenciais."

class MainScreen(Screen):
    pass

# Gerenciador de telas
class WindowManager(ScreenManager):
    pass

class MyApp(App):
    def build(self):
        return Builder.load_file('login.kv')

if __name__ == '__main__':
    MyApp().run()
