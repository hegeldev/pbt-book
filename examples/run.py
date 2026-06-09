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


def extract_go_pass(text: str) -> list[str]:
    # A passing `go test` just prints an `ok <package> <time>` line; keep it (with
    # the timing stripped) so the book can show the test going green.
    out = [ln for ln in text.splitlines() if ln.startswith("ok") and "lru-example" in ln]
    return [re.sub(r"\t[\d.]+s\s*$", "", ln) for ln in out]


def extract_go_stateful(text: str) -> list[str]:
    # Like extract_go, but the stateful runner also logs two hegel-internal
    # draws per step (the number of steps to take, and which rule to run). Those
    # are implementation detail rather than part of the user's model, so we drop
    # them; everything else (the drawn capacity, the "Step N" labels, and the
    # failing invariant) is kept, prefixes and all, to match the other go output.
    lines = text.splitlines()
    out = slice_lines(lines, "--- FAIL:", re.compile(r"^FAIL\tlru-example"))
    drop = [re.compile(r": nSteps = "), re.compile(r": idx = ")]
    out = [ln for ln in out if not any(p.search(ln) for p in drop)]
    text = "\n".join(out)
    text = re.sub(r" \(\d+\.\d+s\)", "", text)
    text = re.sub(r"^(FAIL\tlru-example(?:/\S+)?)\t\d+\.\d+s", r"\1", text, flags=re.M)
    return text.splitlines()


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


# Verbose iteration. This runs the same "capacity >= 1" property as the
# `-nonzero` examples but with verbosity turned up and a fixed seed, so the run
# prints every generated test case and every shrink step. The full trace is
# hundreds of lines, so unlike the examples above there is *no* automatic
# extractor: we only write the full ``<name>.raw.txt`` here, and the trimmed
# ``<name>.txt`` that the book includes is curated *by hand* from it (keeping a
# few initial cases, the first failure, and a sample of the shrinking). That
# means re-running this script will NOT clobber the hand-edited verbose .txt.
#
# Only Rust appears here. At the library versions pinned in this directory the
# other clients can't produce a per-case verbose trace, so the book marks their
# tabs with a TODO:
#   * Go (v0.5.3) hardcodes the server to `--verbosity normal` and exposes no
#     verbosity setting at all.
#   * C++ (hegel-cpp 0.3.9) and TypeScript (@hegeldev/hegel) only print the
#     *final* counterexample's draws (gated on the last-run flag), so verbose
#     adds nothing that shows the generate/shrink loop.
#
# The test pins a fixed seed so the trace is reproducible; the book shows the
# test *without* it (inline, not via {{#include}}), as the seed is only a capture
# detail. The seed must be one that actually *finds* the bug (the property is only
# almost-always falsifiable) — if you change it, re-check that the run still fails.
VERBOSE_EXAMPLES = [
    ("rust-verbose", "rust", "rust",
     ["cargo", "test", "--test", "lru_verbose", "--color", "never", "--",
      "--nocapture"]),
]


# Replay iteration. Hegel saves the failing example it finds into a `.hegel/`
# database and, on the next run, *replays* it instead of searching from scratch.
# To capture that we run the (verbose) test twice: once to populate the database
# with a normal from-scratch search, then again WITHOUT clearing it — the second
# run jumps straight to the saved counterexample. That replay trace is short, so
# unlike the verbose search it uses the normal extractor (no hand trimming).
#
# Rust only, for the same reason as the verbose iteration above.
REPLAY_EXAMPLES = [
    ("rust-verbose-replay", "rust", "rust",
     ["cargo", "test", "--test", "lru_verbose", "--color", "never", "--",
      "--nocapture"], extract_rust),
]


# Stateful (model-based) iteration. These run a state machine that drives the
# real cache and a correct reference model side by side, checked by a get rule
# and a same-size invariant (see src/intro/stateful.md). They fail for the same
# underlying reason as the others — the cache never evicts — but via the model.
#
# Only Rust and Go appear here: hegel-cpp (0.3.9) and hegel-typescript do not yet
# support stateful testing (it is planned), so the book marks their tabs with a
# TODO. The output is short, so both use the normal extractors (no hand trim).
STATEFUL_EXAMPLES = [
    ("rust-stateful", "rust", "rust",
     ["cargo", "test", "--test", "stateful", "--color", "never", "--",
      "--nocapture"], extract_rust),
    ("go-stateful", "go", "go", ["go", "test", "./stateful/"], extract_go_stateful),
    # Second iteration: the same state machine against CappedCache, which stops
    # accepting new keys when full. Its size stays within capacity (so the
    # same-size invariant passes) but it keeps the wrong entries, so the get rule
    # is what catches it.
    ("rust-stateful-capped", "rust", "rust",
     ["cargo", "test", "--test", "stateful_capped", "--color", "never", "--",
      "--nocapture"], extract_rust),
    ("go-stateful-capped", "go", "go",
     ["go", "test", "./stateful_capped/"], extract_go_stateful),
]


# Passing iteration: the same state machine against a *correct* LRU cache
# (LRUCache). Unlike everything else here, these runs are supposed to *succeed* —
# the model and the cache agree under every sequence — so they go through
# run_passing (which expects exit 0) rather than run_one (which retries until it
# sees a failure). Rust and Go only, as with the other stateful examples.
PASSING_EXAMPLES = [
    ("rust-stateful-real", "rust", "rust",
     ["cargo", "test", "--test", "stateful_real", "--color", "never"], extract_rust),
    ("go-stateful-real", "go", "go",
     ["go", "test", "./stateful_real/"], extract_go_pass),
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

    # Verbose examples (extract is None) have no automatic extractor: we capture
    # the full trace as provenance and the book's <name>.txt is hand-curated, so
    # we deliberately do not write/overwrite it here.
    if extract is None:
        ok = proc.returncode != 0
        tries = f" (after {attempt} tries)" if attempt > 1 else ""
        note = "" if ok else f"  [!] no failure in {MAX_TRIES} tries"
        print(f"   exit={proc.returncode}{tries}, {len(combined.splitlines())} raw"
              f" lines -> expected-output/{name}.raw.txt (hand-trim into"
              f" {name}.txt){note}")
        return ok

    trimmed = normalise(extract(combined))
    (OUT / f"{name}.txt").write_text(trimmed)

    ok = proc.returncode != 0 and trimmed.strip() != ""
    tries = f" (after {attempt} tries)" if attempt > 1 else ""
    note = "" if ok else f"  [!] no failure in {MAX_TRIES} tries"
    print(f"   exit={proc.returncode}{tries}, {len(trimmed.splitlines())} display"
          f" lines -> expected-output/{name}.txt{note}")
    return ok


def normalise(extracted: list[str]) -> str:
    """Collapse blank runs and apply the path/home substitutions shared by all
    trimmed outputs."""
    trimmed = "\n".join(extracted)
    trimmed = re.sub(r"\n{3,}", "\n\n", trimmed).rstrip() + "\n"
    for pat, repl in GLOBAL_SUBS:
        trimmed = re.sub(pat, repl, trimmed)
    return trimmed


def run_replay(name: str, lang: str, subdir: str, cmd: list[str], extract) -> bool:
    cwd = HERE / subdir
    print(f"== {name}: {' '.join(cmd)} (run twice, replaying from the database)"
          f" (in {cwd.relative_to(REPO)})")

    # First run: clear the database and search from scratch, so a failing example
    # gets saved. Retry until it actually fails (and therefore saves something).
    for attempt in range(1, MAX_TRIES + 1):
        first = run_cmd(cwd, cmd)
        if first.returncode != 0:
            break

    # Second run: do NOT clear the database, so Hegel replays the saved example
    # instead of searching again. This is the run we capture.
    proc = subprocess.run(
        cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    )
    combined = proc.stdout
    (OUT / f"{name}.raw.txt").write_text(combined)

    trimmed = normalise(extract(combined))
    (OUT / f"{name}.txt").write_text(trimmed)

    ok = first.returncode != 0 and proc.returncode != 0 and trimmed.strip() != ""
    note = "" if ok else "  [!] populate or replay run did not fail"
    print(f"   populate exit={first.returncode}, replay exit={proc.returncode},"
          f" {len(trimmed.splitlines())} display lines ->"
          f" expected-output/{name}.txt{note}")
    return ok


def run_passing(name: str, lang: str, subdir: str, cmd: list[str], extract) -> bool:
    cwd = HERE / subdir
    print(f"== {name}: {' '.join(cmd)} (expecting success) (in {cwd.relative_to(REPO)})")

    # A correct implementation passes, so unlike run_one we expect exit 0 and do
    # not retry. We still clear the database first so the run is independent.
    proc = run_cmd(cwd, cmd)
    combined = proc.stdout
    (OUT / f"{name}.raw.txt").write_text(combined)

    trimmed = normalise(extract(combined))
    (OUT / f"{name}.txt").write_text(trimmed)

    ok = proc.returncode == 0 and trimmed.strip() != ""
    note = "" if ok else f"  [!] expected success, got exit {proc.returncode} (or no output)"
    print(f"   exit={proc.returncode}, {len(trimmed.splitlines())} display lines ->"
          f" expected-output/{name}.txt{note}")
    return ok


def main() -> int:
    OUT.mkdir(exist_ok=True)
    only = set(sys.argv[1:])
    results = []
    all_examples = (
        EXAMPLES
        + [(n, l, s, c, None) for (n, l, s, c) in VERBOSE_EXAMPLES]
        + STATEFUL_EXAMPLES
    )
    for name, lang, subdir, cmd, extract in all_examples:
        # `just examples rust` runs every rust iteration; `rust-nonzero` runs one.
        if only and name not in only and lang not in only:
            continue
        results.append(run_one(name, lang, subdir, cmd, extract))
    for name, lang, subdir, cmd, extract in REPLAY_EXAMPLES:
        if only and name not in only and lang not in only:
            continue
        results.append(run_replay(name, lang, subdir, cmd, extract))
    for name, lang, subdir, cmd, extract in PASSING_EXAMPLES:
        if only and name not in only and lang not in only:
            continue
        results.append(run_passing(name, lang, subdir, cmd, extract))
    return 0 if all(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
