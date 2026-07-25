from pathlib import Path
import customtkinter as ctk
from views.ui.main_window import FingerLingoApp


# The runnable file
def setup_app():
    # Finds the current directory (the 'src' folder)
    current_dir = Path(__file__).resolve().parent

    # Map exactly where the fonts are
    dacosta_path = current_dir / "assets" / "Dacosta-Yq2M4.ttf"
    nunito_path = current_dir / "assets" / "Nunito-Regular.ttf"

    # Load them into CustomTkinter
    ctk.FontManager.load_font(str(dacosta_path))
    ctk.FontManager.load_font(str(nunito_path))

    # Set the global theme
    ctk.set_appearance_mode("dark")


if __name__ == "__main__":
    setup_app()  # Load everything
    app = FingerLingoApp()  # Build the app window
    app.mainloop()  # Start
