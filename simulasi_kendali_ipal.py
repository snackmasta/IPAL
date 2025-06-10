import random
import time

# Parameter batasan
LEVEL_MIN = 30
LEVEL_MAX = 80
DO_SETPOINT = 2.0  # mg/L
PH_MIN = 6.5
PH_MAX = 8.5
SUHU_MIN = 20
SUHU_MAX = 35
LUMPUR_MAX = 70
CHEMICAL_MIN = 10
SLUDGE_SETPOINT = 60

# Status awal
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

def log(msg):
    print(f"[LOG] {msg}")

def alarm(msg):
    print(f"[ALARM] {msg}")

def monitoring():
    # Simulasi fluktuasi sensor
    state['level'] += random.randint(-5, 5)
    state['do'] += random.uniform(-0.3, 0.3)
    state['ph'] += random.uniform(-0.2, 0.2)
    state['suhu'] += random.uniform(-1, 1)
    state['lumpur'] += random.randint(-2, 3)
    state['chemical'] -= random.uniform(0, 1)
    state['sludge'] += random.randint(0, 2)
    state['penampung'] += random.randint(-3, 4)
    # Clamp values
    for k in state:
        if isinstance(state[k], (int, float)):
            state[k] = max(0, state[k])

def kendali_ipal():
    log("Inisialisasi Sistem")
    for step in range(1, 21):
        print(f"\n=== Siklus {step} ===")
        monitoring()
        log(f"Level: {state['level']} | DO: {state['do']:.2f} | pH: {state['ph']:.2f} | Suhu: {state['suhu']:.1f} | Lumpur: {state['lumpur']} | Chemical: {state['chemical']:.1f} | Sludge: {state['sludge']} | Penampung: {state['penampung']}")
        if state['manual']:
            log("Mode manual aktif. Operator override.")
            break
        # Level kontrol
        if state['level'] < LEVEL_MIN:
            log("Matikan pompa inlet (level rendah)")
            continue
        if state['level'] > LEVEL_MAX:
            log("Transfer ke bak pemisah lumpur")
            if random.random() < 0.1:
                alarm("Overload bak pemisah lumpur! Transfer dihentikan.")
                continue
        # Unit Biologis
        if state['do'] < DO_SETPOINT:
            log("Aktifkan blower/aerator (DO rendah)")
            state['do'] += 0.5
        if not (PH_MIN <= state['ph'] <= PH_MAX):
            log("Aktifkan dosing chemical (pH tidak normal)")
            state['ph'] = 7.0
        if not (SUHU_MIN <= state['suhu'] <= SUHU_MAX):
            alarm("Suhu di luar rentang operasional!")
        # Pengendapan akhir
        if state['lumpur'] > LUMPUR_MAX:
            log("Pompa lumpur ke pengolahan lumpur")
            state['lumpur'] -= 10
            state['sludge'] += 10
        # Disinfeksi
        if state['chemical'] < CHEMICAL_MIN:
            alarm("Stok disinfektan habis!")
            state['chemical'] += 20
        # Bak penampung akhir
        if state['penampung'] > 90:
            log("Aktifkan pompa buang/recirculation")
            state['penampung'] -= 30
        # Pengolahan lumpur
        if state['sludge'] > SLUDGE_SETPOINT:
            log("Proses pengeringan/stabilisasi lumpur")
            state['sludge'] -= 20
        # Logging
        if random.random() < 0.05:
            alarm("Terjadi gangguan sistem! Logging alarm.")
        time.sleep(0.5)
    log("Selesai simulasi.")

if __name__ == "__main__":
    kendali_ipal()
