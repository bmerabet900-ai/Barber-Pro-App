import sqlite3
import os
import webbrowser
from datetime import datetime, timedelta
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.utils import platform

# --- Database Setup ---
DB_NAME = 'barber_pro_final.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS queue 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  name TEXT, phone TEXT, app_time TEXT, 
                  status INTEGER DEFAULT 0, confirmed_at TEXT)''')
    conn.commit()
    conn.close()

class BarberApp(App):
    def build(self):
        init_db()
        Window.clearcolor = (0.02, 0.05, 0.1, 1) 
        self.next_person_wait_start = None
        
        # --- المتغير السحري الجديد لتتبع المكالمات ---
        self.call_offset = 0 

        main_layout = BoxLayout(orientation='vertical', padding=15, spacing=10)

        # 1. Header
        header = Label(text="BARBER PRO v1.0", font_size=24, bold=True, color=(0.1, 0.9, 0.5, 1), size_hint_y=0.1)
        main_layout.add_widget(header)

        # 2. Input Section
        input_area = BoxLayout(orientation='vertical', spacing=8, size_hint_y=0.3)
        self.name_in = TextInput(hint_text="Client Name", multiline=False, font_size=18, halign="center")
        
        self.btn_fetch = Button(text="📲 FETCH NEXT CALL", background_color=(0.1, 0.6, 0.4, 1), bold=True, font_size=20)
        self.btn_fetch.bind(on_release=self.fetch_last_call)
        
        btn_add = Button(text="⚡ MANUAL BOOK", background_color=(0, 0.4, 0.7, 1), bold=True)
        btn_add.bind(on_release=self.add_to_queue)
        
        input_area.add_widget(self.name_in)
        input_area.add_widget(self.btn_fetch)
        input_area.add_widget(btn_add)
        main_layout.add_widget(input_area)

        # 3. Queue List
        scroll = ScrollView(size_hint_y=0.6)
        self.queue_list = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.queue_list.bind(minimum_height=self.queue_list.setter('height'))
        scroll.add_widget(self.queue_list)
        main_layout.add_widget(scroll)

        self.refresh_ui()
        Clock.schedule_interval(self.refresh_ui, 1)

        return main_layout

    def fetch_last_call(self, instance):
        if platform == 'android':
            try:
                from jnius import autoclass
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                Uri = autoclass('android.net.Uri')
                activity = PythonActivity.mActivity
                resolver = activity.getContentResolver()
                
                call_uri = Uri.parse("content://call_log/calls")
                cursor = resolver.query(call_uri, None, None, None, "date DESC")
                
                # نستخدم call_offset للرجوع في السجل مكالمة بمكالمة
                if cursor and cursor.moveToPosition(self.call_offset):
                    num_col = cursor.getColumnIndex("number")
                    last_num = cursor.getString(num_col)
                    cursor.close()
                    
                    if last_num:
                        self.add_to_queue_direct(last_num)
                        self.call_offset += 1 # زيادة العداد للمكالمة القادمة
                        self.name_in.text = f"Fetched Call #{self.call_offset}"
                else:
                    self.name_in.text = "End of call log!"
                    self.call_offset = 0 # تصفير العداد إذا وصلنا للنهاية
            except Exception as e:
                self.name_in.text = "Error: Check Permissions"
        else:
            self.name_in.text = "Not on Android"

    def calculate_next_time(self):
        conn = sqlite3.connect(DB_NAME); c = conn.cursor()
        c.execute("SELECT app_time FROM queue ORDER BY id DESC LIMIT 1")
        last = c.fetchone(); conn.close()
        now = datetime.now()
        if last:
            last_t = datetime.strptime(last[0], "%H:%M")
            next_t = now.replace(hour=last_t.hour, minute=last_t.minute) + timedelta(minutes=45)
            if next_t < now: next_t = now
        else:
            next_t = now
        return next_t.strftime("%H:%M")

    def add_to_queue_direct(self, phone):
        name = "📞 Phone Client"
        time_slot = self.calculate_next_time()
        conn = sqlite3.connect(DB_NAME)
        conn.execute("INSERT INTO queue (name, phone, app_time, status) VALUES (?,?,?,?)", (name, phone, time_slot, 0))
        conn.commit(); conn.close()
        self.refresh_ui()

    def add_to_queue(self, instance):
        name = self.name_in.text.strip()
        if not name: name = "⚡ Quick Client"
        time_slot = self.calculate_next_time()
        conn = sqlite3.connect(DB_NAME)
        conn.execute("INSERT INTO queue (name, phone, app_time, status) VALUES (?,?,?,?)", (name, "No Phone", time_slot, 0))
        conn.commit(); conn.close()
        self.name_in.text = ""
        self.refresh_ui()

    def refresh_ui(self, dt=None):
        self.queue_list.clear_widgets()
        conn = sqlite3.connect(DB_NAME); c = conn.cursor()
        c.execute("SELECT id, name, phone, app_time, status, confirmed_at FROM queue ORDER BY id ASC")
        rows = c.fetchall()
        now = datetime.now()
        busy_id = -1
        haircut_elapsed = 0
        for r in rows:
            if r[4] == 1:
                busy_id = r[0]
                if r[5]:
                    try:
                        conf_time = datetime.strptime(r[5], "%Y-%m-%d %H:%M:%S")
                        haircut_elapsed = (now - conf_time).total_seconds()
                    except: haircut_elapsed = 0
                break
        is_chair_busy = (busy_id != -1 and haircut_elapsed < 2700)
        found_next_p = False
        for r in rows:
            app_id, name, phone, app_time, status, conf_at = r
            row_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=120, spacing=5, padding=5)
            info_box = BoxLayout(orientation='vertical', size_hint_x=0.6)
            if status == 1:
                rem = max(0, 2700 - haircut_elapsed); m, s = divmod(int(rem), 60)
                lbl = Label(text=f"✂️ {name}\n⏰ {m:02d}:{s:02d}", color=(0.2, 1, 0.2, 1))
            elif status == 0:
                if not found_next_p:
                    found_next_p = True
                    if is_chair_busy:
                        lbl = Label(text=f"⌚ {app_time} | {name}\n⏳ Wait...", color=(0.6, 0.6, 0.6, 1))
                    else:
                        if self.next_person_wait_start is None: self.next_person_wait_start = now
                        elapsed = (now - self.next_person_wait_start).total_seconds()
                        rem = 600 - elapsed
                        if rem <= 0:
                            c.execute("DELETE FROM queue WHERE id=?", (app_id,))
                            continue
                        m, s = divmod(int(rem), 60)
                        lbl = Label(text=f"⌚ {app_time} | {name}\n⚠️ {m:02d}:{s:02d}", color=(1, 0.6, 0, 1))
                else:
                    lbl = Label(text=f"⌚ {app_time} | {name}\n💤 Queue", color=(0.4, 0.4, 0.4, 1))
            info_box.add_widget(lbl)
            row_box.add_widget(info_box)
            btn_box = BoxLayout(orientation='vertical', size_hint_x=0.4, spacing=2)
            if status == 1:
                btn_fin = Button(text="FINISH", background_color=(0.5, 0.5, 0.5, 1), bold=True)
                btn_fin.bind(on_release=lambda x, id=app_id: self.update_status(id, 2))
                btn_box.add_widget(btn_fin)
            elif status == 0 and not is_chair_busy:
                btn_app = Button(text="APPROVE", background_color=(0, 0.7, 0.3, 1), bold=True)
                btn_app.bind(on_release=lambda x, id=app_id: self.update_status(id, 1))
                btn_box.add_widget(btn_app)
            row_box.add_widget(btn_box)
            self.queue_list.add_widget(row_box)
        conn.commit(); conn.close()

    def update_status(self, app_id, new_status):
        conn = sqlite3.connect(DB_NAME)
        if new_status == 1:
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn.execute("UPDATE queue SET status=1, confirmed_at=? WHERE id=?", (now_str, app_id))
            self.next_person_wait_start = None
        elif new_status == 2:
            conn.execute("DELETE FROM queue WHERE id=?", (app_id,))
        conn.commit(); conn.close()
        self.refresh_ui()

if __name__ == '__main__':
    BarberApp().run()
