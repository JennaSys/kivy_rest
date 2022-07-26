from kivymd.app import MDApp
from kivymd.uix.card import MDCardSwipe
from kivymd.uix.list import OneLineIconListItem
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen
from kivy.properties import NumericProperty, StringProperty
from kivy.metrics import dp
from kivy.utils import platform

from apputils import fetch, Notify

REST_ENDPOINT = 'http://192.168.2.154:8000/api'


class LoginScreen(Screen):
    def clear(self):
        self.ids.username.text = ""
        self.ids.password.text = ""


class AppMenu(MDDropdownMenu):
    def __init__(self):
        self.items = []
        self.add_item(id="refresh", text="Refresh", icon="reload", on_release=app.get_books)
        self.add_item(id="login", text="Login", icon="login", on_release=app.login)

        super().__init__(items=self.items, width_mult=2.5)

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
            fetch(f"{REST_ENDPOINT}/books/{book_id}", self.load_data)

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

        body = {'title': self.ids.title.text, 'author': self.ids.author.text}
        if self.book_id > 0:
            body['id'] = self.book_id

        rest_resource = "books" if self.book_id < 0 else f"books/{self.book_id}"
        method = 'POST' if self.book_id < 0 else 'PUT'
        fetch(f"{REST_ENDPOINT}/{rest_resource}", self.save_success, method=method, data=body, cookie=app.session_cookie)

    def save_success(self, request, result):
        Notify(text=f"Book {'added' if self.book_id < 0 else 'updated'}").open()
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
        fetch(f"{REST_ENDPOINT}/books/{self.book_id}", self.delete_success, method='DELETE', cookie=app.session_cookie)

    def delete_success(self, request, result):
        Notify(text="Book deleted").open()
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
        if platform in ['win', 'linux', 'macosx']:
            Window.size = (400, 600)
        self.title = "Books"

        self.menu = AppMenu()
        self.sm = self.root
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

        fetch(f"{REST_ENDPOINT}/books", self.load_data)

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
    app = MainApp()
    app.run()

# TODO: Refactor module into views/functionality

# TODO: Get rid of all hard coded pixel sizing
# TODO: Make slide out easier on mobile (get rid of icon click?)
# TODO: Change startup splash icon

# TODO: Add menu item to set (and locally save) rest endpoint
# TODO: Add About screen showing version/build date/JennaSys
