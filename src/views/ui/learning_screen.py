import customtkinter as ctk
import cv2
from PIL import Image
from .base_screen import BaseScreen
from src.utils import config
from src.models.camera import Camera
from src.models.hand_detector import HandDetector


# Seen after selection_screen
class LearningScreen(BaseScreen):
    def __init__(self, parent, lesson_name, on_back_click):
        super().__init__(parent)
        self.lesson_name = lesson_name
        self.on_back_click = on_back_click

        # Initialize the assets
        self.camera = Camera()
        self.detector = HandDetector()

        # Build the UI
        self.title = ctk.CTkLabel(
            self, text=f"Lesson: {self.lesson_name}",
            font=self.title_font, text_color=config.TEXT_COLOR
        )
        self.title.pack(pady=(20, 5))

        self.sign_label = ctk.CTkLabel(
            self, text="Show a sign...",
            font=self.button_font, text_color=config.SUBTEXT_COLOR
        )
        self.sign_label.pack(pady=(0, 10))

        # This label will hold the video frames
        self.video_label = ctk.CTkLabel(self, text="")
        self.video_label.pack(expand=True)

        self.back_btn = ctk.CTkButton(
            self, text="End Lesson", font=self.button_font,
            fg_color=config.BTN_BG, hover_color=config.BTN_HOVER,
            command=self._clean_and_go_back
        )
        self.back_btn.pack(pady=20)

        # Start the video loop
        self.loop_id = None
        self._update_frame()

    def _update_frame(self):
        # frame from the Camera class
        frame = self.camera.get_frame()

        if frame is not None:
            # Run the MediaPipe logic
            results = self.detector.detect(frame)
            self.detector.draw(frame, results)

            fingers = self.detector.get_raised_fingers(frame, results)
            sign = self.detector.get_stable_sign_label(fingers)

            # Updates the text on the screen
            self.sign_label.configure(text=f"Detected: {sign}")

            # convert OpenCV BGR to Tkinter-friendly RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Convert array to PIL Image, then to CTkImage
            pil_image = Image.fromarray(rgb_frame)
            ctk_image = ctk.CTkImage(
                light_image=pil_image,
                dark_image=pil_image,
                size=(640, 480)  # Lock the video size
            )

            # put the new image onto the label
            self.video_label.configure(image=ctk_image)

        # Tell Tkinter to run this function again in 15ms (~60 FPS)
        self.loop_id = self.after(15, self._update_frame)

    def _clean_and_go_back(self):
        # IMPORTANT: Stop the loop and turn off the webcam light
        if self.loop_id:
            self.after_cancel(self.loop_id)

        self.camera.release()
        self.detector.close()

        self.on_back_click()
