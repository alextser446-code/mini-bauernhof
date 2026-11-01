# My Mini Farm

My Mini Farm is a small, mouse-controlled farming game made with Python and Tkinter. Plant seeds, water crops as they grow, harvest and sell your produce, discover new plants, and build up your farm. The game is a personal indie project and is still being developed.

## Features

- A visual farm with several plots, crop growth stages, and changing sunny, cloudy, and rainy weather.
- Six crops with different shop availability, growth times, watering needs, and sale values: Carrot, Tomato, Strawberry, Pumpkin, Golden Flower, and the rare Dragon Fruit.
- A seed shop whose stock refreshes every 60 seconds. Two customers arrive during each stock cycle and may buy items from the shop, so stock can disappear before you do.
- A marketplace where you can sell harvested crops. Sale prices vary between stock cycles.
- A crop library that records plants you have discovered.
- A Mixing Bucket for combining crops into hybrids. Recipes unlock in order, and hybrids can be sold for higher prices.
- Tutorial and farming quests, achievements, and a statistics menu for lifetime harvests, watering rounds, and gross coins earned.
- Three animated farm helpers: watering, planting, and harvesting robots.
- An optional fourth plot that can be unlocked with coins.
- Automatic save files for the packaged Windows game.

## How to play

1. Open **Shop** and buy seeds while they are in stock.
2. Select a seed from the inventory at the bottom of the screen, then click an empty plot to plant it.
3. Select **Water** and click the planted crop when it needs water. Some crops need multiple watering rounds.
4. Wait for the crop to finish growing, then select **Harvest** and click it.
5. Open **Marketplace** to sell your harvest and earn coins. Use coins to buy more seeds, unlock a plot, and purchase robots.
6. Check **Quests**, **Achievements**, **Crop Library**, and **Mixing Bucket** as your farm grows.

The Dragon Fruit is exceptionally rare and takes the longest to grow. Watch its watering prompts carefully.

## Run from source

You need Windows and Python 3 with Tkinter. Tkinter is included with the standard Python for Windows installer; make sure **tcl/tk and IDLE** is selected during installation.

Open PowerShell in the folder containing `Terragame.py`, then run:

```powershell
python Terragame.py
```

## Build the Windows executable

Install PyInstaller and build from the same folder as `Terragame.py`:

```powershell
python -m pip install pyinstaller
python -m PyInstaller --clean --noconfirm --onefile --windowed --name Terragame Terragame.py
```

The executable will be created at:

```text
dist/Terragame.exe
```

The packaged game stores its save file separately from the source code at `%APPDATA%/TerraGame/save.json`. Running the `.py` source does not load or write this packaged-game save file.

## Built with

- Python
- Tkinter for the graphical interface
- PyInstaller for the Windows executable

## Project status

This is an actively developed project. Features, balance, and interface details may change as the farm grows.
