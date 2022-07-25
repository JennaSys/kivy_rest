import json

from kivymd.app import MDApp
from kivymd.uix.card import MDCardSwipe
from kivymd.uix.list import OneLineIconListItem
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
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
    def handle_addnew(self):
        print(f"Add New!")
        app.sm.get_screen('edit').open()


class BookEdit(Screen):
    book_id = NumericProperty()

    def open(self, book_id=None):
        app.switch_screen('edit')
        self.book_id = book_id if book_id else -1
        if book_id:
            req = UrlRequest(f"{REST_ENDPOINT}/books/{book_id}",
                             on_success=self.load_data,
                             timeout=5,
                             on_failure=lambda rq, rp: print("Oops!"),
                             on_error=lambda rq, rp: Snackbar(text="Server error!", bg_color=(1, 0, 0, 1)).open()
                             )

    def close(self, ref):
        self.clear()
        app.switch_screen('books')

    def load_data(self, request, result):
        book_data = result.get('book', None)
        if book_data:
            self.book_id = book_data['id']
            self.ids.title.text = book_data['title']
            self.ids.author.text = book_data['author']

    def handle_save(self):
        print("Saving")

        params = {'title': self.ids.title.text, 'author': self.ids.author.text}
        if self.book_id > 0:
            params['id'] = self.book_id

        cookie = app.session_cookie if app.session_cookie else ''
        headers = {'Cookie': cookie, 'Content-type': 'application/json'}
        rest_resource = "books" if self.book_id < 0 else f"books/{self.book_id}"
        req = UrlRequest(f"{REST_ENDPOINT}/{rest_resource}",
                         method='POST' if self.book_id < 0 else 'PUT',
                         req_body=json.dumps(params),
                         req_headers=headers,
                         on_success=self.save_success,
                         timeout=5,
                         on_failure=lambda rq, rp: print("Oops!"),
                         on_error=lambda rq, rp: Snackbar(text=f"Server error: {rp}!", bg_color=(1, 0, 0, 1)).open()
                         )

    def save_success(self, request, result):
        Snackbar(text=f"Book {'added' if self.book_id < 0 else 'updated'}!", bg_color=(0, .6, 0, 1)).open()
        self.clear()
        app.switch_screen('books')
        app.get_books()

    def clear(self):
        self.book_id = -1
        self.ids.title.text = ""
        self.ids.author.text = ""


class Book(MDCardSwipe):
    book_id = NumericProperty()
    text = StringProperty()
    secondary_text = StringProperty()

    dialog = None

    def do_delete(self):
        self.dialog.dismiss()
        print(f"Delete {self.book_id}!")

        req = UrlRequest(f"{REST_ENDPOINT}/books/{self.book_id}",
                         method='DELETE',
                         cookies=app.session_cookie if app.session_cookie else '',
                         on_success=self.delete_success,
                         timeout=5,
                         on_failure=lambda rq, rp: print("Oops!"),
                         on_error=lambda rq, rp: Snackbar(text=f"Server error: {rp}!", bg_color=(1, 0, 0, 1)).open()
                         )

    def delete_success(self, request, result):
        Snackbar(text="Book deleted", bg_color=(0, .6, 0, 1)).open()
        app.get_books()

    def delete_dialog(self):
        if not self.dialog:
            self.dialog = MDDialog(
                title="Delete Book",
                text=f"Are you sure you want to permanently delete '{self.text}'?",
                type='confirmation',
                auto_dismiss=False,
                buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        text_color=app.theme_cls.primary_color,
                        on_release=lambda x: self.dialog.dismiss()
                    ),
                    MDFlatButton(
                        text="DELETE",
                        text_color=app.theme_cls.primary_color,
                        on_release=lambda x: self.do_delete()
                    ),
                ],
            )
        self.dialog.open()

    def handle_delete(self):
        if self.open_progress > 0.0:
            self.delete_dialog()

    def handle_edit(self, book_id):
        if self.open_progress == 0.0:
            print("Edit book_id:", book_id)
            app.sm.get_screen('edit').open(book_id)


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
        # Window.size = (300, 400)
        Window.size = (400, 600)
        self.title = "Books"

        self.sm = self.root

        # TODO: Change menu to class
        self.menu = MDDropdownMenu(
            items=[{"viewclass": "MenuItem",
                    "text": "Login",
                    "icon": "login",
                    "height": dp(48),
                    "on_release": self.login,
                    }],
            width_mult=2.5,
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
        self.get_books()

    def get_books(self):
        books_screen = self.sm.get_screen('books')
        books = [child for child in books_screen.ids.booklist.children]
        for book in books:
            if isinstance(book, Book):
                books_screen.ids.booklist.remove_widget(book)

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

    def cancel_login(self):
        self.switch_screen('books')

    def login(self):
        self.switch_screen('login')

    def logout(self):
        self.menu.dismiss()
        cookie = self.session_cookie if app.session_cookie else ''
        headers = {'Cookie': cookie, 'Accept': 'application/json'}
        req = UrlRequest(f"{REST_ENDPOINT}/logout",
                         req_headers=headers,
                         on_success=lambda rq, rp: Snackbar(text="Logged out", bg_color=(0, .6, 0, 1)).open(),
                         timeout=5,
                         on_failure=lambda rq, rp: print("Oops!"),
                         on_error=lambda rq, rp: Snackbar(text="Server error!", bg_color=(1, 0, 0, 1)).open()
                         )
        self.session_cookie = None
        self.menu.items = [{"viewclass": "MenuItem",
                            "text": "Login",
                            "icon": "login",
                            "height": dp(48),
                            "on_release": self.login}]

    def do_login(self):
        login_screen = self.sm.get_screen('login')
        username = login_screen.ids.username.text
        password = login_screen.ids.password.text

        params = {'username': username, 'password': password}
        headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
        req = UrlRequest(f"{REST_ENDPOINT}/login",
                         method='POST',
                         req_body=json.dumps(params),
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
        self.menu.items = [{"viewclass": "MenuItem",
                            "text": "Logout",
                            "icon": "logout",
                            "height": dp(48),
                            "on_release": self.logout}]


if __name__ == '__main__':
    app = MainApp()
    app.run()

# TODO: Unify http error messages
# TODO: Handle 401 (on_failure) with need to login message
# TODO: Create convenience function for http requests
