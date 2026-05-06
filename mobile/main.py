from kivy.app import App
from kivy.uix.label import QLabel

class CrossLinkBareBones(App):
    def build(self):
        return QLabel(text="CROSS-LINK V0.5\nIf you see this, Kivy is working!\nNow we know the problem is in the other files.")

if __name__ == '__main__':
    CrossLinkBareBones().run()
