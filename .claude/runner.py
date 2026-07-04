#!/usr/bin/env python3
"""Harness runner — deterministic task registry + dispatcher.

Layout:
  tasks/CURRENT/<YYYY-MM-DD>-<task>/       open tasks (INIT..VALIDATED, ESCALATED)
  tasks/DONE/<YYYY-MM>/<YYYY-MM-DD>-<task>/ closed tasks (DONE/PASS) — archive, prune by month
  tasks/ACTIVE                             canonical id of the active task

Task ids are date-prefixed: `new pay-bug` -> `<today>-pay-bug`. Commands accept the
full id or the bare suffix (`use pay-bug`) when unambiguous.

Commands:
  new <task> [--complexity LOW|MEDIUM|HIGH]  scaffold tasks/CURRENT/<today>-<task>, make active
  list [--all|--done]                        tasks: where/stage/status/next_actor
  use <id>                                   switch the active task
  active                                     print active task id
  status [id]                                key STATE fields (active if omitted)
  next [id]                                  dispatch descriptor for next_actor
  done [id] [--force]                        close: move CURRENT -> DONE/<month>, clear active
  install-hooks                              set core.hooksPath -> .claude/githooks

The runner never decides content — only routing, from STATE.yaml (single truth).
"""
import argparse, os, sys, datetime, glob, shutil, re

ROOT    = os.path.dirname(os.path.abspath(__file__))
TASKS   = os.path.join(ROOT, "tasks")
CURRENT = os.path.join(TASKS, "CURRENT")   # open working set
DONE    = os.path.join(TASKS, "DONE")      # archive (month-partitioned)
ACTIVE  = os.path.join(TASKS, "ACTIVE")

ROLE_IO = {
    "Planner":   (["TASK.md","STATE.yaml"], ["PLAN.md","STATE.yaml"]),
    "Executor":  (["TASK.md","PLAN.md","STATE.yaml"], ["EXEC.md","STATE.yaml"]),
    "Validator": (["TASK.md","PLAN.md","EXEC.md","STATE.yaml"], ["VALIDATION.md","STATE.yaml"]),
    "Engineer":  (["<all>"], ["TASK.md","STATE.yaml"]),
}
FIRST_ACTOR = {"LOW": "Executor", "MEDIUM": "Planner", "HIGH": "Planner"}

def die(m): print(f"error: {m}", file=sys.stderr); sys.exit(1)
def today(): return datetime.datetime.now().strftime("%Y-%m-%d")

def _open_dirs():
    return [d for d in sorted(glob.glob(os.path.join(CURRENT, "*")))
            if os.path.isfile(os.path.join(d, "STATE.yaml"))]

def _closed_dirs():
    return [d for d in sorted(glob.glob(os.path.join(DONE, "*", "*")))
            if os.path.isfile(os.path.join(d, "STATE.yaml"))]

def _find(tid):
    """Resolve a full id or an unambiguous bare suffix to its task dir."""
    dirs = _open_dirs() + _closed_dirs()
    by_name = {os.path.basename(d): d for d in dirs}
    if tid in by_name:
        return by_name[tid]
    hits = [d for d in dirs if os.path.basename(d).endswith("-" + tid)]
    return hits[0] if len(hits) == 1 else None

def tdir(tid):
    d = _find(tid)
    if not d: die(f"no such task '{tid}'")
    return d

def full_id(tid): return os.path.basename(tdir(tid))
def spath(tid): return os.path.join(tdir(tid), "STATE.yaml")

def field(text, key):
    for line in text.splitlines():
        s = line.strip()
        if s.startswith(key + ":"):
            return s.split(":",1)[1].split("#")[0].strip()
    return None

def read_state(tid): return open(spath(tid), encoding="utf-8").read()

def all_tasks():
    out = []
    for d in _open_dirs():
        out.append((os.path.basename(d), d, "tasks/CURRENT", False))
    for d in _closed_dirs():
        mth = os.path.basename(os.path.dirname(d))
        out.append((os.path.basename(d), d, "tasks/DONE/" + mth, True))
    return sorted(out, key=lambda x: (x[3], x[0]))

def get_active():
    if os.path.isfile(ACTIVE):
        return open(ACTIVE).read().strip() or None
    return None

def set_active(tid):
    os.makedirs(TASKS, exist_ok=True)
    open(ACTIVE, "w").write((tid or "") + "\n")

def resolve(tid):
    return tid or get_active() or die("no active task; use `runner.py use <id>`")

def log(tid, line):
    ts = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M")
    with open(os.path.join(tdir(tid), "LOG.md"), "a", encoding="utf-8") as f:
        f.write(f"- {ts} {line}\n")

def month_of(tid):
    m = re.match(r"(\d{4}-\d{2})-\d{2}-", tid)
    return m.group(1) if m else datetime.datetime.now().strftime("%Y-%m")

# ---- commands ----
def cmd_new(a):
    tid = f"{today()}-{a.id}"
    if _find(tid): die(f"task '{tid}' already exists")
    d = os.path.join(CURRENT, tid); os.makedirs(d)
    cx = a.complexity; actor = FIRST_ACTOR[cx]
    open(os.path.join(d,"TASK.md"),"w").write(
        f"# TASK — {tid}\nowner: Engineer\nimmutable: true\n\n## Requirements\n- R1: \n\n## Acceptance\n- A1: \n\n## Constraints\n- \n")
    for f in ("PLAN.md","EXEC.md","VALIDATION.md"):
        open(os.path.join(d,f),"w").write(f"# {f.split('.')[0]} — {tid}\n")
    open(os.path.join(d,"STATE.yaml"),"w").write(
        f"task_id: {tid}\nstage: INIT\nstatus: PENDING\niteration: 0\n"
        f"complexity: {cx}\nnext_actor: {actor}\nplan_version: 0\n"
        f"exec_version: 0\nvalidation_version: 0\nopen_issues: []\nlast_error: null\n")
    open(os.path.join(d,"LOG.md"),"w").write(f"# LOG — {tid}\n")
    log(tid, f"Engineer INIT created, complexity={cx}, next_actor={actor}")
    set_active(tid)
    print(f"created 'tasks/CURRENT/{tid}' [{cx}] -> INIT, next_actor={actor} (now active)")

def cmd_list(a):
    act = get_active()
    rows = all_tasks()
    if getattr(a, "done", False):  rows = [r for r in rows if r[3]]
    elif not getattr(a, "all", False): rows = [r for r in rows if not r[3]]
    if not rows: print("(no tasks)"); return
    print(f"{'':2}{'TASK':32}{'WHERE':20}{'STAGE':11}{'STATUS':8}NEXT_ACTOR")
    for tid, d, where, closed in rows:
        s = open(os.path.join(d,"STATE.yaml"), encoding="utf-8").read()
        mark = "*" if tid == act else " "
        print(f"{mark:2}{tid:32}{where:20}{field(s,'stage') or '?':11}"
              f"{field(s,'status') or '?':8}{field(s,'next_actor') or '?'}")

def cmd_use(a):
    d = _find(a.id)
    if not d: die(f"no such task '{a.id}'")
    set_active(os.path.basename(d)); print(f"active task -> {os.path.basename(d)}")

def cmd_active(a): print(get_active() or "(none)")

def cmd_status(a):
    tid = resolve(a.id); s = read_state(tid)
    for k in ("task_id","stage","status","iteration","complexity",
              "next_actor","open_issues","last_error"):
        print(f"{k:14}{field(s,k)}")

def cmd_next(a):
    tid = resolve(a.id); s = read_state(tid)
    stage, actor = field(s,"stage"), field(s,"next_actor")
    if stage == "DONE" or actor in (None,"","none"):
        print(f"[{tid}] {stage}: nothing to dispatch."); return
    reads, writes = ROLE_IO.get(actor, (["?"],["?"]))
    oi = field(s,"open_issues")
    print(f"DISPATCH  task={tid}  stage={stage}  actor={actor}")
    print(f"  skill : skills/{actor}/SKILLS.md")
    print(f"  reads : {', '.join(reads)}")
    print(f"  writes: {', '.join(writes)}")
    if oi and oi != "[]": print(f"  open_issues: {oi}")
    if actor == "Engineer" and stage == "PLANNED":
        print("  action: HIGH plan awaiting approval (stage=APPROVED) or requirement rework.")

def cmd_done(a):
    tid = full_id(resolve(a.id)); s = read_state(tid)
    stage, status, oi = field(s,"stage"), field(s,"status"), field(s,"open_issues")
    clean = stage == "DONE" and status == "PASS" and oi in (None,"[]","")
    if not clean and not a.force:
        die(f"task '{tid}' not finished: stage={stage} status={status} "
            f"open_issues={oi}. Close it via the pipeline, or use --force.")
    if not clean:
        print(f"warning: forcing close of unfinished task (stage={stage} status={status})")
    src = tdir(tid); mth = month_of(tid)
    log(tid, f"Engineer CLOSED done={clean}; archived to tasks/DONE/{mth}")
    if not os.path.abspath(src).startswith(os.path.abspath(DONE)):  # open -> archive
        dst = os.path.join(DONE, mth); os.makedirs(dst, exist_ok=True)
        shutil.move(src, os.path.join(dst, tid))
    if get_active() in (tid, None) or a.id is None: set_active("")
    print(f"✔ task '{tid}' closed -> tasks/DONE/{mth}/{tid}. active task -> none.")
    print("  all state is in artifacts — the Claude window is safe to clear "
          "now (/clear or start a new session).")

def cmd_install_hooks(a):
    repo = os.path.dirname(ROOT)
    if os.system(f'git -C "{repo}" config core.hooksPath .claude/githooks') == 0:
        print("core.hooksPath -> .claude/githooks (pre-commit gate active)")
    else:
        die("git config failed (is this a git repo?)")

def main():
    p = argparse.ArgumentParser(prog="runner.py")
    sub = p.add_subparsers(dest="cmd", required=True)
    n = sub.add_parser("new"); n.add_argument("id")
    n.add_argument("--complexity", choices=["LOW","MEDIUM","HIGH"], default="MEDIUM")
    n.set_defaults(fn=cmd_new)
    l = sub.add_parser("list"); l.add_argument("--all", action="store_true")
    l.add_argument("--done", action="store_true"); l.set_defaults(fn=cmd_list)
    u = sub.add_parser("use"); u.add_argument("id"); u.set_defaults(fn=cmd_use)
    sub.add_parser("active").set_defaults(fn=cmd_active)
    st = sub.add_parser("status"); st.add_argument("id", nargs="?"); st.set_defaults(fn=cmd_status)
    nx = sub.add_parser("next"); nx.add_argument("id", nargs="?"); nx.set_defaults(fn=cmd_next)
    d = sub.add_parser("done"); d.add_argument("id", nargs="?")
    d.add_argument("--force", action="store_true"); d.set_defaults(fn=cmd_done)
    sub.add_parser("install-hooks").set_defaults(fn=cmd_install_hooks)
    a = p.parse_args(); a.fn(a)

if __name__ == "__main__":
    main()
