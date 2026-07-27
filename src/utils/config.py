# APP SETTINGS
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 600
APP_TITLE = "FingerLingo"

# COLOR PALETTE
MAIN_BACKGROUND_COLOR = "#00674F"
GLASS_BG = "#063A2D"
GLASS_BORDER = "#1B5E4B"
TEXT_COLOR = "#FFFFFF"
SUBTEXT_COLOR = "#A3D9C9"
BTN_BG = "#06261E"
BTN_HOVER = "#0F4839"
BTN_BORDER = "#258067"

# FONTS
FONT_TITLE = "Dacosta"
FONT_BODY = "Nunito"

# --- Lesson content: each entry is one letter/sign in the lesson ---
# edit again for dynamic, since it won't be as simple as booleans on a list (for example, J and Z are dynamic, and C is unreliable for now)
LESSONS = {
    "A - E": [
        {"letter": "A", "image": "A.png", "target": [True, False, False, False, False]},
        {"letter": "B", "image": "B.png", "target": [False, True, True, True, True]},
        {"letter": "C", "image": "C.png", "target": [False, False, False, False, False]},  # placeholder, unreliable for now
        {"letter": "D", "image": "D.png", "target": [False, True, False, False, False]},
        {"letter": "E", "image": "E.png", "target": [False, False, False, False, False]},  # will collide with C / closed hand
    ],
}


SIGN_CONFIRM_FRAMES = 30