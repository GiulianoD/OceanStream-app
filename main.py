from kivymd.app import MDApp
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.card import MDCard
from kivy.clock import Clock
from kivy.config import Config
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty, NumericProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label
from plyer import storagepath
from datetime import datetime
import json
import requests
import os
import jwt
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

### JSON

def ler_arquivo_json(caminho_arquivo='dados.json'):
    """
    Lê dados de um arquivo JSON.

    Args:
        caminho_arquivo (str): Caminho para o arquivo JSON.

    Returns:
        dict | list: Dados carregados do arquivo JSON.
                     Retorna None se ocorrer um erro.
    """
    try:
        with open(caminho_arquivo, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
        print("JSON carregado com sucesso!")
        return dados
    except FileNotFoundError:
        print(f"Erro: O arquivo '{caminho_arquivo}' não foi encontrado.")
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar o JSON: {e}")
    return None

def salvar_arquivo_json(data, caminho_arquivo='dados.json'):
    """
    Salva um dicionário em um arquivo JSON.
    
    :param data: Dicionário a ser salvo.
    :param file_path: Caminho e nome do arquivo JSON.
    """
    try:
        with open(caminho_arquivo, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        print(f"Dicionário salvo como JSON em: {caminho_arquivo}")
    except Exception as e:
        print(f"Erro ao salvar JSON: {e}")
dados = ler_arquivo_json()

def salvar_cards(dict):
    dict_completo = {
        "nome": "Overview - Cards",
        "atualizado_em": str(datetime.now()),
        "cartoes": dict
    }
    salvar_arquivo_json(dict_completo)

### Telas

class CardWidget(MDCard):
    card_id = NumericProperty(0)
    title = StringProperty("")
    active = BooleanProperty(False)

    def __init__(self, card_id, title, **kwargs):
        super().__init__(**kwargs)
        self.card_id = card_id
        self.title = title
        self.active = False

    def update_card_state(self):
        # Atualiza o visual do card com base em seu estado ativo/inativo
        self.md_bg_color = (0.2, 0.8, 0.2, 1) if self.active else (0.9, 0.9, 0.9, 1)


Builder.load_file('paginas/overview.kv')
Builder.load_file('paginas/alertas.kv')
Builder.load_file('paginas/login.kv')
Builder.load_file('paginas/configuracao.kv')


class Overview(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cards = []  # Lista para armazenar os widgets dos cards
        self.card_configs = dados['cartoes']

    def toggle_card(self, card_index):  
        """
        Minimiza um card e reorganiza os cartões visíveis.
        """

        # encontra o indice entre os cards ativos
        indice_ref = int(card_index)
        indice_geral = 0
        indice_active = indice_ref

        while indice_geral<indice_ref:
            if not self.card_configs[indice_geral]['active']:
                indice_active-=1
            indice_geral+=1

        print(f'Indice geral: {card_index}')
        print(f'Indice ativo: {indice_active}')

        card_config = self.card_configs[card_index]
        card = self.cards[indice_active]

        # Alterna entre maximizado e minimizado
        card_config["maximize"] = not card_config["maximize"]

        if card_config["maximize"]:
            # Maximiza o card: retorna ao tamanho original e conteúdo original
            card.clear_widgets()
            card.add_widget(
                Label(
                    text=card_config["text"],
                    color=(0, 0, 0, 1),
                    size_hint=(1, 1),
                )
            )
            card.add_widget(
                MDRectangleFlatButton(
                    text="Minimizar",
                    size_hint=(None, None),
                    size=(150, 40),
                    pos_hint={"center_x": 0.5, "center_y": 0.5},
                    on_release=lambda btn, i=card_index: self.toggle_card(i),
                )
            )
            card.height = 120
        else:
            # Minimiza o card: substitui o conteúdo pelo indicador de minimização
            card.clear_widgets()
            card.add_widget(
                Label(
                    text=card_config["text"],
                    color=(0.5, 0.5, 0.5, 1),
                    size_hint=(1, 1),
                )
            )
            card.add_widget(
                MDRectangleFlatButton(
                    text="Maximizar",
                    size_hint=(None, None),
                    size=(150, 40),
                    pos_hint={"center_x": 0.5, "center_y": 0.5},
                    on_release=lambda btn, i=card_index: self.toggle_card(i),
                )
            )
            card.height = 60

        # Reorganiza os cartões
        self.reorganize_cards()

    def reorganize_cards(self):
        """
        Reorganiza os cartões no contêiner para refletir o estado atual.
        """
        card_container = self.ids.card_container
        card_container.clear_widgets()
        for card in self.cards:
            card_container.add_widget(card)

    def genereate_cards(self):
        """
        Recria os cards no container com base nos parâmetros ativos em self.selected_parameters.
        """
        print('Recriando cartões na visão geral...')
        app = MDApp.get_running_app()  # Acessa a instância do aplicativo
        selected_parameters = app.selected_parameters  # Obtém os parâmetros selecionados
        card_container = self.ids.card_container

        # Limpa widgets existentes
        card_container.clear_widgets()
        self.cards.clear()

        # Identificar variáveis principais e verificar se possuem conteúdo
        active_parameters = {key: value for key, value in selected_parameters.items() if value}
        inactive_parameters = {key: value for key, value in selected_parameters.items() if not value}

        # print(selected_parameters)
        print("Parâmetros com conteúdo (ativos):", active_parameters)
        print("Parâmetros sem conteúdo (inativos):", inactive_parameters)

        # Filtra e recria os cartões ativos
        for idx, config in enumerate(self.card_configs):
            equipment = config.get("text")  # Usa o texto como identificador do equipamento

            print(equipment)
            # is_active = equipment in selected_parameters
            is_active = any(equipment in key for key in active_parameters)
            self.card_configs[idx]['active'] = is_active
            if not is_active:
                # parent_widget.remove_widget(card_widget)
                # selected_parameters.pop(equipment, None)
                continue

            # Configura os widgets do cartão
            new_card = MDCard(
                size_hint=(1, None),
                height=120,
                elevation=2,
                radius=[20, 20, 20, 20],
            )
            new_card.add_widget(Label(text=config["text"], color=(0, 0, 0, 1)))
            new_card.add_widget(
                MDRectangleFlatButton(
                    text="Minimizar",
                    size_hint=(None, None),
                    size=(150, 40),
                    pos_hint={"center_x": 0.5, "center_y": 0.5},
                    on_release=lambda btn, i=idx: self.toggle_card(i),
                )
            )
            self.cards.append(new_card)
            card_container.add_widget(new_card)
        salvar_cards(self.card_configs)

    def on_enter(self):
        print('overview on_enter')
        self.genereate_cards()

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
        
        app = MDApp.get_running_app()
        if app.gerenciador.current == "overview":
            app.gerenciador.get_screen("overview").genereate_cards()

    def on_screen_change(self, instance, value):
        # Oculta a toolbar se a tela atual for 'login' ou 'configuracao'
        if value in ['login', 'configuracao', 'load']:
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
