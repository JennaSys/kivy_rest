import os

from kivy.factory import Factory
from kivymd.uix.screen import MDScreen
from kivy.properties import NumericProperty
from kivymd.app import MDApp

from apputils import fetch, Notify, load_kv

load_kv(__name__)


class BookEdit(MDScreen):
    book_id = NumericProperty(None, allownone=True)

    def open(self, book_id=None):
        app = MDApp.get_running_app()
        authorized = app.is_auth()
        self.ids.save_edit.disabled = not authorized
        for field in self.ids.edit_fields.children:
            if isinstance(field, Factory.BookField):
                field.cursor = (0, 0)
                field.disabled = not authorized

        self.ids.title.focus = True
        app.switch_screen('edit')

        self.book_id = book_id
        if book_id is not None:
            rest_endpoint = os.environ['REST_ENDPOINT']
            fetch(f"{rest_endpoint}/books/{book_id}", self.load_data)

    def close(self, ref=None):
        self.clear()
        app = MDApp.get_running_app()
        app.sm.get_screen('books').open()

    def load_data(self, request, result):
        book_data = result.get('book', None)
        if book_data:
            self.book_id = book_data['id']
            self.ids.title.text = book_data['title']
            self.ids.author.text = book_data['author']

    def handle_save(self):
        body = {'title': self.ids.title.text, 'author': self.ids.author.text}
        if self.book_id is not None:
            body['id'] = self.book_id

        rest_resource = "books" if self.book_id is None else f"books/{self.book_id}"
        method = 'POST' if self.book_id is None else 'PUT'
        app = MDApp.get_running_app()
        rest_endpoint = os.environ['REST_ENDPOINT']

        fetch(f"{rest_endpoint}/{rest_resource}", self.save_success, method=method, data=body, cookie=app.session_cookie)

    def save_success(self, request, result):
        Notify(text=f"Book {'added' if self.book_id is None else 'updated'}").open()
        self.clear()
        app = MDApp.get_running_app()
        app.sm.get_screen('books').get_books()
        app.sm.get_screen('books').open()

    def clear(self):
        self.book_id = None
        self.ids.title.text = ""
        self.ids.author.text = ""
