import os

from kivy.base import EventLoop
from kivy.uix.screenmanager import RiseInTransition, FallOutTransition, SlideTransition, ScreenManager
# from kivymd.app import MDApp
from kivymd.tools.hotreload.app import MDApp
from kivymd.uix.list import OneLineIconListItem
from kivymd.uix.menu import MDDropdownMenu
from kivy.core.window import Window
from kivy.properties import StringProperty
from kivy.metrics import dp
from kivy.utils import platform

REST_ENDPOINT = 'https://restdemo.jennasys.com/api'


class AppMenu(MDDropdownMenu):
    def __init__(self):
        self.items = []
        super().__init__(items=self.items, width_mult=3)

    def add_item(self, **kwargs):
        base_item = {"viewclass": "MenuItem",
                     "text": "",
                     "icon": "",
                     "height": dp(48),
                     "on_release": None,
                     }
        base_item.update(kwargs)
        self.items.append(base_item)

    def remove_item(self, item_id):
        self.items = [item for item in self.items if item['id'] != item_id]

    def click(self, ref):
        self.caller = ref
        self.open()


class MenuItem(OneLineIconListItem):
    icon = StringProperty()


class SM(ScreenManager):
    def get_classes(self):
        return {screen.__class__.__name__: screen.__class__.__module__ for screen in self.screens}


class MainApp(MDApp):
    use_kivy_settings = False

    sm = None
    menu = None
    session_cookie = None

    def build_config(self, config):
        config.setdefaults('app', {'rest_endpoint': REST_ENDPOINT})

    def build_settings(self, settings):
        jsondata = """ [{"type": "title",
                         "title": "Kivy REST Demo Settings"},
                        {"type": "string",
                         "title": "REST Endpoint",
                         "desc": "URL for REST API endpoint",
                         "section": "app",
                         "key": "rest_endpoint"}] """
        settings.add_json_panel('REST Demo', self.config, data=jsondata)

    def open_settings(self, *largs):
        self.menu.dismiss()
        MDApp.open_settings(self, *largs)

    def on_config_change(self, config, section, key, value):
        if config is self.config:
            token = (section, key)
            if token == ('app', 'rest_endpoint'):
                os.environ['REST_ENDPOINT'] = value

    def build_app(self, *args):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Teal"
        self.theme_cls.accent_palette = "Pink"

        self.title = "Books"
        self.icon = 'images/icon.png'

        if platform in ['win', 'linux', 'macosx']:
            Window.size = (400, 600)

        os.environ['REST_ENDPOINT'] = self.config.get('app', 'rest_endpoint')

        KV_FILES = []
        self.sm = SM()
        CLASSES = self.sm.get_classes()

        self.menu = AppMenu()
        self.menu.add_item(id="about", text="About", icon="information", on_release=self.sm.get_screen('about').open)
        self.menu.add_item(id="settings", text="Settings", icon="cog", on_release=self.open_settings)
        self.menu.add_item(id="refresh", text="Refresh", icon="reload", on_release=self.sm.get_screen('books').get_books)
        self.menu.add_item(id="login", text="Login", icon="login", on_release=self.sm.get_screen('login').open)

        return self.sm

    def on_start(self):
        EventLoop.window.bind(on_keyboard=self.keyboard_hook)
        self.sm.get_screen('books').open()
        self.sm.get_screen('books').get_books()

    def on_stop(self):
        Window.close()

    def keyboard_hook(self, key, scancode, codepoint, modifier, *args):
        if scancode == 27:  # ESC
            if self.sm.current == 'books':
                pass  # Exit App
            elif self.sm.current == 'edit':
                self.sm.get_screen('edit').close()
                return True
            else:
                self.sm.get_screen('books').open()
                return True

    def switch_screen(self, screen_name='books'):
        self.menu.dismiss()
        if screen_name == 'login':
            self.sm.transition = RiseInTransition()
        elif self.sm.current == 'login':
            self.sm.transition = FallOutTransition()
        elif self.sm.current == 'edit':
            self.sm.transition = SlideTransition(direction='right')
        elif screen_name == 'about':
            self.sm.transition = SlideTransition(direction='right')
        else:
            self.sm.transition = SlideTransition(direction='left')
        self.sm.current = screen_name

    def is_auth(self):
        return self.session_cookie is not None


if __name__ == '__main__':
    app = MainApp()
    app.run()
