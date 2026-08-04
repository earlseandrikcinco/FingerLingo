import customtkinter as ctk
from .base_screen import BaseScreen
from utils import config

class QuizScreen(BaseScreen):
    def __init__(self, parent, on_start_quiz, on_back_click, progress_manager=None):
        super().__init__(parent)
        self.on_start_quiz = on_start_quiz
        self.progress_manager = progress_manager

        self.title = ctk.CTkLabel(
            self, text="Quiz",
            font=self.title_font, text_color=config.TEXT_COLOR
        )
        self.title.pack(pady=(30, 10))

        self.subtitle = ctk.CTkLabel(
            self, text="Review and test your sign language memory!",
            font=self.subtitle_font, text_color=config.TEXT_COLOR

        )
        self.subtitle.pack(pady=(0, 20))

        #The main scrollable container for available quizzes
        self.scroll_container = ctk.CTkScrollableFrame(
            self, width=600, height=400,
            fg_color=config.GLASS_BG,
            border_width=2, border_color=config.BTN_BORDER
        )
        self.scroll_container.pack(pady=10)

        self._populate_quiz_inbox()

        self.back_btn = ctk.CTkButton(
            self, text="Back to Menu", font=self.button_font,
            fg_color="transparent", border_width=2, border_color=config.BTN_BORDER,
            width=200, height=40, command=on_back_click
        )
        self.back_btn.pack(pady=(15, 0))

    def _populate_quiz_inbox(self):
        ready_quizzes = []

        # Find all lessons where user has unlocked/completed cards
        if self.progress_manager:
            for lesson_name, cards in config.LESSONS.items():
                learnt_count = self.progress_manager.get_learnt_count(lesson_name)
                total_cards = len(cards)
                
                # Unlocks if user has finished or started learning the lesson
                if learnt_count > 0:
                    ready_quizzes.append({
                        "name": lesson_name,
                        "progress": f"{learnt_count}/{total_cards}",
                        "is_complete": learnt_count == total_cards
                    })

        #TEMPORARY MOCK FOR TESTING FRONTEND UI 
        if not ready_quizzes:
            # Comment this block out once progress_manager is fully connected
            ready_quizzes = [
                {"name": "A - E", "progress": "5/5", "is_complete": True},
                {"name": "F - J", "progress": "3/5", "is_complete": False},
                {"name": "0 - 10", "progress": "11/11", "is_complete": True},
            ]

        #CASE 1: EMPTY STATE
        if not ready_quizzes:
            empty_frame = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
            empty_frame.pack(expand=True, fill="both", pady=80)

            empty_icon = ctk.CTkLabel(
                empty_frame, text="📥",
                font=("Arial", 48)
            )
            empty_icon.pack(pady=(0, 10))

            empty_text = ctk.CTkLabel(
                empty_frame, text="Your Quiz Inbox is Empty!",
                font=self.title_font, text_color=config.TEXT_COLOR
            )
            empty_text.pack(pady=5)

            empty_sub = ctk.CTkLabel(
                empty_frame, 
                text="Complete at least one lesson from 'Choose Your Lesson' to unlock quizzes.",
                font=self.subtitle_font, text_color=config.SUBTEXT_COLOR
            )
            empty_sub.pack(pady=5)
            return

        #CASE 2: POPULATED INBOX ITEMS 
        for item in ready_quizzes:
            quiz_card = ctk.CTkFrame(
                self.scroll_container,
                fg_color=config.BTN_BG,
                border_color=config.BTN_BORDER,
                border_width=1,
                corner_radius=12,
                height=65
            )
            quiz_card.pack(fill="x", padx=15, pady=8)
            quiz_card.pack_propagate(False)

            # Left side: Lesson Name & Status
            info_frame = ctk.CTkFrame(quiz_card, fg_color="transparent")
            info_frame.pack(side="left", padx=15, pady=10)

            title_lbl = ctk.CTkLabel(
                info_frame, text=f"Quiz: {item['name']}",
                font=self.button_font, text_color=config.TEXT_COLOR,
                anchor="w"
            )
            title_lbl.pack(anchor="w")

            status_lbl = ctk.CTkLabel(
                info_frame, text=f"Learned: {item['progress']} signs",
                font=self.subtitle_font, text_color=config.SUBTEXT_COLOR,
                anchor="w"
            )
            status_lbl.pack(anchor="w")

            # Right side: Start Quiz Action
            start_btn = ctk.CTkButton(
                quiz_card, text="Start Quiz",
                font=self.button_font,
                fg_color=config.BTN_BORDER,
                hover_color=config.BTN_HOVER,
                width=110, height=35,
                command=lambda name=item['name']: self.on_start_quiz(name)
            )
            start_btn.pack(side="right", padx=15)