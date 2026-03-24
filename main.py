import requests


# -------------------
# TRIEDA - ELEKTRÁREŇ (OBJEKT)
# -------------------
class Elektraren:
    """
    Trieda Elektraren reprezentuje jednu solárnu elektráreň.
    Obsahuje základné informácie (atribúty) a metódy na prácu s nimi.
    """

    def __init__(self, nazov, plant_id):
        # VLASTNOSTI (atribúty objektu)
        self.nazov = nazov              # názov elektrárne
        self.plant_id = plant_id        # identifikátor elektrárne
        self.aktualny_vykon = 0         # aktuálny výkon (W)
        self.denna_energia = 0          # vyrobená energia za deň (kWh)

    # METÓDA - nastaví aktuálny výkon
    def nastav_vykon(self, vykon):
        """
        Nastaví aktuálny výkon elektrárne.
        :param vykon: výkon vo wattoch
        """
        self.aktualny_vykon = vykon

    # METÓDA - nastaví dennú energiu
    def nastav_energiu(self, energia):
        """
        Nastaví dennú vyrobenú energiu.
        :param energia: energia v kWh
        """
        self.denna_energia = energia

    # METÓDA - zobrazí informácie o elektrárni
    def zobraz_info(self):
        """
        Vypíše všetky dôležité informácie o elektrárni.
        """
        print(f"Elektráreň: {self.nazov}")
        print(f"ID: {self.plant_id}")
        print(f"Aktuálny výkon: {self.aktualny_vykon} W")
        print(f"Denná energia: {self.denna_energia} kWh")


# -------------------
# TRIEDA - API KLIENT
# -------------------
class GrowattClient:
    """
    Trieda GrowattClient zabezpečuje komunikáciu so serverom Growatt.
    Slúži na prihlásenie a získavanie dát z API.
    """

    def __init__(self, email, heslo):
        # prihlasovacie údaje
        self.email = email
        self.heslo = heslo

        # vytvorenie session (uchováva cookies)
        self.session = requests.Session()

    # METÓDA - prihlásenie do systému
    def prihlasenie(self):
        """
        Pokúsi sa prihlásiť na server Growatt.
        :return: True ak úspech, inak False
        """
        url = "https://server.growatt.com/login"

        data = {
            "account": self.email,
            "password": self.heslo
        }

        response = self.session.post(url, data=data)

        # kontrola úspešnosti prihlásenia
        if response.status_code == 200 and '"result":1' in response.text:
            print("✅ Prihlásenie úspešné")
            return True
        else:
            print("❌ Prihlásenie zlyhalo")
            return False

    # METÓDA - získanie aktuálneho výkonu
    def ziskaj_aktualny_vykon(self, plant_id):
        """
        Získa aktuálny výkon elektrárne.
        :param plant_id: ID elektrárne
        :return: výkon (W)
        """
        url = "https://server.growatt.com/panel/getMAXTotalData"

        data = {
            "plantId": plant_id,
            "type": "1"
        }

        response = self.session.post(url, data=data)

        if response.status_code == 200:
            try:
                json_data = response.json()
                return json_data.get("power", 0)
            except:
                return 0
        return 0

    # METÓDA - získanie dennej energie
    def ziskaj_dennu_energiu(self, plant_id, datum):
        """
        Získa množstvo vyrobenej energie za konkrétny deň.
        :param plant_id: ID elektrárne
        :param datum: dátum (YYYY-MM-DD)
        :return: energia (kWh)
        """
        url = "https://server.growatt.com/panel/getMAXDayChart"

        data = {
            "plantId": plant_id,
            "date": datum
        }

        response = self.session.post(url, data=data)

        if response.status_code == 200:
            try:
                json_data = response.json()
                return json_data.get("energy", 0)
            except:
                return 0
        return 0


# -------------------
# HLAVNÝ PROGRAM
# -------------------

# prihlasovacie údaje (pre školský projekt - v praxi by mali byť bezpečne uložené)
email = "fricosk"
heslo = "kanur1"
plant_id = "732784"

# vytvorenie objektu elektrárne
moja_elektraren = Elektraren("Moja FVE", plant_id)

# vytvorenie klienta pre komunikáciu s API
client = GrowattClient(email, heslo)

# pokus o prihlásenie
if client.prihlasenie():

    # získanie dát zo servera
    vykon = client.ziskaj_aktualny_vykon(plant_id)
    energia = client.ziskaj_dennu_energiu(plant_id, "2026-03-18")

    # uloženie dát do objektu elektrárne
    moja_elektraren.nastav_vykon(vykon)
    moja_elektraren.nastav_energiu(energia)

    # výpis informácií
    moja_elektraren.zobraz_info()
else:
    print("Nepodarilo sa prihlásiť")