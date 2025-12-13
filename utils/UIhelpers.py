import tkinter as tk
from config import COLORS, SHADOW_OFFSET

def create_shadow_card(parent, **kwargs):
    bg_color = kwargs.pop('bg', COLORS["card_bg"])
    padx = kwargs.pop('padx', 0)
    pady = kwargs.pop('pady', 0)
    
    container = tk.Frame(parent, bg=COLORS["bg_main"], **kwargs)
    container.grid_rowconfigure(0, weight=1)
    container.grid_columnconfigure(0, weight=1)

    shadow = tk.Frame(container, bg=COLORS["shadow"])
    shadow.grid(row=0, column=0, sticky="nsew", 
                padx=(SHADOW_OFFSET, 0), pady=(SHADOW_OFFSET, 0))

    card = tk.Frame(container, bg=bg_color)
    card.grid(row=0, column=0, sticky="nsew", 
              padx=(0, SHADOW_OFFSET), pady=(0, SHADOW_OFFSET))
    
    content_frame = tk.Frame(card, bg=bg_color)
    content_frame.pack(fill="both", expand=True, padx=padx, pady=pady)

    card.tkraise()

    return container, content_frame