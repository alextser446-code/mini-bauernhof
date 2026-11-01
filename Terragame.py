import random
import time
import tkinter as tk
from tkinter import messagebox
import json
import os
import sys
from pathlib import Path


geld = 20
feld = [None, None, None, None]
freigeschaltete_beete = 3
BEET_SLOT_PREIS = 250
beet_slot_kaufbutton = None
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
        "stem": "#315c35", "leaf1": "#338e52", "leaf2": "#66c77a",
    },
}

MISCHUNGEN = {
    "Pumpkin Carrot": {
        "zutaten": ("Carrot", "Pumpkin"),
        "verkaufsspanne": (90, 120),
    },
    "Strawberry Tomato": {
        "zutaten": ("Strawberry", "Tomato"),
        "verkaufsspanne": (60, 85),
    },
}

freigeschaltete_mischungen = 1
mixing_fenster = None
mixing_labels = {}
mixing_buttons = {}

preise = {name: daten["price"] for name, daten in PFLANZEN.items()}
verkaufsspannen = {
    "Carrot": (7, 10),
    "Tomato": (16, 22),
    "Strawberry": (27, 35),
    "Pumpkin": (55, 70),
    "Strawberry Tomato": (60, 85),
    "Pumpkin Carrot": (90, 120),
    "Golden Flower": (275, 350),
    "Dragon Fruit": (1100, 1500),
}


def wuerfle_verkaufspreise():
    neue_preise = {}

    for name, (minimum, maximum) in verkaufsspannen.items():
        moegliche_preise = list(range(minimum, maximum + 1))
        gewichte = [maximum - preis + 1 for preis in moegliche_preise]
        neue_preise[name] = random.choices(
            moegliche_preise,
            weights=gewichte,
            k=1,
        )[0]

    return neue_preise


verkaufspreise = wuerfle_verkaufspreise()

samen_inventar = {name: 0 for name in PFLANZEN}
ernte_lager = {
    name: 0 for name in (*PFLANZEN, *MISCHUNGEN)
}

bibliothek = set()

shop_chancen = {name: daten["chance"] for name, daten in PFLANZEN.items()}
shop_mengen = {name: daten["stock"] for name, daten in PFLANZEN.items()}

fenster = tk.Tk()
fenster.title("My Mini Farm")
fenster.geometry("1000x760")
fenster.configure(bg="#d9edc2")

werkzeug = "Carrot"
beet_positionen = [
    (10, 220, 245, 430),
    (255, 220, 490, 430),
    (500, 220, 735, 430),
    (745, 220, 990, 430),
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
KUNDEN_REISEZEIT = 10
WASSER_ROBOTER_PREIS = 3500
WASSER_ROBOTER_DAUER = 9
WASSER_ROBOTER_GESCHWINDIGKEIT = 180  # Pixel pro Sekunde
WASSER_ROBOTER_HEIM_X = 500
WASSER_ROBOTER_HEIM_Y = 490

EINPFLANZ_ROBOTER_PREIS = 5000
ERNTE_ROBOTER_PREIS = 2000
ARBEITS_ROBOTER_GESCHWINDIGKEIT = 180
ARBEITS_ROBOTER_DAUER = 2

EINPFLANZ_ROBOTER_HEIM_X = 570
ERNTE_ROBOTER_HEIM_X = 430

einpflanz_roboter_besitzt = False
ernte_roboter_besitzt = False

einpflanz_roboter_auftrag = None
ernte_roboter_auftrag = None

einpflanz_roboter_x = EINPFLANZ_ROBOTER_HEIM_X
ernte_roboter_x = ERNTE_ROBOTER_HEIM_X
einpflanz_roboter_y = WASSER_ROBOTER_HEIM_Y
ernte_roboter_y = WASSER_ROBOTER_HEIM_Y

einpflanz_roboter_letztes_update = None
ernte_roboter_letztes_update = None

einpflanz_roboter_kaufbutton = None
ernte_roboter_kaufbutton = None

wasser_roboter_besitzt = False 
wasser_roboter_auftrag = None
wasser_roboter_kaufbutton = None
wasser_roboter_x = WASSER_ROBOTER_HEIM_X
wasser_roboter_y = WASSER_ROBOTER_HEIM_Y
wasser_roboter_letztes_update = None

kunden = []

shop_reset_zeit = time.monotonic() + 60

TUTORIAL_QUESTS = [
    ("Tutorial 1/10: Buy your first seed", "seeds_bought", 1, 5),
    ("Tutorial 2/10: Plant a crop", "planted", 1, 5),
    ("Tutorial 3/10: Water a crop", "watered", 1, 5),
    ("Tutorial 4/10: Harvest a crop", "harvested", 1, 5),
    ("Tutorial 5/10: Sell your harvest", "sold", 1, 5),
    ("Tutorial 6/10: Open the Library", "library_opened", 1, 5),
    ("Tutorial 7/10: Let a customer reach the shop", "customer_arrived", 1, 5),
    ("Tutorial 8/10: Open the Mixing Bucket", "mixing_opened", 1, 5),
    ("Tutorial 9/10: Mix a hybrid crop", "mixes", 1, 10),
    ("Tutorial 10/10: Earn 10 coins from sales", "coins_earned", 10, 10),
]

QUEST_STEPS = [
    ("planted", [2, 5, 10, 20, 35], "crops"),
    ("watered", [2, 5, 10, 20, 35], "watering rounds"),
    ("harvested", [2, 5 ,10, 20, 40], "crops harvested"),
    ("sold", [2, 5, 10, 20, 40], "crops sold"),
    ("coins_earned", [25, 75, 150, 300, 600], "coins earned"),
    ("discovered", [2, 3, 4,  5, 6], "plant discovered"),
    ("customer_arrived", [2, 5, 10, 20, 40], "customers"),
    ("mixes", [2, 3, 5, 8, 12], "hybrid crops mixed"),
    ("seeds_bought", [2, 5, 10, 20, 35], "seeds bought"),
]

QUESTS = [
    {
        "title": titel,
        "event": ereignis,
        "ziel": ziel,
        "belohnung": belohnung,
    }
    for titel, ereignis, ziel, belohnung in TUTORIAL_QUESTS
]

for ereignis, stufen, beschreibung in QUEST_STEPS:
    for ziel in stufen:
        QUESTS.append({
            "title": f"Farm Challenge {len(QUESTS) + 1}: Reach {ziel} {beschreibung}",
            "event": ereignis,
            "ziel": ziel,
            "belohnung": ziel * 2 + 5,
        })

for ziel in (1, 2, 3):
    QUESTS.append({
        "title": f"Farm Challenge {len(QUESTS) + 1}: Buy {ziel} robots",
        "event": "robots_bought",
        "ziel": ziel,
        "belohnung": ziel * 10,
    })

for ziel in (2, 5):
    QUESTS.append({
        "title": f"Farm Challenge {len(QUESTS) + 1}: Let customers buy {ziel} items",
        "event": "customer_items",
        "ziel": ziel,
        "belohnung": ziel * 5,
    })

quest_fortschritt = {}
quest_index = 0
quest_fenster = None
quest_liste = None
quest_status_label = None

ACHIEVEMENTS = [
    ("First Harvest", "harvested", 1, 5),
    ("Green Thumb", "harvested", 10, 20),
    ("Seed Collector", "seeds_bought", 10, 15),
    ("Master Waterer", "watered", 10, 20),
    ("First Hybrid", "mixes", 1, 25),
    ("Robot Owner", "robots_bought", 1, 15),
    ("Earn 100 Coins", "coins_earned", 100, 30),
]

achievements_claimed = set()

achievement_fenster = None 
achievement_liste = None
statistik_fenster = None
statistik_label = None


def aktualisiere_achievement_fenster():
    if achievement_fenster is None or achievement_liste is None:
        return
    try:
        if not achievement_fenster.winfo_exists():
            return
        achievement_liste.delete(0, tk.END)

        for titel, ereignis, ziel, belohnung in ACHIEVEMENTS:
            fortschritt = min(quest_fortschritt.get(ereignis, 0), ziel)

            if fortschritt >= ziel:
                status = f"UNLOCKED (+{belohnung} coins)"
            else:
                status = f"{fortschritt}/{ziel}"

            achievement_liste.insert(
                tk.END,
                f"{status} - {titel}",
            )

    except tk.TclError:
        pass

def zeige_achievements():
    global achievement_fenster, achievement_liste
    if achievement_fenster is not None and achievement_fenster.winfo_exists():
        achievement_fenster.lift()
        aktualisiere_achievement_fenster()
        return
    achievement_fenster = tk.Toplevel(fenster)
    achievement_fenster.title("Achievements")
    achievement_fenster.geometry("430x350")
    achievement_fenster.configure(bg="#d9edc2")

    tk.Label(
        achievement_fenster,
        text="Farm Achievements",
        font=("Arial", 20, "bold"),
        bg="#d9edc2",
        fg="#31572c",
    ).pack(pady=12)

    achievement_liste = tk.Listbox(
        achievement_fenster,
        width=45,
        height=12,
        font=("Arial", 12),
    )
    achievement_liste.pack(padx=15, pady=10, fill="both", expand=True)

    aktualisiere_achievement_fenster()


def aktualisiere_statistiken():
    if statistik_fenster is None or statistik_label is None:
        return
    try:
        if not statistik_fenster.winfo_exists():
            return
        statistik_label.config(
            text=(
                f"Total items harvested: "
                f"{quest_fortschritt.get('harvested', 0)}\n\n"
                f"Watering rounds completed: "
                f"{quest_fortschritt.get('watered', 0)}\n\n"
                f"Total coins received before spending: "
                f"{quest_fortschritt.get('total_income', 0)}"
        )
        )
    except tk.TclError:
        pass

def zeige_statistiken():
    global statistik_fenster, statistik_label
    if statistik_fenster is not None and statistik_fenster.winfo_exists():
        statistik_fenster.lift()
        aktualisiere_statistiken()
        return
    statistik_fenster = tk.Toplevel(fenster)
    statistik_fenster.title("Farm Statistics")
    statistik_fenster.geometry("430x260")
    statistik_fenster.configure(bg="#d9edc2")

    tk.Label(
        statistik_fenster,
        text="Farm Statistics",
        font=("Arial", 20, "bold"),
        bg="#d9edc2",
        fg="#31572c",
    ).pack(pady=15)

    statistik_label = tk.Label(
        statistik_fenster,
        text="",
        font=("Arial", 13, "bold"),
        bg="#d9edc2",
        fg="#31572c",
        justify="left",
    )
    statistik_label.pack(padx=20, pady=10, anchor="w")

    aktualisiere_statistiken()
   

def aktualisiere_quest_fenster():
    if quest_fenster is None:
        return

    try:
        if not quest_fenster.winfo_exists():
            return

        quest_liste.delete(0, tk.END)

        for nummer, quest in enumerate(QUESTS):
            if nummer < quest_index:
                status = "DONE"
            elif nummer == quest_index:
                status = "NOW"
            else:
                status = "LOCKED"

            quest_liste.insert(tk.END, f"{status} - {quest['title']}")

        if quest_index >= len(QUESTS):
            quest_status_label.config(text="All 60 quests completed!")
        else:
            quest = QUESTS[quest_index]
            wert = min(
                quest_fortschritt.get(quest["event"], 0),
                quest["ziel"],
            )
            quest_status_label.config(
                text=(
                    f"Current quest: {quest['title']}\n"
                    f"Progress: {wert}/{quest['ziel']} | "
                    f"Reward: {quest['belohnung']} coins"
                )
            )
    except tk.TclError:
        pass


def quest_event(ereignis, anzahl=1):
    global quest_index, geld

    quest_fortschritt[ereignis] = (
        quest_fortschritt.get(ereignis, 0) + anzahl
    )

    belohnung_erhalten = 0

    while quest_index < len(QUESTS):
        quest = QUESTS[quest_index]
        aktueller_wert = quest_fortschritt.get(quest["event"], 0)

        if aktueller_wert < quest["ziel"]:
            break

        geld += quest["belohnung"]
        belohnung_erhalten += quest["belohnung"]
        quest_index += 1

    achievement_belohnung = 0
    neue_achievements = []

    for titel, achievement_event, ziel, belohnung in ACHIEVEMENTS:
        fortschritt = quest_fortschritt.get(achievement_event, 0)

        if fortschritt >= ziel and titel not in achievements_claimed:
            achievements_claimed.add(titel)
            achievement_belohnung += belohnung            
            neue_achievements.append(titel)

    geld += achievement_belohnung
    quest_fortschritt["total_income"] = (
        quest_fortschritt.get("total_income", 0)
        + belohnung_erhalten        + achievement_belohnung    )

    try:
        if geld_text is not None and geld_text.winfo_exists():
            geld_text.config(text=f"Coins: {geld}")

        if achievement_belohnung > 0 and status_text is not None:
            namen = ", ".join(neue_achievements)
            status_text.config(
                text=(
                    f"Achievement unlocked: {namen}! "
                    f"+{achievement_belohnung} coins."
                )
            )

        if belohnung_erhalten > 0 and status_text is not None:
            status_text.config(
                text=f"Quest completed! You earned {belohnung_erhalten} coins."
            )
    except tk.TclError:
        pass

    aktualisiere_quest_fenster()
    aktualisiere_achievement_fenster()
    aktualisiere_statistiken()


def zeige_quests():
    global quest_fenster, quest_liste, quest_status_label

    if quest_fenster is not None and quest_fenster.winfo_exists():
        quest_fenster.lift()
        aktualisiere_quest_fenster()
        return

    quest_fenster = tk.Toplevel(fenster)
    quest_fenster.title("Quests")
    quest_fenster.geometry("600x500")
    quest_fenster.configure(bg="#d9edc2")

    tk.Label(
        quest_fenster,
        text="Farm Quests",
        font=("Arial", 20, "bold"),
        bg="#d9edc2",
        fg="#31572c",
    ).pack(pady=10)

    quest_status_label = tk.Label(
        quest_fenster,
        text="",
        font=("Arial", 11, "bold"),
        bg="#d9edc2",
        fg="#31572c",
        wraplength=560,
    )
    quest_status_label.pack(pady=8)

    quest_liste = tk.Listbox(quest_fenster, width=75, height=20)
    quest_liste.pack(padx=10, pady=8, fill="both", expand=True)

    aktualisiere_quest_fenster()






shop_labels = {}
shop_buttons = {}
markt_labels = {}
markt_buttons = {}
inventar_buttons = {}
shop_timer_label = None
bibliothek_fenster = None
bibliothek_labels = {}
bibliothek_fortschritt_label = None

def speicher_datei():
    # Beim normalen Start der .py-Datei wird kein Spielstand verwendet.
    if not getattr(sys, "frozen", False):
        return None

    appdata = os.getenv("APPDATA")
    if appdata:
        ordner = Path(appdata) / "TerraGame"
    else:
        ordner = Path.home() / "AppData" / "Roaming" / "TerraGame"

    return ordner / "save.json"


def speichere_spielstand():
    pfad = speicher_datei()
    if pfad is None:
        return

    daten = {
        "geld": geld,
        "feld": feld,
        "samen_inventar": samen_inventar,
        "ernte_lager": ernte_lager,
        "bibliothek": list(bibliothek),
        "freigeschaltete_mischungen": freigeschaltete_mischungen,
        "quest_fortschritt": quest_fortschritt,
        "quest_index": quest_index,
        "achievements_claimed": list(achievements_claimed),
        "wasser_roboter_besitzt": wasser_roboter_besitzt,
        "einpflanz_roboter_besitzt": einpflanz_roboter_besitzt,
        "ernte_roboter_besitzt": ernte_roboter_besitzt,
        "shop_bestand": shop_bestand,
        "shop_restzeit": max(0, shop_reset_zeit - time.monotonic()),
        "verkaufspreise": verkaufspreise,
        "werkzeug": werkzeug,
        "wetter": wetter,
        "freigeschaltete_beete": freigeschaltete_beete,
    }

    try:
        pfad.parent.mkdir(parents=True, exist_ok=True)
        temporaer = pfad.with_suffix(".tmp")

        with temporaer.open("w", encoding="utf-8") as datei:
            json.dump(daten, datei, indent=2)

        temporaer.replace(pfad)
    except (OSError, TypeError, ValueError) as fehler:
        print(f"Could not save game: {fehler}")


def lade_spielstand():
    global geld, feld, freigeschaltete_mischungen, quest_index
    global wasser_roboter_besitzt, einpflanz_roboter_besitzt
    global ernte_roboter_besitzt, shop_reset_zeit, werkzeug, wetter
    global wasser_roboter_auftrag, einpflanz_roboter_auftrag
    global ernte_roboter_auftrag, wasser_roboter_letztes_update
    global einpflanz_roboter_letztes_update, ernte_roboter_letztes_update
    global wasser_roboter_x, wasser_roboter_y
    global einpflanz_roboter_x, einpflanz_roboter_y
    global ernte_roboter_x, ernte_roboter_y
    global freigeschaltete_beete

    pfad = speicher_datei()
    if pfad is None or not pfad.exists():
        return

    try:
        with pfad.open("r", encoding="utf-8") as datei:
            daten = json.load(datei)

        geld = max(0, int(daten.get("geld", geld)))
        freigeschaltete_beete = max(
            3,
            min(
                int(daten.get("freigeschaltete_beete", 3)),
                len(beet_positionen),
            ),
        )

        gespeicherte_samen = daten.get("samen_inventar", {})
        for name in samen_inventar:
            wert = gespeicherte_samen.get(name, 0)
            samen_inventar[name] = max(0, int(wert))

        gespeicherte_ernte = daten.get("ernte_lager", {})
        for name in ernte_lager:
            wert = gespeicherte_ernte.get(name, 0)
            ernte_lager[name] = max(0, int(wert))

        bibliothek.clear()
        bibliothek.update(
            name for name in daten.get("bibliothek", [])
            if name in PFLANZEN
        )

        freigeschaltete_mischungen = max(
            1,
            min(
                int(daten.get("freigeschaltete_mischungen", 1)),
                len(MISCHUNGEN),
            ),
        )

        quest_index = max(
            0,
            min(int(daten.get("quest_index", 0)), len(QUESTS)),
        )
        gespeicherte_quests = daten.get("quest_fortschritt", {})
        quest_fortschritt.clear()
        for ereignis, wert in gespeicherte_quests.items():
            quest_fortschritt[ereignis] = max(0, int(wert))

        achievements_claimed.clear()
        bekannte_achievements = {eintrag[0] for eintrag in ACHIEVEMENTS}
        achievements_claimed.update(
            titel
            for titel in daten.get("achievements_claimed", [])
            if titel in bekannte_achievements
        )

        # Pflanzenfor)tschritt laden und Zeitstempel für diesen Spielstart erneuern.
        gespeichertes_feld = daten.get("feld", [])
        neues_feld = []

        for gespeicherte_pflanze in gespeichertes_feld[:len(feld)]:
            if not isinstance(gespeicherte_pflanze, dict):
                neues_feld.append(None)
                continue

            name = gespeicherte_pflanze.get("pflanze")
            if name not in PFLANZEN:
                neues_feld.append(None)
                continue

            pflanze = erstelle_pflanze(name)
            pflanze["gegossen"] = gespeicherte_pflanze.get(
                "gegossen",
                [False, False, False],
            )

            if (
                not isinstance(pflanze["gegossen"], list)
                or len(pflanze["gegossen"]) != 3
            ):
                pflanze["gegossen"] = [False, False, False]

            wachstum = float(gespeicherte_pflanze.get("wachstum", 0))
            pflanze["wachstum"] = max(
                0.0,
                min(wachstum, PFLANZEN[name]["growth"]),
            )

            pflanze["warte_auf_wasser"] = bool(
                gespeicherte_pflanze.get("warte_auf_wasser", False)
            )
            pflanze["wasser_zeitpunkte"] = gespeicherte_pflanze.get(
                "wasser_zeitpunkte",
                pflanze["wasser_zeitpunkte"],
            )

            gestartet = gespeicherte_pflanze.get("startzeit") is not None
            jetzt = time.monotonic()
            pflanze["startzeit"] = jetzt if gestartet else None
            pflanze["letzte_aktualisierung"] = jetzt if gestartet else None

            if pflanze["warte_auf_wasser"] and pflanze.get("boss"):
                pflanze["giess_deadline"] = jetzt + 15
            else:
                pflanze["giess_deadline"] = None
            neues_feld.append(pflanze)

        neues_feld.extend([None] * (len(feld) - len(neues_feld)))
        feld = neues_feld

        wasser_roboter_besitzt = bool(daten.get("wasser_roboter_besitzt", False))
        einpflanz_roboter_besitzt = bool(
            daten.get("einpflanz_roboter_besitzt", False)
        )
        ernte_roboter_besitzt = bool(daten.get("ernte_roboter_besitzt", False))

        shop_bestand.update({
            name: max(0, int(menge))
            for name, menge in daten.get("shop_bestand", {}).items()
            if name in shop_bestand
        })
        verkaufspreise.update({
            name: max(0, int(preis))
            for name, preis in daten.get("verkaufspreise", {}).items()
            if name in verkaufspreise
        })
        shop_reset_zeit = time.monotonic() + max(
            0, float(daten.get("shop_restzeit", 60))
        )

        if daten.get("werkzeug") in PFLANZEN or daten.get("werkzeug") in (
            "Water", "Harvest"
        ):
            werkzeug = daten["werkzeug"]
        if daten.get("wetter") in ("Sunny", "Cloudy", "Rain"):
            wetter = daten["wetter"]

        # Roboter starten nach dem Laden an ihren festen Ausgangspositionen.
        wasser_roboter_auftrag = None
        einpflanz_roboter_auftrag = None
        ernte_roboter_auftrag = None
        wasser_roboter_letztes_update = None
        einpflanz_roboter_letztes_update = None
        ernte_roboter_letztes_update = None
        wasser_roboter_x = WASSER_ROBOTER_HEIM_X
        wasser_roboter_y = WASSER_ROBOTER_HEIM_Y
        einpflanz_roboter_x = EINPFLANZ_ROBOTER_HEIM_X
        einpflanz_roboter_y = WASSER_ROBOTER_HEIM_Y
        ernte_roboter_x = ERNTE_ROBOTER_HEIM_X
        ernte_roboter_y = WASSER_ROBOTER_HEIM_Y

    except (OSError, json.JSONDecodeError, TypeError, ValueError, AttributeError):
        # Ein fehlender oder beschädigter Spielstand soll den Start nicht verhindern.
        return


def autospeichern():
    if getattr(sys, "frozen", False):
        speichere_spielstand()
    try:
        if fenster.winfo_exists():
            fenster.after(5000, autospeichern)
    except tk.TclError:
        pass


def beim_schliessen():
    speichere_spielstand()
    fenster.destroy()


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
    global shop_bestand, shop_reset_zeit, kunden, verkaufspreise

    if jetzt is None:
        jetzt = time.monotonic()

    shop_bestand = {
        name: random.randint(*shop_mengen[name]) if random.random() < chance else 0
        for name, chance in shop_chancen.items()
    }

    verkaufspreise = wuerfle_verkaufspreise()
    aktualisiere_marktplatz()
    aktualisiere_mixing_bucket()

    # Zwei Kunden starten gleichzeitig rechts und laufen zum shop links.
    kunden = [
        {
            "startzeit": jetzt,
            "start_x": 970,
            "ziel_x": 112,
            "farbe": "#4f83cc",
        },
        {
            "startzeit": jetzt,
            "start_x": 1030,
            "ziel_x": 145,
            "farbe": "#c85b45",
        },
    ]

    shop_reset_zeit = jetzt + 60
    aktualisiere_shop_anzeige()

def aktualisiere_kunden(jetzt):
    global kunden

    noch_unterwegs = []
    
    for kunde in kunden:
        angekommen = jetzt - kunde["startzeit"] >= KUNDEN_REISEZEIT

        if not angekommen:
            noch_unterwegs.append(kunde)
            continue
        quest_event("customer_arrived")

        anzahl_gewünscht = random.randint(0, 3)
        anzahl_gekauft = 0

        for _ in range(anzahl_gewünscht):
            verfügbare_pflanzen = [
                name for name, menge in shop_bestand.items()
                if menge > 0
            ]

            if not verfügbare_pflanzen:
                break

            name = random.choice(verfügbare_pflanzen)
            shop_bestand[name] -= 1
            anzahl_gekauft += 1

        if anzahl_gekauft > 0:
            quest_event("customer_items", anzahl_gekauft)

        status_text.config(
            text=f"A customer bought {anzahl_gekauft} item(s) from the shop."
        )

    kunden = noch_unterwegs
    aktualisiere_shop_anzeige()

def zeichne_kunden():
    jetzt = time.monotonic()

    for kunde in kunden:
        fortschritt = min(
            1,
            (jetzt - kunde["startzeit"]) / KUNDEN_REISEZEIT,
        )
        x = kunde["start_x"] + (kunde["ziel_x"] - kunde["start_x"]) * fortschritt
        y = 200

        # Kopf
        spielfeld.create_oval(
            x - 7, y - 34, x + 7, y - 20,
            fill="#f1c27d",
            outline="#654321",
        )

        # Körper und Arme
        spielfeld.create_line(
            x, y - 20, x, y - 3,
            fill=kunde["farbe"],
            width=8,
        )
        spielfeld.create_line(
            x - 10, y - 15, x + 10, y - 15,
            fill=kunde["farbe"],
            width=4,
        )

        # Beine
        spielfeld.create_line(
            x, y - 3, x - 7, y + 10,
            fill="#333333",
            width=3,
        )
        spielfeld.create_line(
            x, y - 3, x + 7, y + 10,
            fill="#333333",
            width=3,
        )

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
    quest_event("seeds_bought")
    shop_bestand[name] -= 1

    geld_text.config(text=f"Coins: {geld}")
    status_text.config(text=f"You bought one {name} seed.")
    aktualisiere_inventar()
    aktualisiere_shop_anzeige()


def kaufe_wasser_roboter():
    global geld, wasser_roboter_besitzt

    if wasser_roboter_besitzt:
        return

    if geld < WASSER_ROBOTER_PREIS:
        status_text.config(text="You don't have enough coins for the Watering Robot.")
        return

    geld -= WASSER_ROBOTER_PREIS
    wasser_roboter_besitzt = True
    quest_event("robots_bought")

    geld_text.config(text=f"Coins: {geld}")
    status_text.config(text="Watering Robot purchased!")

    if wasser_roboter_kaufbutton is not None:
        wasser_roboter_kaufbutton.config(
            text="Watering Robot owned",
            state="disabled",
        )

def kaufe_einpflanz_roboter():
    global geld, einpflanz_roboter_besitzt

    if einpflanz_roboter_besitzt:
        return

    if geld < EINPFLANZ_ROBOTER_PREIS:
        status_text.config(text="You don't have enough coins. ")
        return

    geld -= EINPFLANZ_ROBOTER_PREIS
    einpflanz_roboter_besitzt = True
    quest_event("robots_bought")
    geld_text.config(text=f"Coins: {geld}")
    status_text.config(text="Planting Robot purchased!")

    if einpflanz_roboter_kaufbutton is not None:
        einpflanz_roboter_kaufbutton.config(
            text="Planting Robot owned",
            state="disabled",
        )


def kaufe_ernte_roboter():
    global geld, ernte_roboter_besitzt

    if ernte_roboter_besitzt:
        return

    if geld < ERNTE_ROBOTER_PREIS:
        status_text.config(text="You don't have enough coins.")
        return

    geld -= ERNTE_ROBOTER_PREIS
    ernte_roboter_besitzt = True
    quest_event("robots_bought")
    geld_text.config(text=f"Coins: {geld}")
    status_text.config(text="Harvest Robot purchased!")

    if ernte_roboter_kaufbutton is not None:
        ernte_roboter_kaufbutton.config(
            text="Harvest Robot owned",
            state="disabled",
        )

def kaufe_extra_beet():
    global geld, freigeschaltete_beete

    if freigeschaltete_beete >=len(beet_positionen):
        status_text.config(text="All farn plots are already unlocked.")
        return

    if geld < BEET_SLOT_PREIS:
        status_text.config(text="You dont have enough coins for another plot.")
        return

    geld -= BEET_SLOT_PREIS
    freigeschaltete_beete += 1

    geld_text.config(text=f"Coins: {geld}")
    status_text.config(text="New farm plot unlocked!")
    zeichne_farm()

    if beet_slot_kaufbutton is not None:
        beet_slot_kaufbutton.config(
            text="All plots unlocked",
            state="disabled",
        )


def zeige_upgrades():
    global wasser_roboter_kaufbutton
    global einpflanz_roboter_kaufbutton
    global ernte_roboter_kaufbutton
    global beet_slot_kaufbutton

    upgrades_fenster = tk.Toplevel(fenster)
    upgrades_fenster.title("Upgrades")
    upgrades_fenster.geometry("400x330")
    upgrades_fenster.configure(bg="#d9edc2")

    tk.Label(
        upgrades_fenster,
        text="Farm Robots",
        font=("Arial", 20, "bold"),
        bg="#d9edc2",
        fg="#31572c",
    ).pack(pady=12)

    upgrades = [
        (
            "Watering Robot",
            wasser_roboter_besitzt,
            WASSER_ROBOTER_PREIS,
            kaufe_wasser_roboter,
        ),
        (
            "Planting Robot",
            einpflanz_roboter_besitzt,
            EINPFLANZ_ROBOTER_PREIS,
            kaufe_einpflanz_roboter,
        ),
        (
            "Harvest Robot",
            ernte_roboter_besitzt,
            ERNTE_ROBOTER_PREIS,
            kaufe_ernte_roboter,
        ),
    ]

    buttons = []

    for name, besitzt, preis, kauf_funktion in upgrades:
        button = tk.Button(
            upgrades_fenster,
            text=f"{name} owned" if besitzt else f"Buy {name} ({preis} coins)",
            command=kauf_funktion,
            state="disabled" if besitzt else "normal",
        )
        button.pack(pady=6)
        buttons.append(button)

    wasser_roboter_kaufbutton = buttons[0]
    einpflanz_roboter_kaufbutton = buttons[1]
    ernte_roboter_kaufbutton = buttons[2]

    beet_slot_kaufbutton = tk.Button(
        upgrades_fenster,
        text=(
            "All plots unlocked"
            if freigeschaltete_beete >= len(beet_positionen)
            else f"Unlock next plot ({BEET_SLOT_PREIS} coins)"
        ),
        command=kaufe_extra_beet,
        state=(
            "disabled"
            if freigeschaltete_beete >= len(beet_positionen)
            else "normal"
        ),
    )
    beet_slot_kaufbutton.pack(pady=8)


def aktualisiere_wasser_roboter(jetzt):
    global wasser_roboter_auftrag
    global wasser_roboter_x, wasser_roboter_y, wasser_roboter_letztes_update

    if not wasser_roboter_besitzt:
        return

    if wasser_roboter_letztes_update is None:
        wasser_roboter_letztes_update = jetzt
    delta_zeit = max(0, jetzt - wasser_roboter_letztes_update)
    wasser_roboter_letztes_update = jetzt

    if wasser_roboter_auftrag is None:
        for nummer, pflanze in enumerate(feld[:freigeschaltete_beete]):
            if pflanze is not None and (
                pflanze["startzeit"] is None
                or pflanze["warte_auf_wasser"]
            ):
                wasser_roboter_auftrag = {
                    "beet": nummer,
                    "phase": "fahrt",
                    "startzeit": None,
                }
                break

    ziel_x = WASSER_ROBOTER_HEIM_X
    ziel_y = WASSER_ROBOTER_HEIM_Y
    pflanze = None

    if wasser_roboter_auftrag is not None:
        nummer = wasser_roboter_auftrag["beet"]
        pflanze = feld[nummer]

        if pflanze is None or (
            pflanze["startzeit"] is not None
            and not pflanze["warte_auf_wasser"]
            and wasser_roboter_auftrag["phase"] == "fahrt"
        ):
            wasser_roboter_auftrag = None
            pflanze = None
        else:
            x1, y1, x2, y2 = beet_positionen[nummer]
            ziel_x = (x1 + x2) / 2
            ziel_y = y1 + 140

    # Bewege den Roboter pro Tick nur ein Stück in Richtung seines Ziels.
    dx = ziel_x - wasser_roboter_x
    dy = ziel_y - wasser_roboter_y
    abstand = (dx ** 2 + dy ** 2) ** 0.5
    bewegung = WASSER_ROBOTER_GESCHWINDIGKEIT * delta_zeit
    angekommen = abstand <= bewegung or abstand == 0

    if angekommen:
        wasser_roboter_x = ziel_x
        wasser_roboter_y = ziel_y
    elif abstand > 0:
        wasser_roboter_x += dx / abstand * bewegung
        wasser_roboter_y += dy / abstand * bewegung

    if wasser_roboter_auftrag is None or pflanze is None:
        return

    if wasser_roboter_auftrag["phase"] == "fahrt" and angekommen:
        # Der Timer beginnt erst bei der Pflanze, nachdem der Roboter angekommen ist.
        wasser_roboter_auftrag["phase"] = "bewässern"
        wasser_roboter_auftrag["startzeit"] = jetzt
        return

    if wasser_roboter_auftrag["phase"] != "bewässern":
        return

    if jetzt - wasser_roboter_auftrag["startzeit"] < WASSER_ROBOTER_DAUER:
        return

    pflanze["gegossen"] = [True, True, True]

    if pflanze["startzeit"] is None:
        pflanze["startzeit"] = jetzt
        pflanze["letzte_aktualisierung"] = jetzt
    elif pflanze["warte_auf_wasser"]:
        if pflanze["wasser_zeitpunkte"]:
            pflanze["wasser_zeitpunkte"].pop(0)

        pflanze["warte_auf_wasser"] = False
        pflanze["giess_deadline"] = None
        pflanze["letzte_aktualisierung"] = jetzt

    status_text.config(text=f"The Watering Robot watered the {pflanze['pflanze']}.")
    quest_event("watered")
    wasser_roboter_auftrag = None


def bewege_arbeitsroboter(x, y, ziel_x, ziel_y, delta_zeit):
    dx = ziel_x - x
    dy = ziel_y - y
    abstand = (dx ** 2 + dy ** 2) ** 0.5
    bewegung = ARBEITS_ROBOTER_GESCHWINDIGKEIT * delta_zeit

    if abstand <= bewegung or abstand == 0:
        return ziel_x, ziel_y, True

    x += dx / abstand * bewegung 
    y += dy / abstand * bewegung
    return x, y, False


def erstelle_pflanze(name):
    daten = PFLANZEN[name]
    extra_water = daten["extra_watering"]

    return {
        "pflanze": name,
        "gegossen": [False, False, False],
        "startzeit": None,
        "wachstum": 0.0,
        "letzte_aktualisierung": None,
        "warte_auf_wasser": False,
        "giess_deadline": None,
        "boss": daten.get("boss", False),
        "wasser_zeitpunkte": [
            daten["growth"] * schritt / (extra_water + 1)
            for schritt in range(1, extra_water + 1)
        ],
    }


def aktualisiere_einpflanz_roboter(jetzt):
    global einpflanz_roboter_auftrag
    global einpflanz_roboter_x, einpflanz_roboter_y
    global einpflanz_roboter_letztes_update

    if not einpflanz_roboter_besitzt:
        return

    if einpflanz_roboter_letztes_update is None:
        einpflanz_roboter_letztes_update = jetzt

    delta_zeit = max(0, jetzt - einpflanz_roboter_letztes_update)
    einpflanz_roboter_letztes_update = jetzt

    if einpflanz_roboter_auftrag is None:
        freie_beete = [
            nummer for nummer, pflanze in enumerate(feld[:freigeschaltete_beete])
            if pflanze is None
        ]
        samen = next(
            (name for name, anzahl in samen_inventar.items() if anzahl > 0),
            None,
        )

        if freie_beete and samen is not None:
            einpflanz_roboter_auftrag = {
                "beet": freie_beete[0],
                "samen": samen,
                "phase": "fahrt",
                "startzeit": None,
            }

    ziel_x = EINPFLANZ_ROBOTER_HEIM_X
    ziel_y = WASSER_ROBOTER_HEIM_Y

    if einpflanz_roboter_auftrag is not None:
        nummer = einpflanz_roboter_auftrag["beet"]
        samen = einpflanz_roboter_auftrag["samen"]

        if feld[nummer] is not None or samen_inventar[samen] <= 0:
            einpflanz_roboter_auftrag = None
        else:
            x1, y1, x2, y2 = beet_positionen[nummer]
            ziel_x = (x1 + x2) / 2
            ziel_y = y1 + 140

    einpflanz_roboter_x, einpflanz_roboter_y, angekommen = (
        bewege_arbeitsroboter(
            einpflanz_roboter_x,
            einpflanz_roboter_y,
            ziel_x,
            ziel_y,
            delta_zeit,
        )
    )

    if einpflanz_roboter_auftrag is None:
        return

    if einpflanz_roboter_auftrag["phase"] == "fahrt" and angekommen:
        einpflanz_roboter_auftrag["phase"] = "pflanzen"
        einpflanz_roboter_auftrag["startzeit"] = jetzt
        return

    if einpflanz_roboter_auftrag["phase"] == "pflanzen":
        if jetzt - einpflanz_roboter_auftrag["startzeit"] < ARBEITS_ROBOTER_DAUER:
            return

        nummer = einpflanz_roboter_auftrag["beet"]
        samen = einpflanz_roboter_auftrag["samen"]

        if feld[nummer] is None and samen_inventar[samen] > 0:
            samen_inventar[samen] -= 1 
            feld[nummer] = erstelle_pflanze(samen)
            quest_event("planted")
            aktualisiere_inventar()
            status_text.config(text=f"The Planting Robot planted {samen}.")

        einpflanz_roboter_auftrag = None



def aktualisiere_ernte_roboter(jetzt):
    global ernte_roboter_auftrag
    global ernte_roboter_x, ernte_roboter_y
    global ernte_roboter_letztes_update

    if not ernte_roboter_besitzt:
        return

    if ernte_roboter_letztes_update is None:
        ernte_roboter_letztes_update = jetzt

    delta_zeit = max(0, jetzt - ernte_roboter_letztes_update)
    ernte_roboter_letztes_update = jetzt

    if ernte_roboter_auftrag is None:
        for nummer, pflanze in enumerate(feld[:freigeschaltete_beete]):
            if (
                pflanze is not None
                and pflanze["startzeit"] is not None
                and not pflanze["warte_auf_wasser"]
                and pflanze["wachstum"]
                    >= PFLANZEN[pflanze["pflanze"]]["growth"]
            ):
                ernte_roboter_auftrag = {
                    "beet": nummer,
                    "phase": "fahrt",
                    "startzeit": None,
                }
                break

    ziel_x = ERNTE_ROBOTER_HEIM_X
    ziel_y = WASSER_ROBOTER_HEIM_Y
    pflanze = None

    if ernte_roboter_auftrag is not None:
        nummer = ernte_roboter_auftrag["beet"]
        pflanze = feld[nummer]

        if (
            pflanze is None
            or pflanze["warte_auf_wasser"]
            or pflanze["wachstum"]
                < PFLANZEN[pflanze["pflanze"]]["growth"]
        ):
            ernte_roboter_auftrag = None
            pflanze = None
        else:
            x1, y1, x2, y2 = beet_positionen[nummer]
            ziel_x = (x1 + x2) / 2
            ziel_y = y1 + 140

    ernte_roboter_x, ernte_roboter_y, angekommen = bewege_arbeitsroboter(
        ernte_roboter_x,
        ernte_roboter_y,
        ziel_x,
        ziel_y,
        delta_zeit,
    )

    if ernte_roboter_auftrag is None or pflanze is None:
        return
        
    if ernte_roboter_auftrag["phase"] == "fahrt" and angekommen:
        ernte_roboter_auftrag["phase"] = "ernten"
        ernte_roboter_auftrag["startzeit"] = jetzt
        return

    if ernte_roboter_auftrag["phase"] == "ernten":
        if jetzt - ernte_roboter_auftrag["startzeit"] < ARBEITS_ROBOTER_DAUER:
            return

        name = pflanze["pflanze"]
        neue_entdeckung = name not in bibliothek
        bibliothek.add(name)
        ertrag = random.randint(1, 3)
        ernte_lager[name] += ertrag
        quest_event("harvested", ertrag)

        if neue_entdeckung:
            quest_event("discovered")
        feld[nummer] = None

        aktualisiere_bibliothek()
        aktualisiere_marktplatz()
        aktualisiere_mixing_bucket()

        if neue_entdeckung:
            status_text.config(
                text=f"The Harvest Robot harvested {name}! New crop discovered!"
            )
        else:
            status_text.config(
                text=f"The Harvest Robot harvested {name}."
            )
        
        ernte_roboter_auftrag = None


def zeige_shop():
    global shop_labels, shop_buttons, shop_timer_label

    fenster_shop = tk.Toplevel(fenster)
    fenster_shop.title("Seed Shop")
    fenster_shop.geometry("500x390")
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
            label.config(
                text=f"{name}: {ernte_lager[name]} | "
                    f"Sell price: {verkaufspreise[name]} coins each"
            )
            markt_buttons[name].config(
                text=f"Sell all ({verkaufspreise[name]} coins each)",
                state="normal" if ernte_lager[name] > 0 else "disabled",
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
    quest_fortschritt["total_income"] = (
        quest_fortschritt.get("total_income", 0) + einnahmen    )
    quest_event("sold", anzahl)
    quest_event("coins_earned", einnahmen)
    ernte_lager[name] = 0

    geld_text.config(text=f"Coins: {geld}")
    status_text.config(text=f"Sold! You earned {einnahmen} coins.")
    aktualisiere_marktplatz()


def zeige_marktplatz():
    global markt_labels, markt_buttons

    fenster_markt = tk.Toplevel(fenster)
    fenster_markt.title("Marketplace")
    fenster_markt.geometry("500x390")
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


def aktualisiere_bibliothek():
    try:
        if bibliothek_fenster is None or not bibliothek_fenster.winfo_exists():
            return

        bibliothek_fortschritt_label.config(
            text=f"Discovered: {len(bibliothek)} / {len(PFLANZEN)}"
        )

        for name, label in bibliothek_labels.items():
            entdeckt = name in bibliothek
            status = "Discovered" if entdeckt else "Not discovered"
            chance = PFLANZEN[name]["chance"] * 100

            label.config(
                text=f"{name}: {status} | Shop chance: {chance:.0f}%"
            )
    except tk.TclError:
        pass


def zeige_bibliothek():
    quest_event("library_opened")
    global bibliothek_fenster
    global bibliothek_labels, bibliothek_fortschritt_label

    try:
        if bibliothek_fenster is not None and bibliothek_fenster.winfo_exists():
            bibliothek_fenster.lift()
            aktualisiere_bibliothek()
            return
    except tk.TclError:
        pass

    bibliothek_fenster = tk.Toplevel(fenster)
    bibliothek_fenster.title("Crop Library")
    bibliothek_fenster.geometry("460x390")
    bibliothek_fenster.configure(bg="#d9edc2")

    tk.Label(
        bibliothek_fenster,
        text="Crop Library",
        font=("Arial", 22, "bold"),
        bg="#d9edc2",
        fg="#31572c",
    ).pack(pady=12)

    bibliothek_fortschritt_label = tk.Label(
        bibliothek_fenster,
        text="",
        font=("Arial", 12, "bold"),
        bg="#d9edc2",
        fg="#31572c",
    )
    bibliothek_fortschritt_label.pack(pady=5)

    bibliothek_labels = {}

    for name in PFLANZEN:
        label = tk.Label(
            bibliothek_fenster,
            text="",
            font=("Arial", 12),
            bg="#d9edc2",
            fg="#31572c",
        )
        label.pack(anchor="w", padx=25, pady=5)
        bibliothek_labels[name] = label

    aktualisiere_bibliothek()


def aktualisiere_mixing_bucket():
    try:
        for ergebnis, label in mixing_labels.items():
            rezept_nr = list(MISCHUNGEN).index(ergebnis)
            zutaten = MISCHUNGEN[ergebnis]["zutaten"]

            status = (
                "Unlocked"
                if rezept_nr < freigeschaltete_mischungen
                else "Locked"
            )
            label.config(
                text=f"{ergebnis}: {zutaten[0]} + {zutaten[1]} ({status})"
            )

            genug_zutaten = all(ernte_lager[name] >= 1 for name in zutaten)
            mixing_buttons[ergebnis].config(
                state=(
                    "normal"
                    if rezept_nr < freigeschaltete_mischungen and genug_zutaten
                    else "disabled"
                )
            )
    except tk.TclError:
        pass


def mische_pflanzen(ergebnis):
    global freigeschaltete_mischungen

    rezept_nr = list(MISCHUNGEN).index(ergebnis)

    if rezept_nr >= freigeschaltete_mischungen:
        status_text.config(text="Mix the current recipe first to unlock this one.")
        return

    zutaten = MISCHUNGEN[ergebnis]["zutaten"]

    if any(ernte_lager[name] < 1 for name in zutaten):
        status_text.config(text="You need one of each ingredient to mix this crop.")
        return

    for name in zutaten:
        ernte_lager[name] -= 1

    ernte_lager[ergebnis] += 1
    quest_event("mixes")

    if rezept_nr == freigeschaltete_mischungen - 1:
        if freigeschaltete_mischungen < len(MISCHUNGEN):
            freigeschaltete_mischungen += 1 
            
    status_text.config(text=f"You mixed a {ergebnis}!")
    aktualisiere_marktplatz()
    aktualisiere_mixing_bucket()


def zeige_mixing_bucket():
    quest_event("mixing_opened")
    global mixing_fenster, mixing_labels, mixing_buttons

    try:
        if mixing_fenster is not None and mixing_fenster.winfo_exists():
            mixing_fenster.lift()
            aktualisiere_mixing_bucket()
            return
    except tk.TclError:
        pass

    mixing_fenster = tk.Toplevel(fenster)
    mixing_fenster.title("Mixing Bucket")
    mixing_fenster.geometry("500x260")
    mixing_fenster.configure(bg="#d9edc2")

    tk.Label(
        mixing_fenster,
        text="Mixing Bucket",
        font=("Arial", 22, "bold"),
        bg="#d9edc2",
        fg="#31572c",
    ).pack(pady=12)

    mixing_labels = {}
    mixing_buttons = {}

    for ergebnis in MISCHUNGEN:
        zeile = tk.Frame(mixing_fenster, bg="#d9edc2")
        zeile.pack(fill="x", padx=15, pady=8)

        mixing_labels[ergebnis] = tk.Label(
            zeile,
            text="",
            font=("Arial", 11),
            bg="#d9edc2",
        )
        mixing_labels[ergebnis].pack(side="left")

        mixing_buttons[ergebnis] = tk.Button(
            zeile,
            text="Mix",
            command=lambda name=ergebnis: mische_pflanzen(name),
        )
        mixing_buttons[ergebnis].pack(side="right")

    aktualisiere_mixing_bucket()


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


def zeichne_wasser_roboter():
    if not wasser_roboter_besitzt:
        return

    x, y = wasser_roboter_x, wasser_roboter_y

    spielfeld.create_oval(
        x - 18, y + 8, x - 5, y + 20,
        fill="#333333",
        tags=("wasser_roboter",),
    )
    spielfeld.create_oval(
        x + 5, y + 8, x + 18, y + 20,
        fill="#333333",
        tags=("wasser_roboter",),
    )
    spielfeld.create_rectangle(
        x - 20, y - 10, x + 20, y + 10,
        fill="#55aadd",
        outline="#24536b",
        width=2,
        tags=("wasser_roboter",),
    )
    spielfeld.create_oval(
        x - 8, y - 22, x + 8, y - 8,
        fill="#42c5f5",
        outline="#24536b",
        tags=("wasser_roboter",),
    )
    if wasser_roboter_auftrag is not None and wasser_roboter_auftrag["phase"] == "bewässern":
        restzeit = max(0, WASSER_ROBOTER_DAUER - int(
            time.monotonic() - wasser_roboter_auftrag["startzeit"]
        ))
        spielfeld.create_text(
            x, y - 42,
            text=f"{restzeit}s",
            fill="white",
            font=("Arial", 12, "bold"),
            tags=("wasser_roboter",),
        )


def zeichne_arbeitsroboter(x, y, farbe, akzent, tag, werkzeugtyp):
    # Schatten und Räder zuerst zeichnen, damit der Wagen darauf steht.
    spielfeld.create_oval(
        x - 23, y + 14, x + 23, y + 23,
        fill="#47603b",
        outline="",
        tags=(tag,),
    )
    for rad_x in (x - 16, x + 8):
        spielfeld.create_oval(
            rad_x, y + 5, rad_x + 12, y + 22,
            fill="#263238",
            outline="#11191d",
            width=2,
            tags=(tag,),
        )
        spielfeld.create_oval(
            rad_x + 3, y + 10, rad_x + 9, y + 17,
            fill="#b8c4c8",
            outline="#35454b",
            tags=(tag,),
        )

    # Fahrgestell und Karosserie
    spielfeld.create_rectangle(
        x - 23, y - 10, x + 23, y + 10,
        fill=farbe,
        outline=akzent,
        width=2,
        tags=(tag,),
    )
    spielfeld.create_rectangle(
        x - 14, y - 17, x + 14, y - 10,
        fill=akzent,
        outline=akzent,
        tags=(tag,),
    )

    # Sensor und zwei Augen
    spielfeld.create_oval(
        x - 9, y - 32, x + 9, y - 14,
        fill="#e9f6f7",
        outline=akzent,
        width=2,
        tags=(tag,),
    )
    spielfeld.create_oval(
        x - 5, y - 26, x - 2, y - 23,
        fill="#20343b",
        outline="",
        tags=(tag,),
    )
    spielfeld.create_oval(
        x + 2, y - 26, x + 5, y - 23,
        fill="#20343b",
        outline="",
        tags=(tag,),
    )

    if werkzeugtyp == "pflanzen":
        # Kleiner Saatgutbehälter
        spielfeld.create_rectangle(
            x - 7, y - 8, x + 7, y + 2,
            fill="#d5ad63",
            outline="#70552d",
            tags=(tag,),
        )
    else:
        # Erntegreifer an der Vorderseite
        spielfeld.create_line(
            x + 20, y - 3, x + 29, y + 3,
            fill="#d9e0e2",
            width=3,
            tags=(tag,),
        )
        spielfeld.create_line(
            x + 29, y + 3, x + 25, y + 9,
            fill="#d9e0e2",
            width=3,
            tags=(tag,),
        )


def zeichne_zusatz_roboter():
    if einpflanz_roboter_besitzt:
        zeichne_arbeitsroboter(
            einpflanz_roboter_x,
            einpflanz_roboter_y,
            "#54b86a",
            "#245b32",
            "einpflanz_roboter",
            "pflanzen",
        )

    if ernte_roboter_besitzt:
        zeichne_arbeitsroboter(
            ernte_roboter_x,
            ernte_roboter_y,
            "#e7a33e",
            "#80551d",
            "ernte_roboter",
            "ernten",
        )


def animier_wasser_roboter():
    if spielfeld is None or not spielfeld.winfo_exists():
        return

    jetzt = time.monotonic()

    aktualisiere_wasser_roboter(jetzt)
    aktualisiere_einpflanz_roboter(jetzt)
    aktualisiere_ernte_roboter(jetzt)

    spielfeld.delete("wasser_roboter")
    zeichne_wasser_roboter()

    spielfeld.delete("einpflanz_roboter")
    spielfeld.delete("ernte_roboter")
    zeichne_zusatz_roboter()

    fenster.after(16, animier_wasser_roboter)

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

        if nummer >= freigeschaltete_beete:
            spielfeld.create_rectangle(
                x1 + 8,
                y1 + 8,
                x2 - 8,
                y2 - 8,
                fill="#555555",
                outline="#dddddd",
                width=3,
            )
            spielfeld.create_text(
                (x1 + x2) / 2,
                (y1 + y2) / 2,
                text="LOCKED\nBuy in Upgrades",
                font=("Arial", 15, "bold"),
                fill="white",
                justify="center",
            )
            continue


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
            wachstum = 0.15
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

        if pflanze["wachstum"] >= dauer:
            glitzer_phase = int(time.monotonic() * 6) % 4
            glitzer_farben = ["#fff7a8", "#ffffff", "#ffe86b", "#ffffff"]

            glitzer_punkte = [
                (x1 + 45, y1 + 125),
                (x1 + 100, y1 + 110),
                (x1 + 155, y1 + 130),
                (x1 + 205, y1 + 115),
            ]

            for stern_nr, (glitzer_x, glitzer_y) in enumerate(glitzer_punkte):
                stern_phase = (glitzer_phase + stern_nr) % 4

                if stern_phase == 3:
                    continue
                groesse = 3 + stern_phase                
                farbe = glitzer_farben[stern_phase]

                spielfeld.create_line(
                    glitzer_x - groesse,
                    glitzer_y,
                    glitzer_x + groesse,
                    glitzer_y,
                    fill=farbe,
                    width=2,
                )
                spielfeld.create_line(
                    glitzer_x,
                    glitzer_y - groesse,
                    glitzer_x,
                    glitzer_y + groesse,
                    fill=farbe,
                    width=2,
                )
                spielfeld.create_oval(
                    glitzer_x - 2,
                    glitzer_y - 2,
                    glitzer_x + 2,
                    glitzer_y + 2,
                    fill=farbe,
                    outline="",
                )

        balken_links = x1 + 40
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

    reife_beete = sum(
        1
        for pflanze in feld[:freigeschaltete_beete]
        if pflanze is not None         
        and pflanze["startzeit"] is not None        
        and not pflanze["warte_auf_wasser"]
        and pflanze["wachstum"] >= PFLANZEN[pflanze["pflanze"]]["growth"]
    )

    spielfeld.create_rectangle(
        690, 10, 980, 45,
        fill="#31572c",
        outline="#f5deb3",
        width=2,
    )
    spielfeld.create_text(
        835, 28,
        text=f"Ready to harvest: {reife_beete}/{freigeschaltete_beete}",
        font=("Arial", 12, "bold"),
        fill="white",
    )

    zeichne_kunden()
    zeichne_wasser_roboter()
    zeichne_zusatz_roboter()
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
        
        if nummer >= freigeschaltete_beete:
            status_text.config(
                text=f"Unlock this plot in Upgrades for {BEET_SLOT_PREIS} coins."
            )
            return

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
                    daten["growth"] * schritt / (extra_water + 1)
                    for schritt in range(1, extra_water + 1)
                ],
            }
            quest_event("planted")

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
                        quest_event("watered")
                        pflanze["startzeit"] = time.monotonic()
                        pflanze["letzte_aktualisierung"] = time.monotonic()
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
                    text="Water the other blue spots before time runs out!"
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
        neue_entdeckung = name not in bibliothek
        bibliothek.add(name)
        aktualisiere_bibliothek()

        ertrag = random.randint(1, 3)
        quest_event("harvested", ertrag)

        if neue_entdeckung:
            quest_event("discovered")
        ernte_lager[name] += ertrag

        feld[nummer] = None

        aktualisiere_marktplatz()
        aktualisiere_mixing_bucket()
        if neue_entdeckung:
            status_text.config(
                text=f"Harvested {ertrag} {name}(s)! New crop discovered in the Library!"
            )
        else:
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
    aktualisiere_kunden(jetzt)
    tag = int((jetzt - spielstart) // 60) + 1

    if tag != letzter_tag:
        letzter_tag = tag
        wetter = random.choice(["Sunny", "Cloudy", "Rain"])

    if tag_text is not None and tag_text.winfo_exists():
        tag_text.config(text=f"DAY {tag}  |  {wetter.upper()}")

    wachstumsfaktor = 1.5 if wetter == "Rain" else 1.0

    for nummer, pflanze in enumerate(feld[:freigeschaltete_beete]):
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
                    text=f"{pflanze['pflanze']} needs water. Its growth is paused, but it will not be lost."
                )

    zeichne_farm()
    if geplant:
        fenster.after(100, aktualisiere_spiel)

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
        text="Statistics",
        command=zeige_statistiken,
        font=("Arial", 12, "bold"),
    ).pack(side="left", padx=5)

    tk.Button(
        werkzeuge,
        text="Quests",
        command=zeige_quests,
        font=("Arial", 12, "bold"),
    ).pack(side="left", padx=5)

    tk.Button(
        werkzeuge,
        text="Achievements",
        command=zeige_achievements,
        font=("Arial", 12, "bold"),
    ).pack(side="left", padx=5)

    tk.Button(
        werkzeuge,
        text="Shop",
        command=zeige_shop,
        font=("Arial", 12, "bold"),
    ).pack(side="left", padx=5)

    tk.Button(
        werkzeuge,
        text="Upgrades",
        command=zeige_upgrades,
        font=("Arial", 12, "bold"),
    ).pack(side="left", padx=5)

    tk.Button(
        werkzeuge,
        text="Mixing Bucket",
        command=zeige_mixing_bucket,
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
        text="Library",
        command=zeige_bibliothek,
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
    fenster.after(16, animier_wasser_roboter)
    aktualisiere_spiel()


lade_spielstand()
fenster.protocol("WM_DELETE_WINDOW", beim_schliessen)
zeige_menue()
fenster.after(5000, autospeichern)
fenster.mainloop()
