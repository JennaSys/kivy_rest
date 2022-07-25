from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.properties import NumericProperty, StringProperty
from kivymd.uix.card import MDCardSwipe


books = [('I Robot', 'Isaac Asimov'),
                 ('React to Python', 'Sheehan'),
                 ('Zen and the Art of Motorcycle Maintenance', 'Robert Pirsig'),
                 ('Cosmos', 'Carl Sagan'),
                 ('The Contrary Farmer', 'Gene Logsdon')]


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
        for book_id, book in enumerate(books):
            self.root.ids.books.add_widget(
                Book(book_id=book_id, text=book[0], secondary_text=book[1])
            )

    def handle_addnew(self, value):
        print(f"Add New!")


if __name__ == '__main__':
    app = MainApp()
    app.run()
