# Questline

A private, neon-styled habit and reminder tracker built to live on your phone. Each habit is a quest: you earn XP, level up through ranks, keep streaks going and unlock badges.

**Open it:** https://claude.ai/artifact/PXvHLqTpouCftdABchdtK3 (private: only you can open it while signed in to claude.ai).

**Put it on your iPhone home screen:** open the link in Safari, tap **Share**, then tap **Add to Home Screen**.

## What it does

- **Daily count quests**, like water (8 glasses = 2 L), steps (8k) and sleep (8–10 h). Tap + to log; tap the number to type an exact amount.
- **Daily check-offs**: yes/no habits, with optional specific days and a time of day.
- **Weekly goals**, like working out 3× a week or going for a drive 1× a week.
- **Reminders and to-dos** with a date, an optional time, repeats (daily, weekly, monthly) and an important flag. Overdue items glow red and show a badge on the tab bar. Each reminder can be added to Google Calendar so your phone alerts you even when Questline is closed.
- **RPG layer**: XP, levels, ranks (Rookie → Boss Mode), a daily streak, a +50 XP perfect-day bonus, 12 badges, confetti, sound effects and haptics.
- **Stats**: an 18-week consistency heatmap, a 14-day clear-rate chart, current and best streaks per quest, lifetime totals (litres drunk, km walked, average sleep) and badges.
- **Everything is editable**: add, edit, reorder, archive, restore or delete quests, edit past days from the week strip, and export or import a JSON backup.

## How it's built

`questline.html` is the whole app: one page of HTML, CSS and plain JavaScript with no build step and no frameworks. It's published as a claude.ai Artifact.

- **Storage:** the artifact's database, readable and writable only by the owner (one `app/profile` doc for quests, reminders and settings, plus one `logs/<YYYY-MM>` doc per month of activity). It syncs live across devices. A local copy is cached in the browser for an instant start, and if the database isn't available the app falls back to on-device storage.
- **XP, levels, streaks and badges** are all calculated from the logs, so editing a past day recalculates everything consistently.

To change the app, edit `questline.html` and republish it to the same artifact URL.
