from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.metrics import dp  # Para definir a altura em pixels (dp)

class NavigationBar(MDBoxLayout):
    def __init__(self, screen_manager, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.screen_manager = screen_manager

        # Criação da barra de navegação inferior
        self.bottom_navigation = MDBottomNavigation()

        # Primeiro item de navegação
        self.nav_item_1 = MDBottomNavigationItem(
            name='overview',
            text='Overview',
            icon='home',
            on_tab_press=lambda *args: self.change_screen('overview')
        )

        # Segundo item de navegação
        self.nav_item_2 = MDBottomNavigationItem(
            name='alertas',
            text='Alertas',
            icon='account',
            on_tab_press=lambda *args: self.change_screen('alertas')
        )

        # Adicionar itens à barra de navegação
        self.bottom_navigation.add_widget(self.nav_item_1)
        self.bottom_navigation.add_widget(self.nav_item_2)

        # Adicionar o ScreenManager (que contém as telas) e a barra de navegação ao layout
        self.add_widget(self.screen_manager)
        self.add_widget(self.bottom_navigation)

    def change_screen(self, screen_name):
        self.screen_manager.current = screen_name
