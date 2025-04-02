from kivymd.app import MDApp
from kivymd.uix.button import MDRectangleFlatButton, MDRaisedButton
from kivymd.uix.card import MDCard
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.selectioncontrol import MDCheckbox
from kivy.clock import Clock
from kivy.config import Config
from kivy.lang import Builder
from kivy.properties import ObjectProperty, ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from plyer import storagepath
from datetime import datetime, timedelta
import json
import requests
import os
import jwt
from threading import Thread
from kivy.animation import Animation
from kivy.core.window import Window
from kivy_garden.matplotlib import FigureCanvasKivyAgg
import matplotlib.pyplot as plt
from kivy.metrics import dp
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView  # se ainda não tiver

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
    "Chuva":                   "res/Chuva - oceanstream.png",                                         # Est.M
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
            return True
        else:
            print(f"Falha no login: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Erro ao tentar fazer login: {str(e)}")
    
    return False

### Telas

Builder.load_file('paginas/splash.kv')
Builder.load_file('paginas/overview.kv')
Builder.load_file('paginas/alertas.kv')
Builder.load_file('paginas/login.kv')
Builder.load_file('paginas/configuracao.kv')
Builder.load_file('paginas/equipamento.kv')

class CardOverview(MDCard):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tamanho = (80, 60)  # ou (width, height) ideal para suas imagens

    def add_image_scrollable(self, imagens_dados, target_layout=None):
        """Adiciona uma linha horizontal scrollável de imagens com labels dentro de um layout específico (FloatLayout ou direto no Card)."""
        altura_total = self.tamanho[1] + 60

        scroll = ScrollView(
            size_hint=(1, None),
            height=altura_total,
            scroll_type=['bars', 'content'],
            bar_width=2,
            do_scroll_x=True,
            do_scroll_y=False,
            pos_hint={"top": 1}
        )

        image_row = BoxLayout(
            orientation='horizontal',
            size_hint_x=None,
            height=altura_total,
                padding=[10, 20, 40, 10],  # esquerda, cima, direita, baixo
            spacing=20
        )
        image_row.bind(minimum_width=image_row.setter('width'))

        for source, top_text, bottom_text in imagens_dados:
            layout = BoxLayout(
                orientation='vertical',
                size_hint=(None, 1),
                width=self.tamanho[0],
                spacing=0
            )

            top_label = Label(
                text=top_text,
                size_hint=(1, None),
                height=25, 
                color=(0, 0, 0, 1)
            )

            image = Image(
                source=source,
                size_hint=(1, None),
                height=self.tamanho[1],
                allow_stretch=True,
                keep_ratio=True
            )

            bottom_label = Label(
                text=str(bottom_text),
                size_hint=(1, None),
                height=20,
                color=(0, 0, 0, 1)
            )

            layout.add_widget(top_label)
            layout.add_widget(image)
            layout.add_widget(bottom_label)

            image_row.add_widget(layout)

        scroll.add_widget(image_row)

        if target_layout:
            target_layout.add_widget(scroll)
        else:
            self.add_widget(scroll)
            self.height = altura_total + 20

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
                       'Chuva' : 'Chuva'
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

    def card_maximizado(self, card, config, str_datetime, idx, imagens_dados=None):
        card.clear_widgets()

        layout = BoxLayout(
            orientation='vertical',
            spacing=10,
            padding=[10, 10, 10, 10],
            size_hint=(1, None)
        )
        layout.bind(minimum_height=layout.setter("height"))
        card.add_widget(layout)

        if imagens_dados:
            card.add_image_scrollable(imagens_dados, target_layout=layout)

        # card.height = layout.height + 20
        card.height = max(180, layout.height + 20)
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
        # Inicia uma thread para processamento pesado
        Thread(target=self._generate_cards_threaded, daemon=True).start()

    def _generate_cards_threaded(self):
        # Esta parte é executada em uma thread separada
        app = MDApp.get_running_app()
        selected_parameters = app.selected_parameters
        ultimosDados = api_ultimosDados()  # Esta chamada pode ser lenta
        
        # Prepara os dados que serão usados na UI
        cards_data = []
        for idx, config in enumerate(self.card_configs):
            equipment = config.get("text")
            is_active = equipment in selected_parameters
            if not is_active:
                continue

            dados = self.identifica_e_retorna_dados(equipment=equipment, ultimosDados=ultimosDados)
            if len(dados) == 2:
                data_hora = dados[0]['TmStamp']
                awac = True
            else:
                data_hora = dados['TmStamp']
                awac = False

            data_hora = data_hora[:-5]
            imagens_dados = []
            
            for param in selected_parameters[equipment]:
                if param in PARAMETROS_IMAGENS:
                    coluna = self.dicionario_parametros[param]
                    if awac:
                        if 'PNORW' in coluna:
                            dado = f"{dados[1][coluna]:.2f}"
                        else:
                            dado = f"{dados[0][coluna]:.2f}"
                    else:
                        dado = f"{dados[coluna]:.2f}"
                    imagens_dados.append((PARAMETROS_IMAGENS[param], param, dado))

            cards_data.append({
                'equipment': equipment,
                'data_hora': data_hora,
                'imagens_dados': imagens_dados,
                'config': config,
                'idx': idx
            })

        # Agendando a atualização da UI na thread principal
        Clock.schedule_once(lambda dt: self._update_ui(cards_data))

    def _update_ui(self, cards_data):
        # Esta parte é executada na thread principal
        card_container = self.ids.card_container
        card_container.clear_widgets()
        self.cards.clear()

        for card_info in cards_data:
            # Cria o header do card
            header_card = MDCard(
                size_hint=(1, None),
                height=40,
                md_bg_color=(0.9, 0.9, 0.95, 1),
                padding=[10, 5, 10, 5],
                radius=[12, 12, 12, 12],
                elevation=1,
            )
            header_label = Label(
                text=f"{card_info['equipment']} - último dado: {card_info['data_hora']}",
                color=(0, 0, 0, 1),
                halign="left",
                valign="middle"
            )
            header_card.add_widget(header_label)
            card_container.add_widget(header_card)

            # Cria o card principal
            new_card = CardOverview()
            if card_info['config'].get("maximize", True):
                self.card_maximizado(
                    card=new_card, 
                    config=card_info['config'], 
                    str_datetime=card_info['data_hora'], 
                    idx=card_info['idx'], 
                    imagens_dados=card_info['imagens_dados']
                )
            else:
                self.card_minimizado(
                    card=new_card, 
                    config=card_info['config'], 
                    str_datetime='', 
                    idx=card_info['idx']
                )

            self.cards.append(new_card)
            card_container.add_widget(new_card)

        # Adiciona espaço em branco para a nav_bar não sobrepor o último card
        card_container.add_widget(Widget(size_hint_y=None, height=65))
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
    canvas_widget = None  # Armazena o widget do gráfico para remoção correta

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_resize=self.detect_orientation)  # Monitora mudanças na tela
        self.build_ui()

    def detect_orientation(self, instance, width, height):
        """Detecta a orientação da tela e atualiza a interface."""
        landscape = width > height
        if landscape != self.is_landscape:
            self.is_landscape = landscape
            self.update_view()  # Atualiza a interface para alternar entre tabela e gráfico

    def update_view(self):
        """Alterna entre tabela e gráfico dependendo da orientação da tela."""
        layout = self.ids.container

        # Remove todos os widgets do container (gráfico ou tabela)
        if self.canvas_widget:
            layout.remove_widget(self.canvas_widget)
            self.canvas_widget = None

        # Remove a tabela (reconstrói do zero depois, se necessário)
        self.rebuild_table(clear_only=True)

        if self.is_landscape:
            self.toggle_header_visibility(False)  # Esconde cabeçalho e filtros
            self.plot_graph()
        else:
            self.toggle_header_visibility(True)   # Mostra tudo
            self.rebuild_table()

    def rebuild_table(self, clear_only=False):
        """Reconstrói a tabela ou apenas limpa, se necessário."""
        table_h = self.ids.header_table
        table = self.ids.data_table

        table.clear_widgets()
        table_h.clear_widgets()

        if clear_only:
            return

        self.build_ui()
        self.update_table()

    def build_ui(self):
        """ Adiciona os elementos da UI para a seleção de datas com calendário """
        layout = self.ids.box_dt
        layout.clear_widgets()  # EVITAR DUPLICAÇÃO

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
            table_h.add_widget(Label(text="Chuva (mm)", bold=True, color=self.cor_label))
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
        """Gera um gráfico com Velocidade e Direção interativo."""
        if not self.data:
            return

        import matplotlib.dates as mdates
        from matplotlib.backend_bases import MouseEvent
        from matplotlib.widgets import Cursor
        from datetime import datetime

        timestamps = [datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S") for row in self.data]
        velocidades = [float(row[1]) for row in self.data]
        try:
            direcoes = [float(row[2]) for row in self.data]
        except IndexError:
            direcoes = [0 for _ in self.data]  # fallback

        fig, ax = plt.subplots(figsize=(10, 4))

        line1, = ax.plot(timestamps, velocidades, marker="o", linestyle="-", color="blue", label="Velocidade (Kn)")
        line2, = ax.plot(timestamps, direcoes, marker="s", linestyle="--", color="red", label="Direção (º)")

        # Formatação do eixo X
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))
        fig.autofmt_xdate()

        ax.set_title("Velocidade e Direção da Corrente")
        ax.set_xlabel("Tempo")
        ax.set_ylabel("Valor")
        ax.legend()
        ax.grid(True)

        # Cursor interativo
        cursor = Cursor(ax, useblit=True, color='black', linewidth=1)

        # Interatividade com texto ao tocar
        annot = ax.annotate("", xy=(0,0), xytext=(20,20), textcoords="offset points",
                            bbox=dict(boxstyle="round", fc="w"), arrowprops=dict(arrowstyle="->"))
        annot.set_visible(False)

        def update_annot(ind, line):
            x, y = line.get_data()
            annot.xy = (x[ind[0]], y[ind[0]])
            text = f"{x[ind[0]].strftime('%H:%M')}: {y[ind[0]]:.2f}"
            annot.set_text(text)
            annot.get_bbox_patch().set_facecolor('lightyellow')
            annot.get_bbox_patch().set_alpha(0.8)

        def hover(event):
            vis = annot.get_visible()
            if event.inaxes == ax:
                for line in [line1, line2]:
                    cont, ind = line.contains(event)
                    if cont:
                        update_annot(ind["ind"], line)
                        annot.set_visible(True)
                        fig.canvas.draw_idle()
                        return
            if vis:
                annot.set_visible(False)
                fig.canvas.draw_idle()

        fig.canvas.mpl_connect("motion_notify_event", hover)

        if self.canvas_widget:
            self.ids.container.remove_widget(self.canvas_widget)

        self.canvas_widget = FigureCanvasKivyAgg(fig)
        self.canvas_widget.size_hint_y = 1
        self.canvas_widget.pos_hint = {"center_x": 0.5, "center_y": 0.5}

        self.ids.container.add_widget(self.canvas_widget)

    def on_enter(self):
        start_date = self.start_date_btn.text
        end_date = self.end_date_btn.text
        self.req_api(start_date, end_date)
        self.update_view()  # Alterna a visualização de acordo com a orientação atual
        self.detect_orientation(Window, Window.width, Window.height)
    
    def toggle_header_visibility(self, visible):
        header = self.ids.get("titulo", None)
        if header:
            header.opacity = 1 if visible else 0
            header.disabled = not visible

        box_dt = self.ids.box_dt
        header_table = self.ids.header_table

        box_dt.height = dp(50) if visible else 0
        header_table.height = dp(40) if visible else 0

        box_dt.opacity = 1 if visible else 0
        box_dt.disabled = not visible
        header_table.opacity = 1 if visible else 0
        header_table.disabled = not visible

class TelaLogin(MDScreen):
    email = ObjectProperty(None)
    senha = ObjectProperty(None)

    def on_enter(self):
        pass

    def submit(self):
        email = self.ids.email.text
        senha = self.ids.senha.text
        self.ids.senha.text = ""

        if login(email=email, senha=senha):
            self.manager.current = 'overview'

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
                       'Chuva' : 'chuva'
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

class SplashScreen(MDScreen):
    def on_kv_post(self, base_widget):
        print(">>> SplashScreen carregada")
        Clock.schedule_once(self.start_animation, 0.5)

    def start_animation(self, *args):
        print(">>> Iniciando animações...")
        logo = self.ids.logo
        title = self.ids.title

        anim_logo = Animation(opacity=1, y=logo.y + 30, duration=2.4, t="out_quad")
        anim_title = Animation(opacity=1, y=title.y + 30, duration=2.4, t="out_quad")

        anim_logo.start(logo)
        anim_title.start(title)

        Clock.schedule_once(self.verifica_token, 5.5)  # <- espera suficiente

    def verifica_token(self, *args):
        print(">>> Verificando token")
        app = MDApp.get_running_app()

        token = get_access_token()
        if is_token_valid(token):
            print(">>> Token válido")
            app.gerenciador.current = "overview"
        else:
            print(">>> Token inválido ou não existe")
            delete_access_token()
            app.gerenciador.current = "login"


class GerenciadorTelas(MDScreenManager):
    pass

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
        self.root_layout = FloatLayout()  # FloatLayout para permitir sobreposição

        self.gerenciador = GerenciadorTelas()
        self.gerenciador.add_widget(SplashScreen(name='splash'))
        self.gerenciador.add_widget(Overview(name='overview'))
        self.gerenciador.add_widget(Alertas(name='alertas'))
        self.gerenciador.add_widget(TelaLogin(name='login'))
        self.gerenciador.add_widget(Configuracao(name='configuracao'))
        self.gerenciador.add_widget(Equipamento(name='equipamento'))

        self.gerenciador.bind(current=self.on_screen_change)

        # Adiciona o gerenciador ocupando toda a tela
        self.gerenciador.size_hint = (1, 1)
        self.root_layout.add_widget(self.gerenciador)

        # Inicialmente, navigation_bar é None
        self.navigation_bar = None

        self.gerenciador.current = 'splash'
        return self.root_layout

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

    def on_screen_change(self, instance, screen_name):
        if screen_name == 'overview':
            if not self.navigation_bar:
                self.navigation_bar = NavigationBar(
                    screen_manager=self.gerenciador,
                    logout_callback=self.logout
                )
                # Garante que não adiciona duplicado
                if self.navigation_bar.parent:
                    self.root_layout.remove_widget(self.navigation_bar)

                self.navigation_bar.size_hint = (1, None)
                self.navigation_bar.height = dp(56)
                self.navigation_bar.pos_hint = {"x": 0, "y": 0}
                self.root_layout.add_widget(self.navigation_bar)

        else:
            if self.navigation_bar:
                self.root_layout.clear_widgets()
                self.root_layout.add_widget(self.gerenciador)
                self.navigation_bar = None

    def logout(self):
        delete_access_token()
        self.gerenciador.current = 'login'


if __name__ == '__main__':
    OceanStream().run()
