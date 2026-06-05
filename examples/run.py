#!/usr/bin/env python3
"""Run each language's LRU-cache example and capture Hegel's failure output.

Every example in this directory deliberately tests a broken LRU cache (one that
never evicts), so every run *fails*. We run each, capture the combined
stdout/stderr, and write two files per language into ``expected-output/``:

* ``<lang>.raw.txt`` — the full, unedited combined output (for provenance).
* ``<lang>.txt``     — a trimmed, path/timing-normalised slice that the book
                       includes via ``{{#include}}``.

The trimming below is intentionally conservative: it removes only volatile noise
(absolute paths, elapsed times, thread ids) and framing that distracts from the
result Hegel reports. Re-run with ``just examples`` (or ``python3 run.py``) to
regenerate after changing an example. These are developer-preview libraries, so
exact wording may drift between versions.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent.resolve()
REPO = HERE.parent
OUT = HERE / "expected-output"

HOME = str(Path.home())

# Substitutions applied to every language's trimmed output.
GLOBAL_SUBS: list[tuple[str, str]] = [
    (re.escape(str(REPO) + "/"), ""),
    (re.escape(HOME), "~"),
]


def slice_lines(lines: list[str], start: str, end: re.Pattern[str]) -> list[str]:
    """Lines from the first containing ``start`` to the first matching ``end``."""
    out: list[str] = []
    started = False
    for line in lines:
        if not started:
            if start in line:
                started = True
            else:
                continue
        out.append(line)
        if end.search(line):
            break
    return out


def between(lines: list[str], start: str, end: re.Pattern[str]) -> list[str]:
    """Like ``slice_lines`` but matched on a substring start and regex end."""
    return slice_lines(lines, start, end)


# Per-language configuration. ``extract`` takes the full combined output and
# returns the trimmed lines to display.
def extract_rust(text: str) -> list[str]:
    lines = text.splitlines()
    out = slice_lines(lines, "running 1 test", re.compile(r"^test result:"))
    drop = [
        re.compile(r"run_lifecycle\.rs"),
        re.compile(r"^Property test failed:"),
        re.compile(r"^note: run with"),
    ]
    out = [ln for ln in out if not any(p.search(ln) for p in drop)]
    text = "\n".join(out)
    text = re.sub(r"^(thread '.*?') \(\d+\) (panicked)", r"\1 \2", text, flags=re.M)
    text = re.sub(r";? *finished in \d+\.\d+s", "", text)
    return text.splitlines()


def extract_go(text: str) -> list[str]:
    lines = text.splitlines()
    out = slice_lines(lines, "--- FAIL:", re.compile(r"^FAIL\tlru-example"))
    text = "\n".join(out)
    text = re.sub(r" \(\d+\.\d+s\)", "", text)
    text = re.sub(r"^(FAIL\tlru-example)\t\d+\.\d+s", r"\1", text, flags=re.M)
    return text.splitlines()


def extract_cpp(text: str) -> list[str]:
    lines = text.splitlines()
    out = slice_lines(lines, "[==========] Running", re.compile(r"^ ?1 FAILED TEST"))
    drop = [
        re.compile(r"^Running main\(\) from"),
        re.compile(r"Reader loop exiting"),  # benign hegel-core teardown log
    ]
    out = [ln for ln in out if not any(p.search(ln) for p in drop)]
    text = "\n".join(out)
    text = re.sub(r" \(\d+ ms(?: total)?\)", "", text)
    return text.splitlines()


def extract_typescript(text: str) -> list[str]:
    lines = text.splitlines()
    return between(
        lines, "var draw_1", re.compile(r"^expected .* to be less than or equal to")
    )


EXAMPLES = [
    ("rust", "rust", ["cargo", "test", "--test", "lru", "--color", "never"], extract_rust),
    ("go", "go", ["go", "test", "./..."], extract_go),
    ("cpp", "cpp", ["./build/lru_test", "--gtest_color=no"], extract_cpp),
    ("typescript", "typescript", ["npm", "test", "--silent"], extract_typescript),
]


def run_one(name: str, subdir: str, cmd: list[str], extract) -> bool:
    cwd = HERE / subdir
    print(f"== {name}: {' '.join(cmd)} (in {cwd.relative_to(REPO)})")
    # Redirect stderr into stdout so the two streams stay interleaved in the
    # order a terminal would show them (Hegel prints draws and framing across
    # both, and the ordering matters).
    proc = subprocess.run(
        cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    )
    combined = proc.stdout
    (OUT / f"{name}.raw.txt").write_text(combined)

    trimmed = "\n".join(extract(combined))
    trimmed = re.sub(r"\n{3,}", "\n\n", trimmed).rstrip() + "\n"
    for pat, repl in GLOBAL_SUBS:
        trimmed = re.sub(pat, repl, trimmed)
    (OUT / f"{name}.txt").write_text(trimmed)

    # Every example is supposed to fail (the cache is broken).
    ok = proc.returncode != 0 and trimmed.strip() != ""
    print(f"   exit={proc.returncode}, {len(trimmed.splitlines())} display lines"
          f" -> expected-output/{name}.txt{'' if ok else '  [!] unexpected'}")
    return ok


def main() -> int:
    OUT.mkdir(exist_ok=True)
    only = set(sys.argv[1:])
    results = []
    for name, subdir, cmd, extract in EXAMPLES:
        if only and name not in only:
            continue
        results.append(run_one(name, subdir, cmd, extract))
    return 0 if all(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
