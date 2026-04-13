# Reflection: Comparing User Profile Outputs

## High-Energy Pop Fan vs. Chill Lofi Listener

The Pop Fan wants upbeat, popular, high-energy pop music (energy 0.85). The Lofi Listener wants the opposite — quiet, acoustic, instrumental tracks to study to (energy 0.35). Their top results are completely different worlds: Sunrise City (pop, happy, 0.82 energy) vs. Library Rain (lofi, chill, 0.35 energy), with zero overlap in their top 5.

This makes sense because they disagree on almost every preference — genre, mood, energy level, acoustic, instrumental, and popularity all point in opposite directions. It is like asking one person what they want to hear at a party and another what they want to hear in a library. The system correctly separates them, which tells us the scoring features are actually working when preferences are cleanly different.

## High-Energy Pop Fan vs. Acoustic Popular Pop

These two profiles look almost identical on paper — both want pop, happy, and similar energy (0.85 vs. 0.80). The only difference is that the Acoustic Popular Pop user set `likes_acoustic: True`. You would expect their results to shift toward acoustic-sounding pop music.

But that is not what happens. Sunrise City still wins for both profiles (5.47 vs. 4.96), even though Sunrise City has an acousticness of only 0.18 — meaning it is not acoustic at all. The acoustic preference only costs 0.5 points when it misses, and genre + mood + energy together are worth up to 4.0 points. So the system essentially ignores the acoustic request because it is not weighted heavily enough to matter. This is like telling a waiter "I want pasta, but make it gluten-free" and getting regular pasta anyway because the kitchen prioritizes the "pasta" part and treats "gluten-free" as optional.

## High-Energy Pop Fan vs. Deep Intense Rock

Both users want loud, high-energy music (0.85 vs. 0.90), but one wants happy pop and the other wants intense rock. Their #1 picks are completely different — Sunrise City (pop, happy) vs. Storm Runner (rock, intense) — which makes sense because genre and mood are the two biggest scoring features.

What is interesting is that Gym Hero (pop, intense, energy 0.93) shows up as #2 for both profiles. For the Pop Fan, it matches on genre (pop) and energy, but misses on mood (intense instead of happy). For the Rock Fan, it matches on mood (intense) and energy, but misses on genre (pop instead of rock). It earns similar scores through completely different reasons. This tells us that a high-energy song with broad appeal can "sneak into" any profile's top list just by being close enough on energy and matching one major feature — the system does not penalize for mismatches, it just does not reward them.

## Chill Lofi Listener vs. Sad But Energetic

The Lofi Listener wants calm, low-energy music (0.35). The Sad But Energetic user also likes quiet genres (classical) but wants high energy (0.90) — a contradictory combination, like asking for a loud lullaby.

The Lofi Listener gets a clean top 5 full of lofi and ambient tracks. The Sad But Energetic user gets Ghost Waltz (classical, melancholy, energy 0.30) as #1 despite wanting energy at 0.90. Ghost Waltz only scores 0.80 on the energy component out of a possible 2.0, but it locks in genre + mood (1.0 + 1.0 = 2.0) which no other song can match. The rest of their top 5 is a scattered mix — Focus Flow, Pixel Party, Library Rain — none of which match on genre or mood, just energy proximity and boolean features. This shows that when a user's preferences contradict each other, the system does not know how to compromise. It just picks whichever song wins the math, even if the result does not feel right to a human listener.

## Deep Intense Rock vs. Chill Metal Listener

Both users like heavy music — rock and metal are neighboring genres. But the Rock Fan wants it loud and intense (energy 0.90), while the Chill Metal Listener wants it quiet and calm (energy 0.20). Their results reveal the most important lesson from our experiments.

Under the original weights (genre = 2.0), both users got aggressive, high-energy songs at #1 — Storm Runner for Rock, Basement Fury for Metal. The system treated genre as the most important thing, almost like a filter. But recommending Basement Fury (aggressive, energy 0.96) to someone who asked for "chill, low-energy metal" is like recommending a horror movie to someone who said they like thrillers but want something relaxing tonight. The label matches, but the vibe is completely wrong.

After we shifted the weights (genre from 2.0 to 1.0, energy from 1.0 to 2.0), the Chill Metal Listener's #1 changed to Spacewalk Thoughts (ambient, chill, energy 0.28). This song is not metal at all, but it matches the mood and energy the user actually asked for. The Rock Fan's results barely changed because Storm Runner already matched on everything. This taught us that weight tuning matters most when user preferences conflict — and that genre should inform recommendations, not override everything else about what the user actually wants to hear.

## Chill Lofi Listener vs. Chill Metal Listener

Both users want chill, low-energy music — they agree on mood and energy but disagree on genre (lofi vs. metal). You would expect their top results to overlap on the chill/low-energy songs but diverge based on genre preference.

After the weight adjustment, that is roughly what happens. Library Rain and Spacewalk Thoughts appear near the top for both profiles — they are the chillest, lowest-energy songs in the catalog. The difference is that the Lofi Listener gets three lofi tracks at the top (Library Rain, Midnight Coding, Focus Flow) because the catalog has multiple lofi songs. The Metal Listener gets Basement Fury at #3 — the only metal song — but it feels out of place next to ambient and lofi tracks at #1 and #2. This highlights a catalog problem, not a scoring problem: if we had a song like "acoustic metal ballad, chill, energy 0.3" in the dataset, it would likely rank #1 for this user. The system can only recommend what it has.

With the diversity penalty turned on, the Lofi Listener's results improve noticeably. Instead of three lofi songs in the top 3 (two by LoRoom), Spacewalk Thoughts (ambient) jumps to #2 and Midnight Coding drops to #3 with a -1.5 genre penalty. The user still gets lofi at #1 and #3, but now they also discover an ambient track that matches their vibe. For the Metal Listener, the diversity penalty has less impact because the top results are already spread across different genres — the problem there was never repetition, it was the lack of chill metal in the catalog.

---

## How the Four Challenges Changed the System

### Challenge 1: Advanced Features

Adding five new features (decade, mood tags, language, duration, replay) increased the max score from 5.5 to 10.0 and gave the system more ways to differentiate songs. The mood tags feature was the most impactful — it rewards partial overlap between a user's vibes and a song's vibes, which is something the single "mood" field could never do. For example, the Deep Intense Rock profile matches Storm Runner on all three tags (aggressive + powerful + driving) for +0.90, while Gym Hero only matches on two (aggressive + euphoric → only euphoric overlaps with the user's tags, so +0.30). This creates meaningful separation between songs that previously scored identically on mood.

But more features also introduced new problems. Basement Fury climbed back to #1 for Chill Metal in Balanced mode because it gained +1.0 for decade match and +1.0 for language match. These features have nothing to do with vibe, but they added enough points to overcome the energy penalty. The lesson: every new feature is a trade-off. It helps some profiles and hurts others.

### Challenge 2: Scoring Modes

The Strategy pattern was the cleanest change architecturally. Three weight dictionaries, one scoring function — switching modes is just passing a different string. The most revealing comparison was the Chill Metal Listener across all three modes: Basement Fury at #1 in Genre-First (genre=3.0 dominates), Basement Fury at #1 in Balanced (decade and language help), Coffee Shop Stories at #1 in Energy-Focused (energy=3.0 rewards low-energy songs). No single mode is "correct" — each embodies a different philosophy about what matters most.

### Challenge 3: Diversity Penalty

The diversity penalty was the most practically useful change. Before it, the Chill Lofi Listener got two LoRoom tracks in the top 3 — same artist, same genre, very similar energy. With the penalty, LoRoom's second song gets -1.5 (repeat genre) or -4.5 (repeat genre + repeat artist), and Spacewalk Thoughts (ambient, different artist) rises to #2. The user still gets lofi as their top pick, but now the results feel like a curated playlist rather than a genre dump.

The penalty values (-3.0 for artist, -1.5 for genre) were chosen to be strong enough to matter but not so strong that they override clear matches. An artist penalty of 3.0 means a second song by the same artist needs to outscore alternatives by 3+ points to still make the list — that is a high bar, which is appropriate since hearing the same artist twice in 5 songs feels repetitive.

### Challenge 4: Visual Output

Switching from plain text to tabulate tables made a bigger difference than expected. The summary table lets you scan all 5 recommendations at a glance — title, artist, genre, mood, energy, score — without reading through walls of text. The detail cards underneath explain why each song was picked, with `+` for bonuses and `-` for diversity penalties. This two-layer format (overview first, details on demand) mirrors how real dashboards present information.

The formatted output also made debugging easier. When comparing results across modes, the table format made it obvious when rankings shifted — you could see at a glance that Spacewalk Thoughts jumped from #4 to #2 when diversity was turned on, without having to count through paragraphs of text.
