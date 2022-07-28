import os

from kivy.base import EventLoop
from kivymd.app import MDApp
from kivymd.uix.list import OneLineIconListItem
from kivymd.uix.menu import MDDropdownMenu
from kivy.core.window import Window
from kivy.properties import StringProperty
from kivy.metrics import dp
from kivy.utils import platform

REST_ENDPOINT = 'http://192.168.2.154:8000/api'


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


class MainApp(MDApp):
    sm = None
    menu = None
    session_cookie = None

    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Teal"
        self.theme_cls.accent_palette = "Pink"

        if platform in ['win', 'linux', 'macosx']:
            Window.size = (400, 600)
        self.title = "Books"

        self.sm = self.root

        self.menu = AppMenu()
        self.menu.add_item(id="refresh", text="Refresh", icon="reload", on_release=self.sm.get_screen('books').get_books)
        self.menu.add_item(id="login", text="Login", icon="login", on_release=self.sm.get_screen('login').open)

        self.sm.get_screen('books').open()

    def on_start(self):
        EventLoop.window.bind(on_keyboard=self.keyboard_hook)
        self.sm.get_screen('books').get_books()

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
        if screen_name == 'login' or self.sm.current == 'edit':
            self.sm.transition.direction = 'right'
        else:
            self.sm.transition.direction = 'left'
        self.sm.current = screen_name

    def is_auth(self):
        return self.session_cookie is not None


if __name__ == '__main__':
    os.environ['REST_ENDPOINT'] = REST_ENDPOINT
    app = MainApp()
    app.run()

# TODO: Android app locks on exit
# TODO: Add is_auth() using ping
# TODO: Add user to title if logged in
# TODO: Add menu item to set (and locally save) rest endpoint (kivy.uix.settings.SettingItem)
# TODO: Add About screen showing version/build date/JennaSys
# TODO: Make slide out easier on mobile (get rid of icon click?)
# TODO: Change transition for login to fade instead of swipe
# TODO: Clicking menu icons does nothing
