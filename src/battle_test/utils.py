import re
from difflib import SequenceMatcher

# Extracts a 4–6 digit number from the text (handles commas in ZIPs)
def extract_zip(text: str) -> str | None:
    text = text.lower()

    # Handle cases like "zip is 95,125"
    match = re.search(r"zip\s+(is\s+)?(\d{2}),?(\d{3})", text)
    if match:
        return match.group(2) + match.group(3)  # Combine to 95125

    # Fallback: any 4 to 6 digit number (to allow 9407-style ZIPs)
    zip_candidates = re.findall(r"\b\d{4,6}\b", text)
    if zip_candidates:
        return zip_candidates[-1]  # Use last one, usually ZIP

    return None


# Extracts name using common patterns and removes bot contamination
def extract_name(text: str) -> str | None:
    patterns = [
        r"\bit'?s\s+([A-Za-z]+(?: [A-Za-z]+)?)",
        r"\bmy name is\s+([A-Za-z]+(?: [A-Za-z]+)?)",
        r"\bi'?m\s+([A-Za-z]+(?: [A-Za-z]+)?)",
        r"\bname'?s\s+([A-Za-z]+(?: [A-Za-z]+)?)",
        r"\bjust\s+([A-Za-z]+(?: [A-Za-z]+)?)",
        r"\bright[, -]+([A-Za-z]+(?: [A-Za-z]+)?)"
    ]

    bot_keywords = ["insurance", "plans", "coverage", "agent"]

    matches = [re.search(p, text, re.IGNORECASE) for p in patterns]
    candidates = [m.group(1).title() for m in matches if m]
    candidates = [c for c in candidates if not any(k in c.lower() for k in bot_keywords)]

    if candidates:
        return max(candidates, key=len)
    return None


# Generic fuzzy matcher for names
def fuzzy_match(a: str, b: str, threshold: float = 0.8) -> bool:
    return SequenceMatcher(None, a, b).ratio() >= threshold


# Fuzzy match for ZIPs (looser threshold)
def fuzzy_zip_match(extracted: str, expected: str, threshold: float = 0.6) -> bool:
    if not extracted or not expected:
        return False
    return SequenceMatcher(None, extracted, expected).ratio() >= threshold


# Checks if user agreed to transfer based on bot question + user response
def customer_agreed(segments) -> bool:
    trigger_phrases = [
        "would you like to", "do you want to", "are you interested in",
        "can i connect you", "shall i transfer you", "speak to an agent",
        "talk to a representative", "talk to a customer care agent", "connect you now"
    ]
    agreement_phrases = [
        "yes", "sure", "okay", "sounds good", "yeah", "yep", "i'm interested",
        "i guess", "all right", "alright"
    ]

    for i, seg in enumerate(segments):
        if seg["speaker"] == "bot":
            if any(tp in seg["text"].lower() for tp in trigger_phrases):
                if i + 1 < len(segments) and segments[i + 1]["speaker"] == "user":
                    if any(ap in segments[i + 1]["text"].lower() for ap in agreement_phrases):
                        return True

    # Fallback: scan user transcript for agreement
    full_text = " ".join(s["text"].lower() for s in segments if s["speaker"] == "user")
    return any(ap in full_text for ap in agreement_phrases)


# Checks if the bot tried to initiate a transfer using known phrases
def bot_attempted_transfer(text: str) -> bool:
    text = text.lower()

    # Direct transfer cues
    phrases = [
        "transfer_call()", "connecting you", "i'll transfer you", "let me connect you",
        "i will now transfer", "one moment", "please hold", "transferring your call",
        "i'll connect you now", "just a moment", "hang tight", "stand by",
        "connecting you now"
    ]

    if any(p in text for p in phrases):
        return True

    # Inferred transfer: bot offered + user agreed
    if (
        "talk to a customer care agent" in text
        and any(phrase in text for phrase in ["yes", "sure", "yeah", "okay", "alright", "i guess"])
    ):
        return True

    return False

