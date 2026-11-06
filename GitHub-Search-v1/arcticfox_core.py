#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GitHub Search v1.0 — core layer.

Shared GitHub API client, configuration and helpers used by both the
GUI edition and the terminal edition. Standard library only.
"""

import json
import os
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

VERSION = "1.0"
APP_NAME = "GitHub Search"
TAGLINE = "GitHub Account & Repository Inspector"
REPO_URL = "https://github.com/arcticfox-cyber/Arctic-Fox-GitHub-Search"

CONF_DIR = Path(os.environ.get("XDG_CONFIG_HOME") or (Path.home() / ".config")) / "github-search"
CONF_FILE = CONF_DIR / "config.json"
REPORT_DIR = Path.home() / "github-search-reports"
API = "https://api.github.com"

CONF = {"token": "", "clone_dir": str(Path.home() / "github")}


class ApiError(Exception):
    """Raised for any GitHub API / network problem with a friendly message."""


# ---------------------------------------------------------------- config ---

def load_conf():
    """Load configuration from disk (kept compatible with v3.0)."""
    try:
        CONF_DIR.mkdir(parents=True, exist_ok=True)
    except OSError:
        pass
    if CONF_FILE.exists():
        try:
            CONF.update(json.loads(CONF_FILE.read_text()))
        except Exception:
            pass
    CONF.setdefault("token", "")
    CONF.setdefault("clone_dir", str(Path.home() / "github"))


def save_conf():
    try:
        CONF_DIR.mkdir(parents=True, exist_ok=True)
        CONF_FILE.write_text(json.dumps(CONF, indent=2))
        os.chmod(CONF_FILE, 0o600)
    except OSError:
        pass


# ------------------------------------------------------------------- api ---

def _headers():
    h = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": f"GitHubSearch/{VERSION}",
    }
    if CONF["token"]:
        h["Authorization"] = "Bearer " + CONF["token"]
    return h


def gh_api(path, params=None):
    """GET one JSON document from the GitHub API."""
    url = API + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=_headers())
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
        if e.code == 403 and ("rate limit" in low or "secondary rate" in low):
            if "search" in path:
                raise ApiError(
                    "Search rate limit reached. Wait a minute or add a token in Settings."
                ) from None
            raise ApiError("API rate limit reached — add a token in Settings.") from None
        if e.code == 401:
            raise ApiError("Invalid token — set it again in Settings.") from None
        if e.code == 422:
            raise ApiError("GitHub could not process that search query (422).") from None
        raise ApiError(f"{e.code}: {msg}") from None
    except urllib.error.URLError as e:
        raise ApiError(f"Network problem: {e.reason}") from None
    except TimeoutError:
        raise ApiError("Connection timed out.") from None


def gh_api_all(path, params=None, cap=600):
    """Fetch every page (up to cap) of a paginated endpoint."""
    out, page = [], 1
    while len(out) < cap:
        p = dict(params or {})
        p.update({"per_page": 100, "page": page})
        chunk = gh_api(path, p)
        if not chunk:
            break
        out.extend(chunk)
        if len(chunk) < 100:
            break
        page += 1
    return out[:cap]


SEARCH_MODES = {"Username": "in:login", "Full Name": "in:name", "Email": "in:email"}


def search_users(text, mode, per_page=20):
    """Search GitHub users by login / full name / email."""
    qual = SEARCH_MODES.get(mode, "in:login")
    q = f"{text} {qual}" if qual != "in:login" else text
    data = gh_api("/search/users", {"q": q, "per_page": per_page})
    return data.get("items", [])


# ---------------------------------------------------------------- output ---

def fmt(n):
    """1234 -> '1,234'."""
    try:
        return f"{int(n):,}"
    except (TypeError, ValueError):
        return str(n)


def time_ago(iso):
    """'2026-01-02T10:00:00Z' -> '10 months ago' (coarse)."""
    try:
        d = datetime.strptime(iso[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
    except (ValueError, TypeError):
        return (iso or "")[:10]
    s = max(0, int(time.time() - d.timestamp()))
    for div, label in ((31536000, "year"), (2592000, "month"), (604800, "week"),
                       (86400, "day"), (3600, "hour"), (60, "minute")):
        if s >= div:
            n = s // div
            return f"{n} {label}{'s' if n != 1 else ''} ago"
    return "just now"


def open_browser(url):
    """Open a URL in the default browser. Returns True on success."""
    try:
        if subprocess.Popen(["xdg-open", url],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL).poll() is None:
            return True
    except (FileNotFoundError, OSError):
        pass
    return False


def clone_repo(full, dest_dir, on_line=None, on_done=None):
    """Clone `owner/name` (shallow) into dest_dir. Streams git progress.

    on_line(text) is called for each progress line; on_done(ok, message)
    once finished. Runs synchronously — call from a worker thread.
    """
    dest = Path(dest_dir).expanduser() / full.split("/")[-1]
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        if on_done:
            on_done(False, f"Already exists: {dest}")
        return
    try:
        p = subprocess.Popen(
            ["git", "clone", "--depth", "1", "--progress",
             f"https://github.com/{full}.git", str(dest)],
            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True,
        )
    except FileNotFoundError:
        if on_done:
            on_done(False, "git is not installed: sudo apt install git")
        return
    for line in p.stderr or []:
        line = line.strip()
        if line and on_line:
            on_line(line.splitlines()[-1][:90])
    p.wait()
    if p.returncode == 0:
        if on_done:
            on_done(True, f"Cloned → {dest}")
    else:
        if on_done:
            on_done(False, "Clone failed — check the repo URL / connection.")


# ------------------------------------------------------------------ misc --

def fetch_bytes(url, timeout=25):
    """Download raw bytes (used for profile avatars)."""
    req = urllib.request.Request(url, headers={
        "User-Agent": f"GitHubSearch/{VERSION}",
        "Accept": "image/png,image/*;q=0.9,*/*;q=0.8",
    })
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


# ---------------------------------------------------------------- reports --

def _report_paths(login):
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    return REPORT_DIR / f"{login}-{stamp}.txt", REPORT_DIR / f"{login}-{stamp}.json"


def save_report(u, repos, gists, events):
    """Write the classic .txt report. Returns the file path."""
    f, _ = _report_paths(u["login"])
    L = [f"GitHub Search report — @{u['login']}",
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
    return f


def save_json(u, repos, gists, events):
    """Write the .json export. Returns the file path."""
    _, f = _report_paths(u["login"])
    payload = {
        "tool": f"GitHub Search {VERSION}",
        "generated": datetime.now().isoformat(timespec="seconds"),
        "profile": u,
        "stats": stats_summary(u, repos),
        "repositories": repos,
        "gists": gists,
        "recent_activity": events,
    }
    f.write_text(json.dumps(payload, indent=2))
    return f


def stats_summary(u, repos):
    """Aggregate numbers for the stats bar."""
    langs = {}
    stars = forks = 0
    for r in repos:
        stars += r.get("stargazers_count", 0) or 0
        forks += r.get("forks_count", 0) or 0
        l = r.get("language")
        if l:
            langs[l] = langs.get(l, 0) + 1
    top_lang = max(langs, key=langs.get) if langs else "—"
    return {
        "repos": u.get("public_repos", len(repos)),
        "loaded": len(repos),
        "stars": stars,
        "forks": forks,
        "top_language": top_lang,
        "followers": u.get("followers", 0),
        "following": u.get("following", 0),
        "gists": u.get("public_gists", 0),
    }
