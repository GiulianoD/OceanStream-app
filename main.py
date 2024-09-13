from kivy.app import App
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button

import requests
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
API_agify = "https://api.agify.io?name=NOME"

GUI = Builder.load_file("tela.kv")

class TelaLogin(GridLayout):
    def __init__(self, **kwargs):
        super(TelaLogin, self).__init__(**kwargs)
        self.cols = 1

        self.top_grid = GridLayout()
        self.top_grid.cols = 2

        self.top_grid.add_widget(Label(text="E-Mail: "))
        self.email = TextInput(multiline=False)
        self.top_grid.add_widget(self.email)

        self.top_grid.add_widget(Label(text="Senha: "))
        self.senha = TextInput(multiline=False)
        self.top_grid.add_widget(self.senha)

        self.add_widget(self.top_grid)

        self.submit = Button(text="Login", font_size=32)
        self.submit.bind(on_press=self.press)
        self.add_widget(self.submit)

    def press(self, instance):
        email = self.email.text
        senha = self.senha.text

        print(f'Email: {email} | Senha: {senha}')
        self.add_widget(Label(text=f'Email: {email} | Senha: {senha}'))

class OceanStream(App):
    def build(self):
        return TelaLogin()
        # return GUI

    # def on_start(self):
    #     self.root.ids["titulo"].text = f"{self.agify('Giuliano')}"

    def agify(selft, nome):
        link = API_agify.replace('NOME', nome)
        requisicao = requests.get(link)

        if requisicao.status_code is not 200:
            return None

        dic_requisicao = requisicao.json()
        idade = dic_requisicao["age"]
        return idade

OceanStream().run()