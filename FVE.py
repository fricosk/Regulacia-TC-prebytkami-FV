import requests
import time

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
            data = resp.json()
            return data
        except Exception as e:
            print(f"Chyba pri stahu {entity_id}: {e}")
            return None

# -------------------
# HLAVNÝ PROGRAM
# -------------------

HA_URL = "http://192.168.2.183:8123"           # zmeň na svoju HA URL
HA_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJmMjU2ZTZiNzFlM2M0NGQ3OTAxMGQ4NWQzMGU1ZDliZCIsImlhdCI6MTc3NDQyNTQ4MywiZXhwIjoyMDg5Nzg1NDgzfQ.uVUUFm4hJpI26JEqMBTY6IhjVqMT3yzITl0a9faphpo" # zmeň na svoj Long-Lived Token

client = HomeAssistantClient(HA_URL, HA_TOKEN)

# statický zoznam Growatt elektrární (výkon + denná energia)
growatt_entities = [
    {"nazov": "Moja FVE", "vykon_id": "sensor.doma_plot_total_vystupny_vykon",
     "energia_id": "sensor.doma_plot_total_energia_dnes"}
]

print("\n--- LIVE VÝPIS ELEKTRÁRNE (Home Assistant) ---")
print(f"{'Názov':20} | {'Výkon':10} | {'Energia':10}")
print("-" * 50)

INTERVAL = 60  # sekundy medzi meraniami

try:
    while True:
        for e in growatt_entities:
            # výkon
            vykon_data = client.ziskaj_stav(e["vykon_id"])
            vykon = float(vykon_data.get("state", 0)) *1000 if vykon_data else 0

            # energia
            energia_data = client.ziskaj_stav(e["energia_id"])
            energia = float(energia_data.get("state", 0)) if energia_data else 0

            # výpis
            print(f"{e['nazov']:20} | {vykon:6.1f} W | {energia:6.2f} kWh")

        print("-" * 50)
        time.sleep(INTERVAL)

except KeyboardInterrupt:
    print("\n🔴 Ukončené používateľom")