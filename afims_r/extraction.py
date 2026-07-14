from __future__ import annotations
import re
from dataclasses import dataclass

NUMBER_RE = re.compile(r"(?<![\w])[-+]?\d+(?:[.,]\d+)?(?:\s?%|\s?(?:kWh|MWh|kWp|kW|MW|Wh|V|A|W|°C|C|Hz|min|km|kg|PLN|EUR|s|h|m))?")
DATE_RE = re.compile(r"\b(?:\d{4}-\d{2}-\d{2}|\d{1,2}[./-]\d{1,2}[./-]\d{2,4})\b")
HASH_RE = re.compile(r"\b[a-fA-F0-9]{64}\b")
NEGATIONS = {"nie", "brak", "bez", "nigdy", "żaden", "żadna", "żadne"}
UNCERTAINTY = {"może", "prawdopodobnie", "hipoteza", "założenie", "możliwe", "potencjalnie"}
CAUSAL = {"powoduje", "prowadzi", "skutkuje", "dlatego", "ponieważ"}

@dataclass(frozen=True)
class InformationModel:
    sentences: tuple[str, ...]
    numbers: tuple[str, ...]
    dates: tuple[str, ...]
    hashes: tuple[str, ...]
    negated_sentences: tuple[str, ...]
    uncertain_sentences: tuple[str, ...]
    causal_sentences: tuple[str, ...]
    entities: tuple[str, ...]

def _sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", text) if s.strip()]

def _entities(text: str) -> list[str]:
    # Conservative deterministic baseline: capitalized multi-token names and identifiers.
    candidates = re.findall(r"\b(?:[A-ZĄĆĘŁŃÓŚŹŻ][\w&.-]+(?:\s+[A-ZĄĆĘŁŃÓŚŹŻ][\w&.-]+)+|[A-Z]{2,}[A-Z0-9_.-]*)\b", text)
    return list(dict.fromkeys(candidates))

def extract(text: str) -> InformationModel:
    sentences = _sentences(text)
    lowered = [(s, set(re.findall(r"\w+", s.lower()))) for s in sentences]
    return InformationModel(
        sentences=tuple(sentences),
        numbers=tuple(NUMBER_RE.findall(text)),
        dates=tuple(DATE_RE.findall(text)),
        hashes=tuple(HASH_RE.findall(text)),
        negated_sentences=tuple(s for s, words in lowered if words & NEGATIONS),
        uncertain_sentences=tuple(s for s, words in lowered if words & UNCERTAINTY),
        causal_sentences=tuple(s for s, words in lowered if words & CAUSAL),
        entities=tuple(_entities(text)),
    )
