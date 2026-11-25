#!/usr/bin/env python3
"""Swiss-cheese ledger for a break-it pass.

The ledger is a JSON file of candidate breakages. Each candidate lists the
holes (conditions) that must line up for harm, the harm itself, and, once
tested, what happened. This script applies one fixed rule to every candidate,
so two agents triaging the same ledger put each candidate in the same bucket.

    cheese.py triage ledger.json            # Markdown triage table, sorted
    cheese.py results ledger.json           # Markdown results table for the report
    cheese.py draft ledger.json C3 > c3.draft   # Swiss-cheese diagram for one candidate
    cheese.py check ledger.json             # permissive work-in-progress check
    cheese.py finish ledger.json            # verify final receipts and list coverage gaps

See references/example-ledger.json for a worked example.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

# How often a hole is open for the person who would hit it, judged *given the
# holes before it in the list* (conditional, the way the slices stack).
FREQ = {
    "always": 0,      # true in every run of the feature; not a defense at all
    "routine": 1,     # most users hit it in a normal week
    "occasional": 2,  # some users, or every deploy/restart/second tab
    "rare": 3,        # needs an unusual but legitimate setup or timing
    "contrived": 5,   # needs hand-edited state, an attacker the threat model excludes, or several rare things at once
}

# What happens when every hole lines up. Order matters: higher is worse.
HARM = {
    "cosmetic": 0,     # wrong text, log noise; nobody acts on it wrongly
    "recoverable": 1,  # visible failure, a retry or reload fixes it
    "stuck": 2,        # visible failure the user can't get past without help
    "wrong": 3,        # silently wrong result, grade, number or saved state
    "exposure": 4,     # data or a privileged surface reachable by someone who shouldn't reach it
    "loss": 4,         # user data destroyed or a write silently dropped
}

# Largest "distance to harm" (sum of hole scores) that still earns a test, per harm.
TEST_WITHIN = {"cosmetic": 1, "recoverable": 2, "stuck": 3, "wrong": 5, "exposure": 6, "loss": 6}
# Beyond the test line, up to this much further, the candidate is noted as accepted risk.
NOTE_MARGIN = 3

STATUSES = {"untested", "held", "broke", "inconclusive", "skipped"}
BASES = {"same", "differs", "n/a", ""}


def distance(c: dict) -> int:
    return sum(FREQ[h["freq"]] for h in c["holes"])


def layers(c: dict) -> int:
    """Holes that are real defenses: an 'always' hole is no slice at all."""
    return sum(1 for h in c["holes"] if h["freq"] != "always")


def bucket(c: dict) -> tuple[str, str]:
    """Return (bucket, reason). Buckets: test, note, skip."""
    if c.get("bucket"):
        return c["bucket"], c.get("bucket_reason", "set by hand")
    harm = c["harm"]
    d = distance(c)
    contrived = [h for h in c["holes"] if h["freq"] == "contrived"]
    if contrived and HARM[harm] < 4:
        return "skip", f"needs a contrived condition ({contrived[0]['condition']}) for a {harm} harm"
    if contrived:
        return "note", f"{harm} harm, but only through a contrived condition ({contrived[0]['condition']})"
    if d <= TEST_WITHIN[harm]:
        return "test", f"{layers(c)} slice(s), distance {d} within {TEST_WITHIN[harm]} for {harm}"
    if d <= TEST_WITHIN[harm] + NOTE_MARGIN:
        return "note", f"distance {d} past the test line ({TEST_WITHIN[harm]}) for {harm}"
    return "skip", f"distance {d} far past the test line ({TEST_WITHIN[harm]}) for {harm}"


ORDER = {"test": 0, "note": 1, "skip": 2}


def load(path: str) -> dict:
    data = json.loads(Path(path).read_text())
    errors = validate(data)
    if errors:
        for e in errors:
            print(f"error: {e}", file=sys.stderr)
        sys.exit(1)
    return data


def validate(data: dict) -> list[str]:
    errs = []
    seen = set()
    for i, c in enumerate(data.get("candidates", [])):
        cid = c.get("id") or f"#{i}"
        if cid in seen:
            errs.append(f"{cid}: duplicate id")
        seen.add(cid)
        for key in ("title", "holes", "harm"):
            if key not in c:
                errs.append(f"{cid}: missing {key}")
        if c.get("harm") not in HARM:
            errs.append(f"{cid}: harm must be one of {', '.join(HARM)}")
        if not c.get("holes"):
            errs.append(f"{cid}: needs at least one hole")
        for h in c.get("holes", []):
            if h.get("freq") not in FREQ:
                errs.append(f"{cid}: hole {h.get('condition')!r} freq must be one of {', '.join(FREQ)}")
            if not h.get("condition"):
                errs.append(f"{cid}: a hole has no condition")
        status = c.get("status", "untested")
        if status not in STATUSES:
            errs.append(f"{cid}: status must be one of {', '.join(sorted(STATUSES))}")
        if c.get("base", "") not in BASES:
            errs.append(f"{cid}: base must be same, differs or n/a")
        if status == "held" and not c.get("control"):
            errs.append(f"{cid}: held with no control; show the probe can fail (see SKILL.md, Test)")
        if status in {"held", "broke"} and not c.get("evidence"):
            errs.append(f"{cid}: {status} with no evidence file")
        if status == "broke" and not c.get("base"):
            errs.append(f"{cid}: broke but base not checked (same | differs | n/a)")
    return errs


def artifact_errors(run: Path, paths: object, label: str) -> list[str]:
    if not isinstance(paths, list) or not paths:
        return [f"{label}: expected a nonempty list of run-relative files"]
    errors = []
    for name in paths:
        if not isinstance(name, str) or not name.strip() or Path(name).is_absolute():
            errors.append(f"{label}: expected a run-relative file, got {name!r}")
            continue
        try:
            path = (run / name).resolve()
            if not path.is_relative_to(run):
                errors.append(f"{label}: {name!r} is outside the run directory")
            elif not path.is_file():
                errors.append(f"{label}: missing file {name!r}")
            else:
                with path.open("rb") as evidence:
                    if not evidence.read(1):
                        errors.append(f"{label}: empty file {name!r}")
        except (OSError, RuntimeError, ValueError) as exc:
            errors.append(f"{label}: cannot read {name!r}: {exc}")
    return errors


def finish(data: dict, run: Path) -> int:
    errors = validate(data)
    gaps = []
    # Diagrams are a required output (SKILL.md step 5): a boundary diagram plus one per serious break.
    # The run folder, then each folder above it up to the task folder (tasks/TASK-NNNN/), whose diagrams/ the review gate uses.
    drafts = list(run.rglob("*.draft"))
    for up in list(run.parents)[:3]:
        drafts += list(up.glob("diagrams/*.draft"))
        if up.name.startswith("TASK-"):
            break
    if not drafts:
        errors.append("no .draft diagram found in the run folder or its task's diagrams/ folder; "
                      "SKILL.md step 5 requires a boundary diagram and a Swiss-cheese diagram per serious break "
                      "(a run that skips them is not finished)")
    if not data.get("candidates"):
        errors.append("ledger needs at least one candidate")
    for index, c in enumerate(data.get("candidates", [])):
        cid = c.get("id") or f"#{index}"
        status = c.get("status")
        if not c.get("id"):
            errors.append(f"{cid}: missing candidate id")
        if status is None:
            errors.append(f"{cid}: missing explicit status")
        elif status == "skipped":
            errors.append(f"{cid}: record an untried candidate as untested with a reason in note")
        elif status in {"untested", "inconclusive"}:
            note = c.get("note")
            if not isinstance(note, str) or not note.strip():
                errors.append(f"{cid}: {status} needs a reason in note")
            else:
                gaps.append(f"- {cid} {c.get('title', '')} ({status}): {note}")
        elif status in {"held", "broke"}:
            if not re.fullmatch(r"[0-9a-fA-F]{7,64}", str(c.get("revision", ""))):
                errors.append(f"{cid}: revision needs the tested commit SHA")
            for field in ("reproduce", "expected", "observed"):
                if not isinstance(c.get(field), str) or not c[field].strip():
                    errors.append(f"{cid}: missing {field}")
            errors.extend(artifact_errors(run, c.get("evidence"), f"{cid} evidence"))
            if status == "held":
                control = c.get("control")
                if not isinstance(control, dict):
                    errors.append(f"{cid}: held needs a control receipt")
                    continue
                if control.get("outcome") != "failure-observed":
                    errors.append(f"{cid}: control must reach the probe and observe the target failure")
                if not isinstance(control.get("observed"), str) or not control["observed"].strip():
                    errors.append(f"{cid}: missing control observation")
                errors.extend(artifact_errors(run, control.get("evidence"), f"{cid} control evidence"))
    for error in errors:
        print(f"error: {error}")
    if not errors:
        print("evidence complete")
    print(f"Coverage gaps: {len(gaps)}")
    for gap in gaps:
        print(gap)
    return int(bool(errors))


def md_cell(s: str) -> str:
    return str(s).replace("|", "\\|").replace("\n", " ")


def holes_text(c: dict) -> str:
    return "; ".join(f"{h['condition']} ({h['freq']})" for h in c["holes"])


def triage(data: dict) -> str:
    rows = []
    for c in data["candidates"]:
        b, why = bucket(c)
        rows.append((ORDER[b], -HARM[c["harm"]], distance(c), c, b, why))
    rows.sort(key=lambda r: r[:3])
    out = ["| ID | Candidate | Holes that must line up | Harm | Slices | Distance | Bucket | Why |",
           "| --- | --- | --- | --- | ---: | ---: | --- | --- |"]
    for _, _, d, c, b, why in rows:
        out.append(f"| {c['id']} | {md_cell(c['title'])} | {md_cell(holes_text(c))} | {c['harm']} | {layers(c)} | {d} | {b} | {md_cell(why)} |")
    counts = {k: sum(1 for r in rows if r[4] == k) for k in ORDER}
    out.append("")
    out.append(f"{counts['test']} to test, {counts['note']} to note as accepted risk, {counts['skip']} skipped.")
    return "\n".join(out)


VERDICT = {
    ("broke", "same"): "Broke, pre-existing on base",
    ("broke", "differs"): "Broke, new in this change",
    ("broke", "n/a"): "Broke, new code (nothing on base)",
    ("held", ""): "Held",
    ("inconclusive", ""): "Inconclusive",
    ("untested", ""): "Not tested",
    ("skipped", ""): "Skipped",
}


def verdict(c: dict) -> str:
    s = c.get("status", "untested")
    key = (s, c.get("base", "")) if s == "broke" else (s, "")
    return VERDICT.get(key, s)


def results(data: dict) -> str:
    rank = {"broke": 0, "inconclusive": 1, "held": 2, "untested": 3, "skipped": 4}
    cs = sorted(data["candidates"], key=lambda c: (rank.get(c.get("status", "untested"), 9), -HARM[c["harm"]], distance(c)))
    out = ["| ID | What we tried | Result | Bucket | Odds (holes) | Harm | Who hits it | Evidence |",
           "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for c in cs:
        ev = ", ".join(f"[{Path(e).name}]({e})" for e in c.get("evidence", [])) or "none"
        odds = f"{layers(c)} slice(s): " + ", ".join(h["freq"] for h in c["holes"])
        out.append(f"| {c['id']} | {md_cell(c['title'])} | {verdict(c)} | {bucket(c)[0]} | {odds} | {c['harm']} | {md_cell(c.get('who', ''))} | {ev} |")
    return "\n".join(out)


def q(s: str) -> str:
    return json.dumps(str(s), ensure_ascii=False)


def default_subtitle(c: dict, held: bool) -> str:
    """A fallback only. Write the candidate's own "subtitle": what you found, in about ten words."""
    if held:
        i = c.get("blocked_at")
        layer = c["holes"][i - 1].get("layer", f"slice {i}") if i else "a later slice"
        return f"Held: the {layer.lower()} slice stopped it"
    return f"{layers(c)} holes line up for {c.get('who', 'a user')}"


def draft(data: dict, cid: str) -> str:
    c = next((c for c in data["candidates"] if c["id"] == cid), None)
    if c is None:
        sys.exit(f"no candidate {cid}")
    status = c.get("status", "untested")
    held = status == "held"
    blocked_at = c.get("blocked_at")  # index of the hole that stayed shut, for a held candidate
    lines = [
        f"diagram {q(c['id'] + ' · ' + c['title'])} version=1",
        f"subtitle {q(c.get('subtitle') or default_subtitle(c, held))}",
        "",
    ]
    start = "Starts with\n" + c.get("trigger", c.get("who", "a user"))
    lines.append(f"node hazard {q(start)} color=slate")
    prev = "hazard"
    for i, h in enumerate(c["holes"], 1):
        g = f"layer{i}"
        shut = held and blocked_at == i
        color = "mint" if shut else ("amber" if h["freq"] in ("always", "routine", "occasional") else "orange")
        lines.append(f"group {g} {q(h.get('layer', f'Slice {i}'))} color=slate")
        label = h["condition"] + "\n" + ("stayed shut" if shut else f"open: {h['freq']}")
        lines.append(f"node hole{i} {q(label)} in={g} color={color}")
        lines.append(f"edge e{i} {prev} -> hole{i}" + (" kind=async" if shut else ""))
        prev = f"hole{i}"
        if shut:
            break
    if not held:
        harm_label = c.get("observe", c["harm"]) + "\n" + f"harm: {c['harm']}"
        lines.append(f"node harm {q(harm_label)} color=red")
        lines.append(f"edge e_harm {prev} -> harm")
    lines += [""]
    used = set()
    for h_i, h in enumerate(c["holes"], 1):
        if held and blocked_at == h_i:
            used.add("mint")
            break
        used.add("amber" if h["freq"] in ("always", "routine", "occasional") else "orange")
    if "amber" in used:
        lines.append('legend amber "Hole that is often open"')
    if "orange" in used:
        lines.append('legend orange "Hole that is rarely open"')
    if "mint" in used:
        lines.append('legend mint "Slice that held"')
        lines.append('legend line dashed "Stopped here"')
    if not held:
        lines.append('legend red "What the user sees"')
    lines.append('legend slate "Who starts it, and each defense"')
    lines += ["", "layout root flow gap=40 fit=slide"]
    return "\n".join(lines) + "\n"


def main(argv: list[str]) -> int:
    if len(argv) < 3 or argv[1] not in {"triage", "results", "draft", "check", "finish"}:
        print(__doc__)
        return 2
    cmd, path = argv[1], argv[2]
    if cmd == "finish":
        return finish(json.loads(Path(path).read_text()), Path(path).parent.resolve())
    if cmd == "check":
        data = json.loads(Path(path).read_text())
        errs = validate(data)
        for e in errs:
            print(f"error: {e}")
        print(f"{len(data.get('candidates', []))} candidates, {len(errs)} errors")
        return 1 if errs else 0
    data = load(path)
    if cmd == "triage":
        print(triage(data))
    elif cmd == "results":
        print(results(data))
    elif cmd == "draft":
        if len(argv) < 4:
            sys.exit("draft needs a candidate id")
        sys.stdout.write(draft(data, argv[3]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
