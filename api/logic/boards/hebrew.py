from codenames.game import Board, Card, CardColor, words_to_random_board

HEBREW_WORDS = [
    "מטען",
    "עלילה",
    "ניצחון",
    "כבש",
    "יוגה",
    "צבי",
    "אף",
    "מפגש",
    "דק",
    "פרץ",
    "שלם",
    "אדם",
    "הרמוניה",
    "זכוכית",
    "חשמל",
    "מעטפת",
    "אנרגיה",
    "קברן",
    "נחת",
    "חייזר",
    "שיר",
    "מיליונר",
    "לפיד",
    "יקום",
    "דרור",
]

HEBREW_BOARD_1 = words_to_random_board(words=HEBREW_WORDS, seed=1)
HEBREW_BOARD_2 = words_to_random_board(words=HEBREW_WORDS, seed=2)
HEBREW_BOARD_3 = words_to_random_board(words=HEBREW_WORDS, seed=3)

# Regex: 'Parsed card: (.*) (.*)' -> 'Card("$2", color=CardColor.$1),'

HEBREW_BOARD_DIFFICULT = Board(
    [
        Card("בריטניה", color=CardColor.GRAY),
        Card("מרכז", color=CardColor.BLUE),
        Card("נבחר", color=CardColor.GRAY),
        Card("שניה", color=CardColor.GRAY),
        Card("טרמפ", color=CardColor.RED),
        Card("ברברי", color=CardColor.BLUE),
        Card("נשק", color=CardColor.BLUE),
        Card("תוכן", color=CardColor.RED),
        Card("קיסריה", color=CardColor.GRAY),
        Card("גלידה", color=CardColor.RED),
        Card("ארז", color=CardColor.BLACK),
        Card("מציאה", color=CardColor.BLUE),
        Card("דק", color=CardColor.GRAY),
        Card("תולעת", color=CardColor.RED),
        Card("מצפון", color=CardColor.RED),
        Card("פירמידה", color=CardColor.GRAY),
        Card("משובש", color=CardColor.BLUE),
        Card("שק", color=CardColor.BLUE),
        Card("פנינה", color=CardColor.RED),
        Card("דקה", color=CardColor.BLUE),
        Card("חג", color=CardColor.BLUE),
        Card("קשר", color=CardColor.RED),
        Card("קור", color=CardColor.RED),
        Card("אויר", color=CardColor.BLUE),
        Card("טבליה", color=CardColor.GRAY),
    ]
)
HEBREW_BOARD_4 = Board(
    [
        Card("שיר", color=CardColor.BLUE),
        Card("הקליד", color=CardColor.BLUE),
        Card("חופשה", color=CardColor.RED),
        Card("ערב", color=CardColor.RED),
        Card("תרמיל", color=CardColor.BLUE),
        Card("חוש", color=CardColor.GRAY),
        Card("הדר", color=CardColor.RED),
        Card("פירמידה", color=CardColor.GRAY),
        Card("עגול", color=CardColor.GRAY),
        Card("אלתור", color=CardColor.RED),
        Card("שנה", color=CardColor.BLUE),
        Card("ריבה", color=CardColor.BLUE),
        Card("נגן", color=CardColor.BLUE),
        Card("בית", color=CardColor.RED),
        Card("דמוקרטיה", color=CardColor.GRAY),
        Card("ערק", color=CardColor.GRAY),
        Card("שחור", color=CardColor.RED),
        Card("פרה", color=CardColor.RED),
        Card("נס", color=CardColor.BLACK),
        Card("בית-ספר", color=CardColor.BLUE),
        Card("מצבה", color=CardColor.BLUE),
        Card("אגרטל", color=CardColor.GRAY),
        Card("מקום", color=CardColor.RED),
        Card("תמונה", color=CardColor.GRAY),
        Card("מבט", color=CardColor.RED),
    ]
)
HEBREW_BOARD_5 = Board(
    [
        Card("שעה", color=CardColor.BLACK),
        Card("נסיון", color=CardColor.BLUE),
        Card("אחראי", color=CardColor.BLUE),
        Card("רכש", color=CardColor.RED),
        Card("גרם", color=CardColor.BLUE),
        Card("הלכה", color=CardColor.RED),
        Card("מונה", color=CardColor.RED),
        Card("חור", color=CardColor.GRAY),
        Card("בן-גוריון", color=CardColor.GRAY),
        Card("ריקוד", color=CardColor.RED),
        Card("פריז", color=CardColor.GRAY),
        Card("אקדח", color=CardColor.RED),
        Card("קניון", color=CardColor.RED),
        Card("דני", color=CardColor.GRAY),
        Card("ענק", color=CardColor.BLUE),
        Card("נפל", color=CardColor.GRAY),
        Card("ענן", color=CardColor.BLUE),
        Card("די", color=CardColor.GRAY),
        Card("רעל", color=CardColor.RED),
        Card("מזרק", color=CardColor.BLUE),
        Card("אחוז", color=CardColor.GRAY),
        Card("ניצחון", color=CardColor.BLUE),
        Card("עצם", color=CardColor.RED),
        Card("לוחם", color=CardColor.RED),
        Card("קהל", color=CardColor.BLUE),
    ]
)
HEBREW_BOARD_6 = Board(
    [
        Card("חיים", color=CardColor.GRAY),
        Card("ערך", color=CardColor.BLACK),
        Card("מסוק", color=CardColor.BLUE),
        Card("שבוע", color=CardColor.GRAY),
        Card("רובוט", color=CardColor.RED),
        Card("פוטר", color=CardColor.GRAY),
        Card("אסור", color=CardColor.BLUE),
        Card("דינוזאור", color=CardColor.BLUE),
        Card("מחשב", color=CardColor.RED),
        Card("מעמד", color=CardColor.GRAY),
        Card("בעל", color=CardColor.RED),
        Card("פנים", color=CardColor.RED),
        Card("פרק", color=CardColor.RED),
        Card("גפילטע", color=CardColor.BLUE),
        Card("שונה", color=CardColor.RED),
        Card("שכר", color=CardColor.RED),
        Card("קפיץ", color=CardColor.BLUE),
        Card("תרסיס", color=CardColor.GRAY),
        Card("דגל", color=CardColor.GRAY),
        Card("חופשה", color=CardColor.BLUE),
        Card("מועדון", color=CardColor.RED),
        Card("ציון", color=CardColor.BLUE),
        Card("שק", color=CardColor.GRAY),
        Card("אקורדיון", color=CardColor.RED),
        Card("ילד", color=CardColor.BLUE),
    ]
)
HEBREW_BOARD_7 = Board(
    [
        Card("משוב", color=CardColor.RED),
        Card("תמנון", color=CardColor.RED),
        Card("לקח", color=CardColor.BLUE),
        Card("גיס", color=CardColor.BLUE),
        Card("עולם", color=CardColor.GRAY),
        Card("יצירה", color=CardColor.GRAY),
        Card("חציל", color=CardColor.GRAY),
        Card("חול", color=CardColor.RED),
        Card("קניון", color=CardColor.RED),
        Card("פתק", color=CardColor.BLACK),
        Card("אלבום", color=CardColor.BLUE),
        Card("קיץ", color=CardColor.GRAY),
        Card("בירה", color=CardColor.BLUE),
        Card("ערק", color=CardColor.RED),
        Card("מתח", color=CardColor.GRAY),
        Card("בלורית", color=CardColor.GRAY),
        Card("טורניר", color=CardColor.BLUE),
        Card("מתג", color=CardColor.BLUE),
        Card("מפרט", color=CardColor.BLUE),
        Card("מזגן", color=CardColor.BLUE),
        Card("זריקה", color=CardColor.BLUE),
        Card("פאה", color=CardColor.RED),
        Card("מפגש", color=CardColor.RED),
        Card("כלי", color=CardColor.GRAY),
        Card("חיל", color=CardColor.RED),
    ]
)

HEBREW_BOARD_8 = Board(
    [
        Card("לילה", color=CardColor.GRAY),
        Card("דרך", color=CardColor.BLUE),
        Card("שממה", color=CardColor.GRAY),
        Card("כנס", color=CardColor.RED),
        Card("שיח", color=CardColor.BLUE),
        Card("לימון", color=CardColor.RED),
        Card("נשמה", color=CardColor.BLUE),
        Card("פאה", color=CardColor.GRAY),
        Card("כלא", color=CardColor.RED),
        Card("טורניר", color=CardColor.BLUE),
        Card("שיט", color=CardColor.BLACK),
        Card("מת", color=CardColor.BLUE),
        Card("מתח", color=CardColor.RED),
        Card("אף", color=CardColor.RED),
        Card("אור", color=CardColor.RED),
        Card("סבא", color=CardColor.GRAY),
        Card("רעב", color=CardColor.GRAY),
        Card("נמל", color=CardColor.BLUE),
        Card("קצב", color=CardColor.BLUE),
        Card("מטריה", color=CardColor.BLUE),
        Card("דבר", color=CardColor.GRAY),
        Card("שר", color=CardColor.BLUE),
        Card("מצקת", color=CardColor.RED),
        Card("עם", color=CardColor.GRAY),
        Card("אפריקה", color=CardColor.RED),
    ]
)
