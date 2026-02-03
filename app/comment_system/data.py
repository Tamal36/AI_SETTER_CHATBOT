# JamieBot/app/comment_system/data.py

# 1. KEYWORDS MAPPING
KEYWORDS = {
    "PRICE": [
        "price", "cost", "how much", "charge", "$", "expensive", "cheap", "money", 
        "payment", "fee", "rates", "discount", "offer", "sale", "budget", "value", 
        "costing", "affordable", "high cost", "low cost", "pricing", "premium", "bargain"
    ],
    "ELIGIBILITY": [
        "beginners", "old", "young", "work for me", "requirements", "start", 
        "age", "location", "qualify", "criteria", "conditions", "eligible", 
        "restrictions", "terms", "application", "who can join", "who is eligible", 
        "requisites", "pre-requisite", "entry requirements", "acceptance", "admission"
    ],
    "INTEREST": [
        "interested", "info", "details", "yes", "please", "want this", "link", 
        "sent", "dm", "how to join", "join", "sign up", "register", "tell me more", 
        "sign me up", "count me in", "apply", "get started", "I’m in", "send me info"
    ],
    "GENERIC": [
        "🔥", "❤️", "wow", "great", "cool", "thanks", "amazing", "love", 
        "beautiful", "awesome", "👏", "🙌", "fantastic", "incredible", "wowza", 
        "unbelievable", "superb", "outstanding", "brilliant", "perfect", "so good", 
        "inspiring", "epic", "legendary", "good vibes", "high five", "👌"
    ]
}

# 2. LOCKED TEMPLATES (From comment_bot2.txt)
TEMPLATES = {
    "INTEREST": [
        "Glad you’re interested 😊\nDM us on Instagram",
        "Happy to share more 👍\nDM us on Instagram"
    ],
    "PRICE": [
        "I’ll explain the pricing properly 👍\nDM us on Instagram"
    ],
    "ELIGIBILITY": [
        "I’ll explain how it works 😊\nDM us on Instagram"
    ],
    "GENERIC": [
        "Thanks for the support 🙌\nDM us on Instagram if you want details"
    ],
    "UNKNOWN": [
        "DM us for details" 
    ],
    # Special Overrides
    "YOUTUBE_OVERRIDE": "I’ll explain everything properly 👍\nDM us on Instagram @yourpage"
}