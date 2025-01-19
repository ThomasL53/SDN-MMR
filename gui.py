import tkinter as tk
from tkinter import messagebox
import subprocess
import re

class Application(tk.Tk):
    def __init__(self, intf):
        super().__init__()
        
        self.intf = intf
        self.latence_ms = tk.DoubleVar(value=0)
        self.perte_pct = tk.DoubleVar(value=0)
        
        self.create_widgets()

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        self.latence_ms_scale = tk.Scale(self, label="Latence (ms)", variable=self.latence_ms, from_=0, to=500, resolution=10)
        self.latence_ms_scale.pack(padx=10, pady=10, fill='x')
        
        self.perte_pct_scale = tk.Scale(self, label="Taux de perte % ", variable=self.perte_pct, from_=0, to=100, resolution=1)
        self.perte_pct_scale.pack(padx=20, pady=20, fill='x')
        
        self.apply_button = tk.Button(self, text="Appliquer les paramètres", command=self.apply_settings)
        self.apply_button.pack(pady=10)
        
    def apply_settings(self):
        latence_ms = self.latence_ms.get()
        perte_pct = self.perte_pct.get()
        subprocess.run(f"sudo tc qdisc del dev {self.intf} root", shell=True)
        subprocess.run(f"sudo tc qdisc add dev {self.intf} root netem delay {latence_ms}ms loss {perte_pct}%", shell=True)
        print(f"Paramètres appliqués - Latence: {latence_ms}ms, taux de perte : {perte_pct}%")

    def on_closing(self):
        if messagebox.askokcancel("Quitter", "La fermeture de cette fenêtre entraînera l'arrêt des perturbations"):
            subprocess.run(f"sudo tc qdisc del dev {self.intf} root", shell=True)
            subprocess.run(f"sudo tc qdisc add dev {self.intf} root netem delay 5ms", shell=True)
            self.destroy()

def recover_itf_client():
    # Exécution de la commande pour afficher les règles Qdisc actuelles
    output = subprocess.check_output("sudo tc qdisc show", shell=True).decode('utf-8')

    output_lines = output.split('\n')

    intf_line = next((line for line in output_lines if "delay 5ms" in line),None)
    match = re.search(r"dev\s+(\S+)\s+root",intf_line )

    extracted_intf = match.group(1)
    return extracted_intf



if __name__ == "__main__":
    intf = recover_itf_client()
    app = Application(intf)
    app.title("Pertubation du lien avec tc netem")
    app.geometry("400x300")
    app.mainloop()