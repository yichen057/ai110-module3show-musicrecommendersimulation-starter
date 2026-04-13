"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from tabulate import tabulate
from src.recommender import load_songs, recommend_songs, max_score


def format_reasons(explanation: str) -> str:
    """Compress explanation into a single-line summary."""
    parts = explanation.replace("Matched on: ", "").split(", ")
    short = []
    for part in parts:
        if part.startswith("DIVERSITY:"):
            short.append(part.replace("DIVERSITY: ", "").strip())
        else:
            short.append(part)
    return " | ".join(short)


def print_profile_header(name: str, prefs: dict) -> None:
    """Print a formatted header for a user profile."""
    print(f"\n{'='*100}")
    print(f"  PROFILE: {name}")
    print(f"  Genre: {prefs['favorite_genre']}  |  Mood: {prefs['favorite_mood']}  "
          f"|  Energy: {prefs['target_energy']}  |  Decade: {prefs['preferred_decade']}"
          f"  |  Language: {prefs['preferred_language']}"
          f"  |  Tags: {prefs['liked_mood_tags'].replace('|', ', ')}")
    print(f"{'='*100}")


def print_results_table(recommendations: list, ms: float) -> None:
    """Print a single table with scores and reasons per song."""
    rows = []
    for rank, (song, score, explanation) in enumerate(recommendations, 1):
        reasons = format_reasons(explanation)
        rows.append([
            f"#{rank}",
            song["title"],
            song["artist"],
            f"{song['genre']}/{song['mood']}",
            song["energy"],
            f"{score:.2f}/{ms:.1f}",
            reasons,
        ])

    print(tabulate(
        rows,
        headers=["Rank", "Title", "Artist", "Genre/Mood", "Energy", "Score", "Breakdown"],
        tablefmt="grid",
        maxcolwidths=[None, None, None, None, None, None, 80],
    ))


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"\nLoaded {len(songs)} songs from catalog.\n")

    profiles = {
        "High-Energy Pop Fan": {
            "favorite_genre": "pop",
            "favorite_mood": "happy",
            "target_energy": 0.85,
            "likes_acoustic": False,
            "prefers_instrumental": False,
            "prefers_popular": True,
            "preferred_decade": 2020,
            "liked_mood_tags": "uplifting|euphoric|bright",
            "preferred_language": "english",
            "target_duration_sec": 210,
            "values_replayability": True,
        },
        "Chill Lofi Listener": {
            "favorite_genre": "lofi",
            "favorite_mood": "chill",
            "target_energy": 0.35,
            "likes_acoustic": True,
            "prefers_instrumental": True,
            "prefers_popular": False,
            "preferred_decade": 2020,
            "liked_mood_tags": "dreamy|peaceful|cozy",
            "preferred_language": "instrumental",
            "target_duration_sec": 220,
            "values_replayability": True,
        },
        "Deep Intense Rock": {
            "favorite_genre": "rock",
            "favorite_mood": "intense",
            "target_energy": 0.90,
            "likes_acoustic": False,
            "prefers_instrumental": False,
            "prefers_popular": True,
            "preferred_decade": 2010,
            "liked_mood_tags": "aggressive|powerful|driving",
            "preferred_language": "english",
            "target_duration_sec": 260,
            "values_replayability": True,
        },
        # --- Adversarial profiles for stress-testing ---
        "Sad But Energetic": {
            "favorite_genre": "classical",
            "favorite_mood": "melancholy",
            "target_energy": 0.90,
            "likes_acoustic": True,
            "prefers_instrumental": True,
            "prefers_popular": False,
            "preferred_decade": 1990,
            "liked_mood_tags": "melancholic|haunting|dark",
            "preferred_language": "instrumental",
            "target_duration_sec": 340,
            "values_replayability": False,
        },
        "Acoustic Popular Pop": {
            "favorite_genre": "pop",
            "favorite_mood": "happy",
            "target_energy": 0.80,
            "likes_acoustic": True,
            "prefers_instrumental": False,
            "prefers_popular": True,
            "preferred_decade": 2020,
            "liked_mood_tags": "uplifting|carefree|warm",
            "preferred_language": "english",
            "target_duration_sec": 200,
            "values_replayability": True,
        },
        "Chill Metal Listener": {
            "favorite_genre": "metal",
            "favorite_mood": "chill",
            "target_energy": 0.20,
            "likes_acoustic": False,
            "prefers_instrumental": False,
            "prefers_popular": False,
            "preferred_decade": 2000,
            "liked_mood_tags": "dark|nocturnal|intimate",
            "preferred_language": "english",
            "target_duration_sec": 280,
            "values_replayability": False,
        },
    }

    # Default: Balanced mode with diversity enabled
    mode = "balanced"
    ms = max_score(mode)

    for profile_name, user_prefs in profiles.items():
        print_profile_header(profile_name, user_prefs)

        recommendations = recommend_songs(
            user_prefs, songs, k=5, mode=mode, diverse=True
        )

        print()
        print_results_table(recommendations, ms)
        print()


if __name__ == "__main__":
    main()
