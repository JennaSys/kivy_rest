from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.properties import NumericProperty, StringProperty
from kivymd.uix.card import MDCardSwipe

from kivy.network.urlrequest import UrlRequest


REST_ENDPOINT = 'http://192.168.2.154:8000/api'


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
    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Teal"
        self.theme_cls.accent_palette = "Pink"
        # Window.size = (300, 400)
        Window.size = (400, 600)
        self.title = "Book List"

    def on_start(self):
        #     for book_id, book in enumerate(books):
        #         self.root.ids.books.add_widget(
        #             Book(book_id=book_id, text=book[0], secondary_text=book[1])
        #         )
        req = UrlRequest(f"{REST_ENDPOINT}/books",
                         on_success=self.load_data,
                         timeout=5,
                         on_failure=lambda rq, rp: print("Oops!"),
                         on_error=lambda rq, rp: print("Error!"))

    def load_data(self, request, result):
        books = result.get('books', None)
        if books:
            for book in books:
                self.root.ids.books.add_widget(
                    Book(book_id=book['id'], text=book['title'], secondary_text=book['author'])
                )

    def handle_addnew(self, value):
        print(f"Add New!")


if __name__ == '__main__':
    app = MainApp()
    app.run()
