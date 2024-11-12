from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFloatingActionButton, MDRaisedButton, MDIconButton
from kivy.metrics import dp
from kivy.animation import Animation
from kivymd.uix.label import MDLabel
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

class NavigationBar(MDBoxLayout):
    def __init__(self, screen_manager, logout_callback, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.screen_manager = screen_manager
        self.logout_callback = logout_callback  # Callback de logout

        # Layout da toolbar expansível
        self.toolbar = MDBoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(56),  # Altura inicial para o ícone de expansão
            padding=[dp(10), dp(10)]
        )

        # Ícone de expansão fixo no topo da toolbar
        self.expand_button = MDFloatingActionButton(
            icon="menu",  # Ícone de menu para o botão superior
            size_hint=(None, None),
            size=(dp(56), dp(56)),
            md_bg_color=[0, 0, 1, 1],  # Cor azul para teste
            pos_hint={'center_x': 0.5},
            on_release=self.toggle_toolbar
        )

        # Título "Menu", inicialmente invisível e posicionado abaixo do botão de expansão
        self.menu_title = Label(
            text="Menu",
            font_size="20sp",
            halign="center",
            size_hint_y=None,
            height=dp(30),
            opacity=0,  # Começa invisível
            pos_hint={'center_x': 0.5},
            color=(0, 0, 0, 1)  # Cor preta
        )

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
            {"text": "Informações", "icon": "information", "screen": "informacoes"},
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
                on_release=lambda x, screen=option["screen"]: self.switch_to_screen(screen),
                pos_hint={"center_x": 0.5}  # Centralizar o ícone horizontalmente
            )

            # Configurar o label abaixo do ícone
            label = MDLabel(
                text=option["text"],
                font_style="Caption",
                halign="center",
                size_hint_y=None,
                height=dp(20),
                pos_hint={"center_x": 0.5}  # Centralizar o texto horizontalmente
            )

            # Adicionar o ícone e o label ao BoxLayout
            option_box.add_widget(button)
            option_box.add_widget(label)
            self.options_icons_box.add_widget(option_box)


        # Botão de logout, centralizado abaixo das opções
        self.logout_button = MDRaisedButton(
            text="Logout",
            pos_hint={"center_x": 0.5},
            on_release=self.logout
        )

        # Adicionar componentes à toolbar em ordem
        self.toolbar.add_widget(self.expand_button)  # Ícone de expansão no topo da toolbar
        self.toolbar.add_widget(self.menu_title)      # Título "Menu" abaixo do ícone de expansão
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
            
            # Inicia animação do título
            anim_title.start(self.menu_title)
        else:
            # Recolhe a área de opções e oculta o título "Menu"
            anim_options = Animation(height=0, d=0.3)
            anim_toolbar = Animation(height=dp(56), d=0.3)  # Retorna a altura total da toolbar para o inicial
            anim_title = Animation(opacity=0, d=0.3)        # Oculta o título "Menu"

            # Remove os widgets para que não possam ser clicados
            self.options_box.clear_widgets()

            # Inicia animação do título
            anim_title.start(self.menu_title)

        # Inicia animações
        anim_toolbar.start(self.toolbar)
        anim_options.start(self.options_box)

    def switch_to_screen(self, screen_name):
        # Mudar para a tela especificada
        if self.screen_manager.has_screen(screen_name):
            self.screen_manager.current = screen_name
        else:
            print(f"Tela '{screen_name}' não encontrada.")

    def logout(self, instance):
        self.toggle_toolbar(instance)
        # Função para logout que chama o callback passado
        self.logout_callback()
        self.screen_manager.current = 'login'  # Redireciona para a tela de login
