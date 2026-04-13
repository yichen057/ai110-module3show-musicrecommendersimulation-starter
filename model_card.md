# Model Card: Music Recommender Simulation

## 1. Model Name

**VibeFinder 1.0**

---

## 2. Intended Use

VibeFinder suggests songs from a small 18-song catalog based on a user's taste profile. It takes in preferences like favorite genre, mood, energy level, decade, language, mood tags, and a few yes/no flags, then ranks every song by how well it fits.

It assumes each user has one fixed set of preferences. It does not learn or adapt over time. It is built for classroom exploration, not for real music streaming. It should not be used to make decisions about what music to license, promote, or remove.

---

## 3. How the Model Works

Each song gets a score from 0 to 10.0 (Balanced mode) based on how well it matches the user's preferences. The system checks 11 things:

- **Genre** (1.0 points): Does the song's genre exactly match the user's favorite? If yes, +1.0. If no, +0.
- **Mood** (1.0 points): Same idea. Exact match = +1.0, otherwise nothing.
- **Energy** (up to 2.0 points): How close is the song's energy to the user's target? A perfect match earns 2.0. The farther apart they are, the fewer points.
- **Acoustic** (0.5 points): Is the song acoustic, and does the user want acoustic? If they agree, +0.5.
- **Instrumental** (0.5 points): Same logic for instrumental tracks.
- **Popularity** (0.5 points): Same logic for mainstream vs. niche preference.
- **Decade proximity** (up to 1.0 points): How close is the release decade to the user's preferred era? Uses a 40-year max span.
- **Mood tags** (up to 1.5 points): Detailed tags like "dreamy", "aggressive", "nostalgic." Each matching tag earns 0.3 points, capped at 1.5.
- **Language** (1.0 points): Does the lyrics language match the user's preference? Exact match = +1.0.
- **Duration** (up to 0.5 points): How close is the song's length to the user's preferred duration? 5-minute tolerance.
- **Replay value** (0.5 points): Is the song highly replayable, and does the user care about that?

The system supports three scoring modes (Balanced, Genre-First, Energy-Focused) via a Strategy pattern. Each mode uses different weights but the same scoring logic. An optional diversity penalty prevents the same artist or genre from dominating the top results.

We started with genre weighted at 2.0 and energy at 1.0. During testing, we found genre was too dominant. We flipped them: genre down to 1.0, energy up to 2.0.

---

## 4. Data

The catalog has 18 songs stored in a CSV file. Each song has 16 attributes: title, artist, genre, mood, energy, tempo, valence, danceability, acousticness, instrumentalness, popularity, release_decade, mood_tags, lyrics_language, duration_sec, and replay_value.

There are 14 different genres, but most have only 1 song. Lofi has 3 songs and pop has 2. Moods include happy, chill, intense, melancholy, aggressive, and others — 14 unique values total. Languages include english (11 songs), instrumental (5), spanish (1), and japanese (1).

Energy ranges from 0.22 (Sunday Morning Tea) to 0.96 (Basement Fury). Release decades span from 1990 to 2020. Duration ranges from 180 to 345 seconds.

The dataset is missing some common genres like country, reggae, and k-pop. There are no songs that combine unusual trait pairs — like calm metal or energetic classical — which limits testing. Three features in the CSV (tempo, valence, danceability) are not used by the scoring function.

---

## 5. Strengths

The system works well when a user's preferences line up cleanly with a song in the catalog. For example:

- The **Chill Lofi Listener** got Library Rain as #1 with 9.37/10.0. Nearly every feature matched, including mood tags (dreamy + cozy + peaceful).
- The **High-Energy Pop Fan** got Sunrise City at 9.04/10.0. Mood tags and decade proximity added useful differentiation beyond the original 6 features.
- The **Deep Intense Rock** profile got Storm Runner at 9.37/10.0. All three mood tags (aggressive, powerful, driving) matched perfectly.

The explanation output is a strength. Each recommendation shows exactly which features matched and how many points each one earned. The tabulate formatted tables make it easy to compare results at a glance.

The Strategy pattern lets users switch between Balanced, Genre-First, and Energy-Focused modes to see how the same profile produces different results under different philosophies.

The diversity penalty breaks filter bubbles. Without it, the Chill Lofi Listener gets three lofi songs (two by LoRoom) in the top 3. With it, an ambient track surfaces at #2, giving the user variety.

---

## 6. Limitations and Bias

The system uses exact string matching for genre and mood. "Pop" and "indie pop" get zero partial credit, even though they sound similar. Same for "chill" and "relaxed."

This creates a filter bubble for rare genres. Classical, metal, folk, and world each have only 1 song. The diversity penalty helps by preventing the same genre from repeating, but users of rare genres still have only one matching song.

During testing, the Chill Metal Listener profile asked for chill, low-energy music. The system originally recommended Basement Fury (aggressive, energy 0.96) as #1 because the old genre weight of 2.0 overpowered everything else. After the weight shift, Basement Fury dropped — but adding advanced features (decade, language) accidentally pushed it back to #1 in Balanced mode. More features do not automatically improve accuracy.

The scoring function still ignores tempo, valence, and danceability. Dance-oriented and tempo-sensitive listeners remain invisible.

The language feature introduces a new bias: 11 of 18 songs are English. Non-English users (Spanish, Japanese) have only 1 song each that can earn the +1.0 language bonus.

The popularity feature creates a feedback loop. Songs below the 0.5 popularity threshold can never earn the +0.5 bonus for mainstream users.

---

## 7. Evaluation

We tested six user profiles across three scoring modes, with and without diversity penalties.

**Standard profiles (Balanced mode):**
- High-Energy Pop Fan — Sunrise City scored 9.04/10.0. Matched intuition.
- Chill Lofi Listener — Library Rain scored 9.37/10.0. Matched intuition.
- Deep Intense Rock — Storm Runner scored 9.37/10.0. Matched intuition.

**Adversarial profiles:**
- Sad But Energetic (classical + melancholy + high energy) — Ghost Waltz won at 7.39 despite energy mismatch. Genre + mood + decade + language bonus outweighed everything.
- Acoustic Popular Pop (pop + happy + acoustic) — Sunrise City won at 8.54 even though it is not acoustic.
- Chill Metal Listener — Results varied by mode: Basement Fury #1 in Balanced (5.76) and Genre-First (6.28), Coffee Shop Stories #1 in Energy-Focused (5.48).

**Diversity testing (Chill Lofi Listener):**
- Without diversity: top 3 = Library Rain, Midnight Coding (LoRoom), Focus Flow (LoRoom). Two by LoRoom, all lofi.
- With diversity: top 3 = Library Rain, Spacewalk Thoughts (ambient), Midnight Coding (-1.5 genre penalty). Ambient track surfaces.

We hand-calculated scores for key songs and verified all calculations matched program output.

---

## 8. Future Work

- **Add genre similarity.** Instead of exact matching, give partial credit for related genres. Pop and indie pop could earn 0.5 instead of 0.0.
- **Use the remaining unused features.** Tempo, valence, and danceability are still in the CSV but not scored. A dance-loving user should not get Ghost Waltz (danceability 0.28) when Neon Cumbia (0.92) exists.
- **Tune diversity penalties per mode.** The current penalties (-3.0 artist, -1.5 genre) are fixed. They could be mode-specific — Genre-First mode might use a smaller genre penalty.
- **Add a user-facing mode selector.** A CLI flag like `--mode energy-focused --diverse` would let users switch modes without editing main.py.

---

## 9. Personal Reflection

My biggest learning moment came in two parts. First, watching genre weight at 2.0 break the Chill Metal recommendation — the system handed back aggressive thrash metal to someone asking for calm music. That taught me weights are design decisions, not just numbers.

The deeper lesson came when adding five new features. I expected the system to get smarter. Instead, Basement Fury climbed back to #1 for Chill Metal because it gained decade and language bonuses. More features do not automatically mean better results. Every new feature can help one profile and hurt another.

I used Claude to help design adversarial profiles, implement the Strategy pattern, build the diversity penalty, and format output with tabulate. It was useful for spotting data tensions — like the fact that acoustic songs are almost never popular. But I had to hand-verify every score calculation. AI tools accelerate work, but verification is still my responsibility.

I was surprised that if-statements, addition, and a greedy loop can produce results that genuinely feel like a real recommender. When Library Rain scored 9.37 with mood tags like "dreamy + cozy + peaceful," it felt like the system understood the vibe. It did not — it just matched strings and added numbers. The illusion breaks when preferences conflict, and that is where adversarial testing is essential.

The diversity penalty was the most satisfying feature. It solved a real user experience problem with simple subtraction. The Strategy pattern showed me why design patterns exist — not for complexity, but for making changes easy. This project changed how I think about Spotify. When a recommendation feels wrong, it might be a weight, a missing feature, a catalog gap, or a lack of diversity logic. Recommender systems are never "done" — they are a series of trade-offs made visible through evaluation.
