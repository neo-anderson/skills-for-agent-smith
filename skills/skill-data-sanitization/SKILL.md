---
name: skill-data-sanitization
description: Scrub personal data and client-specific assumptions from agent skills before sharing.
version: 1.1.0
author: neo-anderson
license: MIT
metadata:
  openclaw:
    emoji: "🧼"
    requires:
      bins: [python3]
    homepage: https://github.com/neo-anderson/skills-for-agent-smith
---

# Skill Data Sanitization

Skills authored while probing a LIVE system/user data silently absorb personal artifacts (real IDs, titles, dataset sizes). Audit every such skill before declaring it done — the "examples" in code blocks are the usual leak vector.

## When to Use

- Immediately after creating or substantially updating any skill whose knowledge came from touching real user data (app scripting probes, DB reads, file scans, live API calls).
- Before sharing/exporting/syncing a skill outside this machine.
- Not needed for skills written purely from public docs (still safe to run — it's cheap).

## Procedure

1. **Harvest probe tokens.** While probing, collect every literal identifier seen in outputs: UUIDs, short IDs, hashes, tokens, exact counts, note/to-do/file titles. You will grep for these explicitly.
2. **Regex sweep of ALL skill files** (SKILL.md + references/ + templates/ + scripts/) via one small Python script (stdlib `re`/`os`; any code-execution tool works) checking at least:
   - `/Users/|/home/` paths and the username
   - the harvested real identifiers, verbatim
   - generic high-entropy shapes: `\b[A-Za-z0-9]{20,}\b`, hex/base64 runs (keep `/` and `-` OUT of base64 char classes — slash-joined prose like `sharing/exporting` otherwise false-positives)
   - verbatim user-data strings (titles/names from probe output)
   - exact large counts of user data (item counts, file numbers)
3. **Replace per policy:**
   - Real ID → synthetic token of IDENTICAL shape/length/alphabet (keeps the example instructive)
   - Exact personal stat → approximate (`1,234` → `~1,200`)
   - User-data strings in examples → the source doc's own examples, or generic ones
4. **Re-scan after patching**; clean = zero hits on harvested tokens and paths.
5. **Agent-agnostic pass** (do whenever the skill may run outside this client): grep the skill text for client-specific assumptions and neutralize them —
   - tool-name references (`execute_code`, `skill_manage`, `terminal(...)`, `browser_exec`, `sessions_spawn`, …) → reword to capability language ("any code-execution tool", "the skill-edit tool")
   - client paths and hub URLs (`~/.hermes/`, `~/.openclaw/`, registry links) → describe generically ("the client's skills directory")
   - tool-coupled workflows (auto-patching, memory/todo integration) → state the intent, not the tool
   - unknown frontmatter namespaces (`metadata.hermes` in OpenClaw etc.) are harmlessly ignored — fine locally; drop or relocate under the target's namespace (`metadata.openclaw`) when publishing
   - publishing checklist: `name` matches the parent folder, description ≤160 chars, required binaries/OS declared in the target schema (e.g. `metadata.openclaw.requires.bins`)
6. Report to the user what was scrubbed and what was neutralized (transparency builds trust in the skill).

## Personal vs. portable (do NOT scrub the second)

- **Portable/machine-convention:** OS/app names (Things3's process name is `Things3` everywhere), `/Applications/X.app` standard locations, permission-prompt flows, `~`-relative paths.
- **Personal:** usernames/home dirs, harvested identifiers, verbatim user content, exact dataset sizes, hostnames/ports/credentials, machine serials.
- **Frontmatter `author:`** commonly contains the user's name — deliberate attribution, not an accident; flag it when the skill is meant to be shared, leave it otherwise.

## Pitfalls

- Probe IDs slip in as "example output" or inline comments — grep harvested literals, don't eyeball.
- The long-token regex false-positives on package names/API constants; review hits rather than auto-replacing.
- Exact performance stats ("0.85s on MY 6k-item list") encode data volume; round to order of magnitude and keep the ratio lesson.
- Audit supporting files too: references copied from user data (exported notes, logs) are the worst offenders — they can contain whole documents.

## Verification

The sweep script prints `none` for every personal category on the final scan, and the harvested-token list is empty. For cross-client use, also confirm zero un-neutralized client tool names/paths and that `name` matches the folder. Only then say the skill is share-ready.
