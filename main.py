from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.utils import platform

class BarberScreen(BoxLayout):
    def __init__(self, **kwargs):
        # إعداد واجهة التطبيق
        super().__init__(orientation='vertical', padding=20, spacing=20, **kwargs)
        self.status_label = Label(text="Barber Pro v1.0\nمرحبا بك يا شاف!", font_size='20sp', halign="center")
        self.add_widget(self.status_label)
        
        # زر لتجربة التفاعل
        self.action_btn = Button(text="التحقق من سجل المكالمات", size_hint=(1, 0.2))
        self.action_btn.bind(on_press=self.check_logs)
        self.add_widget(self.action_btn)

    def check_logs(self, instance):
        self.status_label.text = "جاري البحث في السجل...\n(تم تفعيل الزر بنجاح)"

class BarberApp(App):
    def build(self):
        self.screen = BarberScreen()
        # نطلب من التطبيق الانتظار ثانية واحدة بعد التشغيل ثم طلب الصلاحيات
        Clock.schedule_once(self.request_android_permissions, 1)
        return self.screen

    def request_android_permissions(self, dt):
        if platform == 'android':
            try:
                from android.permissions import request_permissions, Permission
                # طلب جميع الصلاحيات اللازمة لتطبيقك
                request_permissions([
                    Permission.READ_CALL_LOG,
                    Permission.WRITE_CALL_LOG,
                    Permission.CALL_PHONE
                ])
                self.screen.status_label.text += "\nتم طلب صلاحيات الأندرويد."
            except Exception as e:
                self.screen.status_label.text += f"\nخطأ في الصلاحيات: {str(e)}"

if __name__ == '__main__':
    BarberApp().run()
