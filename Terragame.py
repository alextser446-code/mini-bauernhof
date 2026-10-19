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
fenster.geometry("600x430")
fenster.configure(bg="#8bc34a")

tk.Label(
    fenster,
    text="Mein Mini-Bauernhof",
    font=("Arial", 24, "bold"),
    bg="#8bc34a",
).pack(pady=12)

geld_text = tk.Label(
    fenster,
    text="",
    font=("Arial", 16, "bold"),
    bg="#8bc34a",
)
geld_text.pack(pady=5)

felder_frame = tk.Frame(fenster, bg="#8bc34a")
felder_frame.pack(pady=20)

feld_buttons = []


def aktualisiere_anzeige():
    geld_text.config(text=f"Münzen: {geld}")

    for i, pflanze in enumerate(feld):
        if pflanze is None:
            text = f"Feld {i + 1}\nLeer"
        elif not pflanze["gegossen"]:
            text = f"Feld {i + 1}\n{pflanze['pflanze']}\nMuss gegossen werden"
        else:
            verbleibend = max(
                0, int(20 - (time.time() - pflanze["startzeit"]))
            )
            if verbleibend == 0:
                text = f"Feld {i + 1}\n{pflanze['pflanze']}\nErntereif!"
            else:
                text = (
                    f"Feld {i + 1}\n{pflanze['pflanze']}\n"
                    f"Ernte in {verbleibend} Sekunden"
                )

        feld_buttons[i].config(text=text)

    fenster.after(1000, aktualisiere_anzeige)


def pflanzen(platz):
    if feld[platz] is not None:
        messagebox.showinfo("Feld belegt", "Dieses Feld ist schon bepflanzt.")
        return

    auswahl = tk.StringVar(value="Karotte")
    dialog = tk.Toplevel(fenster)
    dialog.title("Samen auswählen")
    dialog.geometry("280x190")
    dialog.configure(bg="#dcedc8")

    tk.Label(
        dialog,
        text="Welche Pflanze möchtest du setzen?",
        bg="#dcedc8",
        font=("Arial", 12),
    ).pack(pady=10)

    tk.Radiobutton(
        dialog,
        text="Karotte – 5 Münzen",
        variable=auswahl,
        value="Karotte",
        bg="#dcedc8",
    ).pack()

    tk.Radiobutton(
        dialog,
        text="Tomate – 15 Münzen",
        variable=auswahl,
        value="Tomate",
        bg="#dcedc8",
    ).pack()

    def bestaetigen():
        global geld
        name = auswahl.get()

        if geld < preise[name]:
            messagebox.showinfo("Zu wenig Geld", "Du hast nicht genug Münzen.")
            return

        geld -= preise[name]
        feld[platz] = {
            "pflanze": name,
            "gegossen": False,
            "startzeit": None,
        }
        dialog.destroy()
        aktualisiere_anzeige()

    tk.Button(
        dialog,
        text="Pflanzen",
        command=bestaetigen,
        font=("Arial", 11, "bold"),
    ).pack(pady=12)


def feld_anklicken(platz):
    global geld

    if feld[platz] is None:
        pflanzen(platz)
        return

    pflanze = feld[platz]

    if not pflanze["gegossen"]:
        pflanze["gegossen"] = True
        pflanze["startzeit"] = time.time()
        messagebox.showinfo(
            "Gegossen",
            f"Du hast die {pflanze['pflanze']} gegossen. "
            "Sie ist in 20 Sekunden erntereif.",
        )
    elif time.time() - pflanze["startzeit"] < 20:
        restzeit = int(20 - (time.time() - pflanze["startzeit"]))
        messagebox.showinfo(
            "Noch nicht erntereif",
            f"Warte noch ungefähr {restzeit} Sekunden.",
        )
        return
    else:
        ertrag = random.randint(1, 3)
        name = pflanze["pflanze"]
        einnahmen = verkaufspreise[name] * ertrag
        geld += einnahmen
        feld[platz] = None
        messagebox.showinfo(
            "Ernte",
            f"Du hast {ertrag} {name}(n) geerntet "
            f"und {einnahmen} Münzen verdient!",
        )

    aktualisiere_anzeige()


for i in range(3):
    button = tk.Button(
        felder_frame,
        text=f"Feld {i + 1}",
        width=16,
        height=6,
        font=("Arial", 12, "bold"),
        bg="#a5d6a7",
        command=lambda platz=i: feld_anklicken(platz),
    )
    button.grid(row=0, column=i, padx=10)
    feld_buttons.append(button)

tk.Label(
    fenster,
    text="Klicke auf ein leeres Feld zum Pflanzen.\n"
    "Gieße die Pflanze und warte 20 Sekunden bis zur Ernte.",
    font=("Arial", 12),
    bg="#8bc34a",
).pack(pady=12)

aktualisiere_anzeige()
fenster.mainloop()
