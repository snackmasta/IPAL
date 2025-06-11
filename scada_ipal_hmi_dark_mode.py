# Autor: Agung Rambujana 3A-TOI 221364002
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
        self.geometry("1200x1000")
        self.resizable(False, False)
        self.configure(bg="#23272E")  # Dark background
        self.running = True
        self.create_widgets()
        self.sim_thread = threading.Thread(target=self.sim_loop, daemon=True)
        self.sim_thread.start()

    def create_widgets(self):
        # Status Bar
        status_frame = ttk.Frame(self)
        status_frame.pack(fill='x', padx=5, pady=2)
        status_frame.configure(style="Dark.TFrame")
        # Indicator Lamp for System Status
        self.status_indicator = tk.Label(status_frame, text="STOPPED", font=("Arial", 14, "bold"), width=12, relief="groove", bg="#444950", fg="#E0E0E0")
        self.status_indicator.pack(side='left', padx=10, pady=2)
        self.start_btn = tk.Button(status_frame, text="START", command=self.start_system, bg="#388E3C", fg="#E0E0E0", activebackground="#2E7D32", activeforeground="#FFF", font=("Arial", 10, "bold"))
        self.start_btn.pack(side='left', padx=2)
        self.stop_btn = tk.Button(status_frame, text="STOP", command=self.stop_system, bg="#B71C1C", fg="#E0E0E0", activebackground="#8A1313", activeforeground="#FFF", font=("Arial", 10, "bold"))
        self.stop_btn.pack(side='left', padx=2)
        self.estop_btn = tk.Button(status_frame, text="E-STOP", command=self.estop_system, bg="#FF8C00", fg="#23272E", activebackground="#FF6F00", activeforeground="#FFF", font=("Arial", 10, "bold"))
        self.estop_btn.pack(side='left', padx=2)
        # Tambahan: Tombol kontrol dan indikator lamp
        lamp_frame = ttk.LabelFrame(status_frame, text="Indicators & Controls")
        lamp_frame.pack(side='left', padx=20)
        lamp_frame.configure(style="Dark.TLabelframe")
        # Indikator lampu (ON/OFF)
        self.lamp_vars = {}
        lamp_names = ["INLET OK", "TRANSFER OK", "BLOWER OK", "DOSING OK", "LUMPUR OK", "BUANG OK"]
        for i, name in enumerate(lamp_names):
            var = tk.StringVar(value="OFF")
            self.lamp_vars[name] = var
            lamp = tk.Label(lamp_frame, text=name, width=12, relief="groove", bg="#333", fg="#E0E0E0")
            lamp.grid(row=0, column=i, padx=2)
            self.lamp_vars[name+"_widget"] = lamp
        # Tombol tambahan
        self.btn_manual = tk.Button(lamp_frame, text="MANUAL", bg="#374151", fg="#E0E0E0", width=8, command=self.toggle_manual, activebackground="#23272E")
        self.btn_manual.grid(row=1, column=0, padx=2, pady=2)
        self.btn_auto = tk.Button(lamp_frame, text="AUTO", bg="#2E7D32", fg="#E0E0E0", width=8, command=self.toggle_auto, activebackground="#23272E")
        self.btn_auto.grid(row=1, column=1, padx=2, pady=2)
        self.btn_flush = tk.Button(lamp_frame, text="FLUSH", bg="#1976D2", fg="#E0E0E0", width=8, command=self.flush_action, activebackground="#23272E")
        self.btn_flush.grid(row=1, column=2, padx=2, pady=2)
        self.btn_alarm = tk.Button(lamp_frame, text="RESET ALARM", bg="#FBC02D", fg="#23272E", width=10, command=self.reset_alarm, activebackground="#23272E")
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
            btn = tk.Button(lamp_frame, text=f"{pump_labels[p]}", width=12, bg="#444950", fg="#E0E0E0", command=lambda k=p: self.toggle_pump_manual(k), activebackground="#23272E")
            btn.grid(row=2, column=i, padx=2, pady=2)
            self.manual_pump_btns[p] = btn
        self.update_manual_buttons()

        # Main Panel
        main_frame = ttk.Frame(self)
        main_frame.pack(fill='both', expand=True, padx=5, pady=2)
        main_frame.configure(style="Dark.TFrame")

        # Diagram Proses (gambar) - Diperbesar dan dipindah ke kiri
        diagram_frame = ttk.LabelFrame(main_frame, text="Diagram Proses", width=600)
        diagram_frame.grid(row=0, column=0, rowspan=3, sticky='nsew', padx=5, pady=5)
        diagram_frame.configure(style="Dark.TLabelframe")
        main_frame.grid_rowconfigure(0, weight=2)
        main_frame.grid_columnconfigure(0, weight=2)
        try:
            self.diagram_img = PhotoImage(file="diagram_ipal.png")
            tk.Label(diagram_frame, image=self.diagram_img, bg="#23272E").pack(expand=True, fill='both')
        except Exception:
            tk.Label(diagram_frame, text="(Tambahkan diagram_ipal.png)", bg="#23272E", fg="#E0E0E0").pack(expand=True, fill='both')

        # Komponen Panel
        comp_frame = ttk.LabelFrame(main_frame, text="Components", width=200)
        comp_frame.grid(row=0, column=1, sticky='nw', padx=5, pady=5)
        comp_frame.configure(style="Dark.TLabelframe")
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
            ttk.Label(comp_frame, text=f"{pump_labels[p]}:", style="Dark.TLabel").grid(row=i, column=0, sticky='e')
            ttk.Label(comp_frame, textvariable=var, width=6, background='#333', foreground="#E0E0E0", style="Dark.TLabel").grid(row=i, column=1, sticky='w')
        ttk.Label(comp_frame, text="Bak Penampung Awal:", style="Dark.TLabel").grid(row=7, column=0, sticky='e')
        self.ground_tank = ttk.Progressbar(comp_frame, length=100, maximum=100, style="Dark.Horizontal.TProgressbar")
        self.ground_tank.grid(row=7, column=1, sticky='w')
        ttk.Label(comp_frame, text="Bak Akhir:", style="Dark.TLabel").grid(row=8, column=0, sticky='e')
        self.eff_tank = ttk.Progressbar(comp_frame, length=100, maximum=100, style="Dark.Horizontal.TProgressbar")
        self.eff_tank.grid(row=8, column=1, sticky='w')

        # Data Proses Panel
        data_frame = ttk.LabelFrame(main_frame, text="Process Data", width=200)
        data_frame.grid(row=1, column=1, sticky='nw', padx=5, pady=5)
        data_frame.configure(style="Dark.TLabelframe")
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
            ttk.Label(data_frame, text=label+':', style="Dark.TLabel").grid(row=i, column=0, sticky='e')
            var = tk.StringVar()
            ttk.Label(data_frame, textvariable=var, width=10, background='#333', foreground="#E0E0E0", style="Dark.TLabel").grid(row=i, column=1, sticky='w')
            self.data_vars[k] = var

        # Alarm Panel
        alarm_frame = ttk.LabelFrame(main_frame, text="System Alarms", width=200)
        alarm_frame.grid(row=2, column=1, sticky='nw', padx=5, pady=5)
        alarm_frame.configure(style="Dark.TLabelframe")
        self.alarm_box = tk.Text(alarm_frame, height=10, width=30, bg='#2D2323', fg='#FF5252')
        self.alarm_box.pack()

        # Grafik Tren
        trend_frame = ttk.LabelFrame(self, text="Real-Time Trends")
        trend_frame.pack(fill='both', expand=True, padx=5, pady=2)
        trend_frame.configure(style="Dark.TLabelframe")
        self.fig = Figure(figsize=(12,6), dpi=100, facecolor="#23272E")
        self.ax1 = self.fig.add_subplot(121, facecolor="#23272E")
        self.ax2 = self.fig.add_subplot(122, facecolor="#23272E")
        self.canvas = FigureCanvasTkAgg(self.fig, master=trend_frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        self.trend_data = {'level': [], 'penampung': [], 'time': []}
        self.t0 = time.time()

        # Demo Controls
        demo_frame = ttk.Frame(self)
        demo_frame.pack(fill='x', padx=5, pady=2)
        demo_frame.configure(style="Dark.TFrame")
        ttk.Button(demo_frame, text="Normal Operation", command=self.normal_demo, style="Dark.TButton").pack(side='left', padx=2)
        ttk.Button(demo_frame, text="Stop Demo", command=self.stop_demo, style="Dark.TButton").pack(side='left', padx=2)

        # Informasi tambahan di bawah status bar
        info_frame = ttk.Frame(self)
        info_frame.pack(fill='x', padx=5, pady=2)
        info_frame.configure(style="Dark.TFrame")
        ttk.Label(info_frame, text="SCADA IPAL HMI - Autor: Agung Rambujana 3A-TOI 221364002", font=("Arial", 10, "italic"), foreground="#BBB", style="Dark.TLabel").pack(side='left', padx=10)

        # Style untuk dark mode
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Dark.TFrame", background="#23272E")
        style.configure("Dark.TLabelframe", background="#23272E", foreground="#E0E0E0")
        style.configure("Dark.TLabel", background="#23272E", foreground="#E0E0E0")
        style.configure("Dark.TButton", background="#374151", foreground="#E0E0E0")
        style.configure("Dark.Horizontal.TProgressbar", troughcolor="#23272E", background="#388E3C", bordercolor="#23272E", lightcolor="#388E3C", darkcolor="#23272E")

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
        self.ax1.set_facecolor("#23272E")
        self.ax1.plot(self.trend_data['time'], self.trend_data['level'], label='Level Bak Penampung', color="#4FC3F7")
        self.ax1.plot(self.trend_data['time'], self.trend_data['penampung'], label='Bak Akhir', color="#81C784")
        self.ax1.set_title('Tank Levels', color="#E0E0E0")
        self.ax1.set_ylabel('%', color="#E0E0E0")
        self.ax1.legend(facecolor="#23272E", edgecolor="#E0E0E0", labelcolor="#E0E0E0")
        self.ax1.tick_params(axis='x', colors="#E0E0E0")
        self.ax1.tick_params(axis='y', colors="#E0E0E0")
        self.ax2.clear()
        self.ax2.set_facecolor("#23272E")
        self.ax2.plot(self.trend_data['time'], self.trend_data['level'], label='Level Bak Penampung', color="#4FC3F7")
        self.ax2.set_title('Level Bak Penampung', color="#E0E0E0")
        self.ax2.set_ylabel('%', color="#E0E0E0")
        self.ax2.legend(facecolor="#23272E", edgecolor="#E0E0E0", labelcolor="#E0E0E0")
        self.ax2.tick_params(axis='x', colors="#E0E0E0")
        self.ax2.tick_params(axis='y', colors="#E0E0E0")
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
            lamp_widget.config(bg="#43A047" if state_on else "#333", fg="#E0E0E0")
        self.update_manual_buttons()
        # Update system status indicator lamp
        if getattr(self, 'emergency_active', False):
            self.status_indicator.config(text="EMERGENCY", bg="#FF5722", fg="#FFF")
        elif getattr(self, 'system_running', False):
            self.status_indicator.config(text="RUNNING", bg="#388E3C", fg="#FFF")
        else:
            self.status_indicator.config(text="STOPPED", bg="#444950", fg="#E0E0E0")

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
        self.status_indicator.config(text="RUNNING", bg="#388E3C", fg="#FFF")
        self.system_running = True
        alarms.append("[LOG] Sistem dijalankan.")

    def stop_system(self):
        self.status_indicator.config(text="STOPPED", bg="#444950", fg="#E0E0E0")
        self.system_running = False
        alarms.append("[LOG] Sistem dihentikan.")

    def estop_system(self):
        self.status_indicator.config(text="EMERGENCY", bg="#FF5722", fg="#FFF")
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
        self.status_indicator.config(text="STOPPED", bg="#444950", fg="#E0E0E0")
        self.estop_btn.config(text="E-STOP", command=self.estop_system, bg="#FF8C00", activebackground="#FF6F00")
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
                btn.config(state="normal", bg="#FFD600" if self.pump_vars[k].get()=="ON" else "#444950", fg="#23272E" if self.pump_vars[k].get()=="ON" else "#E0E0E0")
            else:
                btn.config(state="disabled", bg="#444950", fg="#E0E0E0")

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
