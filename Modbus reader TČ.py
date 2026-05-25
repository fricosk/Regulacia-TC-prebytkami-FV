from pymodbus.client import ModbusTcpClient

# =========================
# CONFIG
# =========================
IP = "192.168.2.186"
PORT = 5000

client = ModbusTcpClient(IP, port=PORT)

# =========================
# WRITE REGISTRE (2000h blok)
# =========================
WRITE_REGISTERS = {
    8192: ("Počet pripojených jednotiek", "Počet aktívnych riadiacich jednotiek v systéme"),
    8193: ("Nastavená teplota kúrenia", "Žiadaná teplota vykurovania"),
    8194: ("Nastavená teplota TÚV", "Žiadaná teplota teplej úžitkovej vody"),
    8195: ("Nastavená teplota chladenia", "Žiadaná teplota chladenia"),
    8196: ("Prevádzkový režim", "Výber režimu (kúrenie/chladenie/auto)"),
    8197: ("Korekcia teploty zásobníka", "Offset pre meranie zásobníka"),
    8198: ("Rozdiel pre reštart kompresora", "Hysterézia pre opätovné spustenie"),
    8199: ("Výstupná teplota vody", "Cieľová výstupná teplota"),
    8200: ("Horný limit teploty", "Maximálna povolená teplota"),
    8201: ("Zapnutie elektrického dohrevu", "Teplota aktivácie backup ohrevu"),
    8202: ("Teplota vratnej vody", "Meraná vratná teplota systému"),
    8203: ("Teplota dopúšťanej vody", "Teplota dopúšťania systému"),
    8204: ("Nastavený prúd", "Limit prúdu systému"),
    8205: ("Teplota ventilátora", "Riadenie ventilátora podľa teploty"),
    8206: ("Cyklus odmrazovania", "Interval defrost cyklu"),
    8207: ("Začiatok odmrazovania", "Teplota spustenia defrostu"),
    8208: ("Čas odmrazovania", "Maximálny čas defrostu"),
    8209: ("Koniec odmrazovania", "Teplota ukončenia defrostu"),
    8210: ("Rozdiel odmrazovania 1", "Prvý diferenčný limit defrostu"),
    8211: ("Okolitá teplota defrost", "Vonkajšia teplota pre defrost logiku"),
    8212: ("Rozdiel odmrazovania 2", "Druhý diferenčný limit defrostu"),
    8213: ("Expanzný ventil cyklus", "Riadenie expanzného ventilu"),
    8214: ("Prehriatie 1", "Superheat prvý stupeň"),
    8215: ("Teplota výtlaku EV", "Teplota pri otváraní ventilu"),
    8216: ("EV odmrazovanie", "Otvorenie ventilu počas defrostu"),
    8217: ("Min EV otvorenie", "Minimálna pozícia ventilu"),
    8218: ("Kompenzácia prehriatia", "Korekcia superheat"),
    8219: ("Entalpický cyklus", "Riadenie entalpického ventilu"),
    8220: ("Entalpické prehriatie", "Superheat entalpického okruhu"),
    8221: ("Okolitá teplota entalpie", "Teplota pre entalpický ventil"),
    8222: ("Min entalpický ventil", "Min otvorenie entalpického ventilu"),
    8223: ("Počiatočné otvorenie EV", "Start pozícia ventilu"),
    8224: ("Rozdiel výtlaku", "Delta výtlačnej teploty"),
    8225: ("Nútené otvorenie EV", "Force open ventil"),
    8226: ("EV po odmrazovaní", "Pozícia po defroste"),
    8227: ("Režim ventilátora", "Rýchlosť ventilátora"),
    8228: ("Prehriatie 2", "Druhý stupeň superheat"),
    8229: ("Prehriatie chladenia", "Superheat v cooling režime"),
    8230: ("Min EV 1", "Min otvorenie ventil 1"),
    8231: ("Min EV 2", "Min otvorenie ventil 2"),
    8232: ("Min EV 3", "Min otvorenie ventil 3"),
    8233: ("Min EV 4", "Min otvorenie ventil 4"),
    8234: ("Min EV 5", "Min otvorenie ventil 5"),
    8235: ("Režim čerpadla", "Riadenie obehového čerpadla"),
    8236: ("Režim dohrev", "Elektrický dohrev logika"),
    8237: ("Teplota dohrev", "Aktivačná teplota dohrev"),
    8238: ("Oneskorenie dohrev", "Delay pre dohrev"),
    8239: ("Ventil vstrekovania", "Riadenie vstrekovacieho ventilu"),
    8240: ("Ochrana výtlaku", "High discharge protection"),
    8241: ("Oneskorenie nízky tlak", "Low pressure delay"),
    8242: ("Korekcia zásobníka", "Negatívna korekcia"),
    8243: ("Cirkulačný rozdiel", "Delta cirkulácie"),
    8244: ("Min EV 6", "Min otvorenie ventil 6"),
    8245: ("High pressure limit", "Max tlak limit"),
    8246: ("Low pressure limit", "Min tlak limit"),
    8247: ("Chladivo tabuľka", "Typ chladiva"),
    8248: ("Kompenzácia vlastností", "Tabuľková korekcia"),
    8249: ("Časová značka", "System timestamp"),
    8250: ("ON hodina", "Čas zapnutia hodina"),
    8251: ("ON minúta", "Čas zapnutia minúta"),
    8252: ("OFF hodina", "Čas vypnutia hodina"),
    8253: ("OFF minúta", "Čas vypnutia minúta"),
    8266: ("Min teplota", "Dolný limit nastavenia"),
    8272: ("ID panela", "Identifikácia zariadenia"),
    8273: ("Lock/Unlock", "Diaľkové zamknutie"),
    8274: ("Číslo panela", "Panel ID číslo"),
}

# =========================
# READ REGISTRE (4000h blok)
# =========================
READ_REGISTERS = {
    16384: ("Model dosky", "Identifikácia hlavnej dosky"),
    16385: ("Stav výstupov 1", "Digitálne výstupy stav"),
    16386: ("Prietok 1", "Meranie prietoku"),
    16387: ("Prietok 2", "Meranie prietoku"),
    16388: ("Prietok 3", "Meranie prietoku"),
    16389: ("Prietok 4", "Meranie prietoku"),
    16390: ("Chybový kód", "Aktuálna chyba systému"),
    16391: ("Vonkajšia teplota", "Outdoor sensor"),
    16392: ("Vratná voda", "Return temperature"),
    16393: ("Stav výstupov 2", "Druhý blok výstupov"),
    16394: ("Teplota zásobníka", "DHW tank temperature"),
    16395: ("Výstup voda 2", "Second outlet temp"),
    16396: ("Výstup voda 1", "Main outlet temp"),
    16397: ("Sanie 1", "Suction compressor"),
    16398: ("Sanie 2", "Suction compressor"),
    16399: ("Sanie 3", "Suction compressor"),
    16400: ("Sanie 4", "Suction compressor"),
    16401: ("Výtlak 1", "Discharge temperature"),
    16402: ("Výtlak 2", "Discharge temperature"),
    16403: ("Výtlak 3", "Discharge temperature"),
    16404: ("Výtlak 4", "Discharge temperature"),
    16405: ("Výmenník 1", "Heat exchanger temp"),
    16406: ("Výmenník 2", "Heat exchanger temp"),
    16407: ("Výmenník 3", "Heat exchanger temp"),
    16408: ("Výmenník 4", "Heat exchanger temp"),
    16409: ("EV hlavný 1", "Expansion valve opening"),
    16410: ("EV hlavný 2", "Expansion valve opening"),
    16411: ("EV hlavný 3", "Expansion valve opening"),
    16412: ("EV hlavný 4", "Expansion valve opening"),
    16413: ("Prúd 1", "Compressor current"),
    16414: ("Prúd 2", "Compressor current"),
    16415: ("Prúd 3", "Compressor current"),
    16416: ("Prúd 4", "Compressor current"),
    16417: ("Entalpia 1", "Entalpic valve"),
    16418: ("Entalpia 2", "Entalpic valve"),
    16419: ("Entalpia 3", "Entalpic valve"),
    16420: ("Entalpia 4", "Entalpic valve"),
    16421: ("Medzichladič IN 1", "Intercooler input"),
    16422: ("Medzichladič IN 2", "Intercooler input"),
    16423: ("Medzichladič IN 3", "Intercooler input"),
    16424: ("Medzichladič IN 4", "Intercooler input"),
    16425: ("Medzichladič OUT 1", "Intercooler output"),
    16426: ("Medzichladič OUT 2", "Intercooler output"),
    16427: ("Medzichladič OUT 3", "Intercooler output"),
    16428: ("Medzichladič OUT 4", "Intercooler output"),
    16429: ("Dosky", "Počet pripojených dosiek"),
    16430: ("Bity 1", "Status flags"),
    16431: ("Bity 2", "Status flags"),
    16432: ("Bity 3", "Status flags"),
    16433: ("Bity 4", "Status flags"),
    16434: ("Bity 5", "Status flags"),
    16435: ("Bity 6", "Status flags"),
    16436: ("Bity 7", "Status flags"),
}

# =========================
def to_signed(v):
    if v is None:
        return None
    if v > 32767:
        v -= 65536
    return v

def read(addr):
    r = client.read_holding_registers(addr, 1)
    if r.isError():
        return None
    return to_signed(r.registers[0])

def print_all():
    print("\n" + "="*70)
    print("TEPELNÉ ČERPADLO - FULL MAP READ")
    print("="*70)

    print("\n🔧 WRITE REGISTRE (2000h)")
    for addr, (name, desc) in WRITE_REGISTERS.items():
        val = read(addr)
        print(f"{addr:5} | {name:30} | {desc:45} = {val}")

    print("\n📊 READ REGISTRE (4000h)")
    for addr, (name, desc) in READ_REGISTERS.items():
        val = read(addr)
        print(f"{addr:5} | {name:30} | {desc:45} = {val}")

def main():
    if not client.connect():
        print("❌ Modbus nepripojený")
        return

    print("✅ Pripojené")
    print("➡ ENTER = refresh, CTRL+C = exit")

    try:
        while True:
            input("\n🔄 Stlač ENTER pre načítanie...")
            print_all()

    except KeyboardInterrupt:
        print("\nUkončené")

    finally:
        client.close()

if __name__ == "__main__":
    main()