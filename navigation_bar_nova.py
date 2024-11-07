from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFloatingActionButton, MDRaisedButton, MDIconButton
from kivy.metrics import dp
from kivy.animation import Animation
from kivymd.uix.label import MDLabel
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
import os

class NavigationBar(MDBoxLayout):
    def __init__(self, screen_manager, logout_callback, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.screen_manager = screen_manager
        self.logout_callback = logout_callback  # Callback de logout

        # Caminho absoluto para a imagem logo.png
        logo_path = r"logo.png"
        if not os.path.exists(logo_path):
            print(f"Erro: A imagem não foi encontrada no caminho {logo_path}")
        
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

        # Título "Menu", inicialmente invisível para o efeito de deslizamento
        self.menu_title = Label(
            text="Menu",
            font_size="20sp",
            halign="center",
            size_hint_y=None,
            height=dp(30),
            opacity=0,  # Começa invisível para o efeito de deslizamento
            pos_hint={'center_x': 0.5},
            color=(0, 0, 0, 1)  # Cor preta
        )

        # Caixa expansível para as opções, inicialmente oculta
        self.options_box = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(80),
            spacing=dp(20),
            padding=[dp(10), dp(10)],
            opacity=0  # Invisível para o efeito de deslizamento
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
                size_hint=(1, None),  # Cada ícone se expande igualmente
                height=dp(80),
                spacing=dp(5),
            )

            button = MDIconButton(
                icon=option["icon"],
                icon_size="32sp",
                size_hint=(None, None),
                size=(dp(48), dp(48)),
                on_release=lambda x, screen=option["screen"]: self.switch_to_screen(screen)
            )

            label = MDLabel(
                text=option["text"],
                font_style="Caption",
                halign="center",
                size_hint_y=None,
                height=dp(20)
            )

            # Adicionar o ícone e o label ao box
            option_box.add_widget(button)
            option_box.add_widget(label)
            self.options_box.add_widget(option_box)

        # Botão de logout, com efeito de deslizamento
        self.logout_button = MDRaisedButton(
            text="Logout",
            size_hint=(None, None),
            pos_hint={"center_x": 0.5},
            opacity=0,  # Invisível no início
            on_release=self.logout
        )

        # Adicionar apenas o botão de expansão no início
        self.toolbar.add_widget(self.expand_button)
        self.add_widget(self.screen_manager)
        self.add_widget(self.toolbar)

    def toggle_toolbar(self, instance):
        # Alterna entre expandir e recolher a área de opções e o título "Menu"
        if self.toolbar.height == dp(56):
            # Expande a toolbar e revela os ícones e o título
            self.toolbar.add_widget(self.menu_title)          # Adiciona o título "Menu"
            self.toolbar.add_widget(self.options_box)         # Adiciona os ícones de opções
            self.toolbar.add_widget(self.logout_button)       # Adiciona o botão de logout

            # Animações para expandir a toolbar e revelar os itens
            anim_toolbar = Animation(height=dp(206), d=0.3)   # Expande a altura total da toolbar
            anim_title = Animation(opacity=1, d=0.3)          # Anima a opacidade do título para visível
            anim_options = Animation(opacity=1, d=0.3)        # Anima a opacidade dos ícones para visível
            anim_logout = Animation(opacity=1, d=0.3)         # Anima a opacidade do botão de logout para visível
            
            # Inicia animações
            anim_toolbar.start(self.toolbar)
            anim_title.start(self.menu_title)
            anim_options.start(self.options_box)
            anim_logout.start(self.logout_button)

        else:
            # Recolhe a toolbar e esconde os ícones e o título
            anim_toolbar = Animation(height=dp(56), d=0.3)    # Recolhe a altura total da toolbar
            anim_title = Animation(opacity=0, d=0.3)          # Anima a opacidade do título para invisível
            anim_options = Animation(opacity=0, d=0.3)        # Anima a opacidade dos ícones para invisível
            anim_logout = Animation(opacity=0, d=0.3)         # Anima a opacidade do botão de logout para invisível

            # Inicia animações
            anim_toolbar.start(self.toolbar)
            anim_title.start(self.menu_title)
            anim_options.start(self.options_box)
            anim_logout.start(self.logout_button)

            # Remove os widgets após a animação para evitar cliques
            anim_toolbar.bind(on_complete=lambda *args: self._remove_toolbar_widgets())

    def _remove_toolbar_widgets(self):
        """Remove widgets da toolbar após a animação de recolhimento"""
        self.toolbar.remove_widget(self.menu_title)
        self.toolbar.remove_widget(self.options_box)
        self.toolbar.remove_widget(self.logout_button)

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
