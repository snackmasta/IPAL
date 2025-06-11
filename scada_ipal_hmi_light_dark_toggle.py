# SCADA IPAL HMI - Light/Dark Mode Toggle
# Author: Agung Rambujana 3A-TOI 221364002
import tkinter as tk
from tkinter import ttk
from tkinter import PhotoImage
import threading
import time
import random
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
        self.running = True
        self.current_mode = 'dark'  # default mode
        self.create_widgets()
        self.sim_thread = threading.Thread(target=self.sim_loop, daemon=True)
        self.sim_thread.start()

    def create_widgets(self):
        # Status Bar
        status_frame = ttk.Frame(self)
        status_frame.pack(fill='x', padx=5, pady=2)
        # Indicator Lamp for System Status
        self.status_indicator = tk.Label(status_frame, text="STOPPED", font=("Arial", 14, "bold"), width=12, relief="groove")
        self.status_indicator.pack(side='left', padx=10, pady=2)
        self.start_btn = tk.Button(status_frame, text="START", command=self.start_system)
        self.start_btn.pack(side='left', padx=2)
        self.stop_btn = tk.Button(status_frame, text="STOP", command=self.stop_system)
        self.stop_btn.pack(side='left', padx=2)
        self.estop_btn = tk.Button(status_frame, text="E-STOP", command=self.estop_system)
        self.estop_btn.pack(side='left', padx=2)
        # Toggle Light/Dark Mode Button
        self.toggle_mode_btn = tk.Button(status_frame, text="Light Mode", command=self.toggle_mode)
        self.toggle_mode_btn.pack(side='right', padx=10)
        # Indicators & Controls
        lamp_frame = ttk.LabelFrame(status_frame, text="Indicators & Controls")
        lamp_frame.pack(side='left', padx=20)
        self.lamp_vars = {}
        lamp_names = ["INLET OK", "TRANSFER OK", "BLOWER OK", "DOSING OK", "LUMPUR OK", "BUANG OK"]
        for i, name in enumerate(lamp_names):
            var = tk.StringVar(value="OFF")
            self.lamp_vars[name] = var
            lamp = tk.Label(lamp_frame, text=name, width=12, relief="groove")
            lamp.grid(row=0, column=i, padx=2)
            self.lamp_vars[name+"_widget"] = lamp
        self.btn_manual = tk.Button(lamp_frame, text="MANUAL", width=8, command=self.toggle_manual)
        self.btn_manual.grid(row=1, column=0, padx=2, pady=2)
        self.btn_auto = tk.Button(lamp_frame, text="AUTO", width=8, command=self.toggle_auto)
        self.btn_auto.grid(row=1, column=1, padx=2, pady=2)
        self.btn_flush = tk.Button(lamp_frame, text="FLUSH", width=8, command=self.flush_action)
        self.btn_flush.grid(row=1, column=2, padx=2, pady=2)
        self.btn_alarm = tk.Button(lamp_frame, text="RESET ALARM", width=10, command=self.reset_alarm)
        self.btn_alarm.grid(row=1, column=3, padx=2, pady=2)
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
            btn = tk.Button(lamp_frame, text=f"{pump_labels[p]}", width=12, command=lambda k=p: self.toggle_pump_manual(k))
            btn.grid(row=2, column=i, padx=2, pady=2)
            self.manual_pump_btns[p] = btn
        self.update_manual_buttons()

        # Main Panel
        main_frame = ttk.Frame(self)
        main_frame.pack(fill='both', expand=True, padx=5, pady=2)
        # Diagram Proses
        diagram_frame = ttk.LabelFrame(main_frame, text="Diagram Proses", width=600)
        diagram_frame.grid(row=0, column=0, rowspan=3, sticky='nsew', padx=5, pady=5)
        main_frame.grid_rowconfigure(0, weight=2)
        main_frame.grid_columnconfigure(0, weight=2)
        try:
            self.diagram_img = PhotoImage(file="diagram_ipal.png")
            tk.Label(diagram_frame, image=self.diagram_img).pack(expand=True, fill='both')
        except Exception:
            tk.Label(diagram_frame, text="(Tambahkan diagram_ipal.png)").pack(expand=True, fill='both')
        # Komponen Panel
        comp_frame = ttk.LabelFrame(main_frame, text="Components", width=200)
        comp_frame.grid(row=0, column=1, sticky='nw', padx=5, pady=5)
        self.pump_vars = {}
        for i, p in enumerate(pumps):
            var = tk.StringVar(value="OFF")
            self.pump_vars[p] = var
            ttk.Label(comp_frame, text=f"{pump_labels[p]}:").grid(row=i, column=0, sticky='e')
            ttk.Label(comp_frame, textvariable=var, width=6).grid(row=i, column=1, sticky='w')
        ttk.Label(comp_frame, text="Bak Penampung Awal:").grid(row=7, column=0, sticky='e')
        self.ground_tank = ttk.Progressbar(comp_frame, length=100, maximum=100)
        self.ground_tank.grid(row=7, column=1, sticky='w')
        ttk.Label(comp_frame, text="Bak Akhir:").grid(row=8, column=0, sticky='e')
        self.eff_tank = ttk.Progressbar(comp_frame, length=100, maximum=100)
        self.eff_tank.grid(row=8, column=1, sticky='w')
        # Data Proses Panel
        data_frame = ttk.LabelFrame(main_frame, text="Process Data", width=200)
        data_frame.grid(row=1, column=1, sticky='nw', padx=5, pady=5)
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
            ttk.Label(data_frame, textvariable=var, width=10).grid(row=i, column=1, sticky='w')
            self.data_vars[k] = var
        # Alarm Panel
        alarm_frame = ttk.LabelFrame(main_frame, text="System Alarms", width=200)
        alarm_frame.grid(row=2, column=1, sticky='nw', padx=5, pady=5)
        self.alarm_box = tk.Text(alarm_frame, height=10, width=30)
        self.alarm_box.pack()
        # Grafik Tren
        trend_frame = ttk.LabelFrame(self, text="Real-Time Trends")
        trend_frame.pack(fill='both', expand=True, padx=5, pady=2)
        self.fig = Figure(figsize=(12,6), dpi=100)
        self.ax1 = self.fig.add_subplot(121)
        self.ax2 = self.fig.add_subplot(122)
        self.canvas = FigureCanvasTkAgg(self.fig, master=trend_frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        self.trend_data = {'level': [], 'penampung': [], 'time': []}
        self.t0 = time.time()
        # Demo Controls
        demo_frame = ttk.Frame(self)
        demo_frame.pack(fill='x', padx=5, pady=2)
        ttk.Button(demo_frame, text="Normal Operation", command=self.normal_demo).pack(side='left', padx=2)
        ttk.Button(demo_frame, text="Stop Demo", command=self.stop_demo).pack(side='left', padx=2)
        # Informasi tambahan di bawah status bar
        info_frame = ttk.Frame(self)
        info_frame.pack(fill='x', padx=5, pady=2)
        ttk.Label(info_frame, text="SCADA IPAL HMI - Autor: Agung Rambujana 3A-TOI 221364002", font=("Arial", 10, "italic")).pack(side='left', padx=10)
        self.apply_mode(self.current_mode)

    def apply_mode(self, mode):
        # Set style and color for widgets based on mode
        style = ttk.Style()
        if mode == 'dark':
            style.theme_use('clam')
            style.configure("TFrame", background="#23272E")
            style.configure("TLabelframe", background="#23272E", foreground="#E0E0E0")
            style.configure("TLabel", background="#23272E", foreground="#E0E0E0")
            style.configure("TButton", background="#374151", foreground="#E0E0E0")
            style.configure("Horizontal.TProgressbar", troughcolor="#23272E", background="#388E3C", bordercolor="#23272E", lightcolor="#388E3C", darkcolor="#23272E")
            self.status_indicator.config(bg="#444950", fg="#E0E0E0")
            self.alarm_box.config(bg="#2D2323", fg="#FF5252")
            self.toggle_mode_btn.config(text="Light Mode", bg="#23272E", fg="#E0E0E0")
        else:
            style.theme_use('clam')
            style.configure("TFrame", background="#F5F5F5")
            style.configure("TLabelframe", background="#F5F5F5", foreground="#222")
            style.configure("TLabel", background="#F5F5F5", foreground="#222")
            style.configure("TButton", background="#E0E0E0", foreground="#222")
            style.configure("Horizontal.TProgressbar", troughcolor="#F5F5F5", background="#4CAF50", bordercolor="#F5F5F5", lightcolor="#4CAF50", darkcolor="#F5F5F5")
            self.status_indicator.config(bg="#BDBDBD", fg="black")
            self.alarm_box.config(bg="#fff0f0", fg="red")
            self.toggle_mode_btn.config(text="Dark Mode", bg="#F5F5F5", fg="#222")
        # Update lamp widgets
        for lamp in ["INLET OK", "TRANSFER OK", "BLOWER OK", "DOSING OK", "LUMPUR OK", "BUANG OK"]:
            lamp_widget = self.lamp_vars[lamp+"_widget"]
            if self.pump_vars.get(lamp.split()[0].capitalize(), None) and self.pump_vars[lamp.split()[0].capitalize()].get() == "ON":
                lamp_widget.config(bg="#43A047" if mode=='dark' else "#4CAF50", fg="#E0E0E0" if mode=='dark' else "white")
            else:
                lamp_widget.config(bg="#333" if mode=='dark' else "#888", fg="#E0E0E0" if mode=='dark' else "white")
        # Manual pump buttons
        for k, btn in self.manual_pump_btns.items():
            if state['manual']:
                btn.config(state="normal", bg="#FFD600" if self.pump_vars[k].get()=="ON" else ("#444950" if mode=='dark' else "#BDBDBD"), fg="#23272E" if self.pump_vars[k].get()=="ON" else ("#E0E0E0" if mode=='dark' else "black"))
            else:
                btn.config(state="disabled", bg="#444950" if mode=='dark' else "#BDBDBD", fg="#E0E0E0" if mode=='dark' else "black")
        # Main buttons
        self.start_btn.config(bg="#388E3C" if mode=='dark' else "#4CAF50", fg="#FFF" if mode=='dark' else "white")
        self.stop_btn.config(bg="#444950" if mode=='dark' else "#E53935", fg="#E0E0E0" if mode=='dark' else "white")
        self.estop_btn.config(bg="#FF8C00" if mode=='dark' else "#FFA000", fg="#FFF" if mode=='dark' else "white")
        self.btn_manual.config(bg="#607D8B" if mode=='dark' else "#607D8B", fg="white")
        self.btn_auto.config(bg="#43A047" if mode=='dark' else "#43A047", fg="white")
        self.btn_flush.config(bg="#0288D1" if mode=='dark' else "#0288D1", fg="white")
        self.btn_alarm.config(bg="#FBC02D" if mode=='dark' else "#FBC02D", fg="black")
        # Matplotlib
        if mode == 'dark':
            self.fig.set_facecolor("#23272E")
            self.ax1.set_facecolor("#23272E")
            self.ax2.set_facecolor("#23272E")
        else:
            self.fig.set_facecolor("#F5F5F5")
            self.ax1.set_facecolor("#F5F5F5")
            self.ax2.set_facecolor("#F5F5F5")
        self.canvas.draw()

    def toggle_mode(self):
        self.current_mode = 'light' if self.current_mode == 'dark' else 'dark'
        self.apply_mode(self.current_mode)

    def update_gui(self):
        self.ground_tank['value'] = state['level']
        self.eff_tank['value'] = state['penampung']
        for k in self.data_vars:
            val = state[k]
            if isinstance(val, float):
                self.data_vars[k].set(f"{val:.2f}")
            else:
                self.data_vars[k].set(str(val))
        if getattr(self, 'system_running', False) and not state['manual']:
            self.pump_vars['Inlet'].set("ON" if state['level'] >= LEVEL_MIN and state['level'] <= LEVEL_MAX else "OFF")
            self.pump_vars['Transfer'].set("ON" if state['level'] > LEVEL_MAX else "OFF")
            self.pump_vars['Blower'].set("ON" if state['do'] < DO_SETPOINT else "OFF")
            self.pump_vars['Dosing'].set("ON" if not (PH_MIN <= state['ph'] <= PH_MAX) else "OFF")
            self.pump_vars['Lumpur'].set("ON" if state['lumpur'] > LUMPUR_MAX else "OFF")
            self.pump_vars['Buang'].set("ON" if state['penampung'] > 90 else "OFF")
        elif state['manual']:
            pass
        else:
            for k in self.pump_vars:
                self.pump_vars[k].set("OFF")
        self.alarm_box.delete(1.0, tk.END)
        for a in alarms[-10:]:
            self.alarm_box.insert(tk.END, a+"\n")
        t = time.time() - self.t0
        self.trend_data['level'].append(state['level'])
        self.trend_data['penampung'].append(state['penampung'])
        self.trend_data['time'].append(t)
        if len(self.trend_data['time']) > 50:
            for k in self.trend_data:
                self.trend_data[k] = self.trend_data[k][-50:]
        self.ax1.clear()
        if self.current_mode == 'dark':
            self.ax1.set_facecolor("#23272E")
            self.ax1.plot(self.trend_data['time'], self.trend_data['level'], label='Level Bak Penampung', color="#4FC3F7")
            self.ax1.plot(self.trend_data['time'], self.trend_data['penampung'], label='Bak Akhir', color="#81C784")
            self.ax1.set_title('Tank Levels', color="#E0E0E0")
            self.ax1.set_ylabel('%', color="#E0E0E0")
            self.ax1.legend(facecolor="#23272E", edgecolor="#E0E0E0", labelcolor="#E0E0E0")
            self.ax1.tick_params(axis='x', colors="#E0E0E0")
            self.ax1.tick_params(axis='y', colors="#E0E0E0")
        else:
            self.ax1.set_facecolor("#F5F5F5")
            self.ax1.plot(self.trend_data['time'], self.trend_data['level'], label='Level Bak Penampung', color="#1976D2")
            self.ax1.plot(self.trend_data['time'], self.trend_data['penampung'], label='Bak Akhir', color="#388E3C")
            self.ax1.set_title('Tank Levels', color="#222")
            self.ax1.set_ylabel('%', color="#222")
            self.ax1.legend(facecolor="#F5F5F5", edgecolor="#222", labelcolor="#222")
            self.ax1.tick_params(axis='x', colors="#222")
            self.ax1.tick_params(axis='y', colors="#222")
        self.ax2.clear()
        if self.current_mode == 'dark':
            self.ax2.set_facecolor("#23272E")
            self.ax2.plot(self.trend_data['time'], self.trend_data['level'], label='Level Bak Penampung', color="#4FC3F7")
            self.ax2.set_title('Level Bak Penampung', color="#E0E0E0")
            self.ax2.set_ylabel('%', color="#E0E0E0")
            self.ax2.legend(facecolor="#23272E", edgecolor="#E0E0E0", labelcolor="#E0E0E0")
            self.ax2.tick_params(axis='x', colors="#E0E0E0")
            self.ax2.tick_params(axis='y', colors="#E0E0E0")
        else:
            self.ax2.set_facecolor("#F5F5F5")
            self.ax2.plot(self.trend_data['time'], self.trend_data['level'], label='Level Bak Penampung', color="#1976D2")
            self.ax2.set_title('Level Bak Penampung', color="#222")
            self.ax2.set_ylabel('%', color="#222")
            self.ax2.legend(facecolor="#F5F5F5", edgecolor="#222", labelcolor="#222")
            self.ax2.tick_params(axis='x', colors="#222")
            self.ax2.tick_params(axis='y', colors="#222")
        self.canvas.draw()
        # Update lamp widgets
        for lamp, pump in zip(["INLET OK", "TRANSFER OK", "BLOWER OK", "DOSING OK", "LUMPUR OK", "BUANG OK"], ['Inlet', 'Transfer', 'Blower', 'Dosing', 'Lumpur', 'Buang']):
            state_on = self.pump_vars[pump].get() == "ON"
            lamp_widget = self.lamp_vars[lamp+"_widget"]
            if state_on:
                lamp_widget.config(bg="#43A047" if self.current_mode=='dark' else "#4CAF50", fg="#E0E0E0" if self.current_mode=='dark' else "white")
            else:
                lamp_widget.config(bg="#333" if self.current_mode=='dark' else "#888", fg="#E0E0E0" if self.current_mode=='dark' else "white")
        self.update_manual_buttons()
        # Update system status indicator lamp
        if getattr(self, 'emergency_active', False):
            self.status_indicator.config(text="EMERGENCY", bg="#FF5722" if self.current_mode=='dark' else "#FF5722", fg="#FFF" if self.current_mode=='dark' else "white")
        elif getattr(self, 'system_running', False):
            self.status_indicator.config(text="RUNNING", bg="#388E3C" if self.current_mode=='dark' else "#4CAF50", fg="#FFF" if self.current_mode=='dark' else "white")
        else:
            self.status_indicator.config(text="STOPPED", bg="#444950" if self.current_mode=='dark' else "#BDBDBD", fg="#E0E0E0" if self.current_mode=='dark' else "black")

    def sim_loop(self):
        while self.running:
            if not state['manual'] and getattr(self, 'system_running', False):
                self.simulate_step()
            self.update_gui()
            time.sleep(0.7)

    def simulate_step(self):
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
        if state['level'] < LEVEL_MIN:
            alarms.append("[LOG] Matikan pompa inlet (level rendah)")
            return
        if state['level'] > LEVEL_MAX:
            alarms.append("[LOG] Transfer ke bak pemisah lumpur")
            if random.random() < 0.1:
                alarms.append("[ALARM] Overload bak pemisah lumpur! Transfer dihentikan.")
                return
        if state['do'] < DO_SETPOINT:
            alarms.append("[LOG] Aktifkan blower/aerator (DO rendah)")
            state['do'] += 0.5
        if not (PH_MIN <= state['ph'] <= PH_MAX):
            alarms.append("[LOG] Aktifkan dosing chemical (pH tidak normal)")
            state['ph'] = 7.0
        if not (SUHU_MIN <= state['suhu'] <= SUHU_MAX):
            alarms.append("[ALARM] Suhu di luar rentang operasional!")
        if state['lumpur'] > LUMPUR_MAX:
            alarms.append("[LOG] Pompa lumpur ke pengolahan lumpur")
            state['lumpur'] -= 10
            state['sludge'] += 10
        if state['chemical'] < CHEMICAL_MIN:
            alarms.append("[ALARM] Stok disinfektan habis!")
            state['chemical'] += 20
        if state['penampung'] > 90:
            alarms.append("[LOG] Aktifkan pompa buang/recirculation")
            state['penampung'] -= 30
        if state['sludge'] > SLUDGE_SETPOINT:
            alarms.append("[LOG] Proses pengeringan/stabilisasi lumpur")
            state['sludge'] -= 20
        if random.random() < 0.05:
            alarms.append("[ALARM] Terjadi gangguan sistem! Logging alarm.")

    def start_system(self):
        if getattr(self, 'emergency_active', False):
            alarms.append("[ALARM] Tidak dapat menyalakan sistem saat EMERGENCY aktif!")
            return
        self.status_indicator.config(text="RUNNING")
        self.system_running = True
        alarms.append("[LOG] Sistem dijalankan.")

    def stop_system(self):
        self.status_indicator.config(text="STOPPED")
        self.system_running = False
        alarms.append("[LOG] Sistem dihentikan.")

    def estop_system(self):
        self.status_indicator.config(text="EMERGENCY")
        self.system_running = False
        self.emergency_active = True
        self.estop_btn.config(text="RESET", command=self.reset_emergency)
        alarms.append("[ALARM] Emergency Stop diaktifkan!")

    def normal_demo(self):
        self.start_system()
        alarms.append("[LOG] Demo normal operation.")

    def stop_demo(self):
        self.stop_system()
        alarms.append("[LOG] Demo dihentikan.")

    def reset_emergency(self):
        self.emergency_active = False
        self.status_indicator.config(text="STOPPED")
        self.estop_btn.config(text="E-STOP", command=self.estop_system)
        alarms.append("[LOG] Emergency Stop dicabut. Sistem kembali ke posisi STOPPED.")

    def toggle_manual(self):
        state['manual'] = True
        alarms.append("[LOG] Mode MANUAL diaktifkan.")
        self.btn_manual.config(relief="sunken")
        self.btn_auto.config(relief="raised")
        self.update_manual_buttons()

    def toggle_auto(self):
        state['manual'] = False
        alarms.append("[LOG] Mode AUTO diaktifkan.")
        self.btn_manual.config(relief="raised")
        self.btn_auto.config(relief="sunken")
        self.update_manual_buttons()

    def flush_action(self):
        alarms.append("[LOG] FLUSH dijalankan.")
        state['penampung'] = 0

    def reset_alarm(self):
        alarms.clear()
        alarms.append("[LOG] Semua alarm direset.")

    def on_closing(self):
        self.running = False
        self.destroy()

    def update_manual_buttons(self):
        for k, btn in self.manual_pump_btns.items():
            if state['manual']:
                btn.config(state="normal", bg="#FFD600" if self.pump_vars[k].get()=="ON" else ("#444950" if self.current_mode=='dark' else "#BDBDBD"), fg="#23272E" if self.pump_vars[k].get()=="ON" else ("#E0E0E0" if self.current_mode=='dark' else "black"))
            else:
                btn.config(state="disabled", bg="#444950" if self.current_mode=='dark' else "#BDBDBD", fg="#E0E0E0" if self.current_mode=='dark' else "black")

    def toggle_pump_manual(self, pump):
        if not state['manual']:
            return
        if self.pump_vars[pump].get() == "ON":
            self.pump_vars[pump].set("OFF")
            alarms.append(f"[LOG] {pump} dimatikan secara manual.")
        else:
            self.pump_vars[pump].set("ON")
            alarms.append(f"[LOG] {pump} dinyalakan secara manual.")
        self.update_manual_buttons()

if __name__ == "__main__":
    app = SCADAIPALHMI()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
