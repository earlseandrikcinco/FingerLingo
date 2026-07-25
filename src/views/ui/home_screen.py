import customtkinter as ctk
from .base_screen import BaseScreen
from src.utils import config


# Seen upon start of the app
class HomeScreen(BaseScreen): 
    def __init__(self, parent, on_start_click):
        super().__init__(parent) 

        self.glass_card = ctk.CTkFrame(
            self, 
            fg_color=config.GLASS_BG, 
            border_color=config.GLASS_BORDER,
            border_width=2, 
            corner_radius=24, 
            width=550, 
            height=380
        )
        self.glass_card.place(relx=0.5, rely=0.5, anchor="center")
        self.glass_card.pack_propagate(False)

        self.appNameLabel = ctk.CTkLabel(
            self.glass_card, text=config.APP_TITLE, 
            font=self.title_font, text_color=config.TEXT_COLOR
        )
        self.appNameLabel.pack(pady=(45, 5))

        self.subtitleLabel = ctk.CTkLabel(
            self.glass_card, text="Lingo but for your fingers", 
            font=self.subtitle_font, text_color=config.SUBTEXT_COLOR
        )
        self.subtitleLabel.pack(pady=(0, 40))

        self.start_button = ctk.CTkButton(
            self.glass_card, text="Let's Learn", font=self.button_font, 
            fg_color=config.BTN_BG, text_color=config.TEXT_COLOR, 
            hover_color=config.BTN_HOVER, border_width=2, 
            border_color=config.BTN_BORDER, corner_radius=25, 
            width=240, height=50, command=on_start_click 
        )
        self.start_button.pack(pady=10)
