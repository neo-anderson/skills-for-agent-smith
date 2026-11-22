#!/usr/bin/env python3
"""Personal-data sweep for a skill dir or whole skills repo.

Usage: python3 sanitize_sweep.py <dir> [--user NAME] [--token TOK ...] [--regex NAME=PATTERN ...]
Prints hits per file per category; exit 0 = clean, 1 = hits to review.
Review every hit against the SKILL.md replacement policy before patching —
grep-pattern specs, synthetic stand-in tokens, and public doc IDs are expected hits.
"""
import argparse, os, re, sys

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
            try:
                t = open(p, encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            for name, rx in checks.items():
                hits = sorted(set(m if isinstance(m, str) else m[0] for m in re.findall(rx, t, re.I)))
                if hits:
                    print(f"{os.path.relpath(p, a.dir)} [{name}]: {hits}")
                    issues += 1
            if a.token:
                h = [tok for tok in a.token if tok.lower() in t.lower()]
                if h:
                    print(f"{os.path.relpath(p, a.dir)} [harvested]: {h}")
                    issues += 1
            # publishing checklist bits
            if fn == "SKILL.md" and t.startswith("---"):
                m = re.search(r"name:\s*\S+", t)
                if m and m.group(0).split(":", 1)[1].strip() != os.path.basename(os.path.dirname(p)):
                    print(f"{os.path.relpath(p, a.dir)} [name!=folder]: {m.group(0)}")
                    issues += 1
                d = re.search(r"description:\s*\"?([^\"\n]+)", t)
                if d and len(d.group(1)) > 160:
                    print(f"{os.path.relpath(p, a.dir)} [desc>160]: {len(d.group(1))}")
                    issues += 1
    print(f"issues: {issues}")
    sys.exit(0 if issues == 0 else 1)

if __name__ == "__main__":
    main()
