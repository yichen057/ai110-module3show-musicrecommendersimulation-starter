import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

# ---------------------------------------------------------------------------
# Scoring Strategies (Strategy Pattern)
#
# Each mode is a dictionary of weights. score_song() reads from whichever
# strategy is passed in. To add a new mode, just define a new dict.
# ---------------------------------------------------------------------------

SCORING_MODES = {
    "balanced": {
        "genre": 1.0,
        "mood": 1.0,
        "energy": 2.0,
        "acoustic": 0.5,
        "instrumental": 0.5,
        "popularity": 0.5,
        "decade": 1.0,
        "mood_tags": 0.3,
        "mood_tags_max": 1.5,
        "language": 1.0,
        "duration": 0.5,
        "replay": 0.5,
    },
    "genre-first": {
        "genre": 3.0,
        "mood": 1.5,
        "energy": 1.0,
        "acoustic": 0.5,
        "instrumental": 0.5,
        "popularity": 0.5,
        "decade": 0.5,
        "mood_tags": 0.3,
        "mood_tags_max": 1.5,
        "language": 0.5,
        "duration": 0.25,
        "replay": 0.25,
    },
    "energy-focused": {
        "genre": 0.5,
        "mood": 0.5,
        "energy": 3.0,
        "acoustic": 0.5,
        "instrumental": 0.5,
        "popularity": 0.5,
        "decade": 0.5,
        "mood_tags": 0.5,
        "mood_tags_max": 1.5,
        "language": 0.5,
        "duration": 0.5,
        "replay": 0.5,
    },
}

DEFAULT_MODE = "balanced"

# --- Diversity penalties ---
# Applied during greedy selection when a candidate shares artist/genre
# with an already-picked song. Stacks per duplicate.
ARTIST_REPEAT_PENALTY = 3.0   # heavy — same artist twice feels repetitive
GENRE_REPEAT_PENALTY = 1.5    # lighter — same genre twice is less jarring


@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float
    instrumentalness: float = 0.0
    popularity: float = 0.0
    release_decade: int = 2020
    mood_tags: str = ""
    lyrics_language: str = "english"
    duration_sec: int = 210
    replay_value: float = 0.5


@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool
    prefers_instrumental: bool = False
    prefers_popular: bool = False
    preferred_decade: int = 2020
    liked_mood_tags: str = ""
    preferred_language: str = "english"
    target_duration_sec: int = 210
    values_replayability: bool = False


def get_weights(mode: str = DEFAULT_MODE) -> Dict:
    """Return the weight dictionary for a given scoring mode."""
    if mode not in SCORING_MODES:
        raise ValueError(f"Unknown mode '{mode}'. Choose from: {list(SCORING_MODES.keys())}")
    return SCORING_MODES[mode]


def max_score(mode: str = DEFAULT_MODE) -> float:
    """Calculate the theoretical max score for a given mode."""
    w = get_weights(mode)
    return (w["genre"] + w["mood"] + w["energy"] + w["acoustic"]
            + w["instrumental"] + w["popularity"] + w["decade"]
            + w["mood_tags_max"] + w["language"] + w["duration"] + w["replay"])


def score_song(song_dict: Dict, user_prefs: Dict, mode: str = DEFAULT_MODE) -> Tuple[float, str]:
    """Score a single song against user preferences. Returns (score, explanation)."""
    w = get_weights(mode)
    score = 0.0
    reasons = []

    if song_dict["genre"] == user_prefs["favorite_genre"]:
        score += w["genre"]
        reasons.append(f"genre match (+{w['genre']})")

    if song_dict["mood"] == user_prefs["favorite_mood"]:
        score += w["mood"]
        reasons.append(f"mood match (+{w['mood']})")

    energy_diff = abs(song_dict["energy"] - user_prefs["target_energy"])
    energy_score = w["energy"] * (1 - energy_diff)
    score += energy_score
    reasons.append(f"energy similarity (+{energy_score:.2f})")

    if "acousticness" in song_dict and "likes_acoustic" in user_prefs:
        is_acoustic = song_dict["acousticness"] > 0.5
        if is_acoustic == user_prefs["likes_acoustic"]:
            score += w["acoustic"]
            reasons.append(f"acousticness match (+{w['acoustic']})")

    if "instrumentalness" in song_dict and "prefers_instrumental" in user_prefs:
        is_instrumental = song_dict["instrumentalness"] > 0.5
        if is_instrumental == user_prefs["prefers_instrumental"]:
            score += w["instrumental"]
            reasons.append(f"instrumentalness match (+{w['instrumental']})")

    if "popularity" in song_dict and "prefers_popular" in user_prefs:
        is_popular = song_dict["popularity"] > 0.5
        if is_popular == user_prefs["prefers_popular"]:
            score += w["popularity"]
            reasons.append(f"popularity match (+{w['popularity']})")

    # --- Advanced features ---

    # Decade proximity: closer decades score higher, max span = 40 years
    if "release_decade" in song_dict and "preferred_decade" in user_prefs:
        decade_diff = abs(song_dict["release_decade"] - user_prefs["preferred_decade"])
        decade_score = w["decade"] * max(0, 1 - decade_diff / 40)
        score += decade_score
        reasons.append(f"decade proximity (+{decade_score:.2f})")

    # Mood tags: per-tag weight, capped at mood_tags_max
    if "mood_tags" in song_dict and "liked_mood_tags" in user_prefs:
        song_tags = set(song_dict["mood_tags"].split("|")) if song_dict["mood_tags"] else set()
        user_tags = set(user_prefs["liked_mood_tags"].split("|")) if user_prefs["liked_mood_tags"] else set()
        overlap = len(song_tags & user_tags)
        tags_score = min(overlap * w["mood_tags"], w["mood_tags_max"])
        if tags_score > 0:
            score += tags_score
            matched = " + ".join(song_tags & user_tags)
            reasons.append(f"mood tags [{matched}] (+{tags_score:.2f})")

    # Lyrics language: exact match
    if "lyrics_language" in song_dict and "preferred_language" in user_prefs:
        if song_dict["lyrics_language"] == user_prefs["preferred_language"]:
            score += w["language"]
            reasons.append(f"language match (+{w['language']})")

    # Duration proximity: tolerance of 300 seconds (5 minutes)
    if "duration_sec" in song_dict and "target_duration_sec" in user_prefs:
        dur_diff = abs(song_dict["duration_sec"] - user_prefs["target_duration_sec"])
        dur_score = w["duration"] * max(0, 1 - dur_diff / 300)
        score += dur_score
        reasons.append(f"duration fit (+{dur_score:.2f})")

    # Replay value: boolean threshold at 0.5
    if "replay_value" in song_dict and "values_replayability" in user_prefs:
        is_replayable = song_dict["replay_value"] > 0.5
        if is_replayable == user_prefs["values_replayability"]:
            score += w["replay"]
            reasons.append(f"replay match (+{w['replay']})")

    explanation = "Matched on: " + ", ".join(reasons)
    return score, explanation


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        """Initialize the recommender with a catalog of songs."""
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top-k songs sorted by score descending for the given user."""
        scored = []
        for song in self.songs:
            song_dict = {
                "genre": song.genre,
                "mood": song.mood,
                "energy": song.energy,
            }
            user_dict = {
                "favorite_genre": user.favorite_genre,
                "favorite_mood": user.favorite_mood,
                "target_energy": user.target_energy,
            }
            s, _ = score_song(song_dict, user_dict)
            scored.append((s, song))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [song for _, song in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a human-readable explanation of why a song was recommended."""
        song_dict = {
            "genre": song.genre,
            "mood": song.mood,
            "energy": song.energy,
        }
        user_dict = {
            "favorite_genre": user.favorite_genre,
            "favorite_mood": user.favorite_mood,
            "target_energy": user.target_energy,
        }
        _, explanation = score_song(song_dict, user_dict)
        return explanation


def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from a CSV file and return a list of dictionaries with typed values."""
    songs = []
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                "id": int(row["id"]),
                "title": row["title"],
                "artist": row["artist"],
                "genre": row["genre"],
                "mood": row["mood"],
                "energy": float(row["energy"]),
                "tempo_bpm": float(row["tempo_bpm"]),
                "valence": float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
                "instrumentalness": float(row["instrumentalness"]),
                "popularity": float(row["popularity"]),
                "release_decade": int(row["release_decade"]),
                "mood_tags": row["mood_tags"],
                "lyrics_language": row["lyrics_language"],
                "duration_sec": int(row["duration_sec"]),
                "replay_value": float(row["replay_value"]),
            })
    return songs


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5,
                    mode: str = DEFAULT_MODE,
                    diverse: bool = False) -> List[Tuple[Dict, float, str]]:
    """Score all songs against user preferences and return the top-k.

    When diverse=False (default): pure score ranking.
    When diverse=True: greedy selection with penalties for repeated artists/genres.
    """
    scored = [(song, s, exp) for song in songs for s, exp in [score_song(song, user_prefs, mode)]]

    if not diverse:
        return sorted(scored, key=lambda x: x[1], reverse=True)[:k]

    # --- Greedy diverse selection ---
    # Pick songs one at a time. Before each pick, penalize candidates that
    # share an artist or genre with already-selected songs.
    remaining = sorted(scored, key=lambda x: x[1], reverse=True)
    selected = []
    picked_artists = []
    picked_genres = []

    for _ in range(min(k, len(remaining))):
        best_idx = 0
        best_adjusted = -1.0

        for i, (song, base_score, exp) in enumerate(remaining):
            penalty = 0.0
            artist_hits = picked_artists.count(song["artist"])
            genre_hits = picked_genres.count(song["genre"])
            penalty += artist_hits * ARTIST_REPEAT_PENALTY
            penalty += genre_hits * GENRE_REPEAT_PENALTY

            adjusted = base_score - penalty
            if adjusted > best_adjusted:
                best_adjusted = adjusted
                best_idx = i

        song, base_score, exp = remaining.pop(best_idx)

        # Build explanation showing penalty if applied
        penalty = 0.0
        penalty_reasons = []
        artist_hits = picked_artists.count(song["artist"])
        genre_hits = picked_genres.count(song["genre"])
        if artist_hits > 0:
            p = artist_hits * ARTIST_REPEAT_PENALTY
            penalty += p
            penalty_reasons.append(f"repeat artist '{song['artist']}' (-{p:.1f})")
        if genre_hits > 0:
            p = genre_hits * GENRE_REPEAT_PENALTY
            penalty += p
            penalty_reasons.append(f"repeat genre '{song['genre']}' (-{p:.1f})")

        if penalty_reasons:
            exp += ", DIVERSITY: " + ", ".join(penalty_reasons)

        selected.append((song, base_score - penalty, exp))
        picked_artists.append(song["artist"])
        picked_genres.append(song["genre"])

    return selected
