import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

GENRE_WEIGHT = 2.0
MOOD_WEIGHT = 1.0
ENERGY_WEIGHT = 1.0
ACOUSTIC_WEIGHT = 0.5
INSTRUMENTAL_WEIGHT = 0.5
POPULARITY_WEIGHT = 0.5


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


def score_song(song_dict: Dict, user_prefs: Dict) -> Tuple[float, str]:
    """Score a single song against user preferences. Returns (score, explanation)."""
    score = 0.0
    reasons = []

    if song_dict["genre"] == user_prefs["favorite_genre"]:
        score += GENRE_WEIGHT
        reasons.append(f"genre match (+{GENRE_WEIGHT})")

    if song_dict["mood"] == user_prefs["favorite_mood"]:
        score += MOOD_WEIGHT
        reasons.append(f"mood match (+{MOOD_WEIGHT})")

    energy_diff = abs(song_dict["energy"] - user_prefs["target_energy"])
    energy_score = ENERGY_WEIGHT * (1 - energy_diff)
    score += energy_score
    reasons.append(f"energy similarity (+{energy_score:.2f})")

    if "acousticness" in song_dict and "likes_acoustic" in user_prefs:
        is_acoustic = song_dict["acousticness"] > 0.5
        if is_acoustic == user_prefs["likes_acoustic"]:
            score += ACOUSTIC_WEIGHT
            reasons.append(f"acousticness match (+{ACOUSTIC_WEIGHT})")

    if "instrumentalness" in song_dict and "prefers_instrumental" in user_prefs:
        is_instrumental = song_dict["instrumentalness"] > 0.5
        if is_instrumental == user_prefs["prefers_instrumental"]:
            score += INSTRUMENTAL_WEIGHT
            reasons.append(f"instrumentalness match (+{INSTRUMENTAL_WEIGHT})")

    if "popularity" in song_dict and "prefers_popular" in user_prefs:
        is_popular = song_dict["popularity"] > 0.5
        if is_popular == user_prefs["prefers_popular"]:
            score += POPULARITY_WEIGHT
            reasons.append(f"popularity match (+{POPULARITY_WEIGHT})")

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
            })
    return songs


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Score all songs against user preferences and return the top-k as (song, score, explanation) tuples."""
    # --- Beginner-friendly version ---
    # scored = []
    # for song in songs:
    #     s, explanation = score_song(song, user_prefs)
    #     scored.append((song, s, explanation))
    # scored.sort(key=lambda x: x[1], reverse=True)
    # return scored[:k]

    # --- Pythonic way (same logic, compact) ---
    scored = [(song, s, exp) for song in songs for s, exp in [score_song(song, user_prefs)]]
    return sorted(scored, key=lambda x: x[1], reverse=True)[:k]
