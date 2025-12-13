# 📈 Python Crypto Dashboard

A desktop cryptocurrency dashboard built with **Python** and **Tkinter**. It features a modern "Shadow UI" design, real-time data streaming via WebSockets, and interactive technical analysis charts.


## Key Features

* **Real-time Data:** Live price updates using **Binance WebSockets**.
* **Portfolio Pulse:** Visual graph showing the performance of your selected coins relative to each other.
* **Technical Charts:** Interactive candlestick charts with **Moving Averages (MA7, MA25)** using `Matplotlib`.
* **Market Depth:** Live **Order Book** and **Trade Feed** visualization.
* **Multi-Coin Support:** Select and track specific cryptocurrencies (BTC, ETH, SOL, etc.).
* **Custom UI:** Unique aesthetic with custom shadow-styled components and responsive layouts.

## Tech Stack

* **Language:** Python 3
* **GUI Framework:** Tkinter (Standard Library)
* **Charting:** Matplotlib (embedded in Tkinter)
* **Image Processing:** Pillow (PIL)
* **Networking:**
    * `requests` (REST API for historical data/Klines)
    * `websocket-client` (Live streaming data)
* **Data Source:** Binance Public API

## Project Structure

```text
CryptoDashboard/
├── components/         # UI Components
│   ├── ticker.py       # Coin cards & Pulse graph
│   ├── technical.py    # Matplotlib chart logic
│   ├── orderbook.py    # Order book panel
│   └── trades.py       # Recent trades panel
├── utils/              # Helper functions
│   ├── binance_api.py  # API connection logic
│   └── ui_helpers.py   # Shadow card UI generator
├── config.py           # Configuration (Colors, Fonts, Constants)
├── main.py             # Application Entry Point
└── README.md
```

## Installation
**Clone the repository**

```Bash
git clone https://github.com/paritchayath-ship-it/final-project.git
cd final_project
```

---

**Install dependencies**
You need to install the required libraries:

```Bash
pip install requests matplotlib pillow websocket-client
```

---

**Add Coin Icons (Optional)**
Place your coin icons (e.g., BTC.png, ETH.png) in the root directory or ensure the paths match the ticker.py logic to see coin logos.

---

**Run the App**

```Bash
python main.py
```