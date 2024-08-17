import re
from enum import Enum


BAD_WORDS = {
    "хуй", "пизда", "блядь",
    "нахуй", "срань", "говно", "хуй", "пизда", "блядь",
    "гавно", "гімно", "сраний", "їбаний", "йобаний", "ебаный"
}

def is_profane(text):
    words = set(word.lower() for word in text.split())
    return any(word in BAD_WORDS for word in words)

text = "This is a bad example."
if is_profane(text):
    print("The text contains prohibited words.")


class ProfanityFilter(Enum):
    HUY = (r"хуй", r"\bху[йиюе]\w*\b")
    PIZDA = (r"пизда", r"\bп[ие]зд[ауы]\w*\b")
    BLYAD = (r"блядь", r"\bбля[дть]\w*\b")
    EBANYY = (r"ебаный", r"\b[еи]ба[нт][аыуоий]*\b")
    SRANYY = (r"сраний", r"\bсра[нт][аыуоий]*\b")

    @classmethod
    def is_profane(cls, text):
        text = re.sub(r'\W+', ' ', text.lower())
        for item in cls:
            if re.search(item.value[1], text):
                return True
        return False
