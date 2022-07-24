from kivy.app import App
from kivy.uix.gridlayout import GridLayout


class Window(GridLayout):
    @staticmethod
    def on_press_button():
        print('You pressed the button!')


class MainApp(App):
    def build(self):
        return Window(rows=3)


if __name__ == '__main__':
    app = MainApp()
    app.run()
