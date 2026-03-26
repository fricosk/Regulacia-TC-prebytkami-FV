import requests      # knižnica na HTTP komunikáciu (API volania)
import time          # časové funkcie (sleep)
import csv           # práca s CSV súbormi
import os            # práca so súbormi (existencia, cesty)
from datetime import datetime  # aktuálny dátum a čas


# -------------------
# HA klient
# -------------------
class HomeAssistantClient:
    """
    Trieda zabezpečuje komunikáciu s Home Assistant API.
    """

    def __init__(self, base_url, token):
        # odstráni prípadné "/" na konci URL
        self.base_url = base_url.rstrip("/")

        # HTTP hlavičky – autorizácia a typ dát
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    def ziskaj_stav(self, entity_id):
        """
        Načíta aktuálny stav entity zo systému Home Assistant.

        entity_id - napr. sensor.teplota

        návrat:
        - dict (JSON) pri úspechu
        - None pri chybe
        """
        # zostavenie URL pre API požiadavku
        url = f"{self.base_url}/api/states/{entity_id}"

        try:
            # odoslanie HTTP GET požiadavky
            resp = requests.get(url, headers=self.headers, timeout=10)

            # kontrola HTTP chyby (napr. 404, 401)
            resp.raise_for_status()

            # konverzia odpovede na JSON
            return resp.json()

        # -------- OŠETRENIE VÝNIMIEK --------

        except requests.exceptions.Timeout:
            # server neodpovedal v časovom limite
            print(f"Chyba: timeout pri {entity_id}")

        except requests.exceptions.ConnectionError:
            # problém so sieťou alebo serverom
            print(f"Chyba: nemožno sa pripojiť ({entity_id})")

        except requests.exceptions.HTTPError as e:
            # HTTP chyba (napr. entita neexistuje)
            print(f"HTTP chyba pri {entity_id}: {e}")

        except ValueError:
            # chyba pri parsovaní JSON
            print(f"Chyba: neplatný JSON ({entity_id})")

        except Exception as e:
            # všeobecná neočakávaná chyba
            print(f"Iná chyba ({entity_id}): {e}")

        # pri chybe vráti None
        return None


# -------------------
# CSV LOGOVANIE
# -------------------
def zapis_do_csv(subor, nazov, vykon, energia):
    """
    Zapíše jeden riadok do CSV súboru.

    subor   - názov súboru
    nazov   - názov elektrárne
    vykon   - aktuálny výkon (W)
    energia - denná energia (kWh)
    """

    try:
        # zistíme, či súbor už existuje (kvôli hlavičke)
        novy_subor = not os.path.exists(subor)

        # otvorenie súboru v režime "append" (pridávanie dát)
        # newline="" zabraňuje prázdnym riadkom vo Windows
        with open(subor, mode="a", newline="", encoding="utf-8") as f:

            writer = csv.writer(f)

            # ak je súbor nový → zapíš hlavičku
            if novy_subor:
                writer.writerow(["čas", "názov", "výkon_W", "energia_kWh"])

            # aktuálny čas vo formáte YYYY-MM-DD HH:MM:SS
            cas = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # zápis jedného riadku
            writer.writerow([cas, nazov, vykon, energia])

    # -------- OŠETRENIE VÝNIMIEK --------

    except PermissionError:
        # napr. nemáš právo zapisovať do priečinka
        print("Chyba: nemáš oprávnenie zapisovať do súboru")

    except OSError as e:
        # všeobecná chyba práce so súborom (disk, cesta...)
        print(f"Chyba súboru: {e}")

    except Exception as e:
        # neočakávaná chyba
        print(f"Neočakávaná chyba pri zápise CSV: {e}")


# -------------------
# HLAVNÝ PROGRAM
# -------------------

# URL Home Assistant servera
HA_URL = "http://192.168.2.183:8123"

# autentifikačný token (v praxi ho nezverejňovať)
HA_TOKEN = "TU_DAJ_TOKEN"

# vytvorenie klienta
client = HomeAssistantClient(HA_URL, HA_TOKEN)

# zoznam sledovaných entít
growatt_entities = [
    {
        "nazov": "Moja FVE",
        "vykon_id": "sensor.doma_plot_total_vystupny_vykon",
        "energia_id": "sensor.doma_plot_total_energia_dnes"
    }
]

# názov CSV súboru
CSV_SUBOR = "log_fve.csv"

# výpis hlavičky do konzoly
print("\n--- LIVE VÝPIS ELEKTRÁRNE ---")
print(f"{'Názov':20} | {'Výkon':10} | {'Energia':10}")
print("-" * 50)

# interval merania (sekundy)
INTERVAL = 60

try:
    # nekonečný cyklus – program beží stále
    while True:
        for e in growatt_entities:

            try:
                # -------- NAČÍTANIE VÝKONU --------
                vykon_data = client.ziskaj_stav(e["vykon_id"])

                # kontrola + konverzia na float
                # ak data neexistujú → 0
                vykon = float(vykon_data.get("state", 0)) * 1000 if vykon_data else 0

                # -------- NAČÍTANIE ENERGIE --------
                energia_data = client.ziskaj_stav(e["energia_id"])

                energia = float(energia_data.get("state", 0)) if energia_data else 0

            except ValueError:
                # napr. "unknown", "unavailable" → nedá sa konvertovať
                print("Chyba: konverzia na číslo")
                vykon = 0
                energia = 0

            except AttributeError:
                # napr. vykon_data = None → .get() neexistuje
                print("Chyba: neplatné dáta")
                vykon = 0
                energia = 0

            # -------- VÝPIS DO KONZOLY --------
            print(f"{e['nazov']:20} | {vykon:6.1f} W | {energia:6.2f} kWh")

            # -------- ZÁPIS DO CSV --------
            zapis_do_csv(CSV_SUBOR, e["nazov"], vykon, energia)

        print("-" * 50)

        try:
            # pauza medzi meraniami
            time.sleep(INTERVAL)

        except KeyboardInterrupt:
            # ak používateľ preruší počas sleep
            raise

# -------- UKONČENIE PROGRAMU --------
except KeyboardInterrupt:
    print("\n🔴 Ukončené používateľom")