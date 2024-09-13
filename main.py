from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty
from kivy.lang import Builder
import requests
import json
from plyer import storagepath
import os
import jwt
from datetime import datetime

JWT_FILE = "oceanstream.jwt"

class Overview(Screen):
    pass

# class TelaLogin2(Screen):
#     pass

class WindowManager(ScreenManager):
    pass

class TelaLogin(Screen):
    email = ObjectProperty(None)
    senha = ObjectProperty(None)

    def on_enter(self):
        token = self.get_access_token()
        if token:
            if self.is_token_valid(token):
                print("Token válido, redirecionando...")
                # self.manager.current = 'overview'
            else:
                print("Token expirado, deletando...")
                self.delete_access_token()

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
                self.store_access_token(access_token)
                self.manager.current = 'overview'
            else:
                print(f"Falha no login: {response.status_code} - {response.text}")
        
        except Exception as e:
            print(f"Erro ao tentar fazer login: {str(e)}")
        
        # Limpar o campo de senha
        self.ids.senha.text = ""

    def store_access_token(self, token):
        # Salvar o token em um arquivo persistente
        app_storage_dir = storagepath.get_home_dir()  # Diretório de armazenamento do app
        token_file_path = os.path.join(app_storage_dir, JWT_FILE)

        with open(token_file_path, 'w') as token_file:
            token_file.write(token)
        print(f"Token salvo em {token_file_path}")

    def get_access_token(self):
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
            return None

    def delete_access_token(self):
        # Deletar o token armazenado
        app_storage_dir = storagepath.get_home_dir()
        token_file_path = os.path.join(app_storage_dir, JWT_FILE)

        if os.path.exists(token_file_path):
            os.remove(token_file_path)
            print("Token deletado.")
        else:
            print("Nenhum token para deletar.")

    def is_token_valid(self, token):
        try:
            # Decodificar o token JWT para verificar a validade
            decoded_token = jwt.decode(token, options={"verify_signature": False})
            exp_timestamp = decoded_token.get('exp')
            if exp_timestamp:
                exp_date = datetime.fromtimestamp(exp_timestamp)
                if exp_date > datetime.now():
                    return True
                else:
                    return False
            return False
        except Exception as e:
            print(f"Erro ao verificar token: {str(e)}")
            return False

Builder.load_file('paginas/login.kv')
Builder.load_file('paginas/overview.kv')
kv = Builder.load_file('paginas/windowmanager.kv')

class OceanStream(App):
    def build(self):
        return kv

if __name__ == '__main__':
    OceanStream().run()
