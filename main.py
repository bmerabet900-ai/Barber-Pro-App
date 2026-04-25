from kivy.app import App
from kivy.uix.label import Label

class BarberApp(App):
    def build(self):
        # سنلغي طلب الصلاحيات برمجياً حالياً ونكتفي بطلبها من ملف spec
        return Label(text='Barber Pro v1.0\nReady!')

if __name__ == '__main__':
    BarberApp().run()
