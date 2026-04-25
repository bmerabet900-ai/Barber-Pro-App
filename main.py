from kivy.app import App
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.utils import platform

class BarberApp(App):
    def build(self):
        self.label = Label(text='Barber Pro v1.0\nجاري تشغيل التطبيق...', halign="center")
        # طلب الصلاحيات بعد ثانية واحدة من التشغيل لتجنب كراش البداية
        Clock.schedule_once(self.check_permissions, 1)
        return self.label

    def check_permissions(self, dt):
        if platform == 'android':
            try:
                from android.permissions import request_permissions, Permission
                request_permissions([
                    Permission.READ_CALL_LOG,
                    Permission.WRITE_CALL_LOG,
                    Permission.CALL_PHONE
                ])
                self.label.text = "Barber Pro\nتم طلب صلاحيات السجل"
            except Exception as e:
                self.label.text = f"خطأ في الصلاحيات:\n{str(e)}"

if __name__ == '__main__':
    BarberApp().run()
