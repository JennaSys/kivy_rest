import os

from kivymd.app import MDApp
from kivymd.uix.list import OneLineIconListItem
from kivymd.uix.menu import MDDropdownMenu
from kivy.core.window import Window
from kivy.properties import StringProperty
from kivy.metrics import dp
from kivy.utils import platform

from apputils import fetch
from View import Book, LoginScreen

REST_ENDPOINT = 'http://192.168.2.154:8000/api'


class AppMenu(MDDropdownMenu):
    def __init__(self):
        self.items = []
        self.add_item(id="refresh", text="Refresh", icon="reload", on_release=app.get_books)
        self.add_item(id="login", text="Login", icon="login", on_release=LoginScreen.login)

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

        self.menu = AppMenu()
        self.sm = self.root
        self.sm.current = 'books'

    def on_start(self):
        self.get_books()

    def get_books(self):
        self.menu.dismiss()
        books_screen = self.sm.get_screen('books')
        books = [child for child in books_screen.ids.booklist.children]
        for book in books:
            if isinstance(book, Book):
                books_screen.ids.booklist.remove_widget(book)

        fetch(f"{REST_ENDPOINT}/books", self.load_data)

    def load_data(self, request, result):
        book_data = result.get('books', None)
        if book_data:
            books_screen = self.sm.get_screen('books')
            for book in book_data:
                books_screen.ids.booklist.add_widget(
                    Book(book_id=book['id'], text=book['title'], secondary_text=book['author'])
                )

    def switch_screen(self, screen_name='books'):
        self.menu.dismiss()
        if screen_name == 'login' or self.sm.current == 'edit':
            self.sm.transition.direction = 'right'
        else:
            self.sm.transition.direction = 'left'
        self.sm.current = screen_name


if __name__ == '__main__':
    os.environ['REST_ENDPOINT'] = REST_ENDPOINT
    app = MainApp()
    app.run()

# TODO: Android app locks on exit
# TODO: Add is_auth() using ping, and disable save/add/del if not auth
# TODO: Add menu item to set (and locally save) rest endpoint (kivy.uix.settings.SettingItem)
# TODO: Add About screen showing version/build date/JennaSys
# TODO: Make slide out easier on mobile (get rid of icon click?)
# TODO: Back button goes to list - if already on list, then exit
# TODO: Change transition for login to fade instead of swipe
# TODO: Clicking menu icons does nothing
# TODO: Allow tab on login fields?
# TODO: Allow tab on edit fields?
