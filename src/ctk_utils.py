import customtkinter as ctk
from src import config_utils

def CenterWindowToDisplay(Screen: ctk.CTk, width: int, height: int, scale_factor: float = 1.0):
    screen_width = Screen.winfo_screenwidth()
    screen_height = Screen.winfo_screenheight()
    x = int(((screen_width/2) - (width/2)) * scale_factor)
    y = int(((screen_height/2) - (height/1.5)) * scale_factor)
    return f"{width}x{height}+{x}+{y}"

def create_label(parent, text, text_color, font_size, **kwargs):
    label = ctk.CTkLabel(
        parent,
        text=text,
        text_color=text_color,
        font=ctk.CTkFont(family=config_utils.FONT_FAMILY, size=font_size),
        **kwargs
    )

    return label

def create_button(parent, width, height, text, font_size, **kwargs):
    button = ctk.CTkButton(
        parent,
        width=width,
        height=height,
        text=text,
        font=ctk.CTkFont(family=config_utils.FONT_FAMILY, size=font_size),
        **kwargs
    )
    
    return button

def create_entry(parent, width, height, font_size, text_color, corner_radius, placeholder_text, **kwargs):
    entry = ctk.CTkEntry(
        parent,
        width=width,
        height=height,
        font=ctk.CTkFont(family=config_utils.FONT_FAMILY, size=font_size),
        corner_radius=corner_radius,
        placeholder_text=placeholder_text,
        text_color=text_color,
        **kwargs
    )
    
    return entry

def create_cbb(parent, width, height, font_size, values, variable, **kwargs):
    combobox = ctk.CTkComboBox(
        parent,
        width=width,
        height=height,
        font=ctk.CTkFont(family=config_utils.FONT_FAMILY, size=font_size),
        values=values,
        variable=variable,
        **kwargs
    )
    
    return combobox
