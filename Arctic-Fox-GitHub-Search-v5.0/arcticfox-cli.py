#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Arctic Fox GitHub Search — enter a username, get the full profile + all repos"""

import json, os, shutil, subprocess, sys, threading, time
import urllib.error, urllib.parse, urllib.request
from datetime import datetime
from pathlib import Path

VERSION = "5.0.3"
CONF_DIR = Path(os.environ.get("XDG_CONFIG_HOME") or (Path.home() / ".config")) / "arctic-fox"
CONF_FILE = CONF_DIR / "config.json"
REPORT_DIR = Path.home() / "arctic-fox-reports"
API = "https://api.github.com"

R = "\033[0m"; B = "\033[1m"; DIM = "\033[2m"
ICE = "\033[38;5;159m"; CYAN = "\033[38;5;51m"; BLUE = "\033[38;5;39m"
DEEP = "\033[38;5;33m"; GREY = "\033[38;5;245m"; WHITE = "\033[97m"
GREEN = "\033[38;5;114m"; RED = "\033[38;5;203m"; YELL = "\033[38;5;221m"
GLOW = "\033[38;5;195m"

GRAD = [BLUE, DEEP, CYAN, ICE, GLOW, WHITE, GLOW, ICE, CYAN, DEEP]
ART = [
    "  ▄▀█ █▀█ █▀▀ ▀█▀ █ █▀▀   █▀▀ █▀█ █ █  ",
    "  █▀█ █▀▄ █▄▄  █  █ █▄▄   █▀▀ █▄█ ▄▀▄  ",
]
SUB = "GitHub account + repo inspector  ·  Kali Linux  ·  terminal edition  ·  v" + VERSION

CONF = {"token": "", "clone_dir": str(Path.home() / "github")}


def tw():
    return shutil.get_terminal_size((80, 24)).columns


def _paint(off):
    for i, line in enumerate(ART):
        buf = []
        for j, ch in enumerate(line):
            buf.append(GRAD[(j + off + i * 5) % len(GRAD)])
            buf.append(ch)
        print("".join(buf) + R)
    print(f"{GREY}  {SUB}{R}")


def banner():
    sys.stdout.write("\033[2J\033[H\033[?25l")
    for off in range(0, 40, 4):
        sys.stdout.write("\033[H"); _paint(off); sys.stdout.flush(); time.sleep(0.03)
    sys.stdout.write("\033[H"); _paint(2); sys.stdout.write("\033[?25h"); print()


def title(text, color=ICE):
    w = min(64, max(40, tw() - 2))
    print()
    print(color + "┌" + "─" * w + "┐")
    label = f" {text} "
    print(color + "│" + R + B + WHITE + label + R + color + " " * max(0, w - len(label)) + "│")
    print(color + "└" + "─" * w + "┘" + R)


def info(m): print(f"  {CYAN}[i]{R} {m}")
def ok(m):   print(f"  {GREEN}[+]{R} {m}")
def warn(m): print(f"  {YELL}[!]{R} {m}")
def err(m):  print(f"  {RED}[x]{R} {m}")


def ask(label):
    try:
        return input(f"  {CYAN}{label} > {R}").strip()
    except (EOFError, KeyboardInterrupt):
        return "q"


def pause():
    try:
        input(f"\n  {GREY}[ Enter ] back{R}")
    except (EOFError, KeyboardInterrupt):
        pass


class Spinner:
    def __init__(self, msg):
        self.msg = msg; self.ev = threading.Event(); self.t = None

    def __enter__(self):
        sys.stdout.write("\033[?25l")
        self.t = threading.Thread(target=self._run, daemon=True); self.t.start()
        return self

    def _run(self):
        f = "◐◓◑◒"; i = 0
        while not self.ev.is_set():
            sys.stdout.write(f"\r  {ICE}{f[i % 4]}{R} {GREY}{self.msg}…{R} ")
            sys.stdout.flush(); i += 1; time.sleep(0.07)

    def __exit__(self, *a):
        self.ev.set()
        if self.t: self.t.join()
        sys.stdout.write("\r\033[K\033[?25h")


class ApiError(Exception):
    pass


def api(path, params=None):
    url = API + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    req.add_header("User-Agent", f"ArcticFox/{VERSION}")
    if CONF["token"]:
        req.add_header("Authorization", "Bearer " + CONF["token"])
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        try:
            msg = json.load(e).get("message", str(e))
        except Exception:
            msg = str(e)
        low = msg.lower()
        if e.code == 404:
            raise ApiError("No such account found (404).") from None
        if e.code == 403 and "rate limit" in low:
            raise ApiError("Rate limit reached — add a token in Settings (s).") from None
        if e.code == 401:
            raise ApiError("Invalid token — set it again in Settings.") from None
        raise ApiError(f"{e.code}: {msg}") from None
    except urllib.error.URLError as e:
        raise ApiError(f"Network problem: {e.reason}") from None


def api_all(path, params=None, cap=600):
    out, page = [], 1
    while len(out) < cap:
        p = dict(params or {}); p.update({"per_page": 100, "page": page})
        chunk = api(path, p)
        if not chunk: break
        out.extend(chunk)
        if len(chunk) < 100: break
        page += 1
    return out[:cap]


def load_conf():
    CONF_DIR.mkdir(parents=True, exist_ok=True)
    if CONF_FILE.exists():
        try:
            CONF.update(json.loads(CONF_FILE.read_text()))
        except Exception:
            pass


def save_conf():
    CONF_FILE.write_text(json.dumps(CONF, indent=2)); os.chmod(CONF_FILE, 0o600)


def open_url(url):
    for cmd in (["xdg-open", url], ["termux-open-url", url]):
        try:
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            ok("Opened in browser.")
            return
        except FileNotFoundError:
            continue
    warn(f"URL: {url}")


def clone_repo(full):
    dest = Path(CONF["clone_dir"]).expanduser() / full.split("/")[-1]
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        warn(f"Already exists: {dest}"); return
    try:
        with Spinner(f"clone → {dest}"):
            p = subprocess.run(["git", "clone", "--depth", "1",
                                f"https://github.com/{full}.git", str(dest)],
                               capture_output=True, text=True)
    except FileNotFoundError:
        err("git is not installed: sudo apt install git"); return
    if p.returncode == 0:
        ok(f"Clone complete: {dest}")
    else:
        err("Clone fail: " + (p.stderr or "").strip()[:200])


def repo_details(full):
    try:
        with Spinner("details"):
            d = api(f"/repos/{full}")
    except ApiError as e:
        err(str(e)); return
    title("REPO DETAILS")
    for k, v in [
        ("Full name", d.get("full_name")),
        ("Stars", f"{d['stargazers_count']}  Forks: {d['forks_count']}  Watch: {d['subscribers_count']}"),
        ("Language", d.get("language") or "n/a"),
        ("License", (d.get("license") or {}).get("spdx_id") or "none"),
        ("Created", d["created_at"][:10]), ("Pushed", d["pushed_at"][:10]),
        ("Size", f"{d.get('size', 0)} KB"),
        ("Topics", ", ".join(d.get("topics") or []) or "-"),
        ("Homepage", d.get("homepage") or "-"),
        ("Description", d.get("description") or "-"),
    ]:
        print(f"  {GREY}{k:<12}{R} {v}")


def save_report(u, repos, gists, events):
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    f = REPORT_DIR / f"{u['login']}-{datetime.now():%Y%m%d-%H%M%S}.txt"
    L = [f"Arctic Fox report — @{u['login']}",
         f"Generated: {datetime.now():%Y-%m-%d %H:%M:%S}",
         "=" * 60,
         f"Name     : {u.get('name') or '-'}",
         f"Type     : {u['type']}",
         f"Company  : {u.get('company') or '-'}",
         f"Location : {u.get('location') or '-'}",
         f"Bio      : {u.get('bio') or '-'}",
         f"Blog     : {u.get('blog') or '-'}",
         f"Twitter  : {u.get('twitter_username') or '-'}",
         f"Email    : {u.get('email') or '-'}",
         f"Repos    : {u.get('public_repos')}  Gists: {u.get('public_gists')}",
         f"Followers: {u.get('followers')}  Following: {u.get('following')}",
         f"Created  : {u['created_at'][:10]}  Updated: {u['updated_at'][:10]}",
         f"Profile  : {u['html_url']}", "=" * 60, "", "REPOSITORIES:"]
    for r in repos:
        L.append(f"- {r['full_name']}  ★{r['stargazers_count']} ⑂{r['forks_count']} "
                 f"{r.get('language') or 'n/a'}  {r['updated_at'][:10]}")
        if r.get("description"):
            L.append(f"    {r['description']}")
        if r.get("topics"):
            L.append(f"    topics: {', '.join(r['topics'])}")
    L += ["", "GISTS:"]
    for g in gists:
        L.append(f"- {g['html_url']}  {g.get('description') or ''}")
    L += ["", "RECENT ACTIVITY:"]
    for e in events:
        L.append(f"- {e['created_at'][:19]}  {e['type']}  {e['repo']['name']}")
    f.write_text("\n".join(L))
    ok(f"Report saved: {f}")


def dump_user(login):
    banner()
    title(f"@{login}")
    try:
        with Spinner("profile"):
            u = api(f"/users/{login}")
    except ApiError as e:
        err(str(e)); return

    print(f"  {B}{WHITE}{u.get('name') or u['login']}{R}  {GREY}({u['type']}){R}")
    print(f"  {GREY}bio       {R} {u.get('bio') or '-'}")
    print(f"  {GREY}company   {R} {u.get('company') or '-'}")
    print(f"  {GREY}location  {R} {u.get('location') or '-'}")
    print(f"  {GREY}blog      {R} {u.get('blog') or '-'}")
    print(f"  {GREY}twitter   {R} {('@' + u['twitter_username']) if u.get('twitter_username') else '-'}")
    print(f"  {GREY}email     {R} {u.get('email') or '-'}")
    print(f"  {GREY}joined    {R} {u['created_at'][:10]}   {GREY}updated {R}{u['updated_at'][:10]}")
    print(f"  {GREY}repos     {R} {YELL}{u.get('public_repos')}{R}   "
          f"{GREY}gists {R}{u.get('public_gists')}   "
          f"{GREY}followers {R}{u.get('followers')}   {GREY}following {R}{u.get('following')}")
    print(f"  {GREY}profile   {R} {u['html_url']}")

    try:
        orgs = api(f"/users/{login}/orgs")
    except ApiError:
        orgs = []
    if orgs:
        print(f"\n  {GREY}orgs      {R} " + ", ".join(o["login"] for o in orgs))

    try:
        with Spinner("all repos"):
            repos = api_all(f"/users/{login}/repos", {"sort": "updated"})
    except ApiError as e:
        err(str(e)); repos = []

    title(f"REPOS · {len(repos)}")
    names = []
    if not repos:
        warn("No public repositories.")
    for i, r in enumerate(repos, 1):
        names.append(r["full_name"])
        fork = f" {GREY}[fork]{R}" if r.get("fork") else ""
        arch = f" {RED}[archived]{R}" if r.get("archived") else ""
        print(f"{ICE}[{i:03d}]{R} {B}{r['name']}{R}{fork}{arch}")
        print(f"      {YELL}★ {r['stargazers_count']}  ⑂ {r['forks_count']}  "
              f"{r.get('language') or 'n/a'}  {r['updated_at'][:10]}{R}")
        if r.get("description"):
            print(f"      {GREY}{r['description'][:max(20, tw() - 10)]}{R}")
        if r.get("topics"):
            print(f"      {DIM}topics: {', '.join(r['topics'][:8])}{R}")
        print()

    try:
        gists = api_all(f"/users/{login}/gists", cap=100)
    except ApiError:
        gists = []
    if gists:
        title(f"GISTS · {len(gists)}")
        for g in gists:
            print(f"  {ICE}•{R} {g['html_url']}  {GREY}{g.get('description') or ''}{R}")

    try:
        events = api(f"/users/{login}/events/public", {"per_page": 12})
    except ApiError:
        events = []
    if events:
        title("RECENT ACTIVITY")
        for e in events:
            print(f"  {GREY}{e['created_at'][:16].replace('T', ' ')}{R}  "
                  f"{e['type']}  {ICE}{e['repo']['name']}{R}")

    print(f"\n  {ICE}[number]{R} clone/open · {ICE}[o]{R} open profile in browser · "
          f"{ICE}[s]{R} save report · {GREY}[0]{R} back")

    while True:
        c = ask("")
        if c == "0" or c == "q":
            return
        if c == "o":
            open_url(u["html_url"]); continue
        if c == "s":
            save_report(u, repos, gists, events); continue
        if c.isdigit() and 1 <= int(c) <= len(names):
            full = names[int(c) - 1]
            title(full)
            print(f"  {ICE}[1]{R} Clone   {ICE}[2]{R} Details   {ICE}[3]{R} Browser   {GREY}[0]{R} back")
            d = ask("")
            if d == "1":
                clone_repo(full); pause()
            elif d == "2":
                repo_details(full); pause()
            elif d == "3":
                open_url(f"https://github.com/{full}")


def settings():
    while True:
        banner()
        title("SETTINGS")
        print(f"  Token     : {GREEN + 'set' + R if CONF['token'] else GREY + 'none' + R}")
        print(f"  Clone dir : {CONF['clone_dir']}")
        print(f"\n  {ICE}[1]{R} Token set/clear   {ICE}[2]{R} Clone dir   {GREY}[0]{R} back")
        c = ask("")
        if c == "1":
            print(f"  {GREY}github.com/settings/tokens → generate (scope: public_repo){R}")
            CONF["token"] = ask("token (empty = clear)")
            save_conf(); ok("Save."); pause()
        elif c == "2":
            v = ask("clone dir")
            if v: CONF["clone_dir"] = v; save_conf()
        elif c == "0":
            return


def main():
    load_conf()
    args = sys.argv[1:]
    if args:
        dump_user(args[0].lstrip("@").strip())
        return
    try:
        while True:
            banner()
            print(f"  {GREY}enter a username (e.g. arcticfox-cyber)   ·   s = settings   ·   q = exit{R}\n")
            login = ask("username").lstrip("@").strip()
            if login in ("q", ""):
                break
            if login == "s":
                settings(); continue
            dump_user(login)
    except KeyboardInterrupt:
        pass
    print(f"\n  {ICE}Arctic Fox closed. Stay frosty.{R}\n")


if __name__ == "__main__":
    main()
