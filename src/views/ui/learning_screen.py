import os
import customtkinter as ctk
import cv2
from PIL import Image
from .base_screen import BaseScreen
from utils import config
from models.camera import Camera
from models.hand_detector import HandDetector


class LearningScreen(BaseScreen):
    def __init__(self, parent, lesson_name, on_back_click):
        super().__init__(parent)
        self.lesson_name = lesson_name
        self.on_back_click = on_back_click

        self.letters = config.LESSONS.get(lesson_name, [])
        self.current_index = 0
        self.match_streak = 0
        self.state = "preview"  # "preview" | "detecting" | "success" | "complete"
        self.loop_id = None

# Camera/detector are created once and kept alive for the whole
# lesson so we're not re-opening the webcam between every letter.
# We just don't READ from it while showing the preview card.
        self.camera = Camera()
        self.detector = HandDetector()

        self.glass_card = ctk.CTkFrame(
            self,
            fg_color=config.GLASS_BG,
            border_color=config.GLASS_BORDER,
            border_width=2,
            corner_radius=24,
            width=630,
            height=580
        )
        self.glass_card.place(relx=0.5, rely=0.5, anchor="center")
        self.glass_card.pack_propagate(False)

        self.title = ctk.CTkLabel(
            self.glass_card, text=f"Lesson: {self.lesson_name}",
            font=self.title_font, text_color=config.TEXT_COLOR
        )
        self.title.pack(pady=(25, 2))

# The Container that swaps between preview / camera content
        self.content_frame = ctk.CTkFrame(self.glass_card, fg_color="transparent")
        self.content_frame.pack(expand=True, fill="both", padx=20)

        self._build_preview_widgets()
        self._build_camera_widgets()

        self.back_btn = ctk.CTkButton(
            self.glass_card, text="End Lesson", font=self.button_font,
            fg_color=config.BTN_BG, text_color=config.TEXT_COLOR,
            hover_color=config.BTN_HOVER, border_width=2,
            border_color=config.BTN_BORDER, corner_radius=25,
            width=200, height=42,
            command=self._clean_and_go_back
        )
        self.back_btn.pack(pady=15, padx=20)

        self.winfo_toplevel().bind("<Escape>", lambda event: self._clean_and_go_back())

        if not self.letters:
            self._show_lesson_complete(empty=True)
        else:
            self._show_preview_card()

# widget builders 

    def _build_preview_widgets(self):
        self.preview_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")

        self.preview_letter_label = ctk.CTkLabel(
            self.preview_frame, text="", font=self.title_font, text_color=config.TEXT_COLOR
        )
        self.preview_letter_label.pack(pady=(20, 10))

        self.preview_image_label = ctk.CTkLabel(self.preview_frame, text="")
        self.preview_image_label.pack(pady=10)

        self.preview_instruction_label = ctk.CTkLabel(
            self.preview_frame, text="", font=self.subtitle_font, text_color=config.SUBTEXT_COLOR
        )
        self.preview_instruction_label.pack(pady=(5, 20))

        self.ready_btn = ctk.CTkButton(
            self.preview_frame, text="I'm Ready", font=self.button_font,
            fg_color=config.BTN_BG, text_color=config.TEXT_COLOR,
            hover_color=config.BTN_HOVER, border_width=2, border_color=config.BTN_BORDER,
            corner_radius=25, width=200, height=45,
            command=self._start_detecting
        )
        self.ready_btn.pack(pady=10)

    def _build_camera_widgets(self):
        self.camera_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")

        self.target_label = ctk.CTkLabel(
            self.camera_frame, text="", font=self.button_font, text_color=config.TEXT_COLOR
        )
        self.target_label.pack(pady=(10, 5))

        #this row is for the reference image next to the live camera
        self.detect_row = ctk.CTkFrame(self.camera_frame, fg_color="transparent")
        self.detect_row.pack(pady=5)

        self.reference_image_label = ctk.CTkLabel(self.detect_row, text = "")
        self.reference_image_label.pack(side="left", padx=(0,15))

        self.video_label = ctk.CTkLabel(self.detect_row, text="")
        self.video_label.pack(side="left")

        self.sign_label = ctk.CTkLabel(
            self.camera_frame, text="Show a sign...", font=self.subtitle_font,
            text_color=config.SUBTEXT_COLOR
        )
        self.sign_label.pack(pady=(5, 10))

    def _get_image_path(self, filename):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__)) #src/views/ui
        ASSETS_DIR = os.path.join(BASE_DIR, "..", "..", "assets", "lesson_images")
        return os.path.join(ASSETS_DIR, filename)

 #  state transitions 

    def _show_preview_card(self):
        self.state = "preview"
        self.match_streak = 0

        self.camera_frame.pack_forget()
        self.preview_frame.pack(expand=True, fill="both")

        letter_data = self.letters[self.current_index]
        letter = letter_data["letter"]

        self.preview_letter_label.configure(text=f"Letter {letter}")
        self.preview_instruction_label.configure(text=f"Get ready to sign the letter {letter}")


        image_path = self._get_image_path(letter_data.get("image", ""))
        if letter_data.get("image") and os.path.exists(image_path):
            pil_image = Image.open(image_path)
            ctk_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(220, 220))
            self.preview_image_label.configure(image=ctk_image, text="")
        else:
            # fallback so missing images in the assets/lesson_images folder doesn't crash the app
            self.preview_image_label.configure(image=None, text=letter, font=self.title_font)

    def _start_detecting(self):
        self.state = "detecting"
        self.match_streak = 0

        self.preview_frame.pack_forget()
        self.camera_frame.pack(expand=True, fill="both")

        letter_data = self.letters[self.current_index]
        letter = letter_data["letter"]
        self.target_label.configure(text=f"Show: {letter}")

        image_path = self._get_image_path(letter_data.get("image", ""))
        if letter_data.get("image") and os.path.exists(image_path):
            pil_image = Image.open(image_path)
            ctk_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(150, 150))
            self.reference_image_label.configure(image=ctk_image, text="")
        else:
            self.reference_image_label.configure(image=None, text=letter, font=self.title_font)    

        self._update_frame()

    def _update_frame(self):
        if self.state != "detecting":
            return  # stops the loop and preview/success states don't reschedule

        frame = self.camera.get_frame()

        if frame is not None:
            results = self.detector.detect(frame)
            self.detector.draw(frame, results)

            fingers = self.detector.get_raised_fingers(frame, results)
            target = self.letters[self.current_index]["target"]

            if fingers and fingers == target:
                self.match_streak += 1
                self.sign_label.configure(text="Match! Hold it...", text_color="#4CAF50")
            else:
                self.match_streak = 0
                self.sign_label.configure(text="Not quite! Keep Trying!", text_color=config.SUBTEXT_COLOR)

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_frame)
            ctk_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(400, 300))
            self.video_label.configure(image=ctk_image)

            if self.match_streak >= config.SIGN_CONFIRM_FRAMES:
                self._on_correct_sign()
                return

        self.loop_id = self.after(15, self._update_frame)

    def _on_correct_sign(self):
        self.state = "success"
        letter = self.letters[self.current_index]["letter"]
        self.sign_label.configure(text=f"Correct! That's {letter}", text_color="#4CAF50")
        self.after(1200, self._advance_to_next)

    def _advance_to_next(self):
        self.current_index += 1
        if self.current_index >= len(self.letters):
            self._show_lesson_complete()
        else:
            self._show_preview_card()

    def _show_lesson_complete(self, empty=False):
        self.state = "complete"
        self.camera_frame.pack_forget()
        self.preview_frame.pack(expand=True, fill="both")

        BASE_DIR = os.path.dirname(os.path.abspath(__file__)) #src/views/ui
        ASSETS_DIR = os.path.join(BASE_DIR, "..", "..", "assets") #from views/ui, we go to assets   

        image_path = os.path.join(ASSETS_DIR, "congrats.png")
        if os.path.exists(image_path):
            try:
                pil_img = Image.open(image_path)
                ctk_img = ctk.CTkImage(
                    light_image=pil_img,
                    dark_image=pil_img,
                    size=(200, 200) 
                )
                self.preview_image_label.configure(image=ctk_img, text="")
            except Exception as e:
                print(f"Error loading congrats image: {e}")
                self.preview_image_label.configure(image=None, text="Congratulations!")
        else:
            self.preview_image_label.configure(image=None, text="Congratulations!")

        self.preview_letter_label.configure(text="Lesson Complete!" if not empty else "No letters configured")
        self.preview_instruction_label.configure(text="Nice work! Let's head back to pick another lesson.")
        self.ready_btn.configure(text="Back to Lessons", command=self._clean_and_go_back)

    #  cleanup 

    def _clean_and_go_back(self):
        if self.loop_id:
            self.after_cancel(self.loop_id)

        self.camera.release()
        self.detector.close()

        self.on_back_click()