import customtkinter as ctk
from .base_screen import BaseScreen
from src.utils import config


# Seen after "Let's Learn" button from home_screen
class SelectionScreen(BaseScreen):
    def __init__(self, parent, on_lesson_selected, on_back_click):
        super().__init__(parent)
        self.on_lesson_selected = on_lesson_selected

        # Screen Title
        self.title = ctk.CTkLabel(
            self, text="Choose Your Lesson",
            font=self.title_font, text_color=config.TEXT_COLOR
        )
        self.title.pack(pady=(30, 20))

        # Tabview
        self.tab_view = ctk.CTkTabview(
            self, width=600, height=400,
            fg_color=config.GLASS_BG,
            segmented_button_selected_color=config.BTN_BORDER,
            segmented_button_selected_hover_color=config.BTN_HOVER,
            segmented_button_unselected_color=config.BTN_BG
        )
        self.tab_view.pack(pady=10)

        # Add the Tabs
        self.tab_view.add("Alphabet")
        self.tab_view.add("Numbers")
        self.tab_view.add("Greetings")

        # Define the lessons
        alphabet_lessons = ["A - E", "F - J", "K - O",
                            "P - T", "U - Z"]
        digit_lessons = ["0 - 10", "11 - 15", "16 - 19",
                         "20 - 29", "30 - 45", "46 - 60",
                         "61 - 75", "76 - 90", "91 - 100"]
        greeting_lessons = ["Hello / Bye", "Please / Thanks", "How are you?",
                            "Yes / No"]

        # Build the tabs
        self._build_tab_grid("Alphabet", alphabet_lessons)
        self._build_tab_grid("Numbers", digit_lessons)
        self._build_tab_grid("Greetings", greeting_lessons)

        # Back Button
        self.back_btn = ctk.CTkButton(
            self, text="Back to Menu", font=self.button_font,
            fg_color="transparent", border_width=2, border_color=config.BTN_BORDER,
            width=200, height=40, command=on_back_click
        )
        self.back_btn.pack(pady=(20, 0))

    # --- HELPER FUNCTION ---

    def _build_tab_grid(self, tab_name, lessons_array):
        # Grab the specific tab based on the string passed in
        tab = self.tab_view.tab(tab_name)

        # Create the container
        grid_container = ctk.CTkFrame(tab, fg_color="transparent")
        grid_container.pack(expand=True)

        # Loop through the array that was passed in
        for index, lesson_name in enumerate(lessons_array):
            row = index // 3
            col = index % 3

            btn = ctk.CTkButton(
                grid_container,
                text=lesson_name,
                font=self.button_font,
                fg_color=config.BTN_BG,
                hover_color=config.BTN_HOVER,
                width=150, height=60, corner_radius=15,
                command=lambda name=lesson_name: self.on_lesson_selected(name)
            )
            btn.grid(row=row, column=col, padx=15, pady=15)
