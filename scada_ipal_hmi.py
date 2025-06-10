import tkinter as tk
from tkinter import ttk
from tkinter import PhotoImage
import threading
import random
import time
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# Parameter batasan
LEVEL_MIN = 30
LEVEL_MAX = 80
DO_SETPOINT = 2.0
PH_MIN = 6.5
PH_MAX = 8.5
SUHU_MIN = 20
SUHU_MAX = 35
LUMPUR_MAX = 70
CHEMICAL_MIN = 10
SLUDGE_SETPOINT = 60

state = {
    'level': 50,
    'do': 2.5,
    'ph': 7.2,
    'suhu': 28,
    'lumpur': 40,
    'chemical': 50,
    'sludge': 30,
    'penampung': 40,
    'manual': False
}

alarms = []

class SCADAIPALHMI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SCADA IPAL - HMI")
        self.geometry("1100x700")
        self.resizable(False, False)
        self.running = True
        self.create_widgets()
        self.sim_thread = threading.Thread(target=self.sim_loop, daemon=True)
        self.sim_thread.start()

    def create_widgets(self):
        # Status Bar
        status_frame = ttk.Frame(self)
        status_frame.pack(fill='x', padx=5, pady=2)
        self.status_label = ttk.Label(status_frame, text="SYSTEM STOPPED", font=("Arial", 18, "bold"), foreground="blue")
        self.status_label.pack(side='left', padx=10)
        self.start_btn = tk.Button(status_frame, text="START", command=self.start_system, bg="#4CAF50", fg="white", activebackground="#388E3C", activeforeground="white", font=("Arial", 10, "bold"))
        self.start_btn.pack(side='left', padx=2)
        self.stop_btn = tk.Button(status_frame, text="STOP", command=self.stop_system, bg="#E53935", fg="white", activebackground="#B71C1C", activeforeground="white", font=("Arial", 10, "bold"))
        self.stop_btn.pack(side='left', padx=2)
        self.estop_btn = tk.Button(status_frame, text="E-STOP", command=self.estop_system, bg="#FFA000", fg="white", activebackground="#FF6F00", activeforeground="white", font=("Arial", 10, "bold"))
        self.estop_btn.pack(side='left', padx=2)
        # Tambahan: Tombol kontrol dan indikator lamp
        lamp_frame = ttk.LabelFrame(status_frame, text="Indicators & Controls")
        lamp_frame.pack(side='left', padx=20)
        # Indikator lampu (ON/OFF)
        self.lamp_vars = {}
        lamp_names = ["INLET OK", "TRANSFER OK", "BLOWER OK", "DOSING OK", "LUMPUR OK", "BUANG OK"]
        for i, name in enumerate(lamp_names):
            var = tk.StringVar(value="OFF")
            self.lamp_vars[name] = var
            lamp = tk.Label(lamp_frame, text=name, width=12, relief="groove", bg="#888", fg="white")
            lamp.grid(row=0, column=i, padx=2)
            self.lamp_vars[name+"_widget"] = lamp
        # Tombol tambahan
        self.btn_manual = tk.Button(lamp_frame, text="MANUAL", bg="#607D8B", fg="white", width=8, command=self.toggle_manual)
        self.btn_manual.grid(row=1, column=0, padx=2, pady=2)
        self.btn_auto = tk.Button(lamp_frame, text="AUTO", bg="#43A047", fg="white", width=8, command=self.toggle_auto)
        self.btn_auto.grid(row=1, column=1, padx=2, pady=2)
        self.btn_flush = tk.Button(lamp_frame, text="FLUSH", bg="#0288D1", fg="white", width=8, command=self.flush_action)
        self.btn_flush.grid(row=1, column=2, padx=2, pady=2)
        self.btn_alarm = tk.Button(lamp_frame, text="RESET ALARM", bg="#FBC02D", fg="black", width=10, command=self.reset_alarm)
        self.btn_alarm.grid(row=1, column=3, padx=2, pady=2)
        # Tombol manual untuk setiap komponen
        self.manual_pump_btns = {}
        pumps = ['Inlet', 'Transfer', 'Blower', 'Dosing', 'Lumpur', 'Buang']
        pump_labels = {
            'Inlet': 'Pompa Inlet',
            'Transfer': 'Pompa Transfer',
            'Blower': 'Pompa Blower',
            'Dosing': 'Pompa Dosing',
            'Lumpur': 'Pompa Lumpur',
            'Buang': 'Pompa Buang',
        }
        for i, p in enumerate(pumps):
            btn = tk.Button(lamp_frame, text=f"{pump_labels[p]}", width=12, bg="#BDBDBD", fg="black", command=lambda k=p: self.toggle_pump_manual(k))
            btn.grid(row=2, column=i, padx=2, pady=2)
            self.manual_pump_btns[p] = btn
        self.update_manual_buttons()

        # Main Panel
        main_frame = ttk.Frame(self)
        main_frame.pack(fill='both', expand=True, padx=5, pady=2)

        # Komponen Panel
        comp_frame = ttk.LabelFrame(main_frame, text="Components", width=200)
        comp_frame.grid(row=0, column=0, sticky='nw', padx=5, pady=5)
        self.pump_vars = {}
        pumps = ['Inlet', 'Transfer', 'Blower', 'Dosing', 'Lumpur', 'Buang']
        pump_labels = {
            'Inlet': 'Pompa Inlet',
            'Transfer': 'Pompa Transfer',
            'Blower': 'Pompa Blower',
            'Dosing': 'Pompa Dosing',
            'Lumpur': 'Pompa Lumpur',
            'Buang': 'Pompa Buang',
        }
        for i, p in enumerate(pumps):
            var = tk.StringVar(value="OFF")
            self.pump_vars[p] = var
            ttk.Label(comp_frame, text=f"{pump_labels[p]}:").grid(row=i, column=0, sticky='e')
            ttk.Label(comp_frame, textvariable=var, width=6, background='#e0e0e0').grid(row=i, column=1, sticky='w')
        ttk.Label(comp_frame, text="Bak Penampung Awal:").grid(row=7, column=0, sticky='e')
        self.ground_tank = ttk.Progressbar(comp_frame, length=100, maximum=100)
        self.ground_tank.grid(row=7, column=1, sticky='w')
        ttk.Label(comp_frame, text="Bak Akhir:").grid(row=8, column=0, sticky='e')
        self.eff_tank = ttk.Progressbar(comp_frame, length=100, maximum=100)
        self.eff_tank.grid(row=8, column=1, sticky='w')

        # Alarm Panel
        alarm_frame = ttk.LabelFrame(main_frame, text="System Alarms", width=200)
        alarm_frame.grid(row=0, column=1, sticky='nw', padx=5, pady=5)
        self.alarm_box = tk.Text(alarm_frame, height=10, width=30, bg='#fff0f0', fg='red')
        self.alarm_box.pack()

        # Data Proses Panel
        data_frame = ttk.LabelFrame(main_frame, text="Process Data", width=200)
        data_frame.grid(row=0, column=2, sticky='nw', padx=5, pady=5)
        self.data_vars = {}
        data_labels = [
            ('level', 'Level Bak Penampung Awal'),
            ('do', 'DO (mg/L)'),
            ('ph', 'pH'),
            ('suhu', 'Suhu (°C)'),
            ('lumpur', 'Kadar Lumpur'),
            ('chemical', 'Kadar Disinfektan'),
            ('sludge', 'Volume Lumpur'),
            ('penampung', 'Level Bak Akhir'),
        ]
        for i, (k, label) in enumerate(data_labels):
            ttk.Label(data_frame, text=label+':').grid(row=i, column=0, sticky='e')
            var = tk.StringVar()
            ttk.Label(data_frame, textvariable=var, width=10, background='#f0f0f0').grid(row=i, column=1, sticky='w')
            self.data_vars[k] = var

        # Diagram Proses (gambar)
        diagram_frame = ttk.LabelFrame(main_frame, text="Diagram Proses", width=300)
        diagram_frame.grid(row=0, column=3, sticky='nw', padx=5, pady=5)
        try:
            self.diagram_img = PhotoImage(file="diagram_ipal.png")
            tk.Label(diagram_frame, image=self.diagram_img).pack()
        except Exception:
            tk.Label(diagram_frame, text="(Tambahkan diagram_ipal.png)").pack()

        # Grafik Tren
        trend_frame = ttk.LabelFrame(self, text="Real-Time Trends")
        trend_frame.pack(fill='x', padx=5, pady=2)
        self.fig = Figure(figsize=(7,2.5), dpi=100)
        self.ax1 = self.fig.add_subplot(121)
        self.ax2 = self.fig.add_subplot(122)
        self.canvas = FigureCanvasTkAgg(self.fig, master=trend_frame)
        self.canvas.get_tk_widget().pack()
        self.trend_data = {'level': [], 'penampung': [], 'time': []}
        self.t0 = time.time()

        # Demo Controls
        demo_frame = ttk.Frame(self)
        demo_frame.pack(fill='x', padx=5, pady=2)
        ttk.Button(demo_frame, text="Normal Operation", command=self.normal_demo).pack(side='left', padx=2)
        ttk.Button(demo_frame, text="Stop Demo", command=self.stop_demo).pack(side='left', padx=2)

    def update_gui(self):
        # Update komponen
        self.ground_tank['value'] = state['level']
        self.eff_tank['value'] = state['penampung']
        # Update data proses
        for k in self.data_vars:
            val = state[k]
            if isinstance(val, float):
                self.data_vars[k].set(f"{val:.2f}")
            else:
                self.data_vars[k].set(str(val))
        # Update pompa sesuai flowchart
        # Pompa Inlet hanya ON jika level >= LEVEL_MIN dan <= LEVEL_MAX dan sistem RUNNING
        if getattr(self, 'system_running', False) and not state['manual']:
            self.pump_vars['Inlet'].set("ON" if state['level'] >= LEVEL_MIN and state['level'] <= LEVEL_MAX else "OFF")
            self.pump_vars['Transfer'].set("ON" if state['level'] > LEVEL_MAX else "OFF")
            self.pump_vars['Blower'].set("ON" if state['do'] < DO_SETPOINT else "OFF")
            self.pump_vars['Dosing'].set("ON" if not (PH_MIN <= state['ph'] <= PH_MAX) else "OFF")
            self.pump_vars['Lumpur'].set("ON" if state['lumpur'] > LUMPUR_MAX else "OFF")
            self.pump_vars['Buang'].set("ON" if state['penampung'] > 90 else "OFF")
        elif state['manual']:
            # Jangan ubah status pompa jika manual, biarkan tombol manual yang mengatur
            pass
        else:
            # Jika sistem tidak running atau manual, semua OFF
            for k in self.pump_vars:
                self.pump_vars[k].set("OFF")
        # Update alarm
        self.alarm_box.delete(1.0, tk.END)
        for a in alarms[-10:]:
            self.alarm_box.insert(tk.END, a+"\n")
        # Update tren
        t = time.time() - self.t0
        self.trend_data['level'].append(state['level'])
        self.trend_data['penampung'].append(state['penampung'])
        self.trend_data['time'].append(t)
        if len(self.trend_data['time']) > 50:
            for k in self.trend_data:
                self.trend_data[k] = self.trend_data[k][-50:]
        self.ax1.clear()
        self.ax1.plot(self.trend_data['time'], self.trend_data['level'], label='Level Bak Penampung')
        self.ax1.plot(self.trend_data['time'], self.trend_data['penampung'], label='Bak Akhir')
        self.ax1.set_title('Tank Levels')
        self.ax1.set_ylabel('%')
        self.ax1.legend()
        self.ax2.clear()
        self.ax2.plot(self.trend_data['time'], self.trend_data['level'], label='Level Bak Penampung')
        self.ax2.set_title('Level Bak Penampung')
        self.ax2.set_ylabel('%')
        self.ax2.legend()
        self.canvas.draw()
        # Update indikator lamp sesuai status pompa
        lamp_map = [
            ("INLET OK", 'Inlet'),
            ("TRANSFER OK", 'Transfer'),
            ("BLOWER OK", 'Blower'),
            ("DOSING OK", 'Dosing'),
            ("LUMPUR OK", 'Lumpur'),
            ("BUANG OK", 'Buang'),
        ]
        for lamp, pump in lamp_map:
            state_on = self.pump_vars[pump].get() == "ON"
            lamp_widget = self.lamp_vars[lamp+"_widget"]
            lamp_widget.config(bg="#4CAF50" if state_on else "#888")
        self.update_manual_buttons()

    def sim_loop(self):
        while self.running:
            if not state['manual'] and getattr(self, 'system_running', False):
                self.simulate_step()
            self.update_gui()
            time.sleep(0.7)

    def simulate_step(self):
        # Simulasi fluktuasi sensor
        state['level'] += random.randint(-5, 5)
        state['do'] += random.uniform(-0.3, 0.3)
        state['ph'] += random.uniform(-0.2, 0.2)
        state['suhu'] += random.uniform(-1, 1)
        state['lumpur'] += random.randint(-2, 3)
        state['chemical'] -= random.uniform(0, 1)
        state['sludge'] += random.randint(0, 2)
        state['penampung'] += random.randint(-3, 4)
        for k in state:
            if isinstance(state[k], (int, float)):
                state[k] = max(0, state[k])

        # Logika kendali sesuai flowchart
        # 1. Pompa Inlet
        if state['level'] < LEVEL_MIN:
            alarms.append("[LOG] Matikan pompa inlet (level rendah)")
            # Pompa Inlet OFF, tidak ada aksi lain
            return
        # 2. Pompa Transfer
        if state['level'] > LEVEL_MAX:
            alarms.append("[LOG] Transfer ke bak pemisah lumpur")
            if random.random() < 0.1:
                alarms.append("[ALARM] Overload bak pemisah lumpur! Transfer dihentikan.")
                # Transfer dihentikan jika overload
                return
        # 3. Unit Biologis: Pantau DO, pH, Suhu
        if state['do'] < DO_SETPOINT:
            alarms.append("[LOG] Aktifkan blower/aerator (DO rendah)")
            state['do'] += 0.5
        if not (PH_MIN <= state['ph'] <= PH_MAX):
            alarms.append("[LOG] Aktifkan dosing chemical (pH tidak normal)")
            state['ph'] = 7.0
        if not (SUHU_MIN <= state['suhu'] <= SUHU_MAX):
            alarms.append("[ALARM] Suhu di luar rentang operasional!")
        # 4. Pengendapan & Lumpur
        if state['lumpur'] > LUMPUR_MAX:
            alarms.append("[LOG] Pompa lumpur ke pengolahan lumpur")
            state['lumpur'] -= 10
            state['sludge'] += 10
        # 5. Disinfeksi & Chemical
        if state['chemical'] < CHEMICAL_MIN:
            alarms.append("[ALARM] Stok disinfektan habis!")
            state['chemical'] += 20
        # 6. Bak Penampung Akhir
        if state['penampung'] > 90:
            alarms.append("[LOG] Aktifkan pompa buang/recirculation")
            state['penampung'] -= 30
        # 7. Pengolahan Lumpur
        if state['sludge'] > SLUDGE_SETPOINT:
            alarms.append("[LOG] Proses pengeringan/stabilisasi lumpur")
            state['sludge'] -= 20
        # 8. Alarm acak
        if random.random() < 0.05:
            alarms.append("[ALARM] Terjadi gangguan sistem! Logging alarm.")

    def start_system(self):
        if getattr(self, 'emergency_active', False):
            alarms.append("[ALARM] Tidak dapat menyalakan sistem saat EMERGENCY aktif!")
            return
        self.status_label.config(text="SYSTEM RUNNING", foreground="green")
        self.system_running = True
        alarms.append("[LOG] Sistem dijalankan.")

    def stop_system(self):
        self.status_label.config(text="SYSTEM STOPPED", foreground="blue")
        self.system_running = False
        alarms.append("[LOG] Sistem dihentikan.")

    def estop_system(self):
        self.status_label.config(text="EMERGENCY STOP", foreground="red")
        self.system_running = False
        self.emergency_active = True
        self.estop_btn.config(text="RESET", command=self.reset_emergency, bg="#1976D2", activebackground="#0D47A1")
        alarms.append("[ALARM] Emergency Stop diaktifkan!")

    def normal_demo(self):
        self.start_system()
        alarms.append("[LOG] Demo normal operation.")

    def stop_demo(self):
        self.stop_system()
        alarms.append("[LOG] Demo dihentikan.")

    def reset_emergency(self):
        self.emergency_active = False
        self.status_label.config(text="SYSTEM STOPPED", foreground="blue")
        self.estop_btn.config(text="E-STOP", command=self.estop_system, bg="#FFA000", activebackground="#FF6F00")
        alarms.append("[LOG] Emergency Stop dicabut. Sistem kembali ke posisi STOPPED.")

    def toggle_manual(self):
        state['manual'] = True
        alarms.append("[LOG] Mode MANUAL diaktifkan.")
        self.btn_manual.config(relief="sunken")
        self.btn_auto.config(relief="raised")

    def toggle_auto(self):
        state['manual'] = False
        alarms.append("[LOG] Mode AUTO diaktifkan.")
        self.btn_manual.config(relief="raised")
        self.btn_auto.config(relief="sunken")

    def flush_action(self):
        alarms.append("[LOG] FLUSH dijalankan.")
        # Simulasi flush: reset level bak penampung akhir
        state['penampung'] = 0

    def reset_alarm(self):
        alarms.clear()
        alarms.append("[LOG] Semua alarm direset.")

    def on_closing(self):
        self.running = False
        self.destroy()

    def update_manual_buttons(self):
        # Enable tombol manual jika mode manual, disable jika auto
        for k, btn in self.manual_pump_btns.items():
            if state['manual']:
                btn.config(state="normal", bg="#FFD600" if self.pump_vars[k].get()=="ON" else "#BDBDBD")
            else:
                btn.config(state="disabled", bg="#BDBDBD")

    def toggle_pump_manual(self, pump):
        if not state['manual']:
            return
        # Toggle ON/OFF
        if self.pump_vars[pump].get() == "ON":
            self.pump_vars[pump].set("OFF")
            alarms.append(f"[LOG] {pump} dimatikan secara manual.")
        else:
            # Matikan semua pompa lain jika ingin hanya satu ON (jika ingin eksklusif)
            # for k in self.pump_vars:
            #     self.pump_vars[k].set("OFF")
            self.pump_vars[pump].set("ON")
            alarms.append(f"[LOG] {pump} dinyalakan secara manual.")
        self.update_manual_buttons()

if __name__ == "__main__":
    app = SCADAIPALHMI()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
