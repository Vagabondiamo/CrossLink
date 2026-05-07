from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.clock import Clock

class CrossLinkApp(App):
    def build(self):
        # Sfondo nero per vedere bene il testo
        Window.clearcolor = (0, 0, 0, 1)
        
        layout = BoxLayout(orientation='vertical', padding=50)
        self.label = Label(text="CrossLink V0.9\nRunning normally...", font_size='24sp')
        layout.add_widget(self.label)
        
        # Forza l'app a restare attiva
        Clock.schedule_interval(self.check_status, 1.0)
        
        return layout

    def check_status(self, dt):
        self.label.text = f"CrossLink V0.9\nApp is alive!\nTick: {int(Clock.get_boottime())}"

if __name__ == '__main__':
    CrossLinkApp().run()
