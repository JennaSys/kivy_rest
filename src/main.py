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


class BookEdit(Screen):
    def open(self, book_id):
        app.switch_screen('edit')
        self.ids.title.text = "My Test Book"
        self.ids.author.text = "All Me"

    def do_save(self):
        print("Saving")
        app.switch_screen('books')

    def clear(self):
        self.ids.title.text = ""
        self.ids.author.text = ""


class Book(MDCardSwipe):
    book_id = NumericProperty()
    text = StringProperty()
    secondary_text = StringProperty()

    def handle_delete(self):
        if self.open_progress > 0.0:
            print(f"Delete {self.book_id}!")

    def handle_addnew(self):
        if self.open_progress == 0.0:
            print(f"Add New!")


class MainApp(MDApp):
    sm = None
    menu = None
    session_cookie = None

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
        if screen_name == 'login' or self.sm.current == 'edit':
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

    def handle_edit(self, book_id):
        print("Edit book_id:", book_id)
        self.sm.get_screen('edit').open(book_id)


    def cancel_login(self):
        self.switch_screen('books')

    def login(self):
        self.switch_screen('login')

    def logout(self):
        self.menu.dismiss()
        headers = {'Cookie': self.session_cookie, 'Accept': 'application/json'}
        req = UrlRequest(f"{REST_ENDPOINT}/logout",
                         req_headers=headers,
                         cookies=[self.session_cookie],
                         on_success=lambda rq, rp: Snackbar(text="Logged out", bg_color=(0, .6, 0, 1)).open(),
                         timeout=5,
                         on_failure=lambda rq, rp: print("Oops!"),
                         on_error=lambda rq, rp: Snackbar(text="Server error!", bg_color=(1, 0, 0, 1)).open()
                         )
        self.session_cookie = None
        self.menu.items = [{"viewclass": "OneLineListItem",
                            "text": "Login",
                            "height": dp(40),
                            "on_release": self.login}]

    def do_login(self):
        login_screen = self.sm.get_screen('login')
        username = login_screen.ids.username.text
        password = login_screen.ids.password.text

        params = json.dumps({'username': username, 'password': password})
        headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
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

    def login_success(self, request, result):
        self.session_cookie = request.resp_headers.get('Set-Cookie', None)
        Snackbar(text="Login successful!", bg_color=(0, .6, 0, 1)).open()
        self.switch_screen('books')
        self.menu.items = [{"viewclass": "OneLineListItem",
                            "text": "Logout",
                            "height": dp(40),
                            "on_release": self.logout}]


if __name__ == '__main__':
    app = MainApp()
    app.run()
