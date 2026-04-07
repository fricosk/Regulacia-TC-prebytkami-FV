import requests

API_TOKEN = "j2m1svhomy55p5jw90epj8pj701js41b"
BASE_URL = "https://openapi.growatt.com/v1"
PLANT_LIST_URL = f"{BASE_URL}/plant/list"

headers = {
    "token": API_TOKEN,
    "Content-Type": "application/json",
}

response = requests.get(PLANT_LIST_URL, headers=headers)
data = response.json()

if data["error_code"] == 0:
    plants = data["data"]["plants"]
    for plant in plants:
        print(f"🌞 Názov elektrárne: {plant['name']}")
        print(f"   ID elektrárne: {plant['plant_id']}")
        print(f"   Umiestnenie: {plant['city']}, {plant['country']}")
        print(f"   Momentálny výkon: {plant['current_power']} W")
        print(f"   Ceklová výroba: {plant['total_energy']} kWh")
        print(f"   Inštalovaný výkon: {plant['peak_power']} kW\n")
else:
    print("❌ Chyba pri načítaní plant listu:", data["error_msg"])