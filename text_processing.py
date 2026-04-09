"""
Text post-processing pipeline for Koda.
Cleans up Whisper transcription output before pasting.
"""

import re


# --- Custom Vocabulary Replacement ---

def apply_custom_vocabulary(text, custom_words):
    """Replace misheard words with correct versions using case-insensitive word boundary matching."""
    if not custom_words:
        return text
    for misheard, correct in custom_words.items():
        pattern = re.compile(r'\b' + re.escape(misheard) + r'\b', re.IGNORECASE)
        text = pattern.sub(correct, text)
    return text


# --- Filler Word Removal ---

FILLER_PATTERNS = [
    # Pure fillers
    r'\b(um|uh|uhh|umm|hmm|hm|er|err|ah|ahh)\b',
    # Discourse markers
    r'\b(you know|I mean|sort of|kind of)\b',
    # Hedging words (common in speech, rarely useful in prompts)
    r'\b(basically|actually|literally|honestly|obviously|clearly)\b',
    # Stuttered starts
    r'\b(\w+)\s+\1\b',
]


def remove_filler_words(text):
    """Remove common filler words and speech artifacts."""
    for pattern in FILLER_PATTERNS:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    # Clean up double/triple spaces
    text = re.sub(r'\s{2,}', ' ', text)
    # Clean up orphaned commas/periods
    text = re.sub(r',\s*,', ',', text)
    text = re.sub(r'\.\s*\.', '.', text)
    text = re.sub(r'^\s*[,\.]\s*', '', text)
    return text.strip()


# --- Smart Capitalization ---

def auto_capitalize(text):
    """Fix sentence-start capitalization and 'i' → 'I'."""
    if not text:
        return text
    # Capitalize first letter
    text = text[0].upper() + text[1:]
    # Capitalize after sentence endings
    text = re.sub(r'([.!?]\s+)(\w)', lambda m: m.group(1) + m.group(2).upper(), text)
    # Fix standalone 'i'
    text = re.sub(r'\bi\b', 'I', text)
    return text


# --- Code Vocabulary ---

CODE_VOCAB = {
    # Brackets and parens
    "open paren": "(", "close paren": ")",
    "open parenthesis": "(", "close parenthesis": ")",
    "open bracket": "[", "close bracket": "]",
    "open brace": "{", "close brace": "}",
    "open curly": "{", "close curly": "}",
    # Punctuation
    "semicolon": ";", "colon": ":",
    "comma": ",", "period": ".", "dot": ".",
    "exclamation mark": "!", "question mark": "?",
    # Operators
    "equals": "=", "double equals": "==", "triple equals": "===",
    "not equals": "!=", "plus equals": "+=", "minus equals": "-=",
    "arrow": "->", "fat arrow": "=>",
    "greater than": ">", "less than": "<",
    "plus": "+", "minus": "-",
    # Symbols
    "hash": "#", "hashtag": "#",
    "at sign": "@", "at symbol": "@",
    "ampersand": "&", "double ampersand": "&&",
    "pipe": "|", "double pipe": "||",
    "tilde": "~", "backtick": "`",
    "forward slash": "/", "backslash": "\\",
    "underscore": "_", "dash": "-",
    # Whitespace
    "new line": "\n", "newline": "\n",
    "tab": "\t",
    # Quotes
    "double quote": '"', "single quote": "'",
    "open quote": '"', "close quote": '"',
    # Common code words
    "null": "null", "none": "None",
    "true": "True", "false": "False",
}

# Sort by longest key first to match multi-word patterns before single words
_SORTED_VOCAB = sorted(CODE_VOCAB.items(), key=lambda x: len(x[0]), reverse=True)


def expand_code_vocabulary(text):
    """Replace spoken code terms with their symbol equivalents."""
    for spoken, symbol in _SORTED_VOCAB:
        text = re.sub(
            r'\b' + re.escape(spoken) + r'\b',
            lambda m, s=symbol: s,
            text,
            flags=re.IGNORECASE,
        )
    return text


# --- Case Formatting ---

CASE_FORMATTERS = {
    "camel case": lambda words: words[0].lower() + ''.join(w.capitalize() for w in words[1:]),
    "snake case": lambda words: '_'.join(w.lower() for w in words),
    "pascal case": lambda words: ''.join(w.capitalize() for w in words),
    "kebab case": lambda words: '-'.join(w.lower() for w in words),
    "upper case": lambda words: ' '.join(w.upper() for w in words),
    "screaming snake": lambda words: '_'.join(w.upper() for w in words),
    "constant case": lambda words: '_'.join(w.upper() for w in words),
}


def apply_case_formatting(text):
    """Detect 'camel case foo bar' and format accordingly."""
    for command, formatter in CASE_FORMATTERS.items():
        pattern = re.compile(
            r'\b' + re.escape(command) + r'\s+(.+?)(?:\.|,|$)',
            re.IGNORECASE,
        )
        match = pattern.search(text)
        if match:
            words = match.group(1).strip().split()
            if words:
                formatted = formatter(words)
                text = text[:match.start()] + formatted + text[match.end():]
    return text


# --- Processing Pipeline ---

def process_text(text, config):
    """Run the full post-processing pipeline based on config."""
    if not text:
        return text

    pp = config.get("post_processing", {})

    # Always apply case formatting before other processing
    if pp.get("code_vocabulary", False):
        text = apply_case_formatting(text)
        text = expand_code_vocabulary(text)

    if pp.get("remove_filler_words", True):
        text = remove_filler_words(text)

    if pp.get("auto_capitalize", True):
        text = auto_capitalize(text)

    return text.strip()
