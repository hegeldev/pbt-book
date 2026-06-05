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

import re
import shutil
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
    text = re.sub(r"^(FAIL\tlru-example(?:/\S+)?)\t\d+\.\d+s", r"\1", text, flags=re.M)
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


# (output-name, language, subdir, command, extractor). Each language has two
# iterations of the test: the original (capacity >= 0) and a second that only
# draws non-zero capacities (the "-nonzero" outputs). Every iteration-1 command
# is scoped so it doesn't also pick up the iteration-2 test that now sits beside
# it (a separate test crate / executable / file / package per language).
EXAMPLES = [
    ("rust", "rust", "rust",
     ["cargo", "test", "--test", "lru", "--color", "never"], extract_rust),
    ("rust-nonzero", "rust", "rust",
     ["cargo", "test", "--test", "lru_nonzero", "--color", "never"], extract_rust),
    ("go", "go", "go", ["go", "test", "."], extract_go),
    ("go-nonzero", "go", "go", ["go", "test", "./nonzero/"], extract_go),
    ("cpp", "cpp", "cpp", ["./build/lru_test", "--gtest_color=no"], extract_cpp),
    ("cpp-nonzero", "cpp", "cpp",
     ["./build/lru_nonzero_test", "--gtest_color=no"], extract_cpp),
    ("typescript", "typescript", "typescript",
     ["npm", "test", "--silent", "--", "test/lru.test.ts"], extract_typescript),
    ("typescript-nonzero", "typescript", "typescript",
     ["npm", "test", "--silent", "--", "test/lru_nonzero.test.ts"], extract_typescript),
]


# Some of these tests are genuinely flaky: the naive "capacity >= 1" property is
# true of *almost* every randomly generated example (you need more distinct keys
# than the capacity, and most random capacities are large), so a given run may
# not find the bug. That flakiness is itself something the book talks about; here
# we just retry until we get a failure to capture.
MAX_TRIES = 12


def run_cmd(cwd: Path, cmd: list[str]) -> subprocess.CompletedProcess:
    # Clear Hegel's saved-example database so each attempt is an independent
    # from-scratch search rather than a replay of a locally-saved example. (We
    # keep the rest of .hegel — the downloaded server and unicode data — to avoid
    # re-downloading it each run.) Redirect stderr into stdout so the two streams
    # stay interleaved in the order a terminal would show them.
    shutil.rmtree(cwd / ".hegel" / "examples", ignore_errors=True)
    return subprocess.run(
        cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    )


def run_one(name: str, lang: str, subdir: str, cmd: list[str], extract) -> bool:
    cwd = HERE / subdir
    print(f"== {name}: {' '.join(cmd)} (in {cwd.relative_to(REPO)})")

    # The cache is broken, so a run that finds the bug *fails* (non-zero exit).
    # Retry until we get one, since a passing run just means search got unlucky.
    for attempt in range(1, MAX_TRIES + 1):
        proc = run_cmd(cwd, cmd)
        if proc.returncode != 0:
            break
    combined = proc.stdout
    (OUT / f"{name}.raw.txt").write_text(combined)

    trimmed = "\n".join(extract(combined))
    trimmed = re.sub(r"\n{3,}", "\n\n", trimmed).rstrip() + "\n"
    for pat, repl in GLOBAL_SUBS:
        trimmed = re.sub(pat, repl, trimmed)
    (OUT / f"{name}.txt").write_text(trimmed)

    ok = proc.returncode != 0 and trimmed.strip() != ""
    tries = f" (after {attempt} tries)" if attempt > 1 else ""
    note = "" if ok else f"  [!] no failure in {MAX_TRIES} tries"
    print(f"   exit={proc.returncode}{tries}, {len(trimmed.splitlines())} display"
          f" lines -> expected-output/{name}.txt{note}")
    return ok


def main() -> int:
    OUT.mkdir(exist_ok=True)
    only = set(sys.argv[1:])
    results = []
    for name, lang, subdir, cmd, extract in EXAMPLES:
        # `just examples rust` runs both rust iterations; `rust-nonzero` runs one.
        if only and name not in only and lang not in only:
            continue
        results.append(run_one(name, lang, subdir, cmd, extract))
    return 0 if all(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
