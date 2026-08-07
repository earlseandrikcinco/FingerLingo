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

# HYBRID ENGINE CONFIGURATION
SEQUENCE_LENGTH = 45           # Tier 2 dynamic buffer size (1.5s @ 30 FPS)
SIGN_CONFIRM_FRAMES = 15       # Hold time threshold before marking static sign as learned
MOTION_THRESHOLD = 0.012       # Motion filter for dynamic model (std dev)
CONFIDENCE_THRESHOLD = 75.0    # Minimum % confidence filter for inference


# Lesson content: each entry is one letter/sign in the lesson
# edit again for dynamic, since it won't be as simple as booleans on a list (for example, J and Z are dynamic, and C is unreliable for now)
LESSONS = {
    # ALPHABET TABS 
    "A - E": [
        {"letter": "A", "image": "A.png", "type": "static"},
        {"letter": "B", "image": "B.png", "type": "static"},
        {"letter": "C", "image": "C.png", "type": "static"},
        {"letter": "D", "image": "D.png", "type": "static"},
        {"letter": "E", "image": "E.png", "type": "static"},
    ],
    "F - J": [
        {"letter": "F", "image": "F.png", "type": "static"},
        {"letter": "G", "image": "G.png", "type": "static"},
        {"letter": "H", "image": "H.png", "type": "static"},
        {"letter": "I", "image": "I.png", "type": "static"},
        {"letter": "J", "image": "J.png", "type": "dynamic"},  # Tier 2 Dynamic Model
    ],
    "K - O": [
        {"letter": "K", "image": "K.png", "type": "static"},
        {"letter": "L", "image": "L.png", "type": "static"},
        {"letter": "M", "image": "M.png", "type": "static"},
        {"letter": "N", "image": "N.png", "type": "static"},
        {"letter": "O", "image": "O.png", "type": "static"},
    ],
    "P - T": [
        {"letter": "P", "image": "P.png", "type": "static"},
        {"letter": "Q", "image": "Q.png", "type": "static"},
        {"letter": "R", "image": "R.png", "type": "static"},
        {"letter": "S", "image": "S.png", "type": "static"},
        {"letter": "T", "image": "T.png", "type": "static"},
    ],
    "U - Z": [
        {"letter": "U", "image": "U.png", "type": "static"},
        {"letter": "V", "image": "V.png", "type": "static"},
        {"letter": "W", "image": "W.png", "type": "static"},
        {"letter": "X", "image": "X.png", "type": "static"},
        {"letter": "Y", "image": "Y.png", "type": "static"},
        {"letter": "Z", "image": "Z.png", "type": "dynamic"},  # Tier 2 Dynamic Model
    ],

    # DIGIT TABS 
    "0 - 10": [
        {"letter": "0", "image": "0.png", "type": "static"},
        {"letter": "1", "image": "1.png", "type": "static"},
        {"letter": "2", "image": "2.png", "type": "static"},
        {"letter": "3", "image": "3.png", "type": "static"},
        {"letter": "4", "image": "4.png", "type": "static"},
        {"letter": "5", "image": "5.png", "type": "static"},
        {"letter": "6", "image": "6.png", "type": "static"},
        {"letter": "7", "image": "7.png", "type": "static"},
        {"letter": "8", "image": "8.png", "type": "static"},
        {"letter": "9", "image": "9.png", "type": "static"},
        {"letter": "10", "image": "10.png", "type": "dynamic"}, # Tier 2 Dynamic Model
    ],

    # Phrases PLACEHOLDER 
    "Greetings": [
        {"letter": "Hello", "image": "hello.png", "type": "phrase"},
        {"letter": "Thanks", "image": "thanks.png", "type": "phrase"},
    ]
}


SIGN_CONFIRM_FRAMES = 30