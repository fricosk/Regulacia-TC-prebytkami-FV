import requests
import time
import csv
import os
from datetime import datetime

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
            print(f"Chyba: timeout pri {entity_id}")

        except requests.exceptions.ConnectionError:
            print(f"Chyba: nemožno sa pripojiť ({entity_id})")

        except requests.exceptions.HTTPError as e:
            print(f"HTTP chyba pri {entity_id}: {e}")

        except ValueError:
            print(f"Chyba: neplatný JSON ({entity_id})")

        except Exception as e:
            print(f"Iná chyba ({entity_id}): {e}")

        return None


# -------------------
# CSV LOGOVANIE
# -------------------
def zapis_do_csv(subor, nazov, vykon, energia):
    """
    Zapíše jeden riadok do CSV súboru

    subor   - názov súboru
    nazov   - názov elektrárne
    vykon   - aktuálny výkon
    energia - denná energia
    """

    try:
        # zistíme, či súbor existuje (kvôli hlavičke)
        novy_subor = not os.path.exists(subor)

        # otvorenie súboru v režime append (pridávanie riadkov)
        with open(subor, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)

            # ak je súbor nový → zapíš hlavičku
            if novy_subor:
                writer.writerow(["čas", "názov", "výkon_W", "energia_kWh"])

            # aktuálny čas
            cas = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # zápis dát
            writer.writerow([cas, nazov, vykon, energia])

    except PermissionError:
        print("Chyba: nemáš oprávnenie zapisovať do súboru")

    except OSError as e:
        print(f"Chyba súboru: {e}")

    except Exception as e:
        print(f"Neočakávaná chyba pri zápise CSV: {e}")


# -------------------
# HLAVNÝ PROGRAM
# -------------------

HA_URL = "http://192.168.2.183:8123"
HA_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJmMjU2ZTZiNzFlM2M0NGQ3OTAxMGQ4NWQzMGU1ZDliZCIsImlhdCI6MTc3NDQyNTQ4MywiZXhwIjoyMDg5Nzg1NDgzfQ.uVUUFm4hJpI26JEqMBTY6IhjVqMT3yzITl0a9faphpo"

client = HomeAssistantClient(HA_URL, HA_TOKEN)

growatt_entities = [
    {
        "nazov": "Moja FVE",
        "vykon_id": "sensor.doma_plot_total_vystupny_vykon",
        "energia_id": "sensor.doma_plot_total_energia_dnes"
    }
]

CSV_SUBOR = "log_fve.csv"

print("\n--- LIVE VÝPIS ELEKTRÁRNE ---")
print(f"{'Názov':20} | {'Výkon':10} | {'Energia':10}")
print("-" * 50)

INTERVAL = 60

try:
    while True:
        for e in growatt_entities:

            try:
                vykon_data = client.ziskaj_stav(e["vykon_id"])
                vykon = float(vykon_data.get("state", 0)) * 1000 if vykon_data else 0

                energia_data = client.ziskaj_stav(e["energia_id"])
                energia = float(energia_data.get("state", 0)) if energia_data else 0

            except ValueError:
                print("Chyba: konverzia na číslo")
                vykon = 0
                energia = 0

            except AttributeError:
                print("Chyba: neplatné dáta")
                vykon = 0
                energia = 0

            # výpis do konzoly
            print(f"{e['nazov']:20} | {vykon:6.1f} W | {energia:6.2f} kWh")

            # 🔴 zápis do CSV
            zapis_do_csv(CSV_SUBOR, e["nazov"], vykon, energia)

        print("-" * 50)

        try:
            time.sleep(INTERVAL)
        except KeyboardInterrupt:
            raise

except KeyboardInterrupt:
    print("\n🔴 Ukončené používateľom")