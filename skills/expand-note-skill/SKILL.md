---
name: expand-note-skill
description: "Expand shorthand notes and file them in the right app."
version: 0.1.0
author: neo-anderson, Hermes Agent
license: MIT
platforms: [macos, linux, windows]
metadata:
  hermes:
    tags: [notes, shorthand, expansion, routing, orchestration]
    related_skills: [bearcli, apple-notes, obsidian]
---

# Expand & File a Note

Turn a shorthand note into a complete note and file it in the user's chosen app. This is an orchestrator: it expands the shorthand, picks a destination app, discovers tags/wikilinks, and handles cross-linking — then delegates the actual write to the app-specific skill (`bearcli`, `apple-notes`, or `obsidian`).

## When to Use

- User provides a shorthand/fragment note and asks to "expand it" or "turn this into a note" (e.g. "write a bear note expanding on this shorthand by adding in missing details").
- You need to decide where an expanded note belongs (Bear, Apple Notes, Obsidian, elsewhere).

## Procedure

1. **Expand the shorthand.** Fill in the missing details the user implied — dates, names, context, follow-ups. Keep the original meaning; add what's plausibly intended, flag what you guessed. Output the expanded draft to the user for confirmation before writing anything.

2. **Ask where it goes.** Present the destination choices and let the user pick:
   - **Bear notes** → `bearcli` skill (macOS, Bear 2.8+).
   - **Apple Notes** → `apple-notes` skill (macOS, `memo`).
   - **Obsidian** → `obsidian` skill (filesystem vault, wikilinks).
   - **Elsewhere** (a file, a vault path, a service) → handle directly or ask.
   Do not guess the destination — this is the one question that gates everything downstream.

3. **Build the title.** Use the template `DATE — REFERENCE TOPICS`, where DATE is the note's date (ISO `YYYY-MM-DD`) and REFERENCE TOPICS is a comma list of the note's subjects, phrased as short human-readable topics rather than tags (e.g. `today — birthday plan, ramen with Andrew, create new Hermes skill`). Match the casing/style the user used in their shorthand.

4. **Discover existing tags / topics.** Before tagging, list what already exists so you reuse the right tags instead of inventing new ones:
   - Bear: `bearcli tags list --format json` (see `bearcli` skill).
   - Obsidian: `search_files(pattern="*", target="content", file_glob="*.md")` for existing topic tags.
   Match existing subtags (e.g. `#me/family/Gina/*`) over flat ones. If none fit, surface 2–3 concrete suggestions and let the user pick — don't invent tags silently.

5. **Check for duplicates / related content.** Search the destination for the same or similar content (by title keywords, topic tags, or body overlap):
   - Bear: `bearcli search "..." --format json`.
   - Obsidian: `search_files(target="content", pattern="topic-keyword", file_glob="*.md")`.
   - Apple Notes: `memo notes -s "query"`.

6. **Decide cross-link vs. merge.** If a match is found, ASK the user whether to cross-link, merge, or move — then recommend the best option:
   - **Cross-link** (recommend when the notes are related but distinct): add a reference to the existing note (Bear `#tag`/pin, Obsidian `[[wikilink]]`, Apple Notes a plain-text pointer). Best when both carry independent value.
   - **Merge** (recommend when one is a subset/draft of the other): fold the shorthand's content into the existing note and delete the duplicate. Best when they're the same fact stated twice.
   - **Move** (recommend when they're the same note in the wrong place): relocate rather than duplicate. Best when content is identical and only location/folder differs.
   State your recommendation and why, then act on the user's choice.

7. **Write the note.** Delegate to the chosen app's skill (`bearcli` / `apple-notes` / `obsidian`) — do not hand-roll the write. For multi-block edits, write to `/tmp/` first, then apply (see that skill's procedure). Re-read the note afterward and confirm the change landed before reporting success.

8. **Clean up.** Ask before deleting any `/tmp/` working files — they're the diff/undo backup.

## Pitfalls

- **Don't pick the destination yourself.** The whole point is the user chooses; routing to the wrong skill wastes the app-specific write workflow.
- **Don't invent tags/topics.** Discover existing ones first; surface suggestions when nothing fits.
- **Don't skip the duplicate check.** Writing a near-duplicate that could have been cross-linked or merged is the main failure mode — always search first, then recommend.
- **Title date is the note's date, not today** — unless they're the same. Derive it from the shorthand's content.
- **App-specific write rules still apply** — hash models (Bear `overwrite --base`), interactive editors (`memo -a`), wikilink syntax (Obsidian) — follow the destination skill, not a generic write.

## Verification

- Destination matches the user's choice; the correct app-specific skill performed the write.
- Title follows `DATE — TOPICS`.
- Tags (if any) resolve to existing ones; new-subtag suggestions were surfaced, not silently created.
- Duplicate check ran; if a match existed, the user was asked and the chosen action (cross-link/merge/move) was applied.
- Note re-read after writing to confirm the change landed.
