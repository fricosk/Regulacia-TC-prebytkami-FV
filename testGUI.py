import requests
import threading
import time
import tkinter as tk
from tkinter import messagebox


# -------------------
# HA klient
# -------------------
class HomeAssistantClient:
    def __init__(self, base_url, token):
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    def ziskaj_stav(self, entity_id):
        url = f"{self.base_url}/api/states/{entity_id}"

        try:
            resp = requests.get(url, headers=self.headers, timeout=10)
            resp.raise_for_status()
            return resp.json()

        except requests.exceptions.Timeout:
            print("Timeout chyba")

        except requests.exceptions.ConnectionError:
            print("Chyba pripojenia")

        except Exception as e:
            print("Iná chyba:", e)

        return None


# -------------------
# GUI aplikácia
# -------------------
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Monitoring FVE")
        self.root.geometry("350x200")

        # HA nastavenia
        self.client = HomeAssistantClient(
            "http://192.168.2.183:8123",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJmMjU2ZTZiNzFlM2M0NGQ3OTAxMGQ4NWQzMGU1ZDliZCIsImlhdCI6MTc3NDQyNTQ4MywiZXhwIjoyMDg5Nzg1NDgzfQ.uVUUFm4hJpI26JEqMBTY6IhjVqMT3yzITl0a9faphpo"
        )

        self.running = False  # riadi cyklus

        # -------- GUI prvky --------
        self.label_vykon = tk.Label(root, text="Výkon: --- W", font=("Arial", 14))
        self.label_vykon.pack(pady=10)

        self.label_energia = tk.Label(root, text="Energia: --- kWh", font=("Arial", 14))
        self.label_energia.pack(pady=10)

        self.btn_start = tk.Button(root, text="Start", command=self.start)
        self.btn_start.pack(pady=5)

        self.btn_stop = tk.Button(root, text="Stop", command=self.stop)
        self.btn_stop.pack(pady=5)

    # -------------------
    # Štart merania
    # -------------------
    def start(self):
        if not self.running:
            self.running = True
            threading.Thread(target=self.loop, daemon=True).start()

    # -------------------
    # Stop merania
    # -------------------
    def stop(self):
        self.running = False

    # -------------------
    # Hlavný cyklus
    # -------------------
    def loop(self):
        while self.running:
            try:
                vykon_data = self.client.ziskaj_stav("sensor.doma_plot_total_vystupny_vykon")
                energia_data = self.client.ziskaj_stav("sensor.doma_plot_total_energia_dnes")

                vykon = float(vykon_data.get("state", 0)) * 1000 if vykon_data else 0
                energia = float(energia_data.get("state", 0)) if energia_data else 0

            except ValueError:
                vykon = 0
                energia = 0

            except AttributeError:
                vykon = 0
                energia = 0

            # aktualizácia GUI (musí ísť cez main thread)
            self.root.after(0, self.update_labels, vykon, energia)

            time.sleep(5)  # obnovovanie každých 5 sekúnd

    # -------------------
    # Aktualizácia GUI
    # -------------------
    def update_labels(self, vykon, energia):
        self.label_vykon.config(text=f"Výkon: {vykon:.1f} W")
        self.label_energia.config(text=f"Energia: {energia:.2f} kWh")


# -------------------
# Spustenie aplikácie
# -------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()