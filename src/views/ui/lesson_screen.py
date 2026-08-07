import os
import customtkinter as ctk
import cv2
from PIL import Image
from .base_screen import BaseScreen
from utils import config
from models.camera import Camera
from models.hand_detector import HandDetector


class LearningScreen(BaseScreen):
    def __init__(self, parent, lesson_name, on_back_click, progress_manager=None, is_quiz_mode=False):
        super().__init__(parent)
        self.lesson_name = lesson_name
        self.on_back_click = on_back_click
        self.progress_manager = progress_manager
        self.is_quiz_mode = is_quiz_mode

        self.letters = config.LESSONS.get(lesson_name, [])
        self.total_cards = len(self.letters)
        self.current_index = 0
        self.cards_learnt = 0

        self.match_streak = 0
        self.state = "preview"  # "preview" | "detecting" | "card_success" | "complete"
        self.loop_id = None

        # --- ASSET CACHE (Load and store images in a dictionary) ---
        self.image_cache = {}

        # Shared hardware instances
        self.camera = Camera()
        self.detector = HandDetector()

        # Pre-cache lesson assets immediately to ensure instant UI transitions
        self._precache_lesson_images()

        # --- Main Container Card ---
        self.glass_card = ctk.CTkFrame(
            self, fg_color=config.GLASS_BG, border_color=config.GLASS_BORDER,
            border_width=2, corner_radius=24, width=640, height=620
        )
        self.glass_card.place(relx=0.5, rely=0.5, anchor="center")
        self.glass_card.pack_propagate(False)

        # --- Top Progress Header ---
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
        self.lesson_progress_bar.pack(fill="x", padx=30, pady=(10, 10))

        # Swappable Content Container
        self.content_frame = ctk.CTkFrame(self.glass_card, fg_color="transparent")
        self.content_frame.pack(expand=True, fill="both", padx=20)

        # Build sub-views
        self._build_preview_widgets()
        self._build_camera_widgets()
        self._build_card_success_widgets()

        self._update_progress_ui()

        # Bottom Navigation
        self.bottom_nav = ctk.CTkFrame(self.glass_card, fg_color="transparent")
        self.bottom_nav.pack(pady=15, padx=20, fill="x")

        self.back_btn = ctk.CTkButton(
            self.bottom_nav, text="End Lesson", font=self.button_font,
            fg_color="transparent", text_color=config.TEXT_COLOR,
            hover_color=config.BTN_HOVER, border_width=2,
            border_color=config.BTN_BORDER, corner_radius=25, height=40,
            command=self._clean_and_go_back
        )
        self.back_btn.pack(side="left", expand=True, padx=10)

        self.top_level = self.winfo_toplevel()
        self.escape_bind_id = self.top_level.bind("<Escape>", lambda event: self._clean_and_go_back())

        if not self.letters:
            self._show_lesson_complete(empty=True)
        else:
            self._show_preview_card()

    # --- Asset Path & Caching Helpers ---

    def _get_asset_path(self, relative_filename):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        assets_dir = os.path.abspath(os.path.join(base_dir, "..", "..", "assets"))
        return os.path.join(assets_dir, relative_filename)

    def _precache_lesson_images(self):
        """Loads all images into RAM at startup so card switching is instant."""
        for item in self.letters:
            img_name = item.get("image")
            if img_name:
                path = self._get_asset_path(os.path.join("lesson_images", img_name))
                if os.path.exists(path):
                    pil_img = Image.open(path)
                    # Cache both preview size and small reference size
                    self.image_cache[f"{img_name}_large"] = ctk.CTkImage(
                        light_image=pil_img, dark_image=pil_img, size=(200, 200)
                    )
                    self.image_cache[f"{img_name}_small"] = ctk.CTkImage(
                        light_image=pil_img, dark_image=pil_img, size=(130, 130)
                    )

    def _update_progress_ui(self):
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
        self.preview_letter_label.pack(pady=(10, 5))

        self.preview_image_label = ctk.CTkLabel(self.preview_frame, text="")
        self.preview_image_label.pack(pady=10)

        self.preview_instruction_label = ctk.CTkLabel(self.preview_frame, text="", font=self.subtitle_font,
                                                      text_color=config.SUBTEXT_COLOR)
        self.preview_instruction_label.pack(pady=(5, 10))

        self.ready_btn = ctk.CTkButton(
            self.preview_frame, text="I'm Ready", font=self.button_font,
            fg_color=config.BTN_BG, text_color=config.TEXT_COLOR,
            corner_radius=25, width=200, height=42, command=self._start_detecting
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
        self.hold_progress.pack(pady=(2, 8))

        self.skip_btn = ctk.CTkButton(
            self.camera_frame, text="Skip for Now", font=self.button_font,
            fg_color="transparent", text_color="#FF9800", hover_color="#333333",
            border_width=1, border_color="#FF9800", corner_radius=25, height=32,
            command=self._skip_card
        )
        self.skip_btn.pack(pady=(4, 0))

    def _build_card_success_widgets(self):
        """The 'Good Job!' Transition Screen."""
        self.success_card_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")

        self.success_title = ctk.CTkLabel(
            self.success_card_frame, text="🎉 Good Job!",
            font=self.title_font, text_color="#4CAF50"
        )
        self.success_title.pack(pady=(15, 5))

        self.success_subtitle = ctk.CTkLabel(
            self.success_card_frame, text="",
            font=self.subtitle_font, text_color=config.TEXT_COLOR
        )
        self.success_subtitle.pack(pady=(0, 20))

        # Button Group for Options
        self.continue_btn = ctk.CTkButton(
            self.success_card_frame, text="Continue to Next Sign", font=self.button_font,
            fg_color="#4CAF50", text_color="#FFFFFF", hover_color="#388E3C",
            corner_radius=25, width=240, height=45,
            command=self._advance_to_next
        )
        self.continue_btn.pack(pady=8)

        self.retry_btn = ctk.CTkButton(
            self.success_card_frame, text="Practice Again (Reset)", font=self.button_font,
            fg_color="transparent", text_color=config.TEXT_COLOR,
            hover_color=config.BTN_HOVER, border_width=2,
            border_color=config.BTN_BORDER, corner_radius=25, width=240, height=40,
            command=self._retry_current_card
        )
        self.retry_btn.pack(pady=8)

    # --- Screen View Transitions ---

    def _hide_all_frames(self):
        self.preview_frame.pack_forget()
        self.camera_frame.pack_forget()
        self.success_card_frame.pack_forget()

    def _show_preview_card(self):
        self.state = "preview"
        self.match_streak = 0

        self._hide_all_frames()
        self.preview_frame.pack(expand=True, fill="both")

        letter_data = self.letters[self.current_index]
        letter = letter_data["letter"]

        if self.is_quiz_mode:
            self.preview_letter_label.configure(text=f"Quiz Sign: {letter}")
            self.preview_instruction_label.configure(text="Test your memory! Perform the sign without hints.")
            self.preview_image_label.configure(image=None, text="?", font=("Arial", 64))
        else:
            self.preview_letter_label.configure(text=f"Letter {letter}")
            self.preview_instruction_label.configure(text=f"Get ready to sign the letter {letter}")

            img_key = f"{letter_data.get('image')}_large"
            if img_key in self.image_cache and self.image_cache[img_key]:
                self.preview_image_label.configure(image=self.image_cache[img_key], text="")
            else:
                self.preview_image_label.configure(image=None, text=letter, font=self.title_font)

    def _start_detecting(self):
            self.state = "detecting"
            self.match_streak = 0
            self.hold_progress.set(0.0)

            self._hide_all_frames()
            self.camera_frame.pack(expand=True, fill="both")

            letter_data = self.letters[self.current_index]
            letter = letter_data["letter"]

            # QUIZ MODE ADJUSTMENTS
            if self.is_quiz_mode:
                self.target_label.configure(text=f"Quiz Target: {letter}")
                self.reference_image_label.pack_forget()  # Completely hides the widget frame
            else:
                self.target_label.configure(text=f"Show: {letter}")
                self.reference_image_label.pack(side="left", padx=(0, 15)) # Shows it if not in quiz mode
                
                img_key = f"{letter_data.get('image')}_small"
                if img_key in self.image_cache and self.image_cache[img_key]:
                    self.reference_image_label.configure(image=self.image_cache[img_key], text="")
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

    # --- Success, Skip, and Retry Actions ---

    def _on_correct_sign(self):
        """Triggered upon successful gesture hold."""
        if self.loop_id:
            self.after_cancel(self.loop_id)
            self.loop_id = None

        self.state = "card_success"

        # Increment learnt count
        self.cards_learnt += 1
        self._update_progress_ui()

        # FUTURE: self.progress_manager.mark_as_learnt(letter)

        self._show_card_success_screen()

    def _show_card_success_screen(self):
        self._hide_all_frames()
        self.success_card_frame.pack(expand=True, fill="both")

        current_letter = self.letters[self.current_index]["letter"]
        self.success_subtitle.configure(text=f"You successfully signed '{current_letter}'!")

        # Update next button text dynamically
        if self.current_index + 1 < self.total_cards:
            next_letter = self.letters[self.current_index + 1]["letter"]
            self.continue_btn.configure(text=f"Continue to '{next_letter}'")
        else:
            self.continue_btn.configure(text="Finish Lesson 🎉")

    def _retry_current_card(self):
        """Resets status from 'learnt' back to 'learning' and restarts detection."""
        if self.cards_learnt > 0:
            self.cards_learnt -= 1
            self._update_progress_ui()

        # FUTURE: self.progress_manager.mark_as_learning(letter)

        # Reset streak and jump straight back into detection mode
        self._start_detecting()

    def _skip_card(self):
        if self.loop_id:
            self.after_cancel(self.loop_id)
            self.loop_id = None

        self.state = "card_success"
        # Skip doesn't increment self.cards_learnt
        self._advance_to_next()

    def _advance_to_next(self):
        self.current_index += 1
        if self.current_index >= self.total_cards:
            self._show_lesson_complete()
        else:
            self._show_preview_card()

    def _show_lesson_complete(self, empty=False):
        self.state = "complete"
        self._hide_all_frames()
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
        self.preview_instruction_label.configure(
            text=f"You learnt {self.cards_learnt} out of {self.total_cards} signs.")
        self.ready_btn.configure(text="Back to Lessons", command=self._clean_and_go_back)

    # --- Cleanup ---

    def _clean_and_go_back(self):
        if self.loop_id:
            self.after_cancel(self.loop_id)
            self.loop_id = None
        try:
            self.top_level.unbind("<Escape>")
        except Exception:
            pass
        self.camera.release()
        self.detector.close()
        self.on_back_click()