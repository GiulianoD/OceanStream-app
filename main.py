from kivymd.app import MDApp
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.card import MDCard
from kivymd.uix.screen import MDScreen, MDScreen
from kivymd.uix.screenmanager import MDScreenManager
# from kivymd.uix.selectioncontrol import MDCheckbox # usar para manipular as checkboxes
from kivy.clock import Clock
from kivy.config import Config
from kivy.graphics import Color, Rectangle
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty, NumericProperty
from kivy.uix.label import Label
from plyer import storagepath
from datetime import datetime
import json
import requests
import os
import jwt
from kivy.animation import Animation
from kivymd.uix.selectioncontrol import MDCheckbox

class StyledCheckbox(MDCheckbox):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.inactive_color = (1, 1, 1, 1)  # Fundo branco quando desmarcado
        self.line_color_normal = (0.8, 0.8, 0.8, 1)  # Borda cinza claro antes de ser selecionado

    def animate_checkbox(self, state):
        if state == "down":
            anim = Animation(active_color=(0.2, 0.6, 1, 1), duration=0.2)  # Azul vibrante quando marcado
        else:
            anim = Animation(active_color=(1, 1, 1, 1), duration=0.2)  # Mantém fundo branco quando desmarcado
        anim.start(self)



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

# Mapeamento de parâmetros para imagens
PARAMETROS_IMAGENS = {
    "Corrente Fundo":               "res/placeholder/cardicon/corrente_fundo.png",
    "Corrente Meio":                "res/placeholder/cardicon/corrente_meio.png",
    "Corrente Superfície":          "res/placeholder/cardicon/corrente_superficie.png",
    "Ondas":                        "res/placeholder/cardicon/ondas.png",
    "Sea":                          "res/placeholder/cardicon/sea.png",
    "Swell":                        "res/placeholder/cardicon/swell.png",
    "Nível do Mar":                 "res/placeholder/cardicon/nivel_mar.png",
    "Ventos":                       "res/placeholder/cardicon/ventos.png",
    "Altura Significativa de Onda": "res/placeholder/cardicon/altura_onda.png",
    "Altura Máxima":                "res/placeholder/cardicon/altura_maxima.png",
    "Período":                      "res/placeholder/cardicon/periodo.png",
}

def ler_arquivo_json(caminho_arquivo):
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

def salvar_arquivo_json(data, caminho_arquivo):
    try:
        with open(caminho_arquivo, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Erro ao salvar JSON: {e}")

def salvar_cards(dict):
    dict_completo = {
        "nome": "Overview - Cards",
        "atualizado_em": str(datetime.now()),
        "cartoes": dict
    }
    salvar_arquivo_json(data=dict_completo, caminho_arquivo='data/cards.json')

dados_cards = ler_arquivo_json(caminho_arquivo='data/cards.json')

### Telas

Builder.load_file('paginas/overview.kv')
Builder.load_file('paginas/alertas.kv')
Builder.load_file('paginas/login.kv')
Builder.load_file('paginas/configuracao.kv')

class CardOverview(MDCard):
    offset_x = +50
    offset_y = 0
    tamanho = (75, 75)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.visible = True  # Propriedade para controlar a visibilidade das imagens
        self.images = []  # Lista para armazenar as imagens do card
        self.canvas_images = []  # Lista para armazenar os objetos Rectangle das imagens

        # Vincula a atualização das imagens às mudanças de posição e tamanho
        self.bind(pos=self.update_rect, size=self.update_rect)

    def add_image(self, source):
        """Adiciona uma imagem ao card."""
        with self.canvas.after:
            # Define a cor (branca)
            Color(1, 1, 1, 1)
            # Cria o retângulo com a imagem
            rect = Rectangle(source=source, pos=(self.x + self.offset_x, self.y + self.offset_y), size=self.tamanho)
            
            self.canvas_images.append(rect)
            self.images.append(source)

    def update_rect(self, *args):
        """Atualiza a posição e o tamanho das imagens."""
        if self.visible:
            for i, rect in enumerate(self.canvas_images):
                rect.pos = (self.x + self.offset_x + (i * 80), self.y + self.offset_y)  # Ajusta a posição para evitar sobreposição
                rect.size = self.tamanho
        else:
            # Se não estiver visível, define o tamanho como (0, 0) para ocultar
            for rect in self.canvas_images:
                rect.size = (0, 0)

class Overview(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cards = []  # Lista para armazenar os widgets dos cards
        self.card_configs = dados_cards['cartoes']

    def toggle_card(self, card_index):
        indice_ref = int(card_index)
        indice_geral = 0
        indice_active = indice_ref

        while indice_geral < indice_ref:
            if not list(self.card_configs[indice_geral]['selecionado']):
                indice_active -= 1
            indice_geral += 1

        card_config = self.card_configs[card_index]
        card = self.cards[indice_active]

        card_config["maximize"] = not card_config["maximize"]

        if card_config["maximize"]:
            # Maximiza o card: exibe a imagem e o conteúdo original
            card.visible = True
            card.clear_widgets()
            card.add_widget(
                    Label(
                        text=card_config["text"],
                        color=(0, 0, 0, 1),
                        height=30,  # Define uma altura fixa para o Label
                        size_hint_y=None,  # Define que a altura não será ajustada automaticamente
                        pos_hint={"top": 1},  # Alinha o Label no topo do card
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
            # Minimiza o card: oculta a imagem e exibe o conteúdo reduzido
            card.visible = False
            card.clear_widgets()
            card.add_widget(
                Label(
                    text=card_config["text"],
                    color=(0.5, 0.5, 0.5, 1),
                    height=30,  # Define uma altura fixa para o Label
                    size_hint_y=None,  # Define que a altura não será ajustada automaticamente
                    pos_hint={"top": 1},  # Alinha o Label no topo do card
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

        # Atualiza a imagem (oculta ou exibe)
        card.update_rect()
        self.reorganize_cards()
        salvar_cards(self.card_configs)

    def reorganize_cards(self):
        card_container = self.ids.card_container
        card_container.clear_widgets()
        for card in self.cards:
            card_container.add_widget(card)

    def genereate_cards(self):
        app = MDApp.get_running_app()
        selected_parameters = app.selected_parameters
        card_container = self.ids.card_container

        card_container.clear_widgets()
        self.cards.clear()

        active_parameters = {key: value for key, value in selected_parameters.items() if value}

        for idx, config in enumerate(self.card_configs):
            equipment = config.get("text")

            is_active = equipment in active_parameters
            if not is_active:
                self.card_configs[idx]['selecionado'] = []
                continue

            self.card_configs[idx]['selecionado'] = list(selected_parameters[equipment])
            new_card = CardOverview()

            # Adiciona as imagens correspondentes aos parâmetros selecionados
            for param in selected_parameters[equipment]:
                if param in PARAMETROS_IMAGENS:
                    new_card.add_image(PARAMETROS_IMAGENS[param])

            # Verifica o atributo "maximize" e define o estado inicial do card
            if config.get("maximize", True):
                # Card maximizado
                # new_card.add_widget(Label(text=config["text"], color=(0, 0, 0, 1)))
                new_card.add_widget(
                    Label(
                        text=config["text"],
                        color=(0, 0, 0, 1),
                        size_hint_y=None,  # Define que a altura não será ajustada automaticamente
                        height=30,  # Define uma altura fixa para o Label
                        pos_hint={"top": 1},  # Alinha o Label no topo do card
                    )
                )
                new_card.add_widget(
                    MDRectangleFlatButton(
                        text="Minimizar",
                        size_hint=(None, None),
                        size=(150, 40),
                        pos_hint={"center_x": 0.5, "center_y": 0.5},
                        on_release=lambda btn, i=idx: self.toggle_card(i),
                    )
                )
                new_card.height = 120
            else:
                new_card.visible = False
                # new_card.add_widget(Label(text=config["text"], color=(0.5, 0.5, 0.5, 1)))
                new_card.add_widget(
                    Label(
                        text=config["text"],
                        color=(0.5, 0.5, 0.5, 1),
                        size_hint_y=None,  # Define que a altura não será ajustada automaticamente
                        height=30,  # Define uma altura fixa para o Label
                        pos_hint={"top": 1},  # Alinha o Label no topo do card
                    )
                )
                # Card minimizado
                new_card.add_widget(
                    MDRectangleFlatButton(
                        text="Maximizar",
                        size_hint=(None, None),
                        size=(150, 40),
                        pos_hint={"center_x": 0.5, "center_y": 0.5},
                        on_release=lambda btn, i=idx: self.toggle_card(i),
                    )
                )
                new_card.height = 60

            self.cards.append(new_card)
            card_container.add_widget(new_card)

        salvar_cards(self.card_configs)

    def on_enter(self):
        self.genereate_cards()

class Alertas(MDScreen):
    pass

class TelaLogin(MDScreen):
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

class Configuracao(MDScreen):
    pass

class TelaCarregamento(MDScreen):
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

class GerenciadorTelas(MDScreenManager):
    pass

class OceanStream(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_parameters = {}

        for equip in dados_cards['cartoes']:
            if list(equip['selecionado']):
                self.selected_parameters[equip['text']] = set()
                for param in list(equip['selecionado']):
                    self.selected_parameters[equip['text']].add(param)

    def build(self):
        self.gerenciador = GerenciadorTelas()

        self.gerenciador.add_widget(TelaCarregamento(name='load'))
        self.gerenciador.add_widget(Overview(name='overview'))
        self.gerenciador.add_widget(Alertas(name='alertas'))
        self.gerenciador.add_widget(TelaLogin(name='login'))
        self.gerenciador.add_widget(Configuracao(name='configuracao'))

        self.gerenciador.current = 'load'

        self.navigation_bar = NavigationBar(screen_manager=self.gerenciador, logout_callback=self.logout)

        self.gerenciador.bind(current=self.on_screen_change)

        return self.navigation_bar

    def toggle_parameter(self, equipment, parameter, state):
        if equipment not in self.selected_parameters:
            self.selected_parameters[equipment] = set()

        if state == 'down':
            self.selected_parameters[equipment].add(parameter)
        else:
            self.selected_parameters[equipment].discard(parameter)

        print(f"Parâmetros selecionados para {equipment}: {self.selected_parameters[equipment]}")
        
        app = MDApp.get_running_app()
        if app.gerenciador.current == "overview":
            app.gerenciador.get_screen("overview").genereate_cards()

    def on_screen_change(self, instance, value):
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
