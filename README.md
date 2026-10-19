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

---

# ARC Raiders Utility

A private, second-screen companion for ARC Raiders. It tells you whether to keep, recycle or sell any item, based on your own quests, workbench upgrades and stash.

**Open it:** https://claude.ai/artifact/7GNtodf8D9unQwx6EHyG1m (private: only you can open it while signed in to claude.ai). It's laid out for a monitor or tablet next to your PC, and also works on a phone.

## What it does

- **Lookup:** search any item (press `/`) for a verdict stamp: KEEP, RECYCLE, SELL, STOCK (crafting material or trade currency), GEAR or LEARN, with the reason. It also shows sell value against recycled-parts value, what the item is needed for, what it recycles into, and where to find it: ARC drops, loot areas, items that recycle into it, trader deals, crafting recipes and quest rewards.
- **Needs:** a shopping list built from your open quests, your next bench upgrades and any projects you track, minus what's in your stash. Switch between "Next steps" and "Everything left", and filter by quests, workshop or projects.
- **Stash:** drop in stash screenshots and Claude reads the items and counts. You review the list before anything is saved. You can also add items by name. Shows space used against your stash level, stash value, and a "Clear space" list of what to sell or recycle first.
- **Quests:** all 100 trader quests with objectives, maps, items to deliver and rewards. Filter by trader and status, tick quests off, or mark every earlier quest in a chain done at once.
- **Workshop:** set each bench's level and see what the next level needs. A bench shows "Ready" when your stash covers it, and "I upgraded it" takes the materials off your stash list. Projects (Trophy Display, Expeditions) can be tracked phase by phase, including what you've already delivered.
- **Plan:** pick tonight's targets (available quests, items your next steps need, plus anything extra you want to hunt). Maps are ranked by how much of that you can do there: quests on the map, ARC that drop what you need (credited to the easiest one that drops it), and your own pinned spots. "Plan this raid" turns the best map into a checklist; anything not tied to a map is grouped by loot area.
- **Maps:** labeled maps of Dam Battlegrounds, Buried City, The Spaceport, The Blue Gate and both floors of Stella Montis (area names, loot types, extracts, high-value zones), plus satellite tiles for Riven Tides. Add your own pins (extract, loot spot, locked room, ARC, quest, note), drag them to move them, and link an item so the planner sends you there. A side panel lists the open quests and ARC on the map with the drops you still need. You can note the current map condition; it clears at the top of the hour.
- **ARC:** a field guide to all 17 ARC machines, with photo, threat, description, weak point, maps and drops. Parts you still need are marked, and each card shows how many times that ARC has killed you, from your raid log.
- **Loadouts:** build kits from an augment, shield, two weapons with only compatible mods, matching ammo, and quick-use items. Each kit shows the value at risk (and its share of your stash value), weight against the augment's limit, whether the shield fits the augment, and what's missing from your stash.
- **Raid log:** two clicks per raid (map, then Extracted or Died), with optional loot value, kit, cause of death and a note. "Fill from a screenshot" reads the end-of-raid screen, can add the extracted items to your stash list, and can take a lost kit off it. Undo is in the confirmation. Stats cover extract rate (overall and the last 10 raids), average loot, value of kits lost, a strip of recent outcomes, extract rate by map and what killed you. Extracted and died use blue and orange, which color-blind readers can tell apart, plus a ✕ mark on deaths.
- **Pre-raid check** (on the Plan tab): pick the kit for the raid and see whether your stash covers it, then tick a short checklist (shield, repairs, heals and ammo, backpack room, keys, safe pocket) with your own items added. Logging a raid resets it.
- **Blueprints:** all 83 blueprints grouped by weapons, mods, quick use and augments. Tick the ones you've learned. Learned blueprints flip spare copies to SELL, and each row shows where to craft the item and whether your bench is high enough.
- **Setup:** a two-minute setup (bench levels plus the quest each trader is on) so a mid-game account starts with accurate verdicts.

Map conditions aren't scheduled in the app: since update 1.42 they follow region-based schedules and there's no open feed. The Maps tab links to live trackers instead. Marker positions (loot containers, spawns) aren't included because no openly licensed set exists; the labeled maps and your own pins cover that.

## How it's built

- `arc-utility.html` is the whole app: plain HTML, CSS and JavaScript, no build step. It's published as a claude.ai Artifact along with two data files.
- The map viewer is [Leaflet](https://leafletjs.com) 1.9.4 loaded from cdnjs, with its CSS inlined.
- `arc-utility/game.json`, `arc-utility/icons.webp` and the map tiles in `arc-utility/maps/` are made by `tools/build_arc_data.py` from the community data repo [RaidTheory/arcraiders-data](https://github.com/RaidTheory/arcraiders-data) (MIT, the data behind [arctracker.io](https://arctracker.io)). They're published next to the page under `data/` (`data/game.json`, `data/icons.webp`, `data/bots/<id>.webp`, `data/maps/<layer>/<zoom>/<x>_<y>.webp`). The map tiles (135 files, about 12 MB) aren't committed; the script regenerates them. Game content is © Embark Studios; this is a fan tool, not affiliated with them.
- **Storage:** the artifact's database, which only the owner can read or write: `app/progress` (quests, bench levels, projects, learned blueprints, session plan, pre-raid check, map conditions), `app/stash`, `app/pins`, `app/kits` and `app/raids` (the last 2,000 raids in full; older ones are folded into the totals). A copy is cached in the browser, and the app falls back to on-device storage if the database isn't available.
- **Screenshot reading** uses the artifact's `sample` capability with images. It runs on your own Claude account and asks your permission the first time.

## Refreshing the game data after a patch

```sh
git clone --depth 1 https://github.com/RaidTheory/arcraiders-data /tmp/arcraiders-data
python3 tools/build_arc_data.py /tmp/arcraiders-data
```

Then republish `arc-utility.html` to the same artifact URL, with everything in `arc-utility/` published under `data/` (`game.json`, `icons.webp`, `bots/` and `maps/`). Your progress, stash and pins are stored separately, so they're kept. If only the page changed, republish just `arc-utility.html`: files already published stay in place.
