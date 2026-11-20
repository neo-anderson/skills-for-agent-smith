# skills-for-agent-smith

Skills for Agent Smith & friends — from Mr Anderson. OS, app and utility programs for Hermes, OpenClaw & other SKILL.md clients.

| Skill | What it does | Requires |
|---|---|---|
| [`things3`](skills/things3) | Drive Things 3 on macOS via AppleScript: to-dos, projects, areas, tags | macOS + Things3 |
| [`skill-data-sanitization`](skills/skill-data-sanitization) | Audit any agent skill for personal-data leakage and client-specific assumptions before sharing | python3 |
| [`bear-notes`](skills/bear-notes) | Read, search, create, and edit Bear notes via the bearcli bundled in Bear 2.8+ | macOS + Bear 2.8+ |

## Install — Hermes users

Hermes treats this repo natively as a **tap** (custom GitHub skill source). Add it once, then search and selectively install/update individual skills — no cloning:

```bash
hermes skills tap add neo-anderson/skills-for-agent-smith
hermes skills search <query>                                  # taps are searched like registries
hermes skills install neo-anderson/skills-for-agent-smith/things3
hermes skills check            # see updates for hub/tap-installed skills
hermes skills update things3
```

Remove the source anytime: `hermes skills tap remove neo-anderson/skills-for-agent-smith`.

## Install — OpenClaw users

**Whole collection (recommended):** clone once and point OpenClaw at it — all present *and future* skills auto-load:

```bash
git clone https://github.com/neo-anderson/skills-for-agent-smith ~/skills-for-agent-smith
```

```json5
// ~/.openclaw/openclaw.json
{
  skills: {
    load: {
      extraDirs: ["~/skills-for-agent-smith/skills"]
    }
  }
}
```

Extra dirs load at lowest precedence, so your own workspace skills always override them.

**One skill at a time:** copy its folder into a skills root (workspace `skills/` for one agent, `~/.openclaw/skills/` for all agents):

```bash
cp -r ~/skills-for-agent-smith/skills/things3 ~/.openclaw/skills/
```

> Note: `openclaw skills install git:<owner>/<repo>` expects a single-skill repo (`SKILL.md` at the root) and there is no per-path git spec (verified on OpenClaw 2026.9.3) — that's why the extra-dirs/copy flows above are documented instead. Re-copy to update git-sourced skills; `openclaw skills update` only tracks ClawHub installs.

## Repo layout

```
skills/<skill-name>/SKILL.md    # the tap path Hermes scans by default
```

Conventions: `name` frontmatter matches the folder; every skill here passes its own data-sanitization audit (no personal paths, harvested IDs, or tool-specific coupling in executable instructions; client metadata stays namespaced — `metadata.hermes` and `metadata.openclaw` coexist and are ignored by the other client).

## License

MIT
