import customtkinter as ctk
from utils import config
from .home_screen import HomeScreen
from .selection_screen import SelectionScreen
from .lesson_screen import LearningScreen
from .quiz_screen import QuizScreen

# App controller
class FingerLingoApp(ctk.CTk):
    def __init__(self):
        super().__init__(fg_color=config.MAIN_BACKGROUND_COLOR)
        self.title(config.APP_TITLE)
        self.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")

        self.progress_manager = None  # Placeholder for the progress manager instance
        self.current_screen = None
        self.show_home_screen()

    def show_home_screen(self):
        if self.current_screen is not None:
            self.current_screen.destroy()

        # Clicking "Let's Learn" goes to the Selection Screen
        self.current_screen = HomeScreen(
            parent=self, 
            on_start_click=self.show_selection_screen,
            on_quiz_click=self.start_quiz_screen)
        self.current_screen.pack(fill="both", expand=True)  

    # After clicking "Let's Learn"
    def show_selection_screen(self):
        if self.current_screen is not None:
            self.current_screen.destroy()

        # Pass the next step (learning screen) and the back step (home screen)
        self.current_screen = SelectionScreen(
            parent=self,
            on_lesson_selected=self.show_learning_screen,
            on_back_click=self.show_home_screen
        )
        self.current_screen.pack(fill="both", expand=True)

    # After choosing on the selection_screen
    def show_learning_screen(self, lesson_name):
        if self.current_screen is not None:
            self.current_screen.destroy()

        self.current_screen = LearningScreen(
            parent=self,
            lesson_name=lesson_name,
            on_back_click=self.show_selection_screen
        )
        self.current_screen.pack(fill="both", expand=True)

        print(f"Starting camera feed for lesson: {lesson_name}")

    def start_quiz_screen(self):
        if self.current_screen is not None:
            self.current_screen.destroy()

        self.current_screen = QuizScreen(
            parent=self,
            on_start_quiz=self.start_quiz_lesson,
            on_back_click=self.show_home_screen,
            progress_manager=self.progress_manager  # Pass the progress manager to the quiz screen
        )
        self.current_screen.pack(fill="both", expand=True)

    def start_quiz_lesson(self, lesson_name):
        if self.current_screen is not None:
            self.current_screen.destroy()

        self.current_screen = LearningScreen(
            parent=self,
            lesson_name=lesson_name,
            on_back_click=self.start_quiz_screen,
            is_quiz_mode=True 
        )
        self.current_screen.pack(fill="both", expand=True)
        print(f"Starting quiz camera feed for lesson: {lesson_name}")

