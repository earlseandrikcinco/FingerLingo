import customtkinter as ctk
from src.utils import config


# Super class for the whole UI
class BaseScreen(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")

        # Using the font names from config
        self.title_font = ctk.CTkFont(family=config.FONT_TITLE, size=52, weight="bold")
        self.subtitle_font = ctk.CTkFont(family=config.FONT_BODY, size=16)
        self.button_font = ctk.CTkFont(family=config.FONT_BODY, size=18, weight="bold")
