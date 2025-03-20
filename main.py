from kivymd.app import MDApp
from kivymd.uix.button import MDRectangleFlatButton, MDRaisedButton
from kivymd.uix.card import MDCard
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.selectioncontrol import MDCheckbox
from kivy.clock import Clock
from kivy.config import Config
from kivy.graphics import Color, Rectangle
from kivy.lang import Builder
from kivy.properties import ObjectProperty, ListProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from plyer import storagepath
from datetime import datetime, timedelta
import json
import random
import requests
import os
import jwt
from kivy.animation import Animation

from kivy.core.window import Window
from kivy_garden.matplotlib import FigureCanvasKivyAgg
import matplotlib.pyplot as plt

class StyledCheckbox(MDCheckbox):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.inactive_color = (1, 1, 1, 1)  # Fundo branco quando desmarcado
        self.active_color = (0.2, 0.6, 1, 1)
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
API_PRFX = "https://oceanstream-8b3329b99e40.herokuapp.com/"

# Mapeamento de parâmetros para imagens
PARAMETROS_IMAGENS = {
    "Bateria":                 "res/bateria.png",                                                     # Corrente
    "Vel. Corr.":              "res/corrente- oceanstream.png",                                       # Corrente
    "Dir. Corr.":              "res/corrente-seta-direita.png",                                       # Corrente
    "Altura Onda":             "res/Onda com linha- oceanstream.png",                                 # Onda
    "Período Onda":            "res/Onda - oceanstream.png",                                          # Onda
    "Altura":                  "res/Onda com linha- oceanstream.png",                                 # Ondógrafo
    "Período":                 "res/Onda - oceanstream.png",                                          # Ondógrafo
    "Maré Reduzida":           "res/Régua maregrafo com seta - oceanstream (2).png",                  # Marégrafo
    "Vel. Vento":              "res/Pressão atmosférica - oceanstream.png",                           # Est.M
    "Rajada":                  "res/Pressão atmosférica - oceanstream.png",                           # Est.M
    "Dir. Vento":              "res/Rosa dos ventos - com direção de cor diferente-oceanstream.png",  # Est.M
    "Precipitação":            "res/Chuva - oceanstream.png",                                         # Est.M
}

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
            print(f"JWT recuperado.")
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

### API

def verifica_formato_data(data):
    """Verifica se a data está no formato YYYY-MM-DD."""
    try:
        datetime.strptime(data, "%Y-%m-%d")
        return True
    except ValueError:
        return False

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

### Telas

Builder.load_file('paginas/overview.kv')
Builder.load_file('paginas/alertas.kv')
Builder.load_file('paginas/login.kv')
Builder.load_file('paginas/configuracao.kv')
Builder.load_file('paginas/equipamento.kv')

class CardOverview(MDCard):
    offset_x = 50  # Espaçamento horizontal inicial
    offset_y = -10
    mlt = 5  # Multiplicador para o tamanho da imagem
    tamanho = (16 * mlt, 9 * mlt)  # Tamanho da imagem (16x9 proporção)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.visible = True  # Propriedade para controlar a visibilidade das imagens
        self.images = []  # Lista para armazenar as imagens do card
        self.canvas_images = []  # Lista para armazenar os objetos Rectangle das imagens
        self.top_labels = []  # Lista para armazenar os labels acima das imagens
        self.bottom_labels = []  # Lista para armazenar os labels abaixo das imagens

        # Vincula a atualização das imagens e labels às mudanças de posição e tamanho
        self.bind(pos=self.update_rect, size=self.update_rect)

    def add_image(self, source, top_text, bottom_number):
        """Adiciona uma imagem, uma label em cima e uma label em baixo ao card."""
        with self.canvas.after:
            # Define a cor (branca)
            Color(1, 1, 1, 1)
            # Cria o retângulo com a imagem
            rect = Rectangle(source=source, pos=(self.x + self.offset_x, self.y + self.offset_y), size=self.tamanho)
            self.canvas_images.append(rect)
            self.images.append(source)

            # Adiciona a label em cima da imagem
            top_label = Label(
                text=top_text,
                size_hint=(None, None),
                size=(self.tamanho[0], 20),  # Largura da imagem, altura fixa
                pos=(self.x + self.offset_x, self.y + self.offset_y + self.tamanho[1]),  # Acima da imagem
                color=(0, 0, 0, 1),  # Cor preta
                halign="center"  # Centraliza o texto horizontalmente
            )
            self.add_widget(top_label)
            self.top_labels.append(top_label)

            # Adiciona a label em baixo da imagem
            bottom_label = Label(
                text=str(bottom_number),
                size_hint=(None, None),
                size=(self.tamanho[0], 20),  # Largura da imagem, altura fixa
                pos=(self.x + self.offset_x, self.y + self.offset_y - 20),  # Abaixo da imagem
                color=(0, 0, 0, 1),  # Cor preta
                halign="center"  # Centraliza o texto horizontalmente
            )
            self.add_widget(bottom_label)
            self.bottom_labels.append(bottom_label)

    def update_rect(self, *args):
        """Atualiza a posição e o tamanho das imagens e labels."""
        if self.visible:
            for i, (rect, top_label, bottom_label) in enumerate(zip(self.canvas_images, self.top_labels, self.bottom_labels)):
                # Calcula a posição Y para centralizar verticalmente
                image_y = self.y + (self.height - self.tamanho[1]) / 2

                # Posiciona a imagem
                rect.pos = (
                    self.x + self.offset_x + (i * (self.tamanho[0] + 10)),  # Posição X com espaçamento
                    image_y  # Posição Y centralizada
                )
                rect.size = self.tamanho

                # Posiciona a label em cima da imagem
                top_label.font_size = 14
                top_label.pos = (
                    self.x + self.offset_x + (i * (self.tamanho[0] + 10)),  # Posição X com espaçamento
                    image_y + self.tamanho[1] # Acima da imagem
                )
                top_label.size = (self.tamanho[0], 20)  # Largura da imagem, altura fixa

                # Posiciona a label em baixo da imagem
                bottom_label.font_size = 16
                bottom_label.pos = (
                    self.x + self.offset_x + (i * (self.tamanho[0] + 10)),  # Posição X com espaçamento
                    image_y - 20  # Abaixo da imagem
                )
                bottom_label.size = (self.tamanho[0], 20)  # Largura da imagem, altura fixa
        else:
            # Oculta imagens e labels
            for rect in self.canvas_images:
                rect.size = (0, 0)
            for top_label in self.top_labels:
                top_label.size = (0, 0)
            for bottom_label in self.bottom_labels:
                bottom_label.size = (0, 0)

class Overview(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cards = []  # Lista para armazenar os widgets dos cards
        self.card_configs = dados_cards['cartoes']

        self.dicionario_parametros = { # conforme as colunas no banco de dados
                  'Vel. Corr.' : 'vel11',
                  'Dir. Corr.' : 'dir11',
                     'Bateria' : 'PNORS_Battery_Voltage',
                 'Altura Onda' : 'PNORW_Hm0',
                'Período Onda' : 'PNORW_Tp',

                      'Altura' : 'hm0_alisado',
                     'Período' : 'tp_alisado',

               'Maré Reduzida' : 'Mare_Reduzida',

                  'Vel. Vento' : 'Velocidade_Vento',
                      'Rajada' : 'Rajada_Vento',
                  'Dir. Vento' : 'Direcao_Vento',
                'Precipitação' : 'Chuva'
        }

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
            card = self.card_maximizado(card=card, config=card_config, idx=card_index)
        else:
            # Minimiza o card: oculta a imagem e exibe o conteúdo reduzido
            card = self.card_minimizado(card=card, config=card_config, idx=card_index)

        # Atualiza a imagem (oculta ou exibe)
        card.update_rect()
        self.reorganize_cards()
        salvar_cards(self.card_configs)

    def card_maximizado(self, card, config, str_datetime, idx):
        card.visible = True
        card.clear_widgets()

        # Usando FloatLayout para posicionar as labels de forma precisa
        layout = FloatLayout(size_hint=(1, 1))
        card.add_widget(layout)

        # Título do card (label superior)
        label_superior = Label(
            text=config["text"] + '      ',
            color=(0, 0, 0, 1),
            size_hint_y=None,  # Altura não ajustada automaticamente
            size_hint_x=1,  # Largura ajustada para ocupar todo o espaço disponível
            height=30,  # Altura fixa
            pos_hint={"x": 0, "top": 1},  # Alinha à esquerda e no topo
            halign="right",  # Alinha o texto à direita
            text_size=(self.width - 20, None),  # Define o tamanho do texto com um espaço de 20 pixels à direita
        )
        layout.add_widget(label_superior)

        # Label inferior
        label_inferior = Label(
            text= str_datetime + '      ',  # Texto da label inferior
            color=(0, 0, 0, 1),
            font_size=15,
            size_hint_y=None,  # Altura não ajustada automaticamente
            size_hint_x=1,  # Largura ajustada para ocupar todo o espaço disponível
            height=30,  # Altura fixa
            pos_hint={"x": 0, "y": 0},  # Alinha à esquerda e na parte inferior
            halign="right",  # Alinha o texto à direita
            text_size=(self.width - 20, None),  # Define o tamanho do texto com um espaço de 20 pixels à direita
        )
        layout.add_widget(label_inferior)

        card.height = 120
        return card

        # botão minimizar
        # card.add_widget(
        #     MDRectangleFlatButton(
        #         text="Minimizar",
        #         size_hint=(None, None),
        #         size=(150, 40),
        #         pos_hint={"center_x": 0.5, "center_y": 0.5},
        #         on_release=lambda btn, i=idx: self.toggle_card(i),
        #     )
        # )
        card.height = 120
        return card

    def card_minimizado(self, card, config, str_datetime, idx):
        return self.card_maximizado(card, config, str_datetime, idx)
        # falta inserir o datetime aqui no card minimizado
        card.visible = False
        card.clear_widgets()
        card.add_widget(
            Label(
                text=config["text"],
                color=(0.5, 0.5, 0.5, 1),
                height=30, # Define uma altura fixa para o Label
                size_hint_y=None, # Define que a altura não será ajustada automaticamente
                pos_hint={"top": 1}, # Alinha o Label no topo do card
            )
        )
        card.add_widget(
            MDRectangleFlatButton(
                text="Maximizar",
                size_hint=(None, None),
                size=(150, 40),
                pos_hint={"center_x": 0.5, "center_y": 0.5},
                on_release=lambda btn, i=idx: self.toggle_card(i),
            )
        )
        card.height = 60
        return card

    def reorganize_cards(self):
        card_container = self.ids.card_container
        card_container.clear_widgets()
        for card in self.cards:
            card_container.add_widget(card)

    def identifica_e_retorna_dados(self, equipment, ultimosDados):
        if '04' in equipment:
            return [ultimosDados['ADCP-Boia04_corrente'], ultimosDados['ADCP-Boia04_onda']]
        if '08' in equipment:
            return [ultimosDados['ADCP-Boia08_corrente'], ultimosDados['ADCP-Boia08_onda']]
        if '10' in equipment:
            return [ultimosDados['ADCP-Boia10_corrente'], ultimosDados['ADCP-Boia10_onda']]
        if 'II' in equipment:
            return ultimosDados['Ondografo-PII_tab_parametros']
        if 'TGL' in equipment:
            return ultimosDados['Ondografo-TGL_tab_parametros']
        if 'TPD' in equipment:
            return ultimosDados['Ondografo-TPD_tab_parametros']
        if 'TPM' in equipment:
            return ultimosDados['Ondografo-TPM_tab_parametros']
        if 'Est' in equipment:
            return ultimosDados['TU_Estacao_Meteorologica']
        if 'Mar' in equipment:
            return ultimosDados['Maregrafo-TU_Maregrafo_Troll']

    def genereate_cards(self):
        app = MDApp.get_running_app()
        selected_parameters = app.selected_parameters
        card_container = self.ids.card_container

        card_container.clear_widgets()
        self.cards.clear()

        active_parameters = {key: value for key, value in selected_parameters.items() if value}

        ultimosDados = api_ultimosDados()

        for idx, config in enumerate(self.card_configs):
            equipment = config.get("text")

            is_active = equipment in active_parameters
            if not is_active:
                self.card_configs[idx]['selecionado'] = []
                continue

            self.card_configs[idx]['selecionado'] = list(selected_parameters[equipment])
            new_card = CardOverview()

            dados = self.identifica_e_retorna_dados(equipment=equipment, ultimosDados=ultimosDados)
            if len(dados) == 2:
                data_hora = dados[0]['TmStamp']
                awac = True
            else:
                data_hora = dados['TmStamp']
                awac = False

            data_hora = data_hora[:-5]

            # parametros
            for param in selected_parameters[equipment]:
                if param in PARAMETROS_IMAGENS:
                    # agora precisa identificar o parametro no dicionario
                    coluna = self.dicionario_parametros[param]
                    if awac:
                        # primeiro identifica se vai referenciar corrente ou onda
                        if 'PNORW' in coluna:
                            # onda
                            dado = f"{dados[1][coluna]:.2f}"
                        else:
                            # corrente
                            dado = f"{dados[0][coluna]:.2f}"
                    else:
                        # demais equipamentos
                        dado = f"{dados[coluna]:.2f}"

                    new_card.add_image(PARAMETROS_IMAGENS[param], param, dado)  # Adiciona a legenda

            # Verifica o atributo "maximize" e define o estado inicial do card
            if config.get("maximize", True):
                new_card = self.card_maximizado(card=new_card, config=config, str_datetime=data_hora, idx=idx)
            else:
                new_card = self.card_minimizado(card=new_card, config=config, str_datetime='', idx=idx)

            self.cards.append(new_card)
            card_container.add_widget(new_card)

        salvar_cards(self.card_configs)

    def on_enter(self):
        self.genereate_cards()

class Alertas(MDScreen):
    pass

class Equipamento(MDScreen):
    equip = None
    data = ListProperty([])
    cor_label = (0, 0, 0, 1)
    is_landscape = False  # Estado atual da orientação

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_resize=self.detect_orientation)  # Monitora mudanças na tela
        self.build_ui()

        start_date = self.start_date_btn.text
        end_date = self.end_date_btn.text
        self.req_api(start_date, end_date)

    def detect_orientation(self, instance, width, height):
        return
        """Detecta a orientação da tela e atualiza a interface."""
        landscape = width > height
        if landscape != self.is_landscape:
            self.is_landscape = landscape
            self.update_view()  # Atualiza a interface para alternar entre tabela e gráfico

    def update_view(self):
        """Alterna entre tabela e gráfico dependendo da orientação da tela."""
        layout = self.ids.container
        layout.clear_widgets()  # Remove widgets antigos

        if self.is_landscape:
            self.plot_graph()
        else:
            self.build_ui()
            self.update_table()

    def build_ui(self):
        """ Adiciona os elementos da UI para a seleção de datas com calendário """
        layout = self.ids.box_dt

        # Dia de hoje
        hoje = datetime.now()
        hoje_formatado = hoje.strftime("%Y-%m-%d")  # Formato YYYY-MM-DD

        # Dia de ontem
        ontem = hoje - timedelta(days=1)
        ontem_formatado = ontem.strftime("%Y-%m-%d")  # Formato YYYY-MM-DD

        # data inicial
        self.start_date_btn = MDRaisedButton(
            text=ontem_formatado,
            on_release=self.show_start_date_picker)
        # data final
        self.end_date_btn = MDRaisedButton(
            text=hoje_formatado,
            on_release=self.show_end_date_picker)
        # botao submit
        generate_button = MDRaisedButton(
            text="Gerar Dados",
            on_release=self.validate_dates)
        
        layout.add_widget(self.start_date_btn)
        layout.add_widget(self.end_date_btn)
        layout.add_widget(generate_button)

    def identifica_equip(self):
        self.equip = 'Ondografo-PII_tab_parametros' # placeholder
        
        if self.equip == 'Ondografo-PII_tab_parametros':
            titulo = 'Ondógrafo Píer-II'
        if self.equip == 'Ondografo-TPD_tab_parametros':
            titulo = 'Ondógrafo TPD'
        if self.equip == 'Ondografo-TGL_tab_parametros':
            titulo = 'Ondógrafo TGL'
        if self.equip == 'Ondografo-TPM_tab_parametros':
            titulo = 'Ondógrafo TPM'

        if self.equip == 'ADCP-Boia04_corrente':
            titulo = 'Boia 04 - Corrente'
        if self.equip == 'ADCP-Boia08_corrente':
            titulo = 'Boia 08 - Corrente'
        if self.equip == 'ADCP-Boia10_corrente':
            titulo = 'Boia 10 - Corrente'
        if self.equip == 'ADCP-Boia04_onda':
            titulo = 'Boia 04 - Onda'
        if self.equip == 'ADCP-Boia08_onda':
            titulo = 'Boia 08 - Onda'
        if self.equip == 'ADCP-Boia10_onda':
            titulo = 'Boia 10 - Onda'

        if self.equip == 'Maregrafo-TU_Maregrafo_Troll':
            titulo = 'Marégrafo'

        if self.equip == 'TU_Estacao_Meteorologica':
            titulo = 'Estação Meteorológica'
        
        titulo_id = self.ids.titulo
        titulo_id.text = titulo

    def show_start_date_picker(self, instance):
        """ Abre o seletor de data para a data de início """
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=self.set_start_date)
        date_dialog.open()

    def set_start_date(self, instance, value, date_range):
        self.start_date_btn.text = value.strftime("%Y-%m-%d")
    
    def show_end_date_picker(self, instance):
        """ Abre o seletor de data para a data de fim """
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=self.set_end_date)
        date_dialog.open()

    def set_end_date(self, instance, value, date_range):
        self.end_date_btn.text = value.strftime("%Y-%m-%d")

    def req_api(self, start_date, end_date):
        # esvazia lista de dados
        self.data = []
        # identifica equipamento
        self.identifica_equip()
        dados_corr = api_dados(self.equip, start_date, end_date)

        # ADCP - Boia
        # corrente
        if '_corrente' in self.equip:
            for d in dados_corr:
                self.data.append([d['TmStamp'], d['vel11'], d['dir11'], d['PNORS_Battery_Voltage']])
        # onda
        if '_onda' in self.equip:
            for d in dados_corr:
                self.data.append([d['TmStamp'], d['PNORW_Hm0'], d['PNORW_Tp'], d['PNORW_DirTp']])
        if 'Ondografo' in self.equip:
            for d in dados_corr:
                self.data.append([d['TmStamp'], d['hm0_alisado'], d['tp_alisado']])
        if 'Estacao' in self.equip:
            for d in dados_corr:
                self.data.append([d['TmStamp'], d['Velocidade_Vento'], d['Rajada_Vento'], d['Direcao_Vento'], d['Chuva']])
        if 'Maregrafo' in self.equip:
            for d in dados_corr:
                self.data.append([d['TmStamp'], d['Mare_Reduzida']])

        self.data.reverse()
        self.update_table()

    def update_table(self):
        """ Atualiza a tabela com os dados """
        table_h = self.ids.header_table
        table = self.ids.data_table

        table_h.clear_widgets()
        table.clear_widgets()

        # Adiciona o cabeçalho
        if '_corrente' in self.equip: # ADCP Corrente
            table.cols = 4
            table_h.cols = 4
            table_h.add_widget(Label(text="TimeStamp", bold=True, color=self.cor_label))
            table_h.add_widget(Label(text="Velocidade", bold=True, color=self.cor_label))
            table_h.add_widget(Label(text="Direção (°)", bold=True, color=self.cor_label))
            table_h.add_widget(Label(text="Bateria (V)", bold=True, color=self.cor_label))
        if '_onda' in self.equip:
            table.cols = 4
            table_h.cols = 4
            table_h.add_widget(Label(text="TimeStamp", bold=True, color=self.cor_label))
            table_h.add_widget(Label(text="Altura (m)", bold=True, color=self.cor_label))
            table_h.add_widget(Label(text="Período (s)", bold=True, color=self.cor_label))
            table_h.add_widget(Label(text="Direção (°)", bold=True, color=self.cor_label))
        if 'Ondografo' in self.equip:
            table.cols = 3
            table_h.cols = 3
            table_h.add_widget(Label(text="TimeStamp", bold=True, color=self.cor_label))
            table_h.add_widget(Label(text="Altura (m)", bold=True, color=self.cor_label))
            table_h.add_widget(Label(text="Período (s)", bold=True, color=self.cor_label))
        if 'Estacao' in self.equip:
            table.cols = 5
            table_h.cols = 5
            table_h.add_widget(Label(text="TimeStamp", bold=True, color=self.cor_label))
            table_h.add_widget(Label(text="Vel. Vento", bold=True, color=self.cor_label))
            table_h.add_widget(Label(text="Rajada", bold=True, color=self.cor_label))
            table_h.add_widget(Label(text="Dir. Vento (°)", bold=True, color=self.cor_label))
            table_h.add_widget(Label(text="Precipitação (mm)", bold=True, color=self.cor_label))
        if 'Maregrafo' in self.equip:
            table.cols = 2
            table_h.cols = 2
            table_h.add_widget(Label(text="TimeStamp", bold=True, color=self.cor_label))
            table_h.add_widget(Label(text="Maré Reduzida (m)", bold=True, color=self.cor_label))

        # Adiciona os dados
        for row in self.data:
            for cell in row:
                table.add_widget(Label(text=cell, color=self.cor_label))
    
    def validate_dates(self, instance):
        """ Valida o intervalo de datas selecionado pelo usuário e atualiza os dados """
        start_date = self.start_date_btn.text
        end_date = self.end_date_btn.text
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            if (end - start).days > 7:
                self.end_date_btn.text = "Erro: Máx. 7 dias"
            else:
                self.req_api(start_date, end_date)
        except ValueError:
            self.start_date_btn.text = "Selecionar Data Início"
            self.end_date_btn.text = "Selecionar Data Fim"

    def plot_graph(self):
        """Gera um gráfico a partir dos dados da tabela."""
        if not self.data:
            return

        timestamps = [row[0] for row in self.data]
        velocidades = [float(row[1]) for row in self.data]

        fig, ax = plt.subplots()
        ax.plot(timestamps, velocidades, marker="o", linestyle="-", color="blue")
        ax.set_title("Velocidade da Corrente")
        ax.set_xlabel("Tempo")
        ax.set_ylabel("Velocidade (Kn)")
        ax.grid()

        canvas = FigureCanvasKivyAgg(fig)
        self.ids.container.add_widget(canvas)  # Exibe o gráfico na tela

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
        url = API_PRFX+'login'
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
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # apenas no primeiro carregamento precisa consultar os dados do arquivo JSON
        self.first=True

        self.dicionario_parametros = { # conforme os IDs das checkboxes em 'configuracao.kv'
                  'Vel. Corr.' : 'vel',
                  'Dir. Corr.' : 'dir',
                 'Altura Onda' : 'altura',
                'Período Onda' : 'periodo',
                      'Altura' : 'altura',
                     'Período' : 'periodo',
                     'Bateria' : 'bateria',
               'Maré Reduzida' : 'mare',
                  'Vel. Vento' : 'velvento',
                      'Rajada' : 'rajada',
                  'Dir. Vento' : 'dirvento',
                'Precipitação' : 'precipitacao'
        }

    def on_enter(self):
        if self.first:
            self.seleciona_chkbx()
            self.first=False

    def identifica_equipamento(self, equip):
        id_base = 'chkbx_'
        # adcp
        if 'Boia' in equip:
            if '04' in equip:
                id_equip = id_base+'b04_'
            elif '08' in equip:
                id_equip = id_base+'b08_'
            elif '10' in equip:
                id_equip = id_base+'b10_'
        # maregrafo
        elif 'Marégraf' in equip:
            id_equip = id_base+'maregrafo_'
        # estação
        elif 'Estação' in equip:
            id_equip = id_base+'estacao_'
        # ondografo
        elif 'Ondógrafo' in equip:
            if 'II' in equip:
                id_equip = id_base+'pii_'
            elif 'TGL' in equip:
                id_equip = id_base+'tgl_'
            elif 'TPD' in equip:
                id_equip = id_base+'tpd_'
            elif 'TPM' in equip:
                id_equip = id_base+'tpm_'
        return id_equip

    def seleciona_chkbx(self):
        app = MDApp.get_running_app()
        # Percorre cada um dos equipamentos selecionados
        for equip in app.selected_parameters:
            id_equip = self.identifica_equipamento(equip)

            # Percorre cada um dos parametros do equipamento atual
            for parametro in app.selected_parameters[equip]:
                id_parametro = self.dicionario_parametros[parametro]
                chkbx_id = f'{id_equip}{id_parametro}'
                self.alterar_estado_checkbox(chkbx_id, 'down')
        return

    def alterar_estado_checkbox(self, checkbox_id, novo_estado):
        """
        Altera o estado de uma checkbox específica.
        :param checkbox_id: O ID da checkbox (string).
        :param novo_estado: O novo estado ('down' para marcado, 'normal' para desmarcado).
        """
        if checkbox_id in self.ids:
            checkbox = self.ids[checkbox_id]
            if isinstance(checkbox, StyledCheckbox):
                checkbox.state = novo_estado
            else:
                print(f'O ID {checkbox_id} não é uma StyledCheckbox.')
        else:
            print(f'Checkbox com ID {checkbox_id} não encontrada.')

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

# class

class OceanStream(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_parameters = {}

        for equip in dados_cards['cartoes']:
            if list(equip['selecionado']):
                self.selected_parameters[equip['text']] = []
                for param in list(equip['selecionado']):
                    if param not in self.selected_parameters[equip['text']]:  # Evitar duplicatas
                        self.selected_parameters[equip['text']].append(param)

    def build(self):
        self.gerenciador = GerenciadorTelas()

        self.gerenciador.add_widget(TelaCarregamento(name='load'))
        self.gerenciador.add_widget(Overview(name='overview'))
        self.gerenciador.add_widget(Alertas(name='alertas'))
        self.gerenciador.add_widget(TelaLogin(name='login'))
        self.gerenciador.add_widget(Configuracao(name='configuracao'))
        self.gerenciador.add_widget(Equipamento(name='equipamento'))

        self.gerenciador.current = 'load'

        self.navigation_bar = NavigationBar(screen_manager=self.gerenciador, logout_callback=self.logout)

        self.gerenciador.bind(current=self.on_screen_change)

        return self.navigation_bar

    def toggle_parameter(self, equipment, parameter, state):
        if equipment not in self.selected_parameters:
            # self.selected_parameters[equipment] = set()
            self.selected_parameters[equipment] = []

        if state == 'down':
            if parameter not in self.selected_parameters[equipment]:
                self.selected_parameters[equipment].append(parameter)
        else:
            if parameter in self.selected_parameters[equipment]:
                self.selected_parameters[equipment].remove(parameter)

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
