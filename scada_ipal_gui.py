import tkinter as tk
from tkinter import ttk
import threading
import random
import time

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

class SCADAIPAL(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SCADA IPAL Simulator")
        self.geometry("700x500")
        self.resizable(False, False)
        self.create_widgets()
        self.running = True
        self.sim_thread = threading.Thread(target=self.sim_loop, daemon=True)
        self.sim_thread.start()

    def create_widgets(self):
        # Title
        ttk.Label(self, text="SCADA IPAL", font=("Arial", 20, "bold")).pack(pady=10)
        # Frame for process values
        frame = ttk.Frame(self)
        frame.pack(pady=10)
        self.vars = {}
        row = 0
        for key, label in [
            ('level', 'Level Bak Penampung'),
            ('do', 'DO (mg/L)'),
            ('ph', 'pH'),
            ('suhu', 'Suhu (°C)'),
            ('lumpur', 'Lumpur'),
            ('chemical', 'Chemical'),
            ('sludge', 'Sludge'),
            ('penampung', 'Bak Akhir'),
        ]:
            ttk.Label(frame, text=label+':', width=20, anchor='e').grid(row=row, column=0, sticky='e')
            var = tk.StringVar()
            ttk.Label(frame, textvariable=var, width=10, anchor='w', background='#f0f0f0').grid(row=row, column=1, sticky='w')
            self.vars[key] = var
            row += 1
        # Status pompa/aktuator
        self.status_var = tk.StringVar()
        ttk.Label(self, textvariable=self.status_var, font=("Arial", 12), foreground='blue').pack(pady=5)
        # Alarm area
        ttk.Label(self, text="Alarm/Log:", font=("Arial", 10, "bold")).pack()
        self.alarm_box = tk.Text(self, height=7, width=80, bg='#fff0f0', fg='red')
        self.alarm_box.pack(pady=5)
        # Manual override
        self.manual_btn = ttk.Button(self, text="Manual Override", command=self.toggle_manual)
        self.manual_btn.pack(pady=5)

    def update_gui(self):
        for k in self.vars:
            val = state[k]
            if isinstance(val, float):
                self.vars[k].set(f"{val:.2f}")
            else:
                self.vars[k].set(str(val))
        if state['manual']:
            self.status_var.set("MODE MANUAL - Operator override!")
        else:
            self.status_var.set("")
        # Show alarms
        self.alarm_box.delete(1.0, tk.END)
        for a in alarms[-7:]:
            self.alarm_box.insert(tk.END, a+"\n")

    def toggle_manual(self):
        state['manual'] = not state['manual']
        if state['manual']:
            alarms.append("[ALARM] Mode manual diaktifkan oleh operator!")
        else:
            alarms.append("[LOG] Mode otomatis diaktifkan kembali.")
        self.update_gui()

    def sim_loop(self):
        while self.running:
            if not state['manual']:
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
        # Logika kendali
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

    def on_closing(self):
        self.running = False
        self.destroy()

if __name__ == "__main__":
    app = SCADAIPAL()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
