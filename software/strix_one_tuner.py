#!/usr/bin/env python3
"""
STRIX ONE Tuner
Python tuning software for the single-cylinder Alpha-N STRIX ONE ECU.
Mimics the style of TorquEFI STRIX / typical EFI tuners:
- Live gauges (RPM, TPS, Baro, CLT, IAT)
- VE table viewer / editor
- Trigger selection
- Serial connection to firmware
"""

import sys
import serial
import serial.tools.list_ports
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time

class StrixOneTuner:
    def __init__(self, root):
        self.root = root
        self.root.title("STRIX ONE Tuner - Single Cylinder Alpha-N")
        self.root.geometry("900x700")
        self.ser = None
        self.running = True
        self.ve_table = [[60] * 16 for _ in range(16)]

        self.build_ui()
        self.refresh_ports()

    def build_ui(self):
        # Connection frame
        conn = ttk.LabelFrame(self.root, text="Connection")
        conn.pack(fill="x", padx=10, pady=5)

        ttk.Label(conn, text="Port:").grid(row=0, column=0, padx=5)
        self.port_combo = ttk.Combobox(conn, width=20)
        self.port_combo.grid(row=0, column=1, padx=5)
        ttk.Button(conn, text="Refresh", command=self.refresh_ports).grid(row=0, column=2)
        ttk.Button(conn, text="Connect", command=self.connect).grid(row=0, column=3, padx=5)
        ttk.Button(conn, text="Disconnect", command=self.disconnect).grid(row=0, column=4)

        # Live gauges
        gauges = ttk.LabelFrame(self.root, text="Live Data")
        gauges.pack(fill="x", padx=10, pady=5)

        self.labels = {}
        for i, name in enumerate(["RPM", "TPS %", "Baro hPa", "CLT °C", "IAT °C", "Sync", "Trigger"]):
            ttk.Label(gauges, text=name + ":").grid(row=0, column=i*2, padx=5)
            lbl = ttk.Label(gauges, text="---", font=("Consolas", 12, "bold"))
            lbl.grid(row=0, column=i*2+1, padx=5)
            self.labels[name] = lbl

        # Trigger selection
        trig = ttk.LabelFrame(self.root, text="Trigger Mode")
        trig.pack(fill="x", padx=10, pady=5)
        self.trigger_var = tk.StringVar(value="12-1")
        for mode in ["12-1", "Single Tooth", "36-1", "24-1", "24-2"]:
            ttk.Radiobutton(trig, text=mode, variable=self.trigger_var, value=mode,
                            command=self.set_trigger).pack(side="left", padx=10)

        # VE Table
        ve_frame = ttk.LabelFrame(self.root, text="VE Table (TPS % × RPM) - Alpha-N")
        ve_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.ve_text = scrolledtext.ScrolledText(ve_frame, height=18, font=("Consolas", 9))
        self.ve_text.pack(fill="both", expand=True)
        self.update_ve_display()

        # Buttons
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill="x", padx=10, pady=5)
        ttk.Button(btn_frame, text="Read VE from ECU", command=self.read_ve).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Write VE to ECU", command=self.write_ve).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Save Log", command=self.save_log).pack(side="left", padx=5)

        # Log
        log_frame = ttk.LabelFrame(self.root, text="Log")
        log_frame.pack(fill="x", padx=10, pady=5)
        self.log = scrolledtext.ScrolledText(log_frame, height=6)
        self.log.pack(fill="x")

    def refresh_ports(self):
        ports = [p.device for p in serial.tools.list_ports.comports()]
        self.port_combo['values'] = ports
        if ports:
            self.port_combo.current(0)

    def connect(self):
        port = self.port_combo.get()
        if not port:
            messagebox.showerror("Error", "Select a port")
            return
        try:
            self.ser = serial.Serial(port, 115200, timeout=0.5)
            self.log_insert(f"Connected to {port}")
            threading.Thread(target=self.read_loop, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Connection failed", str(e))

    def disconnect(self):
        if self.ser:
            self.ser.close()
            self.ser = None
            self.log_insert("Disconnected")

    def read_loop(self):
        while self.running and self.ser and self.ser.is_open:
            try:
                line = self.ser.readline().decode(errors='ignore').strip()
                if line.startswith("RPM:"):
                    self.parse_status(line)
                elif line:
                    self.log_insert(line)
            except:
                pass
            time.sleep(0.05)

    def parse_status(self, line):
        # RPM:1234,TPS:450,BARO:1013,CLT:80,IAT:25,SYNC:1,TRIG:0
        try:
            parts = dict(p.split(":") for p in line.split(","))
            self.labels["RPM"].config(text=parts.get("RPM", "---"))
            tps = int(parts.get("TPS", 0)) / 10.0
            self.labels["TPS %"].config(text=f"{tps:.1f}")
            self.labels["Baro hPa"].config(text=parts.get("BARO", "---"))
            self.labels["CLT °C"].config(text=parts.get("CLT", "---"))
            self.labels["IAT °C"].config(text=parts.get("IAT", "---"))
            self.labels["Sync"].config(text="YES" if parts.get("SYNC") == "1" else "NO")
            trig_map = {"0": "12-1", "1": "Single", "2": "36-1", "3": "24-1", "4": "24-2"}
            self.labels["Trigger"].config(text=trig_map.get(parts.get("TRIG"), "?"))
        except:
            pass

    def set_trigger(self):
        if not self.ser:
            return
        mode_map = {"12-1": "0", "Single Tooth": "1", "36-1": "2", "24-1": "3", "24-2": "4"}
        cmd = "T" + mode_map[self.trigger_var.get()]
        self.ser.write(cmd.encode())
        self.log_insert(f"Set trigger to {self.trigger_var.get()}")

    def update_ve_display(self):
        self.ve_text.delete(1.0, tk.END)
        header = "TPS\\RPM " + " ".join(f"{i*500:4d}" for i in range(16)) + "\n"
        self.ve_text.insert(tk.END, header)
        for r, row in enumerate(self.ve_table):
            line = f"{r*6:3d}%    " + " ".join(f"{v:4d}" for v in row) + "\n"
            self.ve_text.insert(tk.END, line)

    def read_ve(self):
        self.log_insert("Read VE (protocol placeholder - implement binary transfer)")

    def write_ve(self):
        self.log_insert("Write VE (protocol placeholder)")

    def save_log(self):
        self.log_insert("Log saved (placeholder)")

    def log_insert(self, msg):
        self.log.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {msg}\n")
        self.log.see(tk.END)

    def on_close(self):
        self.running = False
        self.disconnect()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = StrixOneTuner(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
