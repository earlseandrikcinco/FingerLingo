import os
import customtkinter as ctk
import cv2
from PIL import Image
from .base_screen import BaseScreen
from utils import config
from models.camera import Camera
from models.hand_detector import HandDetector


class LearningScreen(BaseScreen):
    def __init__(self, parent, lesson_name, on_back_click, progress_manager=None):
        super().__init__(parent)
        self.lesson_name = lesson_name
        self.on_back_click = on_back_click

        # In the future, this manager will load/save from JSON/SQLite
        self.progress_manager = progress_manager

        # We load the static letters, but we'll track progress dynamically
        self.letters = config.LESSONS.get(lesson_name, [])
        self.total_cards = len(self.letters)
        self.current_index = 0

        # Track how many the user has successfully learnt in this session/overall
        # (For now we start at 0, but later we will load this from the progress_manager)
        self.cards_learnt = 0

        self.match_streak = 0
        self.state = "preview"
        self.loop_id = None
        self.success_timer_id = None

        self.camera = Camera()
        self.detector = HandDetector()

        # --- Main Container Card ---
        self.glass_card = ctk.CTkFrame(
            self, fg_color=config.GLASS_BG, border_color=config.GLASS_BORDER,
            border_width=2, corner_radius=24, width=630, height=620
        )
        self.glass_card.place(relx=0.5, rely=0.5, anchor="center")
        self.glass_card.pack_propagate(False)

        # --- Top Progress Bar & Header ---
        self.header_frame = ctk.CTkFrame(self.glass_card, fg_color="transparent")
        self.header_frame.pack(fill="x", pady=(20, 0), padx=30)

        self.title = ctk.CTkLabel(
            self.header_frame, text=f"Lesson: {self.lesson_name}",
            font=self.title_font, text_color=config.TEXT_COLOR
        )
        self.title.pack(side="left")

        self.progress_text = ctk.CTkLabel(
            self.header_frame, text="0%", font=self.subtitle_font, text_color=config.SUBTEXT_COLOR
        )
        self.progress_text.pack(side="right")

        self.lesson_progress_bar = ctk.CTkProgressBar(
            self.glass_card, height=8, progress_color="#4CAF50", fg_color="#333333"
        )
        self.lesson_progress_bar.set(0.0)
        self.lesson_progress_bar.pack(fill="x", padx=30, pady=(10, 15))

        # Swappable Content Container
        self.content_frame = ctk.CTkFrame(self.glass_card, fg_color="transparent")
        self.content_frame.pack(expand=True, fill="both", padx=20)

        self._build_preview_widgets()
        self._build_camera_widgets()

        # Update initial progress UI
        self._update_progress_ui()

        # Bottom Buttons
        self.bottom_nav = ctk.CTkFrame(self.glass_card, fg_color="transparent")
        self.bottom_nav.pack(pady=15, padx=20, fill="x")

        self.back_btn = ctk.CTkButton(
            self.bottom_nav, text="End Lesson", font=self.button_font,
            fg_color=config.BTN_BG, text_color=config.TEXT_COLOR,
            hover_color=config.BTN_HOVER, border_width=2,
            border_color=config.BTN_BORDER, corner_radius=25, height=42,
            command=self._clean_and_go_back
        )
        self.back_btn.pack(side="left", expand=True, padx=10)

        self.top_level = self.winfo_toplevel()
        self.escape_bind_id = self.top_level.bind("<Escape>", lambda event: self._clean_and_go_back())

        if not self.letters:
            self._show_lesson_complete(empty=True)
        else:
            self._show_preview_card()

    def _get_asset_path(self, relative_filename):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        assets_dir = os.path.abspath(os.path.join(base_dir, "..", "..", "assets"))
        return os.path.join(assets_dir, relative_filename)

    def _update_progress_ui(self):
        """Updates the top progress bar and text based on learnt cards."""
        if self.total_cards > 0:
            ratio = self.cards_learnt / self.total_cards
            percentage = int(ratio * 100)
            self.lesson_progress_bar.set(ratio)
            self.progress_text.configure(text=f"{self.cards_learnt}/{self.total_cards} ({percentage}%)")

    # --- Widget Builders ---

    def _build_preview_widgets(self):
        self.preview_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")

        self.preview_letter_label = ctk.CTkLabel(self.preview_frame, text="", font=self.title_font,
                                                 text_color=config.TEXT_COLOR)
        self.preview_letter_label.pack(pady=(15, 5))

        self.preview_image_label = ctk.CTkLabel(self.preview_frame, text="")
        self.preview_image_label.pack(pady=10)

        self.preview_instruction_label = ctk.CTkLabel(self.preview_frame, text="", font=self.subtitle_font,
                                                      text_color=config.SUBTEXT_COLOR)
        self.preview_instruction_label.pack(pady=(5, 15))

        self.ready_btn = ctk.CTkButton(
            self.preview_frame, text="I'm Ready", font=self.button_font,
            fg_color=config.BTN_BG, text_color=config.TEXT_COLOR,
            corner_radius=25, width=200, height=45, command=self._start_detecting
        )
        self.ready_btn.pack(pady=10)

    def _build_camera_widgets(self):
        self.camera_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")

        self.target_label = ctk.CTkLabel(self.camera_frame, text="", font=self.button_font,
                                         text_color=config.TEXT_COLOR)
        self.target_label.pack(pady=(5, 5))

        self.detect_row = ctk.CTkFrame(self.camera_frame, fg_color="transparent")
        self.detect_row.pack(pady=5)

        self.reference_image_label = ctk.CTkLabel(self.detect_row, text="")
        self.reference_image_label.pack(side="left", padx=(0, 15))

        self.video_label = ctk.CTkLabel(self.detect_row, text="")
        self.video_label.pack(side="left")

        self.sign_label = ctk.CTkLabel(self.camera_frame, text="Show a sign...", font=self.subtitle_font,
                                       text_color=config.SUBTEXT_COLOR)
        self.sign_label.pack(pady=(5, 2))

        self.hold_progress = ctk.CTkProgressBar(self.camera_frame, width=300, height=10, progress_color="#4CAF50",
                                                fg_color="#333333")
        self.hold_progress.set(0.0)
        self.hold_progress.pack(pady=(2, 10))

        # --- The Skip Button ---
        self.skip_btn = ctk.CTkButton(
            self.camera_frame, text="Skip for Now", font=self.button_font,
            fg_color="transparent", text_color="#FF9800", hover_color="#333333",
            border_width=1, border_color="#FF9800", corner_radius=25, height=35,
            command=self._skip_card
        )
        self.skip_btn.pack(pady=(5, 0))

    # --- State Transitions ---

    def _show_preview_card(self):
        self.state = "preview"
        self.match_streak = 0
        self.camera_frame.pack_forget()
        self.preview_frame.pack(expand=True, fill="both")

        letter_data = self.letters[self.current_index]
        letter = letter_data["letter"]

        self.preview_letter_label.configure(text=f"Letter {letter}")
        self.preview_instruction_label.configure(text=f"Get ready to sign the letter {letter}")

        image_path = self._get_asset_path(os.path.join("lesson_images", letter_data.get("image", "")))
        if letter_data.get("image") and os.path.exists(image_path):
            pil_image = Image.open(image_path)
            ctk_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(200, 200))
            self.preview_image_label.configure(image=ctk_image, text="")
        else:
            self.preview_image_label.configure(image=None, text=letter, font=self.title_font)

    def _start_detecting(self):
        self.state = "detecting"
        self.match_streak = 0
        self.hold_progress.set(0.0)

        self.preview_frame.pack_forget()
        self.camera_frame.pack(expand=True, fill="both")

        letter_data = self.letters[self.current_index]
        letter = letter_data["letter"]
        self.target_label.configure(text=f"Show: {letter}")

        image_path = self._get_asset_path(os.path.join("lesson_images", letter_data.get("image", "")))
        if letter_data.get("image") and os.path.exists(image_path):
            pil_image = Image.open(image_path)
            ctk_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(140, 140))
            self.reference_image_label.configure(image=ctk_image, text="")
        else:
            self.reference_image_label.configure(image=None, text=letter, font=self.title_font)

        self._update_frame()

    def _update_frame(self):
        if self.state != "detecting":
            return

        frame = self.camera.get_frame()
        if frame is not None:
            results = self.detector.detect(frame)
            self.detector.draw(frame, results)

            fingers = self.detector.get_raised_fingers(frame, results)
            target_fingers = self.letters[self.current_index].get("target", [])
            is_match = (fingers and fingers == target_fingers)

            if is_match:
                self.match_streak += 1
                self.sign_label.configure(text="Match! Hold it...", text_color="#4CAF50")
            else:
                self.match_streak = 0
                self.sign_label.configure(text="Keep trying...", text_color=config.SUBTEXT_COLOR)

            progress_ratio = min(1.0, self.match_streak / config.SIGN_CONFIRM_FRAMES)
            self.hold_progress.set(progress_ratio)

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_frame)
            ctk_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(380, 285))
            self.video_label.configure(image=ctk_image)

            if self.match_streak >= config.SIGN_CONFIRM_FRAMES:
                self._on_correct_sign()
                return

        self.loop_id = self.after(15, self._update_frame)

    # --- Success & Skip Logic ---

    def _on_correct_sign(self):
        """Triggered when user successfully holds the sign."""
        self.state = "success"
        letter = self.letters[self.current_index]["letter"]
        self.sign_label.configure(text=f"Correct! That's {letter}!", text_color="#4CAF50")
        self.hold_progress.set(1.0)

        # Update progress since they learnt it
        self.cards_learnt += 1
        self._update_progress_ui()

        # FUTURE: self.progress_manager.mark_as_learnt(letter)

        self.success_timer_id = self.after(1200, self._advance_to_next)

    def _skip_card(self):
        """Triggered when the user clicks 'Skip for Now'."""
        self.state = "success"  # Pauses the camera loop safely
        self.sign_label.configure(text="Skipped! We'll try this one later.", text_color="#FF9800")

        # Do NOT increment self.cards_learnt. The bar stays where it is.
        # FUTURE: self.progress_manager.mark_as_skipped(letter)

        self.success_timer_id = self.after(1000, self._advance_to_next)

    def _advance_to_next(self):
        self.current_index += 1
        if self.current_index >= self.total_cards:
            self._show_lesson_complete()
        else:
            self._show_preview_card()

    def _show_lesson_complete(self, empty=False):
        self.state = "complete"
        self.camera_frame.pack_forget()
        self.preview_frame.pack(expand=True, fill="both")

        image_path = self._get_asset_path("congrats.png")
        if os.path.exists(image_path):
            try:
                pil_img = Image.open(image_path)
                ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(180, 180))
                self.preview_image_label.configure(image=ctk_img, text="")
            except Exception:
                self.preview_image_label.configure(image=None, text="Lesson Over")

        self.preview_letter_label.configure(text="Lesson Complete!" if not empty else "No letters configured")

        # Display different text based on if they skipped cards
        if self.cards_learnt == self.total_cards:
            self.preview_instruction_label.configure(text="Perfect score! All signs learnt.")
        else:
            self.preview_instruction_label.configure(
                text=f"You learnt {self.cards_learnt} out of {self.total_cards}. Keep it up!")

        self.ready_btn.configure(text="Back to Lessons", command=self._clean_and_go_back)

    def _clean_and_go_back(self):
        if self.loop_id:
            self.after_cancel(self.loop_id)
            self.loop_id = None
        if self.success_timer_id:
            self.after_cancel(self.success_timer_id)
            self.success_timer_id = None
        try:
            self.top_level.unbind("<Escape>")
        except Exception:
            pass
        self.camera.release()
        self.detector.close()
        self.on_back_click()