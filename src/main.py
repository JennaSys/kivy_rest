import json

from kivymd.app import MDApp
from kivymd.uix.card import MDCardSwipe
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.snackbar import Snackbar
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen
from kivy.properties import NumericProperty, StringProperty
from kivy.network.urlrequest import UrlRequest
from kivy.metrics import dp

REST_ENDPOINT = 'http://192.168.2.154:8000/api'


class LoginScreen(Screen):
    def clear(self):
        self.ids.username.text = ""
        self.ids.password.text = ""


class BookList(Screen):
    pass


class Book(MDCardSwipe):
    book_id = NumericProperty()
    text = StringProperty()
    secondary_text = StringProperty()

    def handle_select(self):
        if self.open_progress == 0.0:
            print(f"Clicked {self.book_id}!")

    def handle_delete(self):
        if self.open_progress > 0.0:
            print(f"Delete {self.book_id}!")

    def handle_addnew(self):
        if self.open_progress == 0.0:
            print(f"Add New!")


class MainApp(MDApp):
    sm = None
    menu = None

    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Teal"
        self.theme_cls.accent_palette = "Pink"
        # Window.size = (300, 400)
        Window.size = (400, 600)
        self.title = "Books"

        self.sm = self.root
        self.menu = MDDropdownMenu(
            items=[{"viewclass": "OneLineListItem",
                    "text": "Login",
                    "height": dp(40),
                    "on_release": self.login,
                    }],
            width_mult=2,
        )
        self.sm.current = 'books'

    def menu_callback(self, ref):
        self.menu.caller = ref
        self.menu.open()

    def switch_screen(self, screen_name='books'):
        self.menu.dismiss()
        if screen_name == 'login':
            self.sm.transition.direction = 'right'
        else:
            self.sm.transition.direction = 'left'
        self.sm.current = screen_name

    def on_start(self):
        req = UrlRequest(f"{REST_ENDPOINT}/books",
                         on_success=self.load_data,
                         timeout=5,
                         on_failure=lambda rq, rp: print("Oops!"),
                         on_error=lambda rq, rp: Snackbar(text="Server error!", bg_color=(1, 0, 0, 1)).open()
                         )

    def load_data(self, request, result):
        book_data = result.get('books', None)
        if book_data:
            books_screen = self.sm.get_screen('books')
            for book in book_data:
                books_screen.ids.booklist.add_widget(
                    Book(book_id=book['id'], text=book['title'], secondary_text=book['author'])
                )

    def handle_addnew(self, value):
        print(f"Add New!")

    def cancel_login(self):
        self.switch_screen('books')

    def login(self):
        self.switch_screen('login')

    def logout(self):
        self.menu.dismiss()
        req = UrlRequest(f"{REST_ENDPOINT}/logout",
                         req_headers={'Accept: application/json'},
                         on_success=self.load_data,
                         timeout=5,
                         on_failure=lambda rq, rp: print("Oops!"),
                         on_error=lambda rq, rp: Snackbar(text="Server error!", bg_color=(1, 0, 0, 1)).open()
                         )
        self.menu.items = [{"viewclass": "OneLineListItem",
                            "text": "Login",
                            "height": dp(40),
                            "on_release": self.login}]

    def do_login(self):
        login_screen = self.sm.get_screen('login')
        username = login_screen.ids.username.text
        password = login_screen.ids.password.text

        params = json.dumps({'username': username, 'password': password})
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        req = UrlRequest(f"{REST_ENDPOINT}/login",
                         method='POST',
                         req_body=params,
                         req_headers=headers,
                         on_success=self.login_success,
                         timeout=5,
                         on_failure=lambda rq, rp: Snackbar(text="Login failed!", bg_color=(1, 0, 0, 1)).open(),
                         on_error=lambda rq, rp: Snackbar(text="Server error!", bg_color=(1, 0, 0, 1)).open()
                         )

        login_screen.clear()

    def login_success(self, request, response):
        Snackbar(text="Login successful!", bg_color=(0, .6, 0, 1)).open()
        self.switch_screen('books')
        self.menu.items = [{"viewclass": "OneLineListItem",
                            "text": "Logout",
                            "height": dp(40),
                            "on_release": self.logout}]


if __name__ == '__main__':
    app = MainApp()
    app.run()
