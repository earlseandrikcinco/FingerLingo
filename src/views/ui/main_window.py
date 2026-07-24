from pathlib import Path
import customtkinter as ctk

#COLOR PALETTE
MAIN_BACKGROUND_COLOR = "#00674F"
GLASS_BG = "#063A2D"          
GLASS_BORDER = "#1B5E4B"      
TEXT_COLOR = "#FFFFFF"        
SUBTEXT_COLOR = "#A3D9C9"     
BTN_BG = "#06261E"            
BTN_HOVER = "#0F4839"         
BTN_BORDER = "#258067"

CURRENT_DIR = Path(__file__).resolve().parent

#Custom font (Dacosta)
DACOSTA_FONT_PATH = CURRENT_DIR.parent.parent / "assets" / "Dacosta-Yq2M4.ttf" 
ctk.FontManager.load_font(str(DACOSTA_FONT_PATH))

#Custom font (Nunito)
NUNITO_FONT_PATH = CURRENT_DIR.parent.parent / "assets" / "Nunito-Regular.ttf"
ctk.FontManager.load_font(str(NUNITO_FONT_PATH))


ctk.set_appearance_mode("dark") 
ctk.set_default_color_theme("blue")

app = ctk.CTk(fg_color = MAIN_BACKGROUND_COLOR)

app.title("FingerLingo")
app.geometry("900x600")

#defined custom fonts 
title_font = ctk.CTkFont(family="Dacosta", size=52, weight="bold")
subtitle_font = ctk.CTkFont(family="Nunito", size=16)
button_font = ctk.CTkFont(family="Nunito", size=18, weight="bold")

#the glass container frame
glass_card = ctk.CTkFrame(app,
                          fg_color=GLASS_BG,
                          border_color=GLASS_BORDER,
                          border_width=2,
                          corner_radius=24,
                          width=550,
                          height=380)

glass_card.place(relx=0.5, rely=0.5, anchor="center")
glass_card.pack_propagate(False)


#contents of the container frame


appNameLabel = ctk.CTkLabel(glass_card, 
                            text="FingerLingo", 
                            font=title_font,
                            text_color=TEXT_COLOR)

appNameLabel.pack(pady=(45, 5))


subtitleLabel = ctk.CTkLabel(glass_card, 
                               text="Lingo but for your fingers", 
                               font=subtitle_font,
                               text_color=SUBTEXT_COLOR)
subtitleLabel.pack(pady=(0, 40))

start_button = ctk.CTkButton(glass_card, 
                             text="Let's Learn", 
                             font=button_font,
                             fg_color = BTN_BG, 
                             text_color= TEXT_COLOR, 
                             hover_color= BTN_HOVER, 
                             border_width=1.5,  
                             border_color=BTN_BORDER, 
                             corner_radius=25, 
                             width=240,
                             height=50,
                             command=lambda: print("ts where the magic happens twin"))

start_button.pack(pady=10)

app.mainloop()