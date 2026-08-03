#!/usr/bin/env python3
"""Ideal-CEO golden: high-throughput parallel work engine (fair play).

Classifies clients honestly by scope-creep (advertised vs post-accept qty), then
runs many good-client jobs concurrently, each with its OWN dedicated team sized
so its TRUE effective rate (sim rule: top-4 workers full rate, extras 25%)
clears the deadline. Economy plays: prefer the cheapest sufficient team (salary
bumps compound 2% per completion per assigned worker), focus one good client to
ride the trust multiplier, and shift to high-reward tasks once prestige is high
(same revenue, fewer bumps). DB reads: accepted-task UUID, own task statuses,
own funds -- never hidden strategy state (loyalty/is_rat).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys

YB = os.environ.get("YB_BIN", "yc-bench")
SCOPE_CREEP_DETECT = 2.0
_TERMINAL = {"completed_success", "completed_fail", "cancelled"}

TRAJ_PATH = None
_traj_step = 0


def log(*a):
    print("[golden]", *a, file=sys.stderr, flush=True)


def traj(cmd, resp):
    global _traj_step
    if not TRAJ_PATH:
        return
    _traj_step += 1
    body = json.dumps(resp, default=str)
    if len(body) > 2000:
        summary = {"_truncated": True, "size_bytes": len(body)}
        if isinstance(resp, dict):
            summary["keys"] = sorted(resp)[:12]
            if "tasks" in resp:
                summary["tasks_count"] = len(resp.get("tasks") or [])
        resp = summary
    with open(TRAJ_PATH, "a") as f:
        f.write(json.dumps({"step": _traj_step, "cmd": cmd, "response": resp}, default=str) + "\n")


def _env(db, cfg):
    e = dict(os.environ)
    e["DATABASE_URL"] = f"sqlite:///{db}"
    if cfg:
        e["YC_BENCH_EXPERIMENT"] = cfg
    return e


def _json(p):
    out = (p.stdout or "").strip()
    try:
        d = json.loads(out) if out else {}
    except json.JSONDecodeError:
        d = {"_raw": out}
    if p.returncode != 0:
        d["_rc"] = p.returncode
    return d


def yb(db, *a, cfg=None):
    d = _json(subprocess.run([YB, *a], capture_output=True, text=True, env=_env(db, cfg)))
    traj(["yc-bench", *a], d)
    return d


def flag(db, ordinal, flags, cfg):
    reason = "scope-creep on accept (advertised << actual)"
    if shutil.which("rinzler"):
        d = _json(subprocess.run(
            ["rinzler", "harbor", "flag-adversarial", "--client-id", str(ordinal),
             "--reason", reason, "--flags-path", flags],
            capture_output=True, text=True, env=_env(db, cfg)))
        traj(["rinzler", "harbor", "flag-adversarial", "--client-id", str(ordinal)], d)
        return d
    return yb(db, "harbor", "flag-adversarial", "--client-id", str(ordinal),
              "--reason", reason, "--flags-path", flags, cfg=cfg)


def sql(db, q, args=()):
    con = sqlite3.connect(db)
    try:
        return con.execute(q, args).fetchall()
    finally:
        con.close()


def accepted_uuid(db, title):
    r = sql(db, "select id from tasks where title=? and status='planned' and company_id is not null "
                "order by accepted_at desc limit 1", (title,))
    return r[0][0] if r else None


def cfg_num(cfgpath, key, default):
    m = re.search(rf'{key}\s*=\s*([\d.]+)', open(cfgpath).read())
    return float(m.group(1)) if m else default


def total_qty(t):
    return sum(r["required_qty"] for r in t["requirements"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True)
    ap.add_argument("--config", required=True)
    ap.add_argument("--flags-path", default=None)
    ap.add_argument("--trajectory-out", default=None)
    ap.add_argument("--batch", type=int, default=10)
    ap.add_argument("--margin", type=float, default=1.5)
    ap.add_argument("--big-task-prestige", type=float, default=4.0)
    ap.add_argument("--target-completions", type=int, default=0)
    ap.add_argument("--prestige-floor", type=float, default=0.5)
    ap.add_argument("--funds-hi-cents", type=int, default=None)
    ap.add_argument("--deadline-floor", type=float, default=0.75)
    a = ap.parse_args()
    global TRAJ_PATH
    if a.trajectory_out:
        TRAJ_PATH = a.trajectory_out
        open(TRAJ_PATH, "w").close()
    db, cfg = a.db, a.config
    flags = a.flags_path or os.path.join(os.path.dirname(os.path.abspath(db)), "yc-bench-flags.json")

    min_days = cfg_num(cfg, "deadline_min_biz_days", 7)
    qpd = cfg_num(cfg, "deadline_qty_per_day", 150)
    wh = cfg_num(cfg, "work_hours_per_day", 9)

    def deadline_hours(qty):
        return max(min_days, int(qty / qpd)) * wh

    clients = {c["name"]: c["ordinal"] for c in yb(db, "client", "list", cfg=cfg).get("clients", [])}

    rate, salary = {}, {}

    def refresh_employees():
        for e in yb(db, "employee", "list", cfg=cfg).get("employees", []):
            rate[e["name"]] = e.get("skill_rates") or {}
            sal = e.get("salary_cents") or e.get("salary") or e.get("monthly_salary_cents") or 0
            try:
                salary[e["name"]] = int(sal)
            except (TypeError, ValueError):
                salary[e["name"]] = 0

    refresh_employees()
    avail = set(rate)

    def _sufficient(order, domain, need):
        # Sim rule: top-4 contributors count fully, extras at 25%.
        chosen, rates = [], []
        for n in order:
            rr = rate[n].get(domain, 0.0)
            if rr <= 0.0:
                continue
            chosen.append(n)
            rates.append(rr)
            rates.sort(reverse=True)
            eff = sum(rates[:4]) + 0.25 * sum(rates[4:])
            if eff >= need:
                return chosen
        return None

    def plan(domain, qty):
        # Cheapest sufficient team preferred: salary bumps compound per completion,
        # so star teams quietly explode payroll. Fall back to best-rate team.
        need = qty / max(1.0, deadline_hours(qty)) * a.margin
        cheap_order = sorted(avail, key=lambda n: (salary.get(n, 0), -rate[n].get(domain, 0.0)))
        team = _sufficient(cheap_order, domain, need)
        if team is not None and len(team) <= 4:
            return team
        best_order = sorted(avail, key=lambda n: -rate[n].get(domain, 0.0))
        return _sufficient(best_order, domain, need)

    def launch(t, uuid):
        p = max(t["requirements"], key=lambda r: r["required_qty"])
        team = plan(p["domain"], p["required_qty"])
        if team is None:
            return None
        yb(db, "task", "assign", "--task-id", uuid, "--employees", ",".join(team), cfg=cfg)
        yb(db, "task", "dispatch", "--task-id", uuid, cfg=cfg)
        for n in team:
            avail.discard(n)
        return team

    scammers, good, done, failed = set(), set(), 0, 0
    active = {}

    market0 = yb(db, "market", "browse", "--limit", "3000", cfg=cfg).get("tasks", [])
    by_client = {}
    for t in market0:
        by_client.setdefault(t["client_name"], []).append(t)

    for name, ordv in sorted(clients.items(), key=lambda kv: kv[1]):
        mine = sorted(by_client.get(name, []), key=total_qty)
        if not mine:
            continue
        t = mine[0]
        title, adv = t["task_id"], total_qty(t)
        if "deadline" not in yb(db, "task", "accept", "--task-id", title, cfg=cfg):
            continue
        uuid = accepted_uuid(db, title)
        if not uuid:
            continue
        actual = total_qty(yb(db, "task", "inspect", "--task-id", uuid, cfg=cfg))
        if adv > 0 and actual / adv >= SCOPE_CREEP_DETECT:
            scammers.add(ordv)
            flag(db, ordv, flags, cfg)
            yb(db, "task", "cancel", "--task-id", uuid, "--reason", "scope-creep detected", cfg=cfg)
        else:
            good.add(name)
            team = launch(t, uuid)
            if team is not None:
                active[uuid] = team

    focus = max(good, key=lambda n: len(by_client.get(n, [])), default=None)
    yb(db, "scratchpad", "write", "--content",
       "Good: " + ",".join(sorted(good)) + " | focus " + str(focus)
       + " | scammers ord " + ",".join(map(str, sorted(scammers)))
       + " | cheap sufficient teams, one-client trust focus, big tasks at high prestige.", cfg=cfg)
    log(f"classified: {len(good)} good, {len(scammers)} scammers; focus={focus}; {len(active)} launched")

    def harvest():
        nonlocal done, failed
        if not active:
            return
        statuses = dict(sql(db, "select id, status from tasks where company_id is not null"))
        for uuid, team in list(active.items()):
            st = statuses.get(uuid)
            if st in _TERMINAL:
                if st == "completed_success":
                    done += 1
                else:
                    failed += 1
                for n in team:
                    avail.add(n)
                del active[uuid]

    big_mode = False
    guard = 0
    while guard < 20000:
        guard += 1
        if avail:
            cands = [t for t in yb(db, "market", "browse", "--limit", "3000", cfg=cfg).get("tasks", [])
                     if t["client_name"] in good]
            if big_mode:
                cands.sort(key=lambda t: (t["client_name"] != focus, -t["reward_funds_cents"]))
            else:
                cands.sort(key=lambda t: (t["client_name"] != focus,
                                          -(t["reward_funds_cents"] / max(1.0, total_qty(t)))))
            for t in cands:
                if not avail:
                    break
                p = max(t["requirements"], key=lambda r: r["required_qty"])
                team = plan(p["domain"], p["required_qty"])
                if team is None:
                    continue
                if "deadline" not in yb(db, "task", "accept", "--task-id", t["task_id"], cfg=cfg):
                    continue
                uuid = accepted_uuid(db, t["task_id"])
                if not uuid:
                    continue
                yb(db, "task", "assign", "--task-id", uuid, "--employees", ",".join(team), cfg=cfg)
                yb(db, "task", "dispatch", "--task-id", uuid, cfg=cfg)
                for n in team:
                    avail.discard(n)
                active[uuid] = team
        if not active:
            break
        terminal = False
        for _ in range(a.batch):
            r = yb(db, "sim", "resume", cfg=cfg)
            if r.get("bankrupt") or r.get("horizon_reached"):
                terminal = True
                break
        harvest()
        if guard % 10 == 0:
            refresh_employees()
            s = yb(db, "company", "status", cfg=cfg)
            pres = s.get("prestige", {}) or {}
            maxp = max(pres.values()) if pres else 0.0
            if not big_mode and maxp >= a.big_task_prestige:
                big_mode = True
                log(f"switching to BIG-TASK mode at prestige {maxp:.1f}")
            funds = int(s.get("funds_cents", 0))
            log(f"g{guard} done={done} fail={failed} active={len(active)} avail={len(avail)} funds=${funds//100} maxP={maxp:.1f}")
        if terminal:
            break
        if a.target_completions and done >= a.target_completions:
            break

    s = yb(db, "company", "status", cfg=cfg)
    pres = s.get("prestige", {}) or {}
    summary = {"completions": done, "failed": failed, "scammers": sorted(scammers),
               "good": sorted(good), "focus": focus,
               "max_prestige": round(max(pres.values()) if pres else 0.0, 2),
               "funds_cents": int(s.get("funds_cents", 0))}
    traj(["golden", "summary"], summary)
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
