import os

from kivymd.app import MDApp
from kivymd.uix.list import OneLineIconListItem
from kivymd.uix.menu import MDDropdownMenu
from kivy.core.window import Window
from kivy.properties import StringProperty
from kivy.metrics import dp
from kivy.utils import platform

from apputils import fetch, Notify
from View import Book

REST_ENDPOINT = 'http://192.168.2.154:8000/api'


class AppMenu(MDDropdownMenu):
    def __init__(self):
        self.items = []
        self.add_item(id="refresh", text="Refresh", icon="reload", on_release=app.get_books)
        self.add_item(id="login", text="Login", icon="login", on_release=app.login)

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

    def menu_callback(self, ref):
        self.menu.caller = ref
        self.menu.open()

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

    def cancel_login(self):
        self.switch_screen('books')

    def login(self):
        self.switch_screen('login')

    def logout(self):
        self.menu.dismiss()

        def on_success(request, result):
            Notify(text="Logged out").open()

        fetch(f"{REST_ENDPOINT}/logout", on_success, cookie=self.session_cookie)

        self.session_cookie = None

        self.menu.add_item(id="login", text="Login", icon="login", on_release=self.login)
        self.menu.remove_item('logout')

    def do_login(self):
        login_screen = self.sm.get_screen('login')
        username = login_screen.ids.username.text
        password = login_screen.ids.password.text

        def login_error(request, result):
            Notify(text="Login failed!", snack_type='error').open()

        body = {'username': username, 'password': password}
        fetch(f"{REST_ENDPOINT}/login", self.login_success, method='POST', data=body, onError=login_error)

        login_screen.clear()

    def login_success(self, request, result):
        self.session_cookie = request.resp_headers.get('Set-Cookie', None)
        Notify(text="Login successful!").open()
        self.switch_screen('books')

        self.menu.add_item(id="logout", text="Logout", icon="logout", on_release=self.logout)
        self.menu.remove_item('login')


if __name__ == '__main__':
    os.environ['REST_ENDPOINT'] = REST_ENDPOINT
    app = MainApp()
    app.run()

# TODO: Get rid of all hard coded pixel sizing
# TODO: Refactor module into views/functionality
# TODO: Android app locks on exit
# TODO: Add is_auth() using ping, and disable save/add/del if not auth
# TODO: Add menu item to set (and locally save) rest endpoint (kivy.uix.settings.SettingItem)
# TODO: Add About screen showing version/build date/JennaSys
# TODO: Make slide out easier on mobile (get rid of icon click?)
# TODO: Back button goes to list - if already on list, then exit
# TODO: Change transition for login to fade instead of swipe
# TODO: Can login methods be moved from mainApp to View?
