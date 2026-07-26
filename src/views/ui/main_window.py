import customtkinter as ctk
from utils import config
from .home_screen import HomeScreen
from .selection_screen import SelectionScreen
from .learning_screen import LearningScreen


# App controller
class FingerLingoApp(ctk.CTk):
    def __init__(self):
        super().__init__(fg_color=config.MAIN_BACKGROUND_COLOR)
        self.title(config.APP_TITLE)
        self.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")

        self.current_screen = None
        self.show_home_screen()

    def show_home_screen(self):
        if self.current_screen is not None:
            self.current_screen.destroy()

        # Clicking "Let's Learn" goes to the Selection Screen
        self.current_screen = HomeScreen(parent=self, on_start_click=self.show_selection_screen)
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
