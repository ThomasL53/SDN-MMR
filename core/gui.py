import tkinter as tk
from tkinter import messagebox, simpledialog
import subprocess

class Application(tk.Tk):
    def __init__(self):
        super().__init__()

        self.intf = self.get_interface_name()
        self.latence_ms = tk.DoubleVar(value=0)
        self.perte_pct = tk.DoubleVar(value=0)
        self.bitrate_kbps = tk.DoubleVar(value=1000)  # Default bitrate set to 1000 Kbps

        self.create_widgets()

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        self.latence_ms_scale = tk.Scale(self, label="Latence (ms)", variable=self.latence_ms, from_=0, to=500, resolution=10)
        self.latence_ms_scale.pack(padx=10, pady=10, fill='x')

        self.perte_pct_scale = tk.Scale(self, label="Taux de perte %", variable=self.perte_pct, from_=0, to=100, resolution=1)
        self.perte_pct_scale.pack(padx=10, pady=10, fill='x')

        self.bitrate_kbps_scale = tk.Scale(self, label="Débit (Kbps)", variable=self.bitrate_kbps, from_=30, to=300, resolution=100)
        self.bitrate_kbps_scale.pack(padx=10, pady=10, fill='x')

        self.apply_button = tk.Button(self, text="Appliquer les paramètres", command=self.apply_settings)
        self.apply_button.pack(pady=10)

    def apply_settings(self):
        latence_ms = self.latence_ms.get()
        perte_pct = self.perte_pct.get()
        bitrate_kbps = self.bitrate_kbps.get()

        subprocess.run(f"sudo tc qdisc del dev {self.intf} root", shell=True)
        subprocess.run(f"sudo tc qdisc add dev {self.intf} root netem delay {latence_ms}ms loss {perte_pct}% rate {bitrate_kbps}kbit", shell=True)

        print(f"Paramètres appliqués - Latence: {latence_ms}ms, Taux de perte: {perte_pct}%, Débit: {bitrate_kbps} Kbps")

    def on_closing(self):
        if messagebox.askokcancel("Quitter", "La fermeture de cette fenêtre entraînera l'arrêt des perturbations"):
            subprocess.run(f"sudo tc qdisc del dev {self.intf} root", shell=True)
            self.destroy()

    def get_interface_name(self):
        intf_name = simpledialog.askstring("Nom de l'interface", "Veuillez entrer le nom de l'interface sur laquelle agir:")
        return intf_name

if __name__ == "__main__":
    app = Application()
    app.title("Perturbation du lien avec tc netem")
    app.geometry("400x400")
    app.mainloop()