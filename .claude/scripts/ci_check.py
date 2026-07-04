#!/usr/bin/env python3
"""Server-side harness gate — scans ALL tasks, fails the build on broken state.

Unlike the local pre-commit hook (which guards the ACTIVE task), CI enforces
repo-wide invariants that must never land on a shared branch:
  - no task in stage ESCALATED
  - no task with non-empty open_issues
  - every STATE.yaml has a known stage and status
  - STATE agrees with its artifacts (anti-forgery):
      * VALIDATED/DONE  => VALIDATION.md exists, version matches, result == status
      * DONE            => validation result PASS
      * EXECUTED+       => exec_version >= 1
      * MED/HIGH past planning => plan_version >= 1
DONE tasks are fine — that is the intended committed end state.
Exit 1 on any violation. Run: python3 .claude/scripts/ci_check.py
"""
import os, sys, glob

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)          # .claude/ (scripts/ lives under it)
CURRENT = os.path.join(ROOT, "tasks", "CURRENT")   # open working set
STAGES = {"INIT","PLANNED","APPROVED","EXECUTED","VALIDATED","DONE","ESCALATED"}
STATUSES = {"PENDING","PASS","FAIL"}

def field(text, key):
    for line in text.splitlines():
        s = line.strip()
        if s.startswith(key + ":"):
            return s.split(":",1)[1].split("#")[0].strip()
    return None

def main():
    viol = []
    # open tasks only: tasks/CURRENT/<YYYY-MM-DD>-<task>/STATE.yaml
    # (archive tasks/DONE/** is clean by construction and not scanned)
    states = sorted(glob.glob(os.path.join(CURRENT, "*", "STATE.yaml")))
    def as_int(x):
        try: return int(x)
        except (TypeError, ValueError): return None
    for sp in states:
        d = os.path.dirname(sp)
        tid = os.path.basename(d)
        s = open(sp, encoding="utf-8").read()
        stage, status, oi = field(s,"stage"), field(s,"status"), field(s,"open_issues")
        cx = field(s,"complexity")
        plan_v, exec_v, val_v = (as_int(field(s,k)) for k in
                                 ("plan_version","exec_version","validation_version"))
        if stage not in STAGES:
            viol.append(f"{tid}: unknown stage '{stage}'")
        if status not in STATUSES:
            viol.append(f"{tid}: unknown status '{status}'")
        if stage == "ESCALATED":
            viol.append(f"{tid}: ESCALATED — unresolved, must not be on the branch")
        if oi not in (None, "[]", ""):
            viol.append(f"{tid}: unresolved open_issues {oi}")
        if stage == "DONE" and status != "PASS":
            viol.append(f"{tid}: DONE but status={status} (must be PASS)")
        # --- STATE <-> artifact consistency (cannot fake a completed pipeline) ---
        if stage in ("EXECUTED","VALIDATED","DONE") and (exec_v or 0) < 1:
            viol.append(f"{tid}: stage {stage} but exec_version={exec_v} (no execution artifact)")
        if cx in ("MEDIUM","HIGH") and stage in ("APPROVED","EXECUTED","VALIDATED","DONE") \
                and (plan_v or 0) < 1:
            viol.append(f"{tid}: {cx} at {stage} but plan_version={plan_v} (no plan)")
        if stage in ("VALIDATED","DONE"):
            vp = os.path.join(d, "VALIDATION.md")
            if not os.path.isfile(vp):
                viol.append(f"{tid}: stage {stage} but VALIDATION.md missing")
            else:
                vt = open(vp, encoding="utf-8").read()
                vres, vver = field(vt,"result"), as_int(field(vt,"validation_version"))
                if vver != val_v:
                    viol.append(f"{tid}: validation_version STATE={val_v} != VALIDATION.md={vver}")
                if vres != status:
                    viol.append(f"{tid}: status={status} but VALIDATION.md result={vres}")
    print(f"harness gate: scanned {len(states)} task(s)")
    if viol:
        print("VIOLATIONS:", file=sys.stderr)
        for v in viol:
            print(f"  ✖ {v}", file=sys.stderr)
        sys.exit(1)
    print("✔ all tasks clean")
    sys.exit(0)

if __name__ == "__main__":
    main()
