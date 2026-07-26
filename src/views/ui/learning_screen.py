import customtkinter as ctk
import cv2
from PIL import Image
from .base_screen import BaseScreen
from utils import config
from models.camera import Camera
from models.hand_detector import HandDetector


# Seen after selection_screen
class LearningScreen(BaseScreen):
    def __init__(self, parent, lesson_name, on_back_click):
        super().__init__(parent)
        self.lesson_name = lesson_name
        self.on_back_click = on_back_click

        # Initialize the assets
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

        # Build the UI
        self.title = ctk.CTkLabel(
            self.glass_card, text=f"Lesson: {self.lesson_name}",
            font=self.title_font, text_color=config.TEXT_COLOR
        )
        self.title.pack(pady=(25, 2))

        self.sign_label = ctk.CTkLabel(
            self.glass_card, text="Show a sign...",
            font=self.button_font, text_color=config.SUBTEXT_COLOR
        )
        self.sign_label.pack(pady=(0, 15))

        #removed "expand=true" so it doesn't push other elements (like the end lessio)
        self.video_label = ctk.CTkLabel(self.glass_card, text="")
        self.video_label.pack(pady=5)


        self.back_btn = ctk.CTkButton(
            self.glass_card, text="End Lesson", font=self.button_font,
            fg_color=config.BTN_BG, text_color=config.TEXT_COLOR,
            hover_color=config.BTN_HOVER, border_width=2,
            border_color=config.BTN_BORDER, corner_radius=25,
            width=200, height=42,
            command=self._clean_and_go_back
        )
        self.back_btn.pack(pady=15, padx=20)

        self.winfo_toplevel().bind("<Escape>", lambda event: self._clean_and_go_back()) #escape button also exits the lesson

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
                size=(400, 300)  # Lock the video size
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
