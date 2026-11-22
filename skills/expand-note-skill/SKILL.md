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

0. **Confirm the target app is a skill, not a CLI.** Before routing, check the available skills list — expand-note-skill orchestrates through app-specific *skills* (`bearcli`, `apple-notes`, `obsidian`), which wrap the CLI. Do not shell out to the raw CLI directly; delegate the actual write to the skill. If none of the note-taking skills match the destination app, tell the user and ask how to proceed rather than inventing a new write path.

1. **Take a backup of the source notes in `/tmp` before any modification.** Copy the source note(s) to `/tmp/` (with a timestamped name) before expanding, merging, moving, or deleting anything. This is the diff/undo safety net — if a merge or move goes wrong you can restore the original. Re-read from the `/tmp` backup to verify or undo. Do not skip this step; it is the primary guard against irreversible data loss.

2. **Expand the shorthand.** Fill in the missing details the user implied — dates, names, context, follow-ups. Keep the original meaning; add what's plausibly intended, flag what you guessed. Output the expanded draft to the user for confirmation before writing anything.

3. **Check the target app is actually reachable before routing.** Gate on the app-specific CLI: run its version/health check (Bear: `/Applications/Bear.app/Contents/MacOS/bearcli --version`; Apple Notes: `memo` present; Obsidian: vault path resolves). A session that asks "where should this go?" while the user's chosen app is already installed wastes a round-trip — the user often has Bear/Obsidian ready and expects you to just proceed. If the CLI is missing, *then* ask whether to install/connect it. Do the health check as step 0, before step 1, and only fall back to the destination question when the check fails.

3. **Build the title.** Use the template `DATE — REFERENCE TOPICS`, where DATE is the note's date (ISO `YYYY-MM-DD`) and REFERENCE TOPICS is a comma list of the note's subjects, phrased as short human-readable topics rather than tags (e.g. `2026-01-01 — new year resolution, ramen with Andrew, create new Hermes skill`). Match the casing/style the user used in their shorthand.

4. **Discover existing tags / topics.** Before tagging, list what already exists so you reuse the right tags instead of inventing new ones:
   - Bear: `bearcli tags list --format json` (see `bearcli` skill).
   - Obsidian: `search_files(pattern="*", target="content", file_glob="*.md")` for existing topic tags.
   Match existing subtags (e.g. `#me/family/Gina/*`) over flat ones. If none fit, surface 2–3 concrete suggestions and let the user pick — don't invent tags silently.

3. **Check for duplicates / related content.** Search the destination for the same or similar content (by title keywords, topic tags, or body overlap). **Search by TITLE first** — the title is the strongest signal of a note's topic, and a body-only search misses notes that are clearly on-topic by name. List all notes whose title matches the target's subject, then read their bodies before concluding anything is related. A keyword search (`baby`, `art`) returns many false hits — a note matching one keyword is not necessarily related, so read content before deciding. Two notes can share tags (`#areas/family/babies`) and still be distinct; only reading content decides whether to merge/cross-link. **Never conclude "no related notes" from a title-less skim** — if you haven't checked titles, you haven't actually checked for related notes.

4. **Search using MULTIPLE methods.** Don't rely on one query. Run a search using the main keywords from the new note, *and* a separate search using the note's tags (from step 4). Keywords and tags surface different notes — a note can be tagged but keyword-invisible, or vice versa. Combine both result sets before concluding there's no related content.

5. **Decide cross-link vs. merge.** If a match is found, ASK the user whether to cross-link, merge, or move — then recommend the best option:
   - **Cross-link** (recommend when the notes are related but distinct): add a reference to the existing note (Bear plain-text pointer, Obsidian `[[wikilink]]`, Apple Notes a plain-text pointer). Best when both carry independent value.
   - **Merge** (recommend when one is a subset/draft of the other): fold the shorthand's content into the existing note and delete the duplicate. Best when they're the same fact stated twice.
   - **Move** (recommend when they're the same note in the wrong place): relocate rather than duplicate. Best when content is identical and only location/folder differs.
   State your recommendation and why, then act on the user's choice.

6. **Get confirmation before merging or rephrasing.** When you merge notes (or parts of notes), preserve the original details and all links — do not drop facts, references, cross-links, or wikilinks in the process. Before moving content, show the user exactly how you plan to format/summarize/rephrase it, and get explicit confirmation. Never silently compress, paraphrase, or drop detail during a merge — the user decides what stays verbatim vs. what gets condensed.

7. **Run a final refactor.** If information was moved into the new note, reorganize the note afterward so it reads well — reorder sections, fix headings, tighten flow, and re-verify all cross-links still resolve. A merge that leaves the note structurally messy defeats the purpose; tidy it up as the last step.

8. **When cross-linking Bear notes, move the *content* across, don't just point.** If the user asks to link note X to note Y, the useful result is: enrich Y with the genuinely new information from X, then strip the duplicated items from X and leave X a pointer line ("See also: Y (id)") — not a dead-end pointer to an empty note. Verify each note's content after the move by re-`cat`-ing it. See `references/cross-note-links.md`.

9. **Write the note.** Delegate to the chosen app's skill (`bearcli` / `apple-notes` / `obsidian`) — do not hand-roll the write. For multi-block edits, write to `/tmp/` first, then apply (see that skill's procedure). Re-read the note afterward and confirm the change landed before reporting success.

10. **Clean up.** Ask before deleting any `/tmp/` working files — they're the diff/undo backup.

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
