import random
import time
import tkinter as tk
from tkinter import messagebox


geld = 20
feld = [None, None, None]
preise = {"Karotte": 5, "Tomate": 15}
verkaufspreise = {"Karotte": 10, "Tomate": 15}

fenster = tk.Tk()
fenster.title("Mein Mini-Bauernhof")
fenster.geometry("1000x760")
fenster.configure(bg="#d9edc2")

werkzeug = "Karotte"
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
wetter = "Sonnig"


def zeige_menue():
    for widget in fenster.winfo_children():
        widget.destroy()

    menue = tk.Frame(fenster, bg="#d9edc2")
    menue.pack(expand=True, fill="both")

    tk.Label(
        menue,
        text="Mein Mini-Bauernhof",
        font=("Arial", 32, "bold"),
        bg="#d9edc2",
        fg="#31572c",
    ).pack(pady=(120, 20))

    tk.Label(
        menue,
        text="Pflanze, gieße und ernte dein eigenes Gemüse!",
        font=("Arial", 16),
        bg="#d9edc2",
        fg="#31572c",
    ).pack(pady=10)

    tk.Button(
        menue,
        text="Spielen",
        font=("Arial", 20, "bold"),
        width=16,
        command=zeige_spiel,
        bg="#70a34b",
        fg="white",
        activebackground="#527d38",
    ).pack(pady=30)

    tk.Button(
        menue,
        text="Beenden",
        font=("Arial", 14),
        width=16,
        command=fenster.destroy,
    ).pack(pady=5)


def waehle_werkzeug(neues_werkzeug):
    global werkzeug
    werkzeug = neues_werkzeug

    if neues_werkzeug == "Wasser":
        status_text.config(
            text="Gießkanne gewählt: Bewässere alle drei blauen Stellen."
        )
    elif neues_werkzeug == "Ernte":
        status_text.config(
            text="Ernte gewählt: Klicke auf ein reifes Beet"
        )
    else:
        status_text.config(
            text=f"{neues_werkzeug}-Samen gewählt: Klicke auf ein leeres Beet."
        )

    zeichne_farm()


def zeichne_farm():
    spielfeld.delete("all")

    #Himmel und Wiese
    spielfeld.create_rectangle(0, 0, 1000, 520, fill="#9bd6f2", outline="")
    spielfeld.create_oval(-100, 280, 1100, 700, fill="#72b85a", outline="")
    spielfeld.create_rectangle(0, 350, 1000, 520, fill="#72b85a", outline="")

    # Sonne
    spielfeld.create_oval(850, 25, 925, 100, fill="#ffdb58", outline="")

    # Wolken
    for x, y in [(270, 55), (520,85)]:
        spielfeld.create_oval(x, y, x + 55, y + 30, fill="white", outline="")
        spielfeld.create_oval(x + 25, y - 15, x + 80, y + 30, fill="white", outline="")
        spielfeld.create_oval(x + 55, y, x + 100, y + 30, fill="white", outline="")

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
                text="Leeres Beet",
                font=("Arial", 16, "bold"),
                fill="#f5deb3",
            )
            continue

        name = pflanze["pflanze"]

        #Kleine Pflanzenprosse
        # Die Pflanzen wachsen sichtbar während der Wartezeit
        if pflanze["startzeit"] is None:
            wachstum = 0.15
        else:
            wachstum = min(1, pflanze["wachstum"] / 40)

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
                fill="#27632a",
                width=6,
            )
            spielfeld.create_oval(
                pflanzen_x - blatt_groesse * 2,
                stamm_oben + 8,
                pflanzen_x,
                stamm_oben + 20,
                fill="#48a848",
                outline="",
            )
            spielfeld.create_oval(
                pflanzen_x,
                stamm_oben,
                pflanzen_x + blatt_groesse * 2,
                stamm_oben + 14,
                fill="#55b84f",
                outline="",
            )

        spielfeld.create_text(
            (x1 + x2) / 2,
            y1 + 35,
            text=name,
            font=("Arial", 16, "bold"),
            fill="white",
        )

        if pflanze["startzeit"] is None:
            anzeige = "Noch nicht bewässert"
            fortschritt = 0
        else:
            restzeit = max(0, 40 - pflanze["wachstum"])
            fortschritt = pflanze["wachstum"] / 40

            if restzeit == 0:
                anzeige = "Erntereif! Klicke zum Ernten."

                for frucht_x in (x1 + 65, x1 + 120, x1 + 175):
                    if name == "Karotte":
                        spielfeld.create_polygon(
                            frucht_x - 8, y1 + 125,
                            frucht_x + 8, y1 +125,
                            frucht_x, y1 + 150,
                            fill="#ff8c00",
                            outline="#bd5e00",
                        )
                    else:
                        spielfeld.create_oval(
                            frucht_x - 11, y1 + 125,
                            frucht_x + 11, y1 + 147,
                            fill="#e53935",
                            outline="#a51d25",
                        )
            else:
                anzeige = f"Wächst noch: {restzeit:04.1f} Sekunden"

        spielfeld.create_text(
            (x1 + x2) / 2,
            y1 + 65,
            text=anzeige,
            font=("Arial", 11, "bold"),
            fill="white",
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

    spielfeld.create_text(
        960,
        445,
        text="Werkzeug",
        font=("Arial", 11, "bold"),
        fill="#31572c",
    )

    if werkzeug == "Wasser":
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
    elif werkzeug == "Ernte":
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
    global geld

    for nummer, (x1, y1, x2, y2) in enumerate(beet_positionen):
        if not (x1 <= event.x <= x2 and y1 <= event.y <= y2):
            continue

        pflanze = feld[nummer]

        # Leeres Beet: Samen darauf pflanzen
        if pflanze is None:
            if werkzeug not in preise:
                status_text.config(text="Wähle zuerst einen Samen aus.")
                return

            if geld < preise [werkzeug]:
                status_text.config(text="Du hast nicht genug Münzen für diesen Samen.")
                return

            geld -= preise[werkzeug]
            feld[nummer] = {
                "pflanze": werkzeug,
                "gegossen": [False, False, False],
                "startzeit": None,
                "wachstum": 0.0,
                "letzte_aktualisierung": None,
            }
            geld_text.config(text=f"Münzen: {geld}")
            status_text.config(
                text="Samen gepflanzt! Wähle die Gießkanne und bewässere alle drei blauen Stellen."
            )
            zeichne_farm()
            return

        # Mit der Gießkanne die drei markierten
        if werkzeug == "Wasser" and pflanze["startzeit"] is None:
            punkt_y = y1 + 165

            for stelle in range(3):
                punkt_x = x1 + 55 + stelle * 65
                abstand = ((event.x - punkt_x) ** 2 + (event.y - punkt_y) ** 2) ** 0.5

                if abstand <= 22:
                    if pflanze["gegossen"][stelle]:
                        status_text.config(text="Diese Stelle ist schon bewässert.")
                        return

                    pflanze["gegossen"][stelle] = True

                    if all(pflanze["gegossen"]):
                        pflanze["startzeit"] = time.monotonic()
                        pflanze["wachstum"] = 0.0
                        pflanze["letzte_aktualisierung"] = time.monotonic()
                        status_text.config(
                            text="Das Beet ist bewässert! Warte 40 Sekunden bis zur Ernte."
                        )
                    else:
                        status_text.config(
                            text="Gut gegossen! Bewässere auch die anderen blauen Stellen."
                        )

                    zeichne_farm()
                    return

            status_text.config(text="Klicke mit der Gießkanne auf einen blauen Punkt im Beet.")
            return

        # Reife Pflanze ernten
        if pflanze["startzeit"] is None:
            status_text.config(text="Bewässere zuerst alle drei Stellen im Beet.")
            return

        if pflanze["wachstum"] < 40:
            restzeit = 40 - pflanze["wachstum"]
            status_text.config(
                text=f"Noch nicht reif - warte {restzeit:.1f} Sekunden."
            )
            return
        
        name = pflanze["pflanze"]
        ertrag = random.randint(1, 3)
        einnahmen = verkaufspreise[name] * ertrag
        geld += einnahmen
        feld[nummer] = None

        geld_text.config(text=f"Münzen: {geld}")
        status_text.config(
            text=f"Geerntet: {ertrag} {name}(n). du hast {einnahmen} Münzen verdient!"
        )
        zeichne_farm()
        return

def aktualisiere_spiel(geplant=True):
    global wetter, letzter_tag

    if spielfeld is None or not spielfeld.winfo_exists():
        return

    jetzt = time.monotonic()
    tag = int((jetzt - spielstart) // 60) + 1

    if tag != letzter_tag:
        letzter_tag = tag
        wetter = random.choice(["Sonnig", "Bewölkt", "Regen"])

    wachstumsfaktor = 1.5 if wetter == "Regen" else 1.0

    for pflanze in feld:
        if pflanze is not None and pflanze["startzeit"] is not None:
            vergangen = max(0, jetzt - pflanze["letzte_aktualisierung"])
            pflanze["wachstum"] = min(
                40,
                pflanze["wachstum"] + vergangen * wachstumsfaktor,
            )
            pflanze["letzte_aktualisierung"] = jetzt

    tag_text.config(text=f"TAG {tag}  |  {wetter}")

    zeichne_farm()

    if geplant:
        fenster.after(100, aktualisiere_spiel)

def zeige_spiel():
    global spielfeld, status_text, geld_text
    global tag_text, spielstart, letzter_tag, wetter

    spielstart = time.monotonic()
    letzter_tag = 1
    wetter = random.choice(["Sonnig", "Bewölkt", "Regen"])


    
    for widget in fenster.winfo_children():
        widget.destroy()

    kopf = tk.Frame(fenster, bg="#d9edc2")
    kopf.pack(fill="x", pady=8)

    tk.Label(
        kopf,
        text="Mein Bauernhof",
        font=("Arial", 24, "bold"),
        bg="#d9edc2",
        fg="#31572c",
    ).pack(side="left", padx=20)

    # Direkt nach dem Label "Mein Bauernhof" einfügen:
    tag_text = tk.Label(
        kopf,
        text="TAG 1  |  ☀ SONNIG",
        font=("Arial", 16, "bold"),
        bg="#d9edc2",
        fg="#b26a00",
    )
    tag_text.pack(side="left", padx=45)

    geld_text = tk.Label(
        kopf,
        text=f"Münzen: {geld}",
        font=("Arial", 18, "bold"),
        bg="#d9edc2",
        fg="#654321",
    )
    geld_text.pack(side="right", padx=20)

    werkzeuge = tk.Frame(fenster, bg="#d9edc2")
    werkzeuge.pack(pady=5)

    tk.Button(
        werkzeuge,
        text="Karottensamen (5 Münzen)",
        command=lambda: waehle_werkzeug("Karotte"),
        font=("Arial", 12, "bold"),
    ).pack(side="left", padx=5)

    tk.Button(
        werkzeuge,
        text="Tomatensamen (15 Münzen)",
        command=lambda: waehle_werkzeug("Tomate"),
        font=("Arial", 12, "bold"),
    ).pack(side="left", padx=5)

    tk.Button(
        werkzeuge,
        text="Gießkanne",
        command=lambda: waehle_werkzeug("Wasser"),
        font=("Arial", 12, "bold"),
    ).pack(side="left", padx=5)

    tk.Button(
        werkzeuge,
        text="Ernten",
        command=lambda: waehle_werkzeug("Ernte"),
        font=("Arial", 12, "bold"),
    ).pack(side="left", padx=5)

    status_text = tk.Label(
        fenster,
        text="Wähle einen Samen aus und klicke auf ein leeres Beet.",
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

    zeichne_farm()
    fenster.bind(
        "<FocusIn>",
        lambda event: aktualisiere_spiel(geplant=False),
    )
    aktualisiere_spiel()


zeige_menue()
fenster.mainloop()
