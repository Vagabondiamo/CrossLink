from kivy.app import App
from kivy.uix.label import Label
from kivy.utils import platform

class CrossLinkBareBones(App):
    def build(self):
        msg = f"CROSS-LINK V0.5\nPlatform: {platform}\nIf you see this, Kivy is working!"
        return Label(text=msg)

    def on_start(self):
        # Proviamo a vedere se il modulo android è importabile
        if platform == 'android':
            try:
                from android.permissions import request_permissions, Permission
                request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])
            except Exception as e:
                pass

if __name__ == '__main__':
    CrossLinkBareBones().run()
