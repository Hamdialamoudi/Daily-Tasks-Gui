"""
Daily Tasks & Priorities GUI - Extended Version
by hamdiwork 🧠🔥

"""

import os
import uuid
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
from threading import Thread
import time
from plyer import notification

EXCEL_FILE = 'tasks.xlsx'
COLUMNS = ['id', 'title', 'description', 'day',
           'start_time', 'end_time', 'priority', 'repeat']
DAYS = ['السبت', 'الأحد', 'الاثنين',
        'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة']
PRIORITIES = ['عالية', 'متوسطة', 'منخفضة']
REPEATS = ['بدون', 'يومي', 'أسبوعي']


class TaskManager:
    def __init__(self, filename=EXCEL_FILE):
        self.filename = filename
        self.df = pd.DataFrame(columns=COLUMNS)
        self.load()

    def load(self):
        if os.path.exists(self.filename):
            try:
                df = pd.read_excel(self.filename, engine='openpyxl')
                for c in COLUMNS:
                    if c not in df.columns:
                        df[c] = ''
                self.df = df[COLUMNS].copy()
            except:
                self.df = pd.DataFrame(columns=COLUMNS)
        else:
            self.df = pd.DataFrame(columns=COLUMNS)

    def save(self):
        self.df.to_excel(self.filename, index=False, engine='openpyxl')

    def add_task(self, title, description, day, start_time, end_time, priority, repeat):
        task_id = str(uuid.uuid4())
        new = {
            'id': task_id,
            'title': title,
            'description': description,
            'day': day,
            'start_time': start_time,
            'end_time': end_time,
            'priority': priority,
            'repeat': repeat
        }
        self.df = pd.concat([self.df, pd.DataFrame([new])], ignore_index=True)
        self.save()
        return task_id

    def update_task(self, task_id, **kwargs):
        idx = self.df.index[self.df['id'] == task_id].tolist()
        if not idx:
            return False
        i = idx[0]
        for k, v in kwargs.items():
            if k in COLUMNS:
                self.df.at[i, k] = v
        self.save()
        return True

    def delete_task(self, task_id):
        self.df = self.df[self.df['id'] != task_id]
        self.save()

    def get_all(self):
        return self.df.copy()


class ReminderThread(Thread):
    def __init__(self, manager):
        super().__init__(daemon=True)
        self.manager = manager
        self.start()

    def run(self):
        while True:
            df = self.manager.get_all()
            now = datetime.now().strftime('%H:%M')
            today = DAYS[datetime.now().weekday()]
            for _, row in df.iterrows():
                if row['start_time'] == now and (row['day'] == today or row['repeat'] in ['يومي', 'أسبوعي']):
                    notification.notify(
                        title=f"تذكير: {row['title']}",
                        message=f"اليوم: {row['day']}\nمن {row['start_time']} إلى {row['end_time']}\n{row['description']}",
                        timeout=10
                    )
            time.sleep(60)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('🗓️ مخطط المهام اليومية - hamdiwork')
        self.geometry('950x650')
        self.manager = TaskManager()
        self.create_widgets()
        self.populate_table()
        ReminderThread(self.manager)

    def create_widgets(self):
        frame_top = ttk.LabelFrame(self, text='إدارة المهام')
        frame_top.pack(fill='x', padx=10, pady=8)

        ttk.Label(frame_top, text='العنوان:').grid(row=0, column=0)
        self.title_entry = ttk.Entry(frame_top, width=25)
        self.title_entry.grid(row=0, column=1)

        ttk.Label(frame_top, text='اليوم:').grid(row=0, column=2)
        self.day_combo = ttk.Combobox(
            frame_top, values=DAYS, state='readonly', width=12)
        self.day_combo.grid(row=0, column=3)
        self.day_combo.current(0)

        ttk.Label(frame_top, text='أولوية:').grid(row=0, column=4)
        self.priority_combo = ttk.Combobox(
            frame_top, values=PRIORITIES, state='readonly', width=10)
        self.priority_combo.grid(row=0, column=5)
        self.priority_combo.current(1)

        ttk.Label(frame_top, text='تكرار:').grid(row=0, column=6)
        self.repeat_combo = ttk.Combobox(
            frame_top, values=REPEATS, state='readonly', width=10)
        self.repeat_combo.grid(row=0, column=7)
        self.repeat_combo.current(0)

        ttk.Label(frame_top, text='بدأ:').grid(row=1, column=0)
        self.start_entry = ttk.Entry(frame_top, width=10)
        self.start_entry.grid(row=1, column=1)

        ttk.Label(frame_top, text='انتهى:').grid(row=1, column=2)
        self.end_entry = ttk.Entry(frame_top, width=10)
        self.end_entry.grid(row=1, column=3)

        ttk.Label(frame_top, text='الوصف:').grid(row=2, column=0)
        self.desc_text = tk.Text(frame_top, width=70, height=3)
        self.desc_text.grid(row=2, column=1, columnspan=6, pady=5)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill='x', padx=10)

        ttk.Button(btn_frame, text='➕ إضافة',
                   command=self.add_task).pack(side='left', padx=5)
        ttk.Button(btn_frame, text='📝 تعديل',
                   command=self.update_task).pack(side='left', padx=5)
        ttk.Button(btn_frame, text='🗑️ حذف', command=self.delete_task).pack(
            side='left', padx=5)
        ttk.Button(btn_frame, text='💾 حفظ Excel',
                   command=self.export_excel).pack(side='left', padx=5)
        ttk.Button(btn_frame, text='📂 تصدير CSV',
                   command=self.export_csv).pack(side='left', padx=5)
        ttk.Button(btn_frame, text='🧹 تفريغ',
                   command=self.clear_fields).pack(side='left', padx=5)

        cols = ('title', 'day', 'start_time', 'end_time',
                'priority', 'repeat', 'description', 'id')
        self.tree = ttk.Treeview(
            self, columns=cols, show='headings', selectmode='browse')
        for c in cols[:-1]:
            self.tree.heading(c, text=c)
        self.tree.column('description', width=250)
        self.tree.column('id', width=0, stretch=False)
        self.tree.pack(fill='both', expand=True, padx=10, pady=8)

        self.tree.bind('<<TreeviewSelect>>', self.on_select)

    def add_task(self):
        title = self.title_entry.get().strip()
        desc = self.desc_text.get('1.0', 'end').strip()
        day = self.day_combo.get()
        start = self.start_entry.get().strip()
        end = self.end_entry.get().strip()
        priority = self.priority_combo.get()
        repeat = self.repeat_combo.get()

        if not title:
            messagebox.showwarning('تحذير', 'أدخل عنوان المهمة')
            return

        task_id = self.manager.add_task(
            title, desc, day, start, end, priority, repeat)
        self.populate_table()
        self.clear_fields()

    def update_task(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo('معلومة', 'اختر مهمة لتحديثها')
            return
        task_id = self.tree.item(sel[0])['values'][7]
        data = dict(
            title=self.title_entry.get().strip(),
            description=self.desc_text.get('1.0', 'end').strip(),
            day=self.day_combo.get(),
            start_time=self.start_entry.get().strip(),
            end_time=self.end_entry.get().strip(),
            priority=self.priority_combo.get(),
            repeat=self.repeat_combo.get()
        )
        self.manager.update_task(task_id, **data)
        self.populate_table()

    def delete_task(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo('معلومة', 'اختر مهمة للحذف')
            return
        task_id = self.tree.item(sel[0])['values'][7]
        self.manager.delete_task(task_id)
        self.populate_table()

    def export_excel(self):
        self.manager.save()
        messagebox.showinfo('تم', 'تم حفظ البيانات في Excel')

    def export_csv(self):
        path = filedialog.asksaveasfilename(defaultextension='.csv')
        if path:
            self.manager.df.to_csv(path, index=False)
            messagebox.showinfo('تم', 'تم تصدير CSV بنجاح')

    def populate_table(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        for _, row in self.manager.get_all().iterrows():
            self.tree.insert('', 'end', values=(row['title'], row['day'], row['start_time'],
                             row['end_time'], row['priority'], row['repeat'], row['description'], row['id']))

    def on_select(self, e):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0])['values']
        self.title_entry.delete(0, 'end')
        self.title_entry.insert(0, vals[0])
        self.day_combo.set(vals[1])
        self.start_entry.delete(0, 'end')
        self.start_entry.insert(0, vals[2])
        self.end_entry.delete(0, 'end')
        self.end_entry.insert(0, vals[3])
        self.priority_combo.set(vals[4])
        self.repeat_combo.set(vals[5])
        self.desc_text.delete('1.0', 'end')
        self.desc_text.insert('1.0', vals[6])

    def clear_fields(self):
        self.title_entry.delete(0, 'end')
        self.desc_text.delete('1.0', 'end')
        self.day_combo.current(0)
        self.priority_combo.current(1)
        self.repeat_combo.current(0)
        self.start_entry.delete(0, 'end')
        self.end_entry.delete(0, 'end')


if __name__ == '__main__':
    app = App()
    app.mainloop()
