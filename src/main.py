"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from src.recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    # User taste profile for content-based filtering
    user_prefs = {
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.80,
        "likes_acoustic": False,
        "prefers_instrumental": False,
        "prefers_popular": True,
    }

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print(f"\n{'='*50}")
    print(f"  Top {len(recommendations)} Recommendations")
    print(f"  User: {user_prefs['favorite_genre']} | {user_prefs['favorite_mood']} | energy {user_prefs['target_energy']}")
    print(f"{'='*50}")

    for rank, (song, score, explanation) in enumerate(recommendations, 1):
        reasons = explanation.replace("Matched on: ", "").split(", ")
        print(f"\n  #{rank}  {song['title']} — {song['artist']}")
        print(f"       Score: {score:.2f} / 5.50")
        print(f"       Genre: {song['genre']} | Mood: {song['mood']} | Energy: {song['energy']}")
        print(f"       Reasons:")
        for reason in reasons:
            print(f"         + {reason}")

    print(f"\n{'='*50}")


if __name__ == "__main__":
    main()
