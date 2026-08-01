import customtkinter as ctk
from .base_screen import BaseScreen
from src.utils import config


# Seen after "Let's Learn" button from home_screen
class SelectionScreen(BaseScreen):
    def __init__(self, parent, on_lesson_selected, on_back_click, progress_manager=None):
        super().__init__(parent)
        self.on_lesson_selected = on_lesson_selected
        self.progress_manager = progress_manager

        # Screen Title
        self.title = ctk.CTkLabel(
            self, text="Choose Your Lesson",
            font=self.title_font, text_color=config.TEXT_COLOR
        )
        self.title.pack(pady=(30, 20))

        # Tabview
        self.tab_view = ctk.CTkTabview(
            self, width=620, height=420,
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
        self.back_btn.pack(pady=(15, 0))

    # --- HELPER FUNCTION ---

    def _build_tab_grid(self, tab_name, lessons_array):
        tab = self.tab_view.tab(tab_name)

        # Scrollable container in case a category has many lessons
        grid_container = ctk.CTkFrame(tab, fg_color="transparent")
        grid_container.pack(expand=True, fill="both", padx=10, pady=10)

        # --- CENTER THE GRID COLUMNS ---
        for col_idx in range(3):
            grid_container.grid_columnconfigure(col_idx, weight=1)

        for index, lesson_name in enumerate(lessons_array):
            row = index // 3
            col = index % 3

            # Determine total cards (n)
            lesson_cards = config.LESSONS.get(lesson_name, [])
            total_cards = len(lesson_cards)

            # Fetch learnt count from progress_manager (or default to 0)
            if self.progress_manager:
                learnt_count = self.progress_manager.get_learnt_count(lesson_name)
            else:
                learnt_count = 0

            progress_str = f"{learnt_count}/{total_cards}"

            # Create Card Frame
            card = ctk.CTkFrame(
                grid_container,
                fg_color=config.BTN_BG,
                border_color=config.BTN_BORDER,
                border_width=1,
                corner_radius=15,
                width=160,
                height=75
            )
            # Grid the card inside its column
            card.grid(row=row, column=col, padx=10, pady=10)
            card.grid_propagate(False)

            is_complete = (learnt_count == total_cards and total_cards > 0)
            progress_color = "#4CAF50" if is_complete else config.SUBTEXT_COLOR

            progress_label = ctk.CTkLabel(
                card,
                text=progress_str,
                font=self.subtitle_font,
                text_color=progress_color
            )
            progress_label.pack(pady=(6, 0))

            btn = ctk.CTkButton(
                card,
                text=lesson_name,
                font=self.button_font,
                fg_color="transparent",
                hover_color=config.BTN_HOVER,
                text_color=config.TEXT_COLOR,
                command=lambda name=lesson_name: self.on_lesson_selected(name)
            )
            btn.pack(fill="both", expand=True, padx=2, pady=(0, 4))
