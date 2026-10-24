import random
import time
import tkinter as tk
from tkinter import messagebox


geld = 20
feld = [None, None, None]
PFLANZEN = {
    "Carrot":{
        "price": 5, "sale": 10, "chance": 0.90, "stock": (1, 6),
        "growth": 40, "extra_watering": 0,
        "stem": "#27632a", "leaf1": "#48a848", "leaf2": "#55b84f",
    },
    "Tomato": {
        "price": 15, "sale": 20, "chance": 0.75, "stock": (1, 3),
        "growth": 60, "extra_watering": 1,
        "stem": "#27632a", "leaf1": "#328c39", "leaf2": "#55b84f",
    },
    "Strawberry": {
        "price": 25, "sale": 35, "chance": 0.55, "stock": (1, 3),
        "growth": 60, "extra_watering": 2,
        "stem": "#27632a", "leaf1": "#226b35", "leaf2": "#68c75e",
    },
    "Pumpkin": {
        "price": 50, "sale": 75, "chance": 0.35, "stock": (1, 2),
        "growth": 90, "extra_watering": 3,
        "stem": "#496b25", "leaf1": "#537c2b", "leaf2": "#83a83e",
    },
    "Golden Flower": {
        "price": 250, "sale": 500, "chance": 0.05, "stock": (1, 1),
        "growth": 120, "extra_watering": 3,
        "stem": "#347342", "leaf1": "#4b9b51", "leaf2": "#7fcf63",
    },
    "Dragon Fruit": {
        "price": 1000, "sale": 5000, "chance": 0.01, "stock": (1, 1),
        "growth": 180, "extra_watering": 5, "boss": True,
        "stem": "#315c35", "leaf1": "338e52", "leaf2": "#66c77a",
    },
}

preise = {name: daten["price"] for name, daten in PFLANZEN.items()}
verkaufspreise = {name: daten["sale"] for name, daten in PFLANZEN.items()}

samen_inventar = {name: 0 for name in PFLANZEN}
ernte_lager = {name: 0 for name in PFLANZEN}

shop_chancen = {name: daten["chance"] for name, daten in PFLANZEN.items()}
shop_mengen = {name: daten["stock"] for name, daten in PFLANZEN.items()}

fenster = tk.Tk()
fenster.title("My Mini Farm")
fenster.geometry("1000x760")
fenster.configure(bg="#d9edc2")

werkzeug = "Carrot"
beet_positionen = [
    (90, 220, 330, 430),
    (380, 220, 620, 430),
    (670, 220, 910, 430),
]
spielfeld = None
status_text = None
geld_text = None
tag_text = None
spielstart = 0.0
letzter_tag = 1
wetter = "Sunny"

shop_bestand = {
    name: random.randint(*shop_mengen[name]) if random.random() < chance else 0
    for name, chance in shop_chancen.items()
}
shop_reset_zeit = time.monotonic() + 300

shop_labels = {}
shop_buttons = {}
markt_labels = {}
markt_buttons = {}
inventar_buttons = {}
shop_timer_label = None


def aktualisiere_inventar():
    for name, button in inventar_buttons.items():
        button.config(
            text=f"{name} seeds: {samen_inventar[name]}",
            state="normal" if samen_inventar[name] > 0 else "disabled",
        )


def aktualisiere_shop_anzeige():
    for name, label in list(shop_labels.items()):
        try:
            label.config(
                text=f"In stock: {shop_bestand[name]}" if shop_bestand[name] > 0 else "Out of stock"
            )
            shop_buttons[name].config(
                state="normal" if shop_bestand[name] > 0 else "disabled"
            )
        except tk.TclError:
            pass

    if shop_timer_label is not None:
        try:
            restzeit = max(0, int(shop_reset_zeit - time.monotonic()))
            shop_timer_label.config(
                text=f"New stock in {restzeit // 60}:{restzeit % 60:02d}"
            )
        except tk.TclError:
            pass


def erneuere_shop(jetzt=None):
    global shop_bestand, shop_reset_zeit

    if jetzt is None:
        jetzt = time.monotonic()

    shop_bestand = {
        name: random.randint(*shop_mengen[name]) if random.random() < chance else 0
        for name, chance in shop_chancen.items()
    }
    shop_reset_zeit = jetzt + 300
    aktualisiere_shop_anzeige()


def kaufe_samen(name):
    global geld
    
    if shop_bestand[name] <= 0:
        status_text.config(text=f"{name} is out of stock.")
        return

    if geld < preise[name]:
        status_text.config(text="You don't have enough coins.")
        return

    geld -= preise[name]
    samen_inventar[name] += 1
    shop_bestand[name] -= 1

    geld_text.config(text=f"Coins: {geld}")
    status_text.config(text=f"You bought one {name} seed.")
    aktualisiere_inventar()
    aktualisiere_shop_anzeige()


def zeige_shop():
    global shop_labels, shop_buttons, shop_timer_label

    fenster_shop = tk.Toplevel(fenster)
    fenster_shop.title("Seed Shop")
    fenster_shop.geometry("360x260")
    fenster_shop.configure(bg="#d9edc2")

    shop_labels = {}
    shop_buttons = {}

    tk.Label(
        fenster_shop,
        text="Seed Shop",
        font=("Arial", 20, "bold"),
        bg="#d9edc2",
    ).pack(pady=10)

    shop_timer_label = tk.Label(
        fenster_shop,
        text="",
        font=("Arial", 11),
        bg="#d9edc2",
    )
    shop_timer_label.pack(pady=5)

    for name in preise:
        zeile = tk.Frame(fenster_shop, bg="#d9edc2")
        zeile.pack(fill="x", padx=15, pady=5)

        tk.Label(
            zeile,
            text=f"{name} - {preise[name]} coins",
            bg="#d9edc2",
            font=("Arial", 12),
        ).pack(side="left")

        shop_labels[name] = tk.Label(
            zeile,
            text="",
            bg="#d9edc2",
            font=("Arial", 10),
        )
        shop_labels[name].pack(side="left", padx=8)

        shop_buttons[name] = tk.Button(
            zeile,
            text="Buy",
            command=lambda n=name: kaufe_samen(n),
        )
        shop_buttons[name].pack(side="right")

    aktualisiere_shop_anzeige()


def aktualisiere_marktplatz():
    for name, label in list(markt_labels.items()):
        try:
            label.config(text=f"{name}: {ernte_lager[name]}")
            markt_buttons[name].config(
                state="normal" if ernte_lager[name] > 0 else "disabled"
            )
        except tk.TclError:
            pass


def verkaufe_ernte(name):
    global geld

    anzahl = ernte_lager[name]
    if anzahl == 0:
        status_text.config(text=f"You have no {name} to sell.")
        return

    einnahmen = anzahl * verkaufspreise[name]
    geld += einnahmen
    ernte_lager[name] = 0

    geld_text.config(text=f"Coins: {geld}")
    status_text.config(text=f"Sold! You earned {einnahmen} coins.")
    aktualisiere_marktplatz()


def zeige_marktplatz():
    global markt_labels, markt_buttons

    fenster_markt = tk.Toplevel(fenster)
    fenster_markt.title("Marketplace")
    fenster_markt.geometry("360x240")
    fenster_markt.configure(bg="#d9edc2")

    markt_labels = {}
    markt_buttons = {}

    tk.Label(
        fenster_markt,
        text="Marketplace",
        font=("Arial", 20, "bold"),
        bg="#d9edc2",
    ).pack(pady=10)

    for name in verkaufspreise:
        zeile = tk.Frame(fenster_markt, bg="#d9edc2")
        zeile.pack(fill="x", padx=15, pady=8)

        markt_labels[name] = tk.Label(
            zeile,
            text="",
            bg="#d9edc2",
            font=("Arial", 12),
        )
        markt_labels[name].pack(side="left")

        markt_buttons[name] = tk.Button(
            zeile,
            text=f"Sell all ({verkaufspreise[name]} coins each)",
            command=lambda n=name: verkaufe_ernte(n),
        )
        markt_buttons[name].pack(side="right")

    aktualisiere_marktplatz()


def zeige_menue():
    for widget in fenster.winfo_children():
        widget.destroy()

    menue = tk.Frame(fenster, bg="#d9edc2")
    menue.pack(expand=True, fill="both")

    tk.Label(
        menue,
        text="My Mini Farm",
        font=("Arial", 32, "bold"),
        bg="#d9edc2",
        fg="#31572c",
    ).pack(pady=(120, 20))

    tk.Label(
        menue,
        text="Plant, water, and harvest your own crops!",
        font=("Arial", 16),
        bg="#d9edc2",
        fg="#31572c",
    ).pack(pady=10)

    tk.Button(
        menue,
        text="Play",
        font=("Arial", 20, "bold"),
        width=16,
        command=zeige_spiel,
        bg="#70a34b",
        fg="white",
        activebackground="#527d38",
    ).pack(pady=30)

    tk.Button(
        menue,
        text="Quit",
        font=("Arial", 14),
        width=16,
        command=fenster.destroy,
    ).pack(pady=5)


def waehle_werkzeug(neues_werkzeug):
    global werkzeug
    werkzeug = neues_werkzeug

    if neues_werkzeug == "Water":
        status_text.config(
            text="Watering can selected: water all three blue spots."
        )
    elif neues_werkzeug == "Harvest":
        status_text.config(
            text="Harvest selected: click a ripe crop."
        )
    else:
        status_text.config(
            text=f"{neues_werkzeug} seeds selected: click an empty plot."
        )

    zeichne_farm()


def zeichne_farm():
    spielfeld.delete("all")

    #Himmel und Wiese
    # Hintergrundfarbe je nach Wetter
    if wetter == "Rain":
        himmelfarbe = "#657b89"
        wiesenfarbe = "#547a43"
    elif wetter == "Cloudy":
        himmelfarbe = "#93a2a7"
        wiesenfarbe = "#68925b"
    else:
        himmelfarbe = "#9bd6f2"
        wiesenfarbe = "#72b85a"

    spielfeld.create_rectangle(
        0, 0, 1000, 520,
        fill=himmelfarbe,
        outline="",
    )
    spielfeld.create_oval(
        -100, 280, 1100, 700,
        fill=wiesenfarbe,
        outline="",
    )
    spielfeld.create_rectangle(
        0, 350, 1000, 520,
        fill=wiesenfarbe,
        outline="",
    )

    # Sun appears only in sunny weather
    if wetter == "Sunny":
        spielfeld.create_oval(
            850, 25, 925, 100,
            fill="#ffdb58",
            outline="",
        )

    # Darker clouds appear during cloudy weather and rain
    if wetter == "Rain":
        wolkenfarbe = "#59666d"
    elif wetter == "Cloudy":
        wolkenfarbe = "#77848a"
    else:
        wolkenfarbe = "white"


    for x, y in [(270, 55), (520, 85)]:
        spielfeld.create_oval(
            x, y, x + 55, y + 30,
            fill=wolkenfarbe,
            outline="",
        )
        spielfeld.create_oval(
            x + 25, y - 15, x + 80, y + 30,
            fill=wolkenfarbe,
            outline="",
        )
        spielfeld.create_oval(
            x + 55, y, x + 100, y + 30,
            fill=wolkenfarbe,
            outline="",
        )

    # Moving raindrops
    if wetter == "Rain":
        regen_versatz = int(time.monotonic() * 120) % 70

        for x in range(30, 980, 75):
            for basis_y in range(-50, 520, 90):
                regen_y = (basis_y + regen_versatz) % 550
                spielfeld.create_line(
                    x,
                    regen_y,
                    x - 8,
                    regen_y + 16,
                    fill="#d8f0f7",
                    width=2,
                )

    # Baum rechts neben der Scheune
    spielfeld.create_rectangle(830, 130, 850, 200, fill="#795548", outline="")
    spielfeld.create_oval(795, 95, 885, 165, fill="#388e3c", outline="")

    # Scheune
    spielfeld.create_rectangle(
        35, 110, 180, 245, fill="#c85b45", outline="#713c32", width=4
    )
    spielfeld.create_polygon(
        20, 115, 108, 50, 195, 115,
        fill="#713c32",
        outline="#713c32",
    )
    spielfeld.create_rectangle(
        85, 175, 130, 245, fill="#70452f", outline="#f3d7a4", width=3
    )

    # Weg
    spielfeld.create_polygon(
        430, 520, 570, 520, 545, 405, 455, 405,
        fill="#c9a978",
        outline="",
    )

    #Zäune
    for x in range(220, 800, 35):
        spielfeld.create_line(x, 175, x, 215, fill="#795548", width=4)
    spielfeld.create_line(215, 185, 805, 185, fill="#795548", width=4)
    spielfeld.create_line(215, 202, 805, 202, fill="#795548", width=4)
     
     # Beete und Pflanzen
    for nummer, (x1, y1, x2, y2) in enumerate(beet_positionen):
        spielfeld.create_rectangle(
            x1, y1, x2, y2,
            fill="#704523",
            outline="#9a673a",
            width=12,
        )
    
        for furche_y in range(y1 + 105, y2 - 10, 18):
            spielfeld.create_line(
                x1 + 18,
                furche_y,
                x2 - 18,
                furche_y,
                fill="#9a673a",
                width=3,
            )

        pflanze = feld[nummer]

        if pflanze is None:
            spielfeld.create_text(
                (x1 + x2) / 2,
                y1 + 45,
                text="Empty plot",
                font=("Arial", 16, "bold"),
                fill="#f5deb3",
            )
            continue

        name = pflanze["pflanze"]
        daten = PFLANZEN[name]
        dauer = daten["growth"]

        if pflanze["startzeit"] is None:
            wachszum = 0.15
            fortschritt = 0
            anzeige = "Not watered yet"
        else:
            wachstum = min(1, pflanze["wachstum"] / dauer)
            fortschritt = pflanze["wachstum"] / dauer

            if pflanze["warte_auf_wasser"]:
                if pflanze["boss"]:
                    sekunden = max(
                        0,
                        int(pflanze["giess_deadline"] - time.monotonic())
                    )
                    anzeige = f"WATER NOW! {sekunden} seconds left!"
                else:
                    anzeige = "Needs water — growth paused"
            elif pflanze["wachstum"] >= dauer:
                anzeige = "Ready to harvest!"
            else:
                restzeit = dauer - pflanze["wachstum"]
                anzeige = f"Growing: {restzeit:04.1f} seconds left"

        stamm_hoehe = 15 + int(wachstum * 45)
        pflanzen_basis_y = y1 + 150

        for pflanzen_x in (x1 + 65, x1 + 120, x1 + 175):
            stamm_oben = pflanzen_basis_y - stamm_hoehe
            blatt_groesse = 7 + int(wachstum * 12)

            spielfeld.create_line(
                pflanzen_x,
                pflanzen_basis_y,
                pflanzen_x,
                stamm_oben,
                fill=daten["stem"],
                width=6,
            )
            spielfeld.create_oval(
                pflanzen_x - blatt_groesse * 2,
                stamm_oben + 8,
                pflanzen_x,
                stamm_oben + 20,
                fill=daten["leaf1"],
                outline="",
            )
            spielfeld.create_oval(
                pflanzen_x,
                stamm_oben,
                pflanzen_x + blatt_groesse * 2,
                stamm_oben + 14,
                fill=daten["leaf2"],
                outline="",
            )

        spielfeld.create_text(
            (x1 + x2) / 2,
            y1 + 35,
            text=name,
            font=("Arial", 16, "bold"),
            fill="white",
        )

        spielfeld.create_text(
            (x1 + x2) / 2,
            y1 + 65,
            text=anzeige,
            font=("Arial", 11, "bold"),
            fill="white",
        )

        if pflanze["wachstum"] >= dauer:
            for frucht_x in (x1 + 65, x1 + 120, x1 + 175):
                frucht_y = y1 + 137

                if name =="Carrot":
                    spielfeld.create_polygon(
                        frucht_x - 9, frucht_y - 13,
                        frucht_x + 9, frucht_y - 13,
                        frucht_x, frucht_y + 15,
                        fill="#ff8c00",
                        outline="#bd5e00",
                    )
                elif name == "Tomato":
                    spielfeld.create_oval(
                        frucht_x - 12, frucht_y - 12,
                        frucht_x + 12, frucht_y + 12,
                        fill="#e53935",
                        outline="#a51d25"
                    )
                elif name == "Strawberry":
                    spielfeld.create_polygon(
                        frucht_x - 12, frucht_y - 7,
                        frucht_x + 12, frucht_y - 7,
                        frucht_x + 8, frucht_y + 10,
                        frucht_x, frucht_y + 16,
                        frucht_x - 8, frucht_y + 10,
                        fill="#f22654",
                        outline="#9f1239",
                    )
                    spielfeld.create_oval(
                        frucht_x - 8, frucht_y - 13,
                        frucht_x + 8, frucht_y - 5,
                        fill="#58a832",
                        outline="",
                    )
                elif name == "Pumpkin":
                    spielfeld.create_oval(
                        frucht_x - 15, frucht_y - 12,
                        frucht_x + 15, frucht_y + 13,
                        fill="#f28c28",
                        outline="#a95116",
                        width=2,
                    )
                    spielfeld.create_line(
                        frucht_x, frucht_y - 12,
                        frucht_x, frucht_y + 12,
                        fill="#a95116",
                        width=2,
                    )
                elif name == "Golden Flower":
                    for dx, dy in [(0, -10), (10, 0), (-10 ,0)]:
                        spielfeld.create_oval(
                            frucht_x + dx - 7, frucht_y + dy - 7,
                            frucht_x + dx + 7, frucht_y + dy + 7,
                            fill="#ffd700",
                            outline="#d89b00",
                        )
                    spielfeld.create_oval(
                        frucht_x - 5, frucht_y -5,
                        frucht_x + 5, frucht_y +5,
                        fill="#7a4b20",
                        outline="",
                    )
                else:
                    spielfeld.create_oval(
                        frucht_x - 14, frucht_y - 10,
                        frucht_x + 14, frucht_y + 10,
                        fill="#d927a9",
                        outline="#75136f",
                        width=2,
                    )
                    for dx in (-10, 0, 10):
                        spielfeld.create_polygon(
                            frucht_x + dx - 3, frucht_y - 8,
                            frucht_x + dx + 3, frucht_y - 15,
                            frucht_x + dx + 5, frucht_y - 6,
                            fill="#58a832",
                            outline="",
                        )

        balken_rechts = x2 - 40
        balken_y = y1 + 190

        spielfeld.create_rectangle(
            balken_links,
            balken_y,
            balken_rechts,
            balken_y + 10,
            fill="#eeeeee",
            outline="white",
        )
        spielfeld.create_rectangle(
            balken_links,
            balken_y,
            balken_links + (balken_rechts - balken_links) * fortschritt,
            balken_y + 10,
            fill="#42a85a",
            outline="",
        )

        # Drei Stellen, die mit mir der Gießkanne bewässert werden müssen
        for stelle, ist_bewaessert in enumerate(pflanze["gegossen"]):
            punkt_x = x1 + 55 + stelle * 65
            punkt_y = y1 + 165
            farbe = "#42c5f5" if not ist_bewaessert else "#b8eaff"

            spielfeld.create_oval(
                punkt_x - 13,
                punkt_y - 13,
                punkt_x + 13,
                punkt_y + 13,
                fill=farbe,
                outline="white",
                width=2,
            )

    spielfeld.create_text(
        960,
        445,
        text="Tool",
        font=("Arial", 11, "bold"),
        fill="#31572c",
    )

    if werkzeug == "Water":
        # Gießkanne
        spielfeld.create_rectangle(
            940, 460, 972, 485,
            fill="#42c5f5",
            outline="#24536b",
            width=3,
        )
        spielfeld.create_line(
            940, 465, 925, 455,
            fill="#24536b",
            width=4,
        )
        spielfeld.create_arc(
            958, 448, 982, 475,
            start=270,
            extent=180,
            style="arc",
            outline="#24536b",
            width=3,
        )
    elif werkzeug == "Harvest":
        # Schere
        spielfeld.create_oval(
            937, 466, 952, 481,
            outline="#555555",
            width=3,
        )
        spielfeld.create_oval(
            950, 466, 965, 481,
            outline="#555555",
            width=3,
        )
        spielfeld.create_line(
            949, 473, 978, 455,
            fill="#555555",
            width=3,
        )
        spielfeld.create_line(
            953, 473, 978, 489,
            fill="#555555",
            width=3,
        )

    else:
        # Samen
        spielfeld.create_oval(
            946, 460, 964, 484,
            fill="#9b6b3d",
            outline="#654321",
            width=2,
        )


def klicke_auf_farm(event):
    for nummer, (x1, y1, x2, y2) in enumerate(beet_positionen):
        if not (x1 <= event.x <= x2 and y1 <= event.y <= y2):
            continue

        pflanze = feld[nummer]

        if pflanze is None:
            if werkzeug not in samen_inventar:
                status_text.config(text="Select seeds from the inventory below.")
                return


            if samen_inventar[werkzeug] <= 0:
                status_text.config(text=f"You have no {werkzeug} seeds.")
                return

            samen_inventar[werkzeug] -= 1
            daten = PFLANZEN[werkzeug]
            extra_water = daten["extra_watering"]

            feld[nummer] = {
                "pflanze": werkzeug,
                "gegossen": [False, False, False],
                "startzeit": None,
                "wachstum": 0.0,
                "letzte_aktualisierung": None,
                "warte_auf_wasser": False,
                "giess_deadline": None,
                "boss": daten.get("boss", False),
                "wasser_zeitpunkte": [
                    daten["growth"] * schritt / (extra_wasser + 1)
                    for schritt in range(1, extra_wasser + 1)
                ],
            }

            aktualisiere_inventar()
            status_text.config(
                text="Seed planted! Water all three blue spots to start."
            )
            zeichne_farm()
            return

        punkt_y = y1 + 165

        if werkzeug == "Water":
            for stelle in range(3):
                punkt_x = x1 + 55 + stelle * 65
                abstand = (
                    (event.x - punkt_x) ** 2
                    + (event.y - punkt_y) ** 2
                ) ** 0.5

                if abstand > 22:
                    continue

                if pflanze["startzeit"] is None:
                    if pflanze["gegossen"][stelle]:
                        status_text.config(text="This spot is already watered.")
                        return

                    pflanze["gegossen"][stelle] = True 

                    if all(pflanze["gegossen"]):
                        pflanze["startzeit"] = time.monotonic()
                        pflanze["letzte_aktualisierung"] = time. monotonic()
                        if pflanze["boss"]:
                            status_text.config(
                                text="Dragon Fruit started! it needs 3 minutes and 5 extra waterings."
                            )
                        else:
                            status_text.config(
                                text="Watering complete! The crop is growing."
                            )
                    else:
                        status_text.config(
                            text="Good! Water the other blue spots too."
                        )

                    zeichne_farm()
                    return

                if not pflanze["warte_auf_wasser"]:
                    status_text.config(text="This crop does not need water right now.")
                    return

                if pflanze["gegossen"][stelle]:
                    status_text.config(text="This spot is already watered.")
                    return

                pflanze["gegossen"][stelle]= True

                if all(pflanze["gegossen"]):
                    if pflanze["wasser_zeitpunkte"]:
                        pflanze["wasser_zeitpunkte"].pop(0)

                    pflanze["warte_auf_wasser"] = False
                    pflanze["giess_deadline"] = None
                    pflanze["letzte_aktualisierung"] = time.monotonic()
                    status_text.config(text="Watering round complete! Growth continues.")
                else:
                    status_text.config(
                        text="Water the other blue spots befor time runs out!"
                    )

                zeichne_farm()
                return

            status_text.config(text="Click one of the blue watering spots.")
            return

        if werkzeug != "Harvest":
            status_text.config(text="Select the Watering Can or Harvest tool.")
            return

        if pflanze["startzeit"] is None:
            status_text.config(text="Water all three spots first.")
            return

        if pflanze["warte_auf_wasser"]:
            status_text.config(text="This crop needs water before it can grow or be harvested.")
            return

        dauer = PFLANZEN[pflanze["pflanze"]]["growth"]
        if pflanze["wachstum"] < dauer:
            restzeit = dauer - pflanze["wachstum"]
            status_text.config(
                text=f"Not ripe yet - wait {restzeit:.1f} seconds."
            )
            return

        name = pflanze["pflanze"]
        ertrag = random.randint(1, 3)
        ernte_lager[name] += ertrag
        feld[nummer] = None

        aktualisiere_marktplatz()
        status_text.config(
            text=f"Harvested {ertrag} {name}(s). Sell them in the Marketplace."
        )
        zeichne_farm()
        return





def aktualisiere_spiel(geplant=True):
    global wetter, letzter_tag

    if spielfeld is None or not spielfeld.winfo_exists():
        return

    jetzt = time.monotonic()
    if jetzt >= shop_reset_zeit:
        erneuere_shop(jetzt)
    else:
        aktualisiere_shop_anzeige()
    tag = int((jetzt - spielstart) // 60) + 1

    if tag != letzter_tag:
        letzter_tag = tag
        wetter = random.choice(["Sunny", "Cloudy", "Rain"])

    wachstumsfaktor = 1.5 if wetter == "Rain" else 1.0

    for nummer, pflanze in enumerate(feld):
        if pflanze is None or pflanze["startzeit"] is None:
            continue

        if pflanze["warte_auf_wasser"]:
            if(
                pflanze["boss"]
                and pflanze["giess_deadline"] is not None
                and jetzt >= pflanze["giess_deadline"]
            ):
                feld[nummer] = None
                status_text.config(
                    text="The Dragon Fruit withered because it was not watered in time!"
                )
            continue

        vergangen = max(0, jetzt - pflanze["letzte_aktualisierung"])
        dauer = PFLANZEN[pflanze["pflanze"]]["growth"]

        pflanze["wachstum"] = min(
            dauer,
            pflanze["wachstum"] + vergangen * wachstumsfaktor,
        )
        pflanze["letzte_aktualisierung"] = jetzt

        if (
            pflanze["wasser_zeitpunkte"]
            and pflanze["wachstum"] >= pflanze["wasser_zeitpunkte"][0]
        ):
            pflanze["wachstum"] >= pflanze["wasser_zeitpunkte"][0]
            pflanze["warte_auf_wasser"] = True
            pflanze["gegossen"] = [False, False, False]

            if pflanze["boss"]:
                pflanze["giess_deadline"] = jetzt + 15
                status_text.config(
                    text="Dragon Fruit needs water now! You have 15 seconds!"
                )
            else:
                pflanze["giess_deadline"] = None
                status_text.config(
                    text=f"{pflanze['pflanze']} needs water. its growth is paused, but it will not be lost."
                )

def zeige_spiel():
    global spielfeld, status_text, geld_text
    global tag_text, spielstart, letzter_tag, wetter

    spielstart = time.monotonic()
    letzter_tag = 1
    wetter = random.choice(["Sunny", "Cloudy", "Rain"])


    
    for widget in fenster.winfo_children():
        widget.destroy()

    kopf = tk.Frame(fenster, bg="#d9edc2")
    kopf.pack(fill="x", pady=8)

    tk.Label(
        kopf,
        text="My Farm",
        font=("Arial", 24, "bold"),
        bg="#d9edc2",
        fg="#31572c",
    ).pack(side="left", padx=20)

    # Day and weather display
    tag_text = tk.Label(
        kopf,
        text="DAY 1  |  SUNNY",
        font=("Arial", 16, "bold"),
        bg="#d9edc2",
        fg="#b26a00",
    )
    tag_text.pack(side="left", padx=45)

    geld_text = tk.Label(
        kopf,
        text=f"Coins: {geld}",
        font=("Arial", 18, "bold"),
        bg="#d9edc2",
        fg="#654321",
    )
    geld_text.pack(side="right", padx=20)

    werkzeuge = tk.Frame(fenster, bg="#d9edc2")
    werkzeuge.pack(pady=5)

    tk.Button(
        werkzeuge,
        text="Shop",
        command=zeige_shop,
        font=("Arial", 12, "bold"),
    ).pack(side="left", padx=5)

    tk.Button(
        werkzeuge,
        text="Marketplace",
        command=zeige_marktplatz,
        font=("Arial", 12, "bold"),
    ).pack(side="left", padx=5)

    tk.Button(
        werkzeuge,
        text="Watering Can",
        command=lambda: waehle_werkzeug("Water"),
        font=("Arial", 12, "bold"),
    ).pack(side="left", padx=5)

    tk.Button(
        werkzeuge,
        text="Harvest",
        command=lambda: waehle_werkzeug("Harvest"),
        font=("Arial", 12, "bold"),
    ).pack(side="left", padx=5)

    status_text = tk.Label(
        fenster,
        text="Choose seeds from your inventory, then click an empty plot.",
        font=("Arial", 12),
        bg="#d9edc2",
        fg="#31572c",
    )
    status_text.pack(pady=5)

    spielfeld = tk.Canvas(
        fenster,
        width=1000,
        height=520,
        highlightthickness=0,
    )
    spielfeld.pack()
    spielfeld.bind("<Button-1>", klicke_auf_farm)
    inventar = tk.Frame(fenster, bg="#d9edc2")
    inventar.pack(pady=8)

    tk.Label(
        inventar,
        text="Seeds:",
        font=("Arial", 12, "bold"),
        bg="#d9edc2",
    ).pack(side="left", padx=5)

    inventar_buttons.clear()

    for name in samen_inventar:
        button = tk.Button(
            inventar,
            text="",
            command=lambda n=name: waehle_werkzeug(n),
        )
        button.pack(side="left", padx=5)
        inventar_buttons[name] = button

    aktualisiere_inventar()

    zeichne_farm()
    fenster.bind(
        "<FocusIn>",
        lambda event: aktualisiere_spiel(geplant=False),
    )
    aktualisiere_spiel()


zeige_menue()
fenster.mainloop()
