#!/usr/bin/env python3
"""Personal-data sweep for a skill dir or whole skills repo.

Usage: python3 sanitize_sweep.py <dir> [--user NAME] [--token TOK ...] [--regex NAME=PATTERN ...]
Prints hits per file per category; exit 0 = clean, 1 = hits to review.

This script is a REPORT, not a fixer: it flags hits and exits non-zero. The
calling skill presents each hit with a recommendation and waits for the user's
decision before patching anything. See the skill body for the per-category
recommendation guide.
"""
import argparse, os, re, sys

# Recommendation applied to each flagged category. Recommendations are guidance
# for the human decision, not auto-applied edits.
RECOMMENDATIONS = {
    "home-paths": "replace with a portable form (/Users/<you>/... -> ~/... or drop the path)",
    "high-entropy": "likely a real ID/token -> synthetic stand-in of identical shape, or delete the example",
    "hex-run": "likely a real ID/token -> synthetic stand-in of identical shape, or delete the example",
    "exact-large-count": "often a false positive (a 4-digit year like 2026-01-01); if real data, approximate, else ask whether to keep",
    "harvested": "real identifier present -> synthetic stand-in or remove",
    "name!=folder": "structural fix: rename the folder (or the frontmatter name) so they match",
    "desc>160": "trim the frontmatter description to <=160 chars",
    "username": "replace the username with a synthetic stand-in or drop it",
}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dir")
    ap.add_argument("--user", default="", help="username to scan for")
    ap.add_argument("--token", action="append", default=[], help="harvested literal from probe outputs (repeatable)")
    ap.add_argument("--regex", action="append", default=[], help="extra check NAME=PATTERN (repeatable)")
    a = ap.parse_args()

    checks = {
        "home-paths": r"/Users/|/home/",
        # high-entropy: no / or - in the class, else slash-joined prose false-positives
        "high-entropy": r"\b[A-Za-z0-9]{20,}\b",
        "hex-run": r"\b[0-9a-f]{16,}\b",
        "exact-large-count": r"\b\d{4,}\b",
    }
    if a.user:
        checks["username"] = r"(?<![a-zA-Z])%s(?![a-zA-Z])" % re.escape(a.user)
    for spec in a.regex:
        name, _, pat = spec.partition("=")
        checks[name] = pat

    issues = 0
    for root, dirs, fs in os.walk(a.dir):
        dirs[:] = [d for d in dirs if d != ".git"]
        for fn in fs:
            p = os.path.join(root, fn)
            rel = os.path.relpath(p, a.dir)
            try:
                t = open(p, encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            file_hits = False
            for name, rx in checks.items():
                hits = sorted(set(m if isinstance(m, str) else m[0] for m in re.findall(rx, t, re.I)))
                if hits:
                    rec = RECOMMENDATIONS.get(name, "review and decide")
                    for h in hits:
                        print(f"{rel} — {name}: {h}  ->  recommendation: {rec}")
                    file_hits = True
                    issues += 1
            if a.token:
                h = [tok for tok in a.token if tok.lower() in t.lower()]
                if h:
                    rec = RECOMMENDATIONS.get("harvested", "review and decide")
                    for tok in h:
                        print(f"{rel} — harvested: {tok}  ->  recommendation: {rec}")
                    file_hits = True
                    issues += 1
            # publishing checklist bits
            if fn == "SKILL.md" and t.startswith("---"):
                m = re.search(r"name:\s*\S+", t)
                if m and m.group(0).split(":", 1)[1].strip() != os.path.basename(os.path.dirname(p)):
                    print(f"{rel} — name!=folder: {m.group(0)}  ->  recommendation: {RECOMMENDATIONS['name!=folder']}")
                    file_hits = True
                    issues += 1
                d = re.search(r'description:\s*\"?([^\"\n]+)', t)
                if d and len(d.group(1)) > 160:
                    print(f"{rel} — desc>160: {len(d.group(1))} chars  ->  recommendation: {RECOMMENDATIONS['desc>160']}")
                    file_hits = True
                    issues += 1
            if file_hits:
                print()  # blank line between files for readability
    print(f"issues: {issues}")
    sys.exit(0 if issues == 0 else 1)

if __name__ == "__main__":
    main()