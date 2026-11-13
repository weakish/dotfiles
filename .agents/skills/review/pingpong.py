#!/usr/bin/env python3
"""Ping-pong bare-`t` reviews between two headless agents, without Herdr.

Run from the repo to review:  python3 <skill-dir>/pingpong.py

Config lives in pair.json next to this script (copy pair.example.json) —
two agent argv lists whose final argument is the `t` prompt, plus
max_passes and timeout_seconds. The real pair.json is gitignored.

Alternates agent A/B, starting with A, for up to max_passes passes.
Each pass runs with REVIEW_T_HEADLESS=1 so it ends its turn after the
bare-`t` flow (report, fix, amend) instead of attempting a Herdr handoff.
The driver stops early when a pass output reports no tree findings, and
exits nonzero if an agent fails, times out, output cannot be drained after
process-group cleanup, or the pass limit is reached without a clean report.
Prints the hash chain from the reviewed tip to the final tip.
"""

from __future__ import annotations

import json
import os
import re
import signal
import subprocess
import sys
import threading
from pathlib import Path
from typing import NamedTuple, NoReturn

SCRIPT_DIR = Path(__file__).resolve().parent
CONFIG_PATH = SCRIPT_DIR / "pair.json"
EXAMPLE_PATH = SCRIPT_DIR / "pair.example.json"
# Contract with SKILL.md: clean bare-`t` passes print the literal `No tree
# findings` (see "Report, then fix"); keep both in sync.
NO_TREE_FINDINGS_RE = re.compile(r"(?m)^No tree findings\.$")


class AgentPair(NamedTuple):
    """Configured agent pair plus its run limits."""

    agents: list[list[str]]
    max_passes: int
    timeout_seconds: int


def fail(message: str) -> NoReturn:
    sys.exit(f"pingpong: {message}")


def load_agent_pair(config_path: Path) -> AgentPair:
    if not config_path.exists():
        fail(
            f"pair.json not found at {config_path}\n"
            f"copy {EXAMPLE_PATH.name} to pair.json and edit the agents (see the "
            "Headless ping-pong section of SKILL.md)"
        )
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        fail(f"pair.json is not valid JSON: {error}")
    if not isinstance(config, dict):
        fail("pair.json must contain a JSON object")
    agents = config.get("agents")
    if (
        not isinstance(agents, list)
        or len(agents) != 2
        or not all(
            isinstance(argv, list)
            and argv
            and all(isinstance(part, str) and part for part in argv)
            for argv in agents
        )
    ):
        fail("pair.json: 'agents' must be a list of two non-empty argv lists")
    if any(argv[-1] != "t" for argv in agents):
        fail("pair.json: each agent argv must end with the bare 't' prompt")
    max_passes = config.get("max_passes", 6)
    timeout_seconds = config.get("timeout_seconds", 3600)
    if (
        not isinstance(max_passes, int)
        or isinstance(max_passes, bool)
        or max_passes < 1
    ):
        fail("pair.json: 'max_passes' must be a positive integer")
    if (
        not isinstance(timeout_seconds, int)
        or isinstance(timeout_seconds, bool)
        or timeout_seconds < 1
    ):
        fail("pair.json: 'timeout_seconds' must be a positive integer")
    return AgentPair([list(argv) for argv in agents], max_passes, timeout_seconds)


def git_head_sha() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], capture_output=True, text=True
    )
    if result.returncode != 0:
        fail(
            "git rev-parse HEAD failed (run from inside a git repo): "
            f"{result.stderr.strip()}"
        )
    return result.stdout.strip()


def run_agent_pass(
    argv: list[str], pass_number: int, timeout_seconds: int
) -> tuple[int, str]:
    env = {**os.environ, "REVIEW_T_HEADLESS": "1"}
    try:
        process = subprocess.Popen(
            argv,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            env=env,
            bufsize=1,
            start_new_session=True,
        )
    except FileNotFoundError:
        fail(f"pass {pass_number}: agent command not found: {argv[0]}")
    assert process.stdout is not None
    collected: list[str] = []

    def echo_and_collect() -> None:
        assert process.stdout is not None
        for line in process.stdout:
            collected.append(line)
            sys.stdout.write(line)
            sys.stdout.flush()

    reader = threading.Thread(target=echo_and_collect, daemon=True)
    reader.start()
    try:
        returncode = process.wait(timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.wait()
        reader.join(timeout=1)
        fail(f"pass {pass_number} ({argv[0]}) timed out after {timeout_seconds}s")
    # The agent may exit while an orphaned grandchild keeps its end of the
    # pipe open; bound the drain and tear the group down like the timeout
    # path does.
    reader.join(timeout=1)
    if reader.is_alive():
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        reader.join(timeout=1)
        if reader.is_alive():
            fail(
                f"pass {pass_number} ({argv[0]}) exited but stdout did not "
                "close after process-group cleanup"
            )
    return returncode, "".join(collected)


def output_reports_no_tree_findings(output: str) -> bool:
    return NO_TREE_FINDINGS_RE.search(output) is not None


def main() -> int:
    agents, max_passes, timeout_seconds = load_agent_pair(CONFIG_PATH)
    start_sha = git_head_sha()
    passes_run = 0
    clean_pass_found = False
    pass_summaries: list[str] = []
    for pass_number in range(1, max_passes + 1):
        argv = agents[(pass_number - 1) % 2]
        side = "A" if pass_number % 2 == 1 else "B"
        label = f"[{side}] {' '.join(argv)}"
        print(f"\n== pass {pass_number}/{max_passes} {label}", flush=True)
        returncode, output = run_agent_pass(argv, pass_number, timeout_seconds)
        if returncode != 0:
            fail(
                f"pass {pass_number} ({argv[0]}) exited with status {returncode}; "
                "ping-pong aborted"
            )
        passes_run += 1
        head_sha = git_head_sha()
        no_findings = output_reports_no_tree_findings(output)
        pass_summaries.append(
            f"  pass {pass_number} [{side}] {argv[0]} -> {head_sha[:7]}"
        )
        if no_findings:
            clean_pass_found = True
            pass_summaries[-1] += " (no tree findings)"
            print(
                f"\n== pass {pass_number} reported no tree findings; ping-pong stops",
                flush=True,
            )
            break
    else:
        print(
            f"\n== reached max_passes={max_passes} without a clean pass; "
            "the tip may still have findings",
            file=sys.stderr,
            flush=True,
        )
    end_sha = git_head_sha()
    print(f"\npingpong: {start_sha[:7]} -> {end_sha[:7]} in {passes_run} pass(es)")
    for summary in pass_summaries:
        print(summary)
    return 0 if clean_pass_found else 1


if __name__ == "__main__":
    sys.exit(main())
