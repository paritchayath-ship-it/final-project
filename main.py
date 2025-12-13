import tkinter as tk
import threading
import json
import websocket
from datetime import datetime

from config import COLORS, COINS_OPTIONS, FONTS
from utils.binanceAPI import get_binance_ticker, get_klines
from utils.UIhelpers import create_shadow_card
from components.ticker import CryptoCard, PulseGraph
from components.orderbook import OrderBookPanel
from components.trades import TradeFeedPanel
from components.technical import ChartPanel

SELECTED_COINS = []

class SelectionPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["bg_main"])
        self.controller = controller
        
        tk.Label(self, text="Select your coins", font=FONTS["h1"], 
                 bg=COLORS["bg_main"], fg=COLORS["text_dark"]).pack(pady=(40, 5))
        
        tk.Label(self, text="Select at least 3 coins to proceed", font=FONTS["body"], 
                 bg=COLORS["bg_main"], fg=COLORS["text_light"]).pack(pady=(0, 30))
        
        grid = tk.Frame(self, bg=COLORS["bg_main"])
        grid.pack()
        
        self.cards = []
        for i, coin in enumerate(COINS_OPTIONS):
            row = i // 3
            col = i % 3

            card_wrap = tk.Frame(grid, bg=COLORS["bg_main"])
            card_wrap.grid(row=row, column=col, padx=15, pady=15)
            
            card = CryptoCard(card_wrap, coin, self.on_select)
            card.pack()
            self.cards.append(card)

        self.btn_next = tk.Button(self, text="NEXT >", font=FONTS["body_bold"], 
                                  bg=COLORS["shadow"], fg=COLORS["text_light"], 
                                  state="disabled", bd=0, padx=40, pady=12,
                                  command=lambda: controller.show_home_page(), cursor="hand2")
        self.btn_next.pack(pady=40)

    def on_select(self, symbol, is_selecting):
        global SELECTED_COINS
        if is_selecting:
            if symbol not in SELECTED_COINS: SELECTED_COINS.append(symbol)
        else:
            if symbol in SELECTED_COINS: SELECTED_COINS.remove(symbol)
            
        if len(SELECTED_COINS) >= 3:
            self.btn_next.config(state="normal", bg=COLORS["accent_blue"], fg=COLORS["white"])
            self.btn_next.config(text=f"CREATE PORTFOLIO ({len(SELECTED_COINS)}) >")
        else:
            self.btn_next.config(state="disabled", bg=COLORS["shadow"], fg=COLORS["text_light"])
            self.btn_next.config(text=f"Select {3 - len(SELECTED_COINS)} more")
        return True


class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["bg_main"])
        
        h = tk.Frame(self, bg=COLORS["bg_main"])
        h.pack(fill="x", padx=40, pady=30)

        dt_frame = tk.Frame(h, bg=COLORS["bg_main"])
        dt_frame.pack(side="left")

        self.lbl_date = tk.Label(dt_frame, text="...", font=FONTS["h1"], bg=COLORS["bg_main"], fg=COLORS["text_dark"])
        self.lbl_date.pack(anchor="w")
        self.lbl_time = tk.Label(dt_frame, text="...", font=FONTS["h2"], bg=COLORS["bg_main"], fg=COLORS["text_light"])
        self.lbl_time.pack(anchor="w")
        self.update_datetime()

        tk.Button(h, text="✎ Change coins", bg=COLORS["bg_main"], fg=COLORS["accent_brown"], 
                  font=FONTS["body"], bd=0, command=lambda: controller.show_selection_page(), 
                  cursor="hand2").pack(side="right", anchor="center")

        tk.Label(self, text="Portfolio Overview", font=FONTS["h2"], 
                 fg=COLORS["text_dark"], bg=COLORS["bg_main"]).pack(pady=(20, 10), anchor="w", padx=40)
        
        self.graph = PulseGraph(self, width=800, height=300)
        self.graph.pack(pady=20)
        
        self.status_lbl = tk.Label(self, text="Loading market data...", font=FONTS["body"], 
                                   bg=COLORS["bg_main"], fg=COLORS["text_light"])
        self.status_lbl.pack()

        threading.Thread(target=self.load_data, daemon=True).start()

    def update_datetime(self):
        now = datetime.now()
        self.lbl_date.config(text=now.strftime("%B %d, %Y"))
        self.lbl_time.config(text=now.strftime("%H:%M:%S"))
        self.after(1000, self.update_datetime)

    def load_data(self):
        data_list = []
        for symbol in SELECTED_COINS:
            ticker = get_binance_ticker(symbol)
            if ticker: data_list.append(ticker)
        
        self.after(0, lambda: self.graph.draw_graph(data_list))
        self.after(0, lambda: self.status_lbl.config(text=f"Updated: {datetime.now().strftime('%H:%M:%S')}"))


class ProDetailPage(tk.Frame):
    def __init__(self, parent, symbol):
        super().__init__(parent, bg=COLORS["bg_main"])
        self.symbol = symbol.lower()
        self.is_running = True
        
        top = tk.Frame(self, bg=COLORS["bg_main"])
        top.pack(fill="x", padx=30, pady=20)
        tk.Label(top, text=symbol, font=FONTS["h1"], bg=COLORS["bg_main"], fg=COLORS["text_dark"]).pack(side="left")
        self.lbl_price = tk.Label(top, text="---", font=FONTS["h1"], bg=COLORS["bg_main"], fg=COLORS["text_dark"])
        self.lbl_price.pack(side="right")

        self.var_book = tk.BooleanVar(value=True)
        self.var_trade = tk.BooleanVar(value=True)
        
        tf = tk.Frame(self, bg=COLORS["bg_main"])
        tf.pack(fill="x", padx=30)
        
        for text, var in [("Order Book", self.var_book), ("Trades", self.var_trade)]:
            tk.Checkbutton(tf, text=text, variable=var, command=self.update_layout,
                           bg=COLORS["bg_main"], fg=COLORS["text_dark"], selectcolor=COLORS["bg_main"],
                           activebackground=COLORS["bg_main"], font=FONTS["body"]).pack(side="left", padx=10)

        self.content = tk.Frame(self, bg=COLORS["bg_main"])
        self.content.pack(fill="both", expand=True, padx=30, pady=20)
        self.content.columnconfigure(0, weight=2)
        self.content.columnconfigure(1, weight=1)

        self.chart_wrap, self.chart_inner = create_shadow_card(self.content, padx=10, pady=10)
        self.chart_wrap.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(0, 20), pady=10)
        self.chart_panel = ChartPanel(self.chart_inner)
        self.chart_panel.pack(fill="both", expand=True)

        self.book_wrap, self.book_inner = create_shadow_card(self.content, padx=10, pady=10)
        self.book_panel = OrderBookPanel(self.book_inner)
        self.book_panel.pack(fill="both", expand=True)
        
        self.trade_wrap, self.trade_inner = create_shadow_card(self.content, padx=10, pady=10)
        self.trade_panel = TradeFeedPanel(self.trade_inner)
        self.trade_panel.pack(fill="both", expand=True)

        self.update_layout()
        threading.Thread(target=self.fetch_chart, daemon=True).start()
        threading.Thread(target=self.start_ws, daemon=True).start()

    def update_layout(self):
        self.book_wrap.grid_forget()
        self.trade_wrap.grid_forget()
        
        row = 0
        if self.var_book.get():
            self.book_wrap.grid(row=row, column=1, sticky="nsew", pady=10)
            row += 1
        if self.var_trade.get():
            self.trade_wrap.grid(row=row, column=1, sticky="nsew", pady=(0, 10) if row > 0 else 10)

    def fetch_chart(self):
        klines = get_klines(self.symbol.upper())
        self.after(0, lambda: self.chart_panel.draw_chart(klines))

    def start_ws(self):
        def on_message(ws, message):
            if not self.is_running: 
                ws.close()
                return
            
            try:
                response = json.loads(message)

                data = response.get('data', response)
                
                self.after(0, lambda: self.process_ws_data(data))
                        
            except Exception as e:
                print(f"WS Parsing Error: {e}")

        def on_error(ws, error):
            print(f"WebSocket Error: {error}")

        def on_open(ws):
            print(f"WebSocket Connected: {self.symbol}")

        symbol_lower = self.symbol.lower()
        
        stream_names = f"{symbol_lower}@trade/{symbol_lower}@depth5@100ms"
        url = f"wss://stream.binance.com:9443/stream?streams={stream_names}"
        
        print(f"Connecting to: {url}")
        
        ws = websocket.WebSocketApp(url, 
                                    on_message=on_message,
                                    on_error=on_error,
                                    on_open=on_open)
        ws.run_forever()


    def process_ws_data(self, data):
        try:
            if 'p' in data: 
                price = float(data['p'])
                self.lbl_price.config(text=f"{price:,.2f}")
                
                if hasattr(self, 'trade_panel'):
                    self.trade_panel.add(data['p'], data['q'], data['m']) 

            bids = data.get('bids') or data.get('b')
            asks = data.get('asks') or data.get('a')

            if bids and asks:
                if hasattr(self, 'book_panel'):
                    self.book_panel.update_data(bids, asks)
                    
        except Exception as e:
            print(f"UI Update Error: {e}")

    def destroy(self):
        self.is_running = False
        super().destroy()


class CryptoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Costra Bakery Crypto")
        self.geometry("1100x700")
        self.configure(bg=COLORS["bg_main"])
        
        self.sidebar = tk.Frame(self, bg=COLORS["card_bg"], width=90)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        
        self.container = tk.Frame(self, bg=COLORS["bg_main"])
        self.container.pack(side="right", fill="both", expand=True)
        
        self.current_frame = None
        self.show_selection_page()

    def update_sidebar(self):
        for w in self.sidebar.winfo_children(): w.destroy()
        
        tk.Button(self.sidebar, text="🏠", font=("Arial", 24), bg=COLORS["card_bg"], 
                  fg=COLORS["accent_blue"], bd=0, command=self.show_home_page, 
                  cursor="hand2").pack(pady=(30, 20))
        
        tk.Frame(self.sidebar, height=1, bg=COLORS["shadow"]).pack(fill="x", padx=20, pady=10)
        
        for coin in SELECTED_COINS:
            short = coin.replace("USDT","")
            tk.Button(self.sidebar, text=short, font=FONTS["body_bold"], 
                      bg=COLORS["card_bg"], fg=COLORS["text_dark"], bd=0,
                      command=lambda c=coin: self.show_detail_page(c), 
                      cursor="hand2", pady=10).pack(fill="x")

    def show_selection_page(self):
        self.sidebar.pack_forget()
        if self.current_frame: self.current_frame.destroy()
        global SELECTED_COINS
        SELECTED_COINS = [] 
        self.current_frame = SelectionPage(self.container, self)
        self.current_frame.pack(fill="both", expand=True)

    def show_home_page(self):
        self.sidebar.pack(side="left", fill="y")
        self.update_sidebar()
        if self.current_frame: self.current_frame.destroy()
        self.current_frame = HomePage(self.container, self)
        self.current_frame.pack(fill="both", expand=True)

    def show_detail_page(self, symbol):
        if self.current_frame: self.current_frame.destroy()
        self.current_frame = ProDetailPage(self.container, symbol)
        self.current_frame.pack(fill="both", expand=True)

if __name__ == "__main__":
    app = CryptoApp()
    app.mainloop()