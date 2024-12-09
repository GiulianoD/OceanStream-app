from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.animation import Animation
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle
from kivy.graphics import Ellipse


class NavigationBar(MDBoxLayout):
    def __init__(self, screen_manager, logout_callback, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.screen_manager = screen_manager
        self.logout_callback = logout_callback  # Callback de logout

        # Layout da toolbar expansível com fundo estilizado
        self.toolbar = MDBoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(56),  # Altura inicial para o botão de expansão
            padding=[dp(10), dp(10)]
        )

        # Adicionar fundo arredondado à toolbar
        with self.toolbar.canvas.before:
            Color(0.89, 0.91, 0.97, 1)  # Cor #E4E9F7
            self.bg_rect = RoundedRectangle(
                size=self.toolbar.size,
                pos=self.toolbar.pos,
                radius=[(20, 20), (20, 20), (0, 0), (0, 0)]  # Bordas arredondadas superiores
            )
            self.toolbar.bind(size=self.update_bg, pos=self.update_bg)

        # Adicionar círculo branco abaixo da logo
        with self.toolbar.canvas:
            Color(1, 1, 1, 1)  # Cor branca
            self.circle = Ellipse(
                size=(dp(100), dp(100)),  # Tamanho do círculo
                pos=(self.toolbar.x + (self.toolbar.width - dp(100)) / 2, self.toolbar.top - dp(50))  # Posição ajustada
            )

        # Substitui o botão de expansão por um botão com a logo do app
        self.expand_button = MDIconButton(
            icon="res/logo.png",
            size_hint=(None, None),
            size=(dp(80), dp(80)),
            icon_size="80sp",
            theme_text_color="Custom",
            text_color=(0.02, 0.58, 0.61, 1), # hex 04949C
            pos_hint={'center_x': 0.5},
            on_release=self.toggle_toolbar
        )

        # Título "Menu", com nova cor, fonte em negrito e fonte maior
        # self.menu_title = Label(
        #     text="Menu",
        #     font_size="28sp",
        #     halign="center",
        #     valign="middle",
        #     size_hint=(None, None),  # Remova dependências de tamanho automático
        #     size=(dp(120), dp(40)),  # Define tamanho fixo para garantir a exibição
        #     opacity=0,  # Começa invisível
        #     pos_hint={'center_x': 0.5},
        #     color=(0.2, 0.6, 0.8, 1), # hex 3399CC
        #     bold=True
        # )

        # Caixa expansível para as opções, inicialmente oculta
        self.options_box = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=0  # Inicia oculta
        )

        # Layout para os ícones de opções
        self.options_icons_box = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(80),
            spacing=dp(10)
        )

        # Lista de opções com ícones e textos correspondentes
        options = [
            {"text": "Configuração", "icon": "cog", "screen": "configuracao"},
            {"text": "Alertas", "icon": "bell", "screen": "alertas"},
            {"text": "Overview", "icon": "information", "screen": "overview"},
            {"text": "Suporte", "icon": "help-circle", "screen": "suporte"},
            {"text": "Ocorrência", "icon": "alert", "screen": "ocorrencia"},
        ]

        # Adicionar botões de opções e labels para os textos
        for option in options:
            option_box = BoxLayout(
                orientation="vertical",
                size_hint=(1, None),
                width=dp(80),
                height=dp(80),
                spacing=dp(5),
                pos_hint={"center_x": 0.5, "center_y": 0.5}
            )

            # Configurar o botão de ícone
            button = MDIconButton(
                icon=option["icon"],
                icon_size="32sp",
                theme_text_color="Custom",
                text_color=(0.02, 0.58, 0.61, 1),  # Cor #04949C
                on_release=lambda x, screen=option["screen"]: self.switch_to_screen(screen),
                pos_hint={"center_x": 0.5}  # Centralizar o ícone horizontalmente
            )

            # Configurar o label abaixo do ícone
            label = Label(
                text=option["text"],
                font_size="12sp",
                halign="center",
                valign="middle",
                size_hint_y=None,
                height=dp(20),
                color=(0.44, 0.44, 0.44, 1),  # Cor #707070
                pos_hint={"center_x": 0.5}  # Centralizar o texto horizontalmente
            )

            # Adicionar o ícone e o label ao BoxLayout
            option_box.add_widget(button)
            option_box.add_widget(label)
            self.options_icons_box.add_widget(option_box)

        # Botão de logout, estilizado
        self.logout_button = MDRaisedButton(
            text="Logout",
            size_hint=(None, None),
            size=(dp(100), dp(36)),
            md_bg_color=(0.2, 0.6, 0.8, 1),  # Cor #3399CC
            text_color=(1, 1, 1, 1),  # Cor #FFF (branco)
            pos_hint={"center_x": 0.5},
            on_release=self.logout
        )

        # Adicionar componentes à toolbar em ordem
        self.toolbar.add_widget(self.expand_button)  # Botão com a logo
        # self.toolbar.add_widget(self.menu_title)      # Título "Menu" abaixo do ícone de expansão
        self.toolbar.add_widget(self.options_box)     # Caixa de opções inicialmente vazia
        self.add_widget(self.screen_manager)
        self.add_widget(self.toolbar)

    def toggle_toolbar(self, instance):
        # Alterna entre expandir e recolher a área de opções e o título "Menu"
        if self.options_box.height == 0:
            # Expande a área de opções e exibe o título "Menu"
            self.options_box.add_widget(self.options_icons_box)
            self.options_box.add_widget(self.logout_button)
            anim_options = Animation(height=dp(150), d=0.3)  # Expande a altura das opções
            anim_toolbar = Animation(height=dp(206), d=0.3)  # Expande a altura total da toolbar
            anim_title = Animation(opacity=1, d=0.3)         # Exibe o título "Menu"
            
        else:
            # Recolhe a área de opções e oculta o título "Menu"
            anim_options = Animation(height=0, d=0.3)
            anim_toolbar = Animation(height=dp(56), d=0.3)  # Retorna a altura total da toolbar para o inicial
            anim_title = Animation(opacity=0, d=0.3)        # Oculta o título "Menu"

            # Remove os widgets para que não possam ser clicados
            self.options_box.clear_widgets()

        # Inicia animações
        anim_toolbar.start(self.toolbar)
        anim_options.start(self.options_box)
        # anim_title.start(self.menu_title)

    def update_bg(self, *args):
        self.bg_rect.size = self.toolbar.size
        self.bg_rect.pos = self.toolbar.pos
        self.circle.pos = (self.toolbar.center_x - dp(50), self.toolbar.height - dp(50))

    def switch_to_screen(self, screen_name):
        # Mudar para a tela especificada
        if self.screen_manager.has_screen(screen_name):
            self.toggle_toolbar(None)
            self.screen_manager.current = screen_name
        else:
            print(f"Tela '{screen_name}' não encontrada.")

    def logout(self, instance):
        self.toggle_toolbar(instance)
        # Função para logout que chama o callback passado
        self.logout_callback()
        self.screen_manager.current = 'login'  # Redireciona para a tela de login
