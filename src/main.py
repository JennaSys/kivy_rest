import json

from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import NumericProperty, StringProperty
from kivymd.uix.card import MDCard, MDCardSwipe
from kivy.network.urlrequest import UrlRequest

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

    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Teal"
        self.theme_cls.accent_palette = "Pink"
        # Window.size = (300, 400)
        Window.size = (400, 600)
        self.title = "Books Demo"

    def switch_screen(self, screen_name='books'):
        self.sm.current = screen_name

    def on_start(self):
        self.sm = self.root
        self.sm.current = 'books'

        req = UrlRequest(f"{REST_ENDPOINT}/books",
                         on_success=self.load_data,
                         timeout=5,
                         on_failure=lambda rq, rp: print("Oops!"),
                         on_error=lambda rq, rp: print("Error!"))

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
        self.sm.current = 'login'

    def do_login(self):
        print("Login")
        login_screen = self.sm.get_screen('login')
        username = login_screen.ids.username.text
        password = login_screen.ids.password.text
        params = json.dumps({'username': username, 'password': password})
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        req = UrlRequest(f"{REST_ENDPOINT}/login",
                         method='POST',
                         req_body=params,
                         req_headers=headers,
                         on_success=lambda rq, rp: self.switch_screen(),
                         timeout=5,
                         on_failure=lambda rq, rp: print("Oops!"),
                         on_error=lambda rq, rp: print("Error!"))


if __name__ == '__main__':
    app = MainApp()
    app.run()
