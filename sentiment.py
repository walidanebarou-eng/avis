# BrewIQ · ml/sentiment.py
# Rule-based FR sentiment + TextBlob fallback

import re
from dataclasses import dataclass

POSITIVE_KEYWORDS = [
    'excellent', 'bon', 'bonne', 'très bon', 'super', 'satisfait',
    'agréable', 'top', 'parfait', 'raisonnable', 'rapport qualité',
    'pas cher', 'petit prix', 'correct', 'bien', 'génial', 'adoré'
]

NEGATIVE_KEYWORDS = [
    'cher', 'coûteux', 'abordable', 'élevé', 'trop cher',
    'décevant', 'mauvais', 'horrible', 'déçu', 'froid', 'lent'
]

# Words that flip positive negatives
FLIP_PHRASES = [
    ('pas cher', 'positive_strong'),
    ('petit prix', 'positive_strong'),
    ('trop coûteux', 'negative'),
    ('prix élevé', 'negative_weak'),
    ('pas très abordable', 'negative_weak'),
]


@dataclass
class SentimentResult:
    label: str          # positif | neutre | négatif
    score: float        # -1.0 → +1.0
    confidence: float   # 0.0 → 1.0
    keywords: list


def analyse_sentiment(text: str) -> SentimentResult:
    """Analyse le sentiment d'un avis client en français."""
    t = text.lower()
    score = 0.0
    found_kw = []

    # Check flip phrases first
    for phrase, impact in FLIP_PHRASES:
        if phrase in t:
            if impact == 'positive_strong':
                score += 0.5
                found_kw.append(f'+{phrase}')
            elif impact == 'negative':
                score -= 0.4
                found_kw.append(f'-{phrase}')
            elif impact == 'negative_weak':
                score -= 0.2
                found_kw.append(f'-{phrase}')

    # Positive keywords
    for kw in POSITIVE_KEYWORDS:
        if kw in t:
            score += 0.2
            found_kw.append(f'+{kw}')

    # Negative keywords (avoid double-counting flip phrases)
    for kw in NEGATIVE_KEYWORDS:
        if kw in t and not any(kw in p for p, _ in FLIP_PHRASES if 'positive' in _):
            if f'+{kw}' not in found_kw:
                score -= 0.15
                found_kw.append(f'-{kw}')

    # Clamp
    score = max(-1.0, min(1.0, score))
    confidence = min(0.95, 0.5 + abs(score) * 0.4 + len(found_kw) * 0.03)

    if score > 0.1:
        label = 'positif'
    elif score < -0.1:
        label = 'négatif'
    else:
        label = 'neutre'

    return SentimentResult(label=label, score=round(score, 3),
                           confidence=round(confidence, 3), keywords=found_kw)


def analyse_batch(reviews: list[str]) -> list[dict]:
    """Analyse une liste d'avis, retourne une liste de dicts."""
    results = []
    for text in reviews:
        r = analyse_sentiment(text)
        results.append({
            'text': text,
            'sentiment': r.label,
            'score': r.score,
            'confidence': r.confidence,
            'keywords': r.keywords
        })
    return results


def sentiment_stats(reviews: list[str]) -> dict:
    """Statistiques agrégées de sentiment."""
    batch = analyse_batch(reviews)
    counts = {'positif': 0, 'neutre': 0, 'négatif': 0}
    scores = []
    for r in batch:
        counts[r['sentiment']] += 1
        scores.append(r['score'])

    total = len(batch)
    avg_score = sum(scores) / total if total else 0

    return {
        'total': total,
        'counts': counts,
        'percentages': {k: round(v / total * 100, 1) for k, v in counts.items()},
        'average_score': round(avg_score, 3),
        'satisfaction_rate': round(counts['positif'] / total * 100, 1) if total else 0
    }
