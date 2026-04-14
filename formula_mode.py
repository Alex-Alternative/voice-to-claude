"""
Formula mode for Koda — converts natural language descriptions to Excel/Sheets formulas.

Two-tier conversion:
  Tier 1 — Rules-based (always available, covers common formulas)
  Tier 2 — Ollama LLM fallback (if llm_polish.enabled = true in config)
"""

import re
import logging

logger = logging.getLogger("koda")

# Excel/Sheets app signatures
FORMULA_APP_PROCESSES = {"excel.exe"}
FORMULA_WINDOW_PATTERNS = [
    re.compile(r"google sheets", re.IGNORECASE),
    re.compile(r"- sheets$", re.IGNORECASE),
    re.compile(r"\bsheets\b", re.IGNORECASE),
]


def is_formula_app(process_name: str, window_title: str) -> bool:
    """Return True if the active window is Excel or Google Sheets."""
    if process_name.lower() in FORMULA_APP_PROCESSES:
        return True
    for pat in FORMULA_WINDOW_PATTERNS:
        if pat.search(window_title):
            return True
    return False


def convert_to_formula(text: str, llm_enabled: bool = False, llm_config: dict = None) -> str | None:
    """
    Convert natural language text to an Excel formula.

    Returns:
        Formula string starting with '=' if matched, else None (use raw text).
    """
    result = _rules_convert(text)
    if result is not None:
        logger.debug("Formula mode: rules match %r -> %r", text, result)
        return result

    if llm_enabled and llm_config:
        result = _llm_convert(text, llm_config)
        if result is not None:
            logger.debug("Formula mode: LLM match %r -> %r", text, result)
        return result

    return None


# ---------------------------------------------------------------------------
# Range parsing helpers
# ---------------------------------------------------------------------------

def _extract_range(text: str) -> str | None:
    """Find and extract the first cell-range description from text."""
    # "column B rows 2 to 10" / "column B row 2 to 10"
    m = re.search(
        r'column\s+([A-Za-z]+)\s+rows?\s+(\d+)\s+(?:to|through)\s+(\d+)',
        text, re.IGNORECASE
    )
    if m:
        col = m.group(1).upper()
        return f"{col}{m.group(2)}:{col}{m.group(3)}"

    # "B2 to B10" / "B2 through B10"
    m = re.search(
        r'([A-Za-z]+)(\d+)\s+(?:to|through)\s+([A-Za-z]+)(\d+)',
        text, re.IGNORECASE
    )
    if m:
        return f"{m.group(1).upper()}{m.group(2)}:{m.group(3).upper()}{m.group(4)}"

    # Already in range notation "A1:B10"
    m = re.search(r'([A-Za-z]+\d+):([A-Za-z]+\d+)', text)
    if m:
        return f"{m.group(1).upper()}:{m.group(2).upper()}"

    return None


def _fmt_val(s: str) -> str:
    """Format a scalar value for use inside a formula."""
    s = s.strip()
    if re.match(r'^-?\d+(\.\d+)?$', s):           # number
        return s
    if re.match(r'^[A-Za-z]+\d+$', s):            # cell reference
        return s.upper()
    return f'"{s}"'                                # string literal


# ---------------------------------------------------------------------------
# Tier 1: Rules-based conversion
# ---------------------------------------------------------------------------

def _rules_convert(text: str) -> str | None:
    """Return an Excel formula string, or None if no rule matches."""
    t = text.strip()
    tl = t.lower()

    # --- TODAY / NOW ---
    if re.match(r"^(today|today'?s date)$", tl):
        return "=TODAY()"
    if re.match(r"^(now|current time|current date and time)$", tl):
        return "=NOW()"

    # --- SUM ---
    m = re.match(r"^(?:sum|total|add up|add)\s+(.+)$", tl)
    if m:
        rng = _extract_range(m.group(1))
        if rng:
            return f"=SUM({rng})"

    # --- AVERAGE ---
    m = re.match(r"^(?:average|mean|avg)\s+(?:of\s+)?(.+)$", tl)
    if m:
        rng = _extract_range(m.group(1))
        if rng:
            return f"=AVERAGE({rng})"

    # --- COUNT (numeric cells) ---
    m = re.match(r"^count\s+(?:numbers?\s+in\s+)?(.+)$", tl)
    if m:
        rng = _extract_range(m.group(1))
        if rng:
            return f"=COUNT({rng})"

    # --- COUNTA (non-empty cells) ---
    m = re.match(r"^count\s+(?:non[\s-]?empty|all(?:\s+cells)?\s+in)\s+(.+)$", tl)
    if m:
        rng = _extract_range(m.group(1))
        if rng:
            return f"=COUNTA({rng})"

    # Also "how many" → COUNT
    m = re.match(r"^how many\s+(?:(?:numbers?|values?|cells?)\s+in\s+)?(.+)$", tl)
    if m:
        rng = _extract_range(m.group(1))
        if rng:
            return f"=COUNT({rng})"

    # --- MAX ---
    m = re.match(r"^(?:max|maximum|highest|largest)\s+(?:of\s+)?(.+)$", tl)
    if m:
        rng = _extract_range(m.group(1))
        if rng:
            return f"=MAX({rng})"

    # --- MIN ---
    m = re.match(r"^(?:min|minimum|lowest|smallest)\s+(?:of\s+)?(.+)$", tl)
    if m:
        rng = _extract_range(m.group(1))
        if rng:
            return f"=MIN({rng})"

    # --- IF ---
    m = re.match(
        r"^if\s+([A-Za-z]+\d+)\s+is\s+"
        r"(greater than|less than|equal to|not equal to|>=|<=|>|<|=)\s+"
        r"(.+?)\s+then\s+(.+?)\s+else\s+(.+)$",
        tl,
    )
    if m:
        cell = m.group(1).upper()
        op_map = {
            "greater than": ">", "less than": "<", "equal to": "=",
            "not equal to": "<>", ">=": ">=", "<=": "<=",
            ">": ">", "<": "<", "=": "=",
        }
        op = op_map.get(m.group(2), m.group(2))
        val = _fmt_val(m.group(3))
        then_val = _fmt_val(m.group(4))
        else_val = _fmt_val(m.group(5))
        return f"=IF({cell}{op}{val},{then_val},{else_val})"

    # --- VLOOKUP ---
    m = re.match(
        r"^(?:vlookup|look up)\s+([A-Za-z]+\d+)\s+in\s+(.+?)\s+column\s+(\d+)(.*)?$",
        tl,
    )
    if m:
        lookup_val = m.group(1).upper()
        rng = _extract_range(m.group(2))
        col_idx = m.group(3)
        approximate = "1" if "approximate" in (m.group(4) or "") else "0"
        if rng:
            return f"=VLOOKUP({lookup_val},{rng},{col_idx},{approximate})"

    # --- CONCAT ---
    m = re.match(r"^(?:concat(?:enate)?|join|combine)\s+(.+)$", tl)
    if m:
        cells = re.findall(r"[A-Za-z]+\d+", m.group(1))
        if len(cells) >= 2:
            return f"=CONCAT({','.join(c.upper() for c in cells)})"

    # --- PERCENTAGE ---
    m = re.match(
        r"^(?:percent(?:age)? of\s+)?([A-Za-z]+\d+)\s+"
        r"(?:over|divided by|out of)\s+([A-Za-z]+\d+)"
        r"(?:\s+(?:as\s+)?percent(?:age)?)?$",
        tl,
    )
    if m:
        return f"=({m.group(1).upper()}/{m.group(2).upper()})*100"

    return None


# ---------------------------------------------------------------------------
# Tier 2: Ollama LLM fallback
# ---------------------------------------------------------------------------

def _llm_convert(text: str, llm_config: dict) -> str | None:
    """Ask a local Ollama model to convert text to a formula. Returns formula or None."""
    try:
        import ollama
        llm_model = llm_config.get("model", "phi3:mini")
        response = ollama.chat(
            model=llm_model,
            messages=[{
                "role": "user",
                "content": (
                    "Convert this natural language description to an Excel formula. "
                    "Return ONLY the formula starting with =, nothing else. "
                    "If you cannot convert it to a formula, return exactly the original text.\n"
                    f"Input: {text}"
                ),
            }],
        )
        result = response["message"]["content"].strip()
        # Must start with = to be treated as a formula
        if result.startswith("="):
            return result
        return None
    except Exception as e:
        logger.debug("Formula LLM fallback failed: %s", e)
        return None
