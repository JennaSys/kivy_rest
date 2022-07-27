import os

from kivymd.uix.card import MDCardSwipe
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen
from kivy.properties import NumericProperty, StringProperty

from apputils import fetch, Notify, load_kv

load_kv(__name__)


class ConfirmDialog(MDDialog):
    def __init__(self, title, text="", on_ok=None):
        app = MDApp.get_running_app()
        kwargs = dict(
            title=title,
            text=text,
            type='confirmation',
            auto_dismiss=False,
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    theme_text_color="Custom",
                    text_color=app.theme_cls.primary_color,
                    on_release=lambda x: self.dismiss()
                ),
                MDFlatButton(
                    text="OK",
                    theme_text_color="Custom",
                    text_color=app.theme_cls.primary_color,
                    on_release=lambda val: on_ok()
                ),
            ])

        super().__init__(**kwargs)


class BookList(Screen):
    @staticmethod
    def handle_addnew():
        app = MDApp.get_running_app()
        app.sm.get_screen('edit').open()

    def open(self):
        app = MDApp.get_running_app()
        authorized = app.is_auth()
        self.ids.add_btn.disabled = not authorized
        self.ids.add_btn.opacity = 1.0 if authorized else 0
        for book in self.ids.booklist.children:
            if isinstance(book, Book):
                book.ids.del_btn.disabled = not authorized

        app.switch_screen('books')

    def get_books(self):
        app = MDApp.get_running_app()
        app.menu.dismiss()
        books = [child for child in self.ids.booklist.children]
        for book in books:
            if isinstance(book, Book):
                self.ids.booklist.remove_widget(book)

        rest_endpoint = os.environ['REST_ENDPOINT']
        fetch(f"{rest_endpoint}/books", self.load_data)

    def load_data(self, request, result):
        book_data = result.get('books', None)
        if book_data:
            app = MDApp.get_running_app()
            authorized = app.is_auth()
            for book in book_data:
                new_book = Book(book_id=book['id'], text=book['title'], secondary_text=book['author'])
                new_book.ids.del_btn.disabled = not authorized
                self.ids.booklist.add_widget(new_book)


class Book(MDCardSwipe):
    book_id = NumericProperty()
    text = StringProperty()
    secondary_text = StringProperty()

    def __init__(self, **kw):
        super().__init__(**kw)
        self.dialog = ConfirmDialog(title="Delete Book",
                                    text=f"Are you sure you want to permanently delete '{self.text}'?",
                                    on_ok=self.do_delete)

    def do_delete(self):
        self.dialog.dismiss()
        app = MDApp.get_running_app()
        REST_ENDPOINT = os.environ['REST_ENDPOINT']

        fetch(f"{REST_ENDPOINT}/books/{self.book_id}", self.delete_success, method='DELETE', cookie=app.session_cookie)

    @staticmethod
    def delete_success(request, result):
        Notify(text="Book deleted").open()
        app = MDApp.get_running_app()
        app.sm.get_screen('books').get_books()

    def handle_delete(self):
        if self.open_progress > 0.0:
            self.dialog.open()

    def handle_edit(self, book_id):
        if self.open_progress == 0.0:
            app = MDApp.get_running_app()
            app.sm.get_screen('edit').open(book_id)