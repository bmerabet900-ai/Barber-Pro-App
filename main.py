from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.utils import platform

class MainScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(Label(text="Barber Pro App v0.1\nStatus: Active\n\nWaiting for Build Success...", halign="center"))

class BarberApp(App):
    def build(self):
        # طلب الصلاحيات برمجياً عند التشغيل
        if platform == 'android':
            try:
                from android.permissions import request_permissions, Permission
                request_permissions([
                    Permission.READ_CALL_LOG, 
                    Permission.WRITE_CALL_LOG, 
                    Permission.CALL_PHONE
                ])
            except Exception as e:
                print(f"Permissions error: {e}")
        return MainScreen()

if __name__ == '__main__':
    BarberApp().run()
