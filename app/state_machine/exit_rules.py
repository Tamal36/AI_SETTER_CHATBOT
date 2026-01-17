import re
import unicodedata


def normalize_text(text: str) -> str:
    """
    Canonical text normalization for all exit rules.
    - lowercases
    - normalizes unicode (smart quotes, etc.)
    - strips punctuation
    - collapses whitespace
    """
    if not text:
        return ""

    # Normalize unicode (handles smart quotes like ’)
    text = unicodedata.normalize("NFKD", text)

    # Lowercase
    text = text.lower()

    # Remove punctuation except apostrophes
    text = re.sub(r"[^\w\s']", " ", text)

    # Collapse multiple spaces
    text = re.sub(r"\s+", " ", text).strip()

    return text

# def seeks_help(text: str) -> bool:
#     """
#     text is already normalized.
#     This detects help-seeking intent, not confusion.
#     """
#     return (
#         "can you help" in text
#         or "what should i do" in text
#         or "what do i do" in text
#         or "what to do" in text
#         or "i dont know what to do" in text
#         or "i dont know how to fix" in text
#     )

HELP_SEEKING_PHRASES = {
    "what should i do",
    "what do i do",
    "how do i fix",
    "how do i solve",
    "help me",
    "i need help",
    "i need your help",
    "i need guidance",
    "guide me",
    "any advice",
    "can you help",
}

def seeks_help(text: str) -> bool:
    """
    text is already normalized.
    This detects help-seeking intent, not confusion.
    """
    return any(phrase in text for phrase in HELP_SEEKING_PHRASES)


# app/state_machine/exit_rules.py

DATING_KEYWORDS = {
    "date", "dating", "girlfriend", "boyfriend", "single",
    "matches", "tinder", "hinge", "bumble", "ghosted",
    "relationship", "women", "men"
}

EMOTION_PHRASES = {
    "feel stuck",
    "tired of this",
    "frustrated",
    "confused",
    "lost",
    "fed up",
    "burned out"
}

ORIENTATION_PHRASES = {
    "hi", "hello", "hey",
    "who are you",
    "what is this",
    "are you real",
    "are you a bot",
    "how does this work"
}

ABUSIVE_KEYWORDS = {
    "fuck", "fucking", "bitch", "slut", "whore",
    "nigger", "rape", "kill", "die",
}

OFF_TOPIC_KEYWORDS = {
    "physics", "quantum", "math", "chemistry",
    "astrology", "politics", "religion",
}

def is_abusive(text: str) -> bool:
    return any(word in text for word in ABUSIVE_KEYWORDS)

def is_off_topic(text: str) -> bool:
    return any(word in text for word in OFF_TOPIC_KEYWORDS)


def has_dating_context(text: str) -> bool:
    
    return any(word in text for word in DATING_KEYWORDS)


def has_emotional_signal(text: str) -> bool:
    lowered = text.lower()
    return any(phrase in lowered for phrase in EMOTION_PHRASES)


def is_orientation_only(text: str) -> bool:
    lowered = text.lower().strip()
    return lowered in ORIENTATION_PHRASES


def entry_boundary_action(
    normalized_text: str,
    extracted_attributes: dict,
) -> str:
    """
    Returns one of:
    - "ALLOW"
    - "WARN_ABUSE"
    - "HARD_STOP"
    """

    abuse_count = extracted_attributes.get("abuse_count", 0)

    if is_abusive(normalized_text):
        abuse_count += 1
        extracted_attributes["abuse_count"] = abuse_count

        if abuse_count >= 2:
            extracted_attributes["hard_stop_triggered"] = True
            return "HARD_STOP"

        return "WARN_ABUSE"

    return "ALLOW"



def should_exit_entry(text: str) -> bool:
    """
    ENTRY → RAPPORT gate.
    """
    normalized = normalize_text(text)

    if is_orientation_only(normalized):
        return False

    return has_dating_context(normalized) or has_emotional_signal(normalized)


##################################
####### RAPPORT EXIT RULES ########
##################################

# app/state_machine/exit_rules.py

RECURRENCE_MARKERS = {
    "always",
    "every time",
    "keep",
    "keeps happening",
    "again and again"
}

OBSTACLE_PHRASES = {
    "can't figure out",
    "dont know why",
    "don't know why",
    "the problem is",
    "what's wrong"
}

UNDERSTANDING_INTENT = {
    "i want to understand",
    "i need to understand",
    "help me understand",
    "why does this happen"
}

STALL_PHRASES = {
    "i don't know",
    "i dont know",
    "not sure",
    "i'm not sure",
    "im not sure",
    "can't explain",
    "cant explain",
    "dating sucks",
    "it just sucks",
    "everything",
}

def is_stall_response(text: str) -> bool:
    return (
        len(text.split()) <= 4
        or any(phrase in text for phrase in STALL_PHRASES)
    )


def has_concrete_detail(text: str) -> bool:
    """
    Concrete = mentions a specific situation, behavior, or pattern
    """
    SIGNAL_WORDS = {
        "messages",
        "texts",
        "dates",
        "matches",
        "ghost",
        "replies",
        "apps",
        "conversation",
        "meet",
        "talking",
        "after",
        "before",
    }
    return any(word in text for word in SIGNAL_WORDS)


def has_specific_pattern(text: str) -> bool:
    lowered = text.lower()
    return any(p in lowered for p in RECURRENCE_MARKERS)


def names_clear_obstacle(text: str) -> bool:
    lowered = text.lower()
    return any(p in lowered for p in OBSTACLE_PHRASES)


def seeks_understanding(text: str) -> bool:
    lowered = text.lower()
    return any(p in lowered for p in UNDERSTANDING_INTENT)


def should_exit_rapport(text: str) -> bool:
    """
    RAPPORT → PROBLEM_DISCOVERY gate (working version).
    """
    normalized = normalize_text(text)
    return (
        has_specific_pattern(normalized)
        or names_clear_obstacle(normalized)
        or seeks_understanding(normalized)
    )

############################################
####### PROBLEM DISCOVERY EXIT RULES ########
############################################

# app/state_machine/exit_rules.py



EXHAUSTION_PHRASES = {
    "tried everything",
    "nothing works",
    "out of ideas",
    "at a loss"
}

# --- PROBLEM DISCOVERY HELPERS ---

PROBLEM_SIGNAL_WORDS = {
    "message", "messages", "text", "texts",
    "ghost", "ghosted",
    "reply", "replies",
    "match", "matches",
    "date", "dates",
    "conversation", "talking",
    "after", "before",
    "first", "few",
}

def is_problem_signal(text: str) -> bool:
    """
    Detects concrete, repeatable dating behavior
    """
    return any(word in text for word in PROBLEM_SIGNAL_WORDS)


def confirms_pattern(text: str) -> bool:
    """
    Detects repetition / absolutes that confirm a pattern
    """
    CONFIRM_WORDS = {
        "always", "every time", "keeps", "never",
        "usually", "most of the time",
    }
    return any(word in text for word in CONFIRM_WORDS)

# def seeks_help(text: str) -> bool:
#     lowered = text.lower()
#     return any(p in lowered for p in HELP_SEEKING_PHRASES)


def expresses_exhaustion(text: str) -> bool:
    lowered = text.lower()
    return any(p in lowered for p in EXHAUSTION_PHRASES)


def should_exit_problem_discovery(text: str) -> bool:
    """
    PROBLEM_DISCOVERY → COACHING_TRANSITION gate (working version).
    """
    normalized = normalize_text(text)
    return seeks_help(normalized) or expresses_exhaustion(normalized)


############################################
####### COACHING TRANSITION EXIT RULES #######
############################################

AFFIRMATIVE_PHRASES = {
    "yes",
    "yeah",
    "yep",
    "sure",
    "okay",
    "ok",
    "i think so",
    "probably",
    "i want help",
    "i do",
    "sounds good",
    "im open",
    "im open to it",
    "i am open",
    "lets do it"
}

NEGATIVE_PHRASES = {
    "no",
    "not really",
    "not sure",
    "i dont think so",
    "i'm not ready",
    "dont want",
    "not interested",
    "maybe later",
    "no thanks"
}


def gives_permission(text: str) -> bool:
    return any(phrase in text for phrase in AFFIRMATIVE_PHRASES)

def declines_permission(text: str) -> bool:
    return any(phrase in text for phrase in NEGATIVE_PHRASES)

def is_affirmative(text: str) -> bool:
    return any(p in text for p in AFFIRMATIVE_PHRASES)


def is_negative(text: str) -> bool:
    return any(p in text for p in NEGATIVE_PHRASES)


def should_exit_coaching_transition(text: str) -> bool:
    """
    COACHING_TRANSITION → QUAL_LOCATION gate (working version).
    """
    normalized = normalize_text(text)

    if is_negative(normalized):
        return False

    if is_affirmative(normalized):
        return True

    # Default: gentle forward motion (working version)
    return True


##################################
####### LOCATION QUAL RULES #######
##################################

US_STATES = {
    "alabama", "alaska", "arizona", "arkansas", "california",
    "colorado", "connecticut", "delaware", "florida", "georgia",
    "hawaii", "idaho", "illinois", "indiana", "iowa", "kansas",
    "kentucky", "louisiana", "maine", "maryland", "massachusetts",
    "michigan", "minnesota", "mississippi", "missouri", "montana",
    "nebraska", "nevada", "new hampshire", "new jersey", "new mexico",
    "new york", "north carolina", "north dakota", "ohio", "oklahoma",
    "oregon", "pennsylvania", "rhode island", "south carolina",
    "south dakota", "tennessee", "texas", "utah", "vermont",
    "virginia", "washington", "west virginia", "wisconsin", "wyoming",
}

CANADA_PROVINCES = {
    "ontario", "quebec", "british columbia", "alberta",
    "manitoba", "saskatchewan", "nova scotia",
    "new brunswick", "newfoundland", "prince edward island",
}


EU_COUNTRIES = {
    "germany", "france", "italy", "spain", "netherlands",
    "belgium", "sweden", "norway", "denmark", "finland",
    "poland", "austria", "switzerland", "ireland",
    "portugal", "czech republic", "greece", "hungary",
}


# ELIGIBLE_LOCATIONS = {
#     "us", "usa", "united states",
#     "canada",
#     "uk", "united kingdom",
#     "eu", "europe"
# }


# ELIGIBLE_COUNTRIES = {
#     "united states", "usa", "us",
#     "canada",
#     "united kingdom", "uk", "england",
# }

US_COUNTRIES = {
    "us", "usa", "united states", "america"
}

CANADA_COUNTRIES = {
    "canada"
}


def extract_location_detail(text: str) -> dict | None:
    """
    Returns structured location info if detected.
    Does NOT decide eligibility.
    """
    # US states
    for state in US_STATES:
        if state in text:
            return {"region": "US", "detail": state}

    # Canada provinces
    for province in CANADA_PROVINCES:
        if province in text:
            return {"region": "CANADA", "detail": province}

    # EU countries
    for country in EU_COUNTRIES:
        if country in text:
            return {"region": "EU", "detail": country}

    # Region mentions
    if "eu" in text or "europe" in text:
        return {"region": "EU", "detail": None}

    if any(c in text for c in US_COUNTRIES):
        return {"region": "US", "detail": None}

    if any(c in text for c in CANADA_COUNTRIES):
        return {"region": "CANADA", "detail": None}

    return None


# def extract_country(text: str) -> str | None:
#     """
#     Very lightweight location extraction.
#     Returns normalized country name if detected.
#     """
#     for country in ELIGIBLE_COUNTRIES:
#         if country in text:
#             return country
#     return None


# def is_location_eligible(text: str) -> bool:
#     # Direct region mentions
#     if "eu" in text or "europe" in text:
#         return True

#     # Core countries
#     if extract_country(text):
#         return True

#     # EU country names
#     return any(country in text for country in EU_COUNTRIES)

def is_location_eligible(text: str) -> bool:
    return extract_location_detail(text) is not None



# def extract_location(text: str) -> str | None:
#     """
#     Very naive extraction for working version.
#     Returns normalized location or None.
#     """
#     for loc in ELIGIBLE_LOCATIONS:
#         if loc in text:
#             return loc
#     return None



# def should_stay_in_qual_location(text: str) -> bool:
#     """
#     Stay if location not clearly provided.
#     """
#     return extract_location(text) is None


############################################
####### RELATIONSHIP GOAL QUAL RULES ########
############################################

CASUAL_PHRASES = {
    "casual",
    "dating",
    "seeing whats out there",
    "just dating",
    "fun"
}

SERIOUS_PHRASES = {
    "serious",
    "long term",
    "relationship",
    "girlfriend",
    "wife",
    "marriage"
}


# def has_relationship_goal(text: str) -> bool:
#     """
#     Returns True if user expresses a recognizable relationship goal.
#     """
#     return (
#         any(p in text for p in CASUAL_PHRASES)
#         or any(p in text for p in SERIOUS_PHRASES)
#     )

def classify_relationship_goal(text: str) -> str | None:
    """
    Returns: 'supported', 'unsupported', or None
    """
    if any(p in text for p in SERIOUS_PHRASES):
        return "supported"

    if any(p in text for p in CASUAL_PHRASES):
        return "unsupported"

    return None


##################################
####### FITNESS QUAL RULES ########
##################################

# OUT_OF_SHAPE_PHRASES = {
#     "out of shape",
#     "overweight",
#     "fat",
#     "unfit",
#     "skinny fat",
#     "no gym"
# }

# AVERAGE_PHRASES = {
#     "average",
#     "okay shape",
#     "normal",
#     "not bad",
#     "decent"
# }

# FIT_PHRASES = {
#     "fit",
#     "muscular",
#     "athletic",
#     "gym",
#     "in shape",
#     "strong"
# }


# def has_fitness_level(text: str) -> bool:
#     """
#     Returns True if user expresses a recognizable fitness level.
#     """
#     return (
#         any(p in text for p in OUT_OF_SHAPE_PHRASES)
#         or any(p in text for p in AVERAGE_PHRASES)
#         or any(p in text for p in FIT_PHRASES)
#     )

LOW_CAPACITY_PHRASES = {
    "burned out",
    "exhausted",
    "overwhelmed",
    "no energy",
    "cant focus",
    "can't focus",
    "falling apart",
    "barely functioning",
}

def has_sufficient_capacity(text: str) -> bool:
    """
    Returns False only in clear low-capacity cases.
    Default is True (pass).
    """
    if any(p in text for p in LOW_CAPACITY_PHRASES):
        return False

    return True


##################################
####### FINANCE QUAL RULES ########
##################################

LOW_BUDGET_PHRASES = {
    "paycheck to paycheck",
    "broke",
    "struggling",
    "tight",
    "no money",
    "cant afford",
    "can't afford"
}

MID_BUDGET_PHRASES = {
    "some savings",
    "a little saved",
    "okay financially",
    "doing alright"
}

HIGH_BUDGET_PHRASES = {
    "doing well",
    "pretty well",
    "pretty good"
    "comfortable",
    "good income",
    "financially stable",
    "well off"
}


def get_financial_bucket(text: str) -> str | None:
    """
    Returns: 'low', 'mid', 'high', or None
    """
    if any(p in text for p in LOW_BUDGET_PHRASES):
        return "low"

    if any(p in text for p in MID_BUDGET_PHRASES):
        return "mid"

    if any(p in text for p in HIGH_BUDGET_PHRASES):
        return "high"

    return None

INVESTMENT_INTENT_PHRASES = {
    "invest in myself",
    "i invest",
    "i usually invest",
    "i get help",
    "i pay for help",
    "i hire",
    "i buy courses",
    "i buy programs",
}

def expresses_investment_mindset(text: str) -> bool:
    """
    Detects willingness to invest without mentioning money explicitly.
    """
    return any(p in text for p in INVESTMENT_INTENT_PHRASES)
