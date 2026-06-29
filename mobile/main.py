import os
import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from plyer import filechooser
from kivy.core.window import Window

Window.clearcolor = (0.2, 0.4, 0.8, 1)


class ConnectScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=50, spacing=20)
        
        layout.add_widget(Label(text="CrossLink", font_size=40, size_hint_y=None, height=60))
        layout.add_widget(Label(text="Inserisci indirizzo server", size_hint_y=None, height=40))
        
        self.url_input = TextInput(multiline=False, hint_text="http://192.168.1.x:8000", size_hint_y=None, height=50)
        layout.add_widget(self.url_input)
        
        connect_btn = Button(text="Connetti", size_hint_y=None, height=50, on_press=self.connect)
        layout.add_widget(connect_btn)
        
        self.status_label = Label(text="", size_hint_y=None, height=40)
        layout.add_widget(self.status_label)
        
        self.add_widget(layout)
    
    def connect(self, *args):
        url = self.url_input.text.strip()
        if not url:
            self.status_label.text = "Inserisci un URL valido"
            return
        
        if not url.startswith("http"):
            url = "http://" + url
        
        try:
            response = requests.get(f"{url}/files", timeout=5)
            if response.status_code == 200:
                self.manager.get_screen('main').server_url = url
                self.manager.current = 'main'
                self.status_label.text = "Connesso!"
            else:
                self.status_label.text = "Server non raggiungibile"
        except Exception as e:
            self.status_label.text = f"Errore: {str(e)}"


class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.server_url = ""
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Header
        header = BoxLayout(size_hint_y=None, height=50)
        header.add_widget(Label(text="CrossLink", font_size=24))
        layout.add_widget(header)
        
        # Bottoni
        btn_layout = BoxLayout(size_hint_y=None, height=60, spacing=10)
        self.send_btn = Button(text="📤 Invia File", on_press=self.send_file)
        self.refresh_btn = Button(text="🔄 Aggiorna", on_press=self.refresh_files)
        btn_layout.add_widget(self.send_btn)
        btn_layout.add_widget(self.refresh_btn)
        layout.add_widget(btn_layout)
        
        # Lista file PC
        layout.add_widget(Label(text="File sul PC", size_hint_y=None, height=40))
        
        self.files_layout = GridLayout(cols=1, size_hint_y=None, spacing=5)
        self.files_layout.bind(minimum_height=self.files_layout.setter('height'))
        
        scroll = ScrollView(size_hint_y=None, height=400)
        scroll.add_widget(self.files_layout)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
        self.refresh_files()
    
    def send_file(self, *args):
        try:
            filechooser.open_file(on_selection=self.handle_file_selection)
        except Exception as e:
            self.show_message(f"Errore: {str(e)}")
    
    def handle_file_selection(self, selection):
        if not selection:
            return
        
        file_path = selection[0]
        filename = os.path.basename(file_path)
        
        try:
            with open(file_path, 'rb') as f:
                files = {'files': (filename, f, 'application/octet-stream')}
                response = requests.post(f"{self.server_url}/upload", files=files)
            
            if response.status_code == 200:
                self.show_message("File inviato!")
                self.refresh_files()
            else:
                self.show_message("Errore invio")
        except Exception as e:
            self.show_message(f"Errore: {str(e)}")
    
    def refresh_files(self, *args):
        try:
            response = requests.get(f"{self.server_url}/files")
            if response.status_code == 200:
                files = response.json()
                self.update_files_list(files)
        except Exception as e:
            self.show_message(f"Errore: {str(e)}")
    
    def update_files_list(self, files):
        self.files_layout.clear_widgets()
        
        if not files:
            self.files_layout.add_widget(Label(text="Nessun file", size_hint_y=None, height=40))
            return
        
        for item in files:
            name = item["name"]
            is_dir = item["is_dir"]
            icon = "📁" if is_dir else "📄"
            
            file_btn = Button(
                text=f"{icon} {name}",
                size_hint_y=None,
                height=50,
                on_press=lambda x, n=name, d=is_dir: self.download_file(n, d)
            )
            self.files_layout.add_widget(file_btn)
    
    def download_file(self, filename, is_dir=False):
        try:
            response = requests.get(f"{self.server_url}/download/{filename}")
            if response.status_code == 200:
                # Salva nella cartella Downloads
                from android.storage import primary_external_storage_path
                
                local_filename = filename
                if is_dir and not filename.lower().endswith(".zip"):
                    local_filename += ".zip"
                    
                download_path = os.path.join(primary_external_storage_path(), "Download", local_filename)
                
                with open(download_path, 'wb') as f:
                    f.write(response.content)
                
                self.show_message(f"Scaricato: {local_filename}")
            else:
                self.show_message("Errore download")
        except Exception as e:
            self.show_message(f"Errore: {str(e)}")
    
    def show_message(self, text):
        self.files_layout.clear_widgets()
        self.files_layout.add_widget(Label(text=text, size_hint_y=None, height=50))


class CrossLinkApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(ConnectScreen(name='connect'))
        sm.add_widget(MainScreen(name='main'))
        return sm


if __name__ == '__main__':
    CrossLinkApp().run()

