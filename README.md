<div align="center">

# 🦊 GITHUB SEARCH v1.0

**GitHub Account & Repository Inspector · Desktop GUI for Kali Linux**

<img src="docs/screenshot-main.png" alt="GitHub Search main window" width="900" />

<p>
  <img src="https://img.shields.io/badge/version-1.0-3DDCFF?style=for-the-badge" alt="Version 1.0" />
  <img src="https://img.shields.io/badge/platform-Kali%20Linux-6C63FF?style=for-the-badge&logo=kalilinux&logoColor=white" alt="Kali Linux" />
  <img src="https://img.shields.io/badge/interface-Tkinter%20GUI-8B7BFF?style=for-the-badge" alt="Tkinter GUI" />
  <img src="https://img.shields.io/badge/license-Proprietary-343A66?style=for-the-badge" alt="Proprietary license" />
</p>

**Search · Inspect · Clone · Export**

[Repository](https://github.com/arcticfox-cyber/GitHub-Search) · [Issues](https://github.com/arcticfox-cyber/GitHub-Search/issues) · [License](LICENSE)

</div>

---

## Overview

GitHub Search is a Python desktop application for searching GitHub users and exploring their publicly available profile and repository information. Search by username, full name, or email; inspect repositories, gists and recent public activity; clone public repositories; and export reports.

The v1.0 interface features the **GitHub Dark Pro** theme, animated interface elements, circular profile avatars, and an in-window Moonlit Fox startup splash.

## Features

| Feature | Description |
|---|---|
| User search | Search by GitHub username, full name, or email |
| Profile inspector | View public profile information, avatar, followers, and organizations |
| Repository explorer | Browse repositories, stars, forks, languages, topics, and update dates |
| Repository details | View repository metadata, license, size, and homepage when available |
| Clone repositories | Shallow-clone a selected public repository |
| Gists and activity | Browse public gists and recent public events |
| Reports | Save TXT reports and export structured JSON data |
| Settings | Save an optional GitHub API token and choose a clone directory |
| GUI | Dark Pro interface with animated controls and startup splash |
| Terminal edition | Search and inspect accounts without launching the GUI |

## Screenshots

<div align="center">

| Main window | Repository details |
|---|---|
| <img src="docs/screenshot-main.png" alt="Main window" width="420" /> | <img src="docs/screenshot-details.png" alt="Repository details" width="420" /> |

**Settings**

<img src="docs/screenshot-settings.png" alt="Settings window" width="600" />

</div>

## Requirements

- Kali Linux (recommended) or a compatible Debian-based Linux distribution
- Python 3
- Tkinter for the graphical interface
- Git for cloning repositories
- Internet connection
- A working desktop session for GUI mode
- Pillow is optional; it improves support for some avatar image formats

Install dependencies on Kali Linux:

~~~bash
sudo apt update
sudo apt install -y python3 python3-tk git xdg-utils
~~~

Optional image support:

~~~bash
python3 -m pip install --user Pillow
~~~

## Installation

### 1. Download the project

Clone the repository:

~~~bash
git clone https://github.com/arcticfox-cyber/GitHub-Search.git
~~~

Or download the repository from GitHub and extract it.

### 2. Open the project folder

~~~bash
cd GitHub-Search
~~~

Make sure the folder contains **install.sh**, **arcticfox_gui.py**, **arcticfox_core.py**, **arcticfox-cli.py**, and the **assets/** directory.

### 3. Run the installer

~~~bash
sudo bash install.sh
~~~

The installer will:

- Check whether the operating system is Kali Linux.
- Install required packages when needed.
- Copy the application files and runtime artwork to `/opt/github-search`.
- Create the `af` and `github-search` terminal commands.
- Add **GitHub Search** to the desktop Applications menu.

After installation, start the application:

~~~bash
af
~~~

### Install on another Debian-based distribution

The installer is designed for Kali Linux. To continue on another Debian-based distribution, use the override only if your system is compatible:

~~~bash
sudo bash install.sh --force
~~~

## Run without installing

You can launch the application directly from the extracted project folder. No system-wide installation is required.

Start the GUI:

~~~bash
bash run.sh
~~~

Open the GUI and search for a username:

~~~bash
bash run.sh octocat
~~~

Start terminal mode:

~~~bash
bash run.sh --cli
~~~

You can also run the Python files directly:

~~~bash
python3 arcticfox_gui.py
python3 arcticfox-cli.py
python3 arcticfox-cli.py octocat
~~~

**Important:** The GUI requires a Linux desktop display. On SSH, headless systems, or Termux/NetHunter-rootless, use terminal mode:

~~~bash
python3 arcticfox-cli.py
~~~

## Commands

After installation:

| Command | Action |
|---|---|
| `af` | Start the desktop GUI |
| `github-search` | Start the desktop GUI |
| `af octocat` | Open the GUI and search for a username |
| `af --cli` | Start the terminal edition |
| `af --cli octocat` | Search a username in terminal mode |
| `af --help` | Show help |
| `bash doctor.sh` | Diagnose common setup and launch problems |

Without installation, run commands from the project directory:

| Command | Action |
|---|---|
| `bash run.sh` | Start the GUI |
| `bash run.sh octocat` | Start GUI and search |
| `bash run.sh --cli` | Start terminal mode |
| `python3 arcticfox-cli.py` | Start terminal edition directly |
| `bash doctor.sh` | Run diagnostics |

## Uninstallation

To remove GitHub Search after installing it, open a terminal in the project folder and run:

~~~bash
sudo bash install.sh --uninstall
~~~

The uninstaller removes:

- `/opt/github-search` — installed application files
- `/usr/local/bin/af` — application launcher
- `/usr/local/bin/github-search` — command symlink
- The desktop Applications menu entry
- The installed application icon

**Your personal data is kept.** The uninstaller intentionally does not delete:

- `~/.config/github-search/` — saved settings and optional GitHub token
- `~/github-search-reports/` — exported reports
- Your cloned repositories, normally stored in `~/github/`

If you also want to erase your personal settings and exported reports, remove them manually after uninstalling:

~~~bash
rm -rf ~/.config/github-search
rm -rf ~/github-search-reports
~~~

Only run those two commands if you are sure you no longer need the saved configuration and reports. They do not remove your cloned repositories.

## Using the GUI

1. Choose **Username**, **Full Name**, or **Email** search mode.
2. Enter a search term and press Enter or click **SEARCH**.
3. Review the profile card, account details, and statistics.
4. Open the **Repositories**, **Gists**, or **Activity** tabs.
5. Select a repository to inspect its details, clone it, or open it on GitHub.
6. Use **Save Report** to create a TXT report or **Export Data** to save JSON.
7. Open **Settings** to configure an optional token or change the clone directory.

## Optional GitHub API token

GitHub Search can access public GitHub information without a token, but unauthenticated requests have a lower rate limit. Adding a personal access token can increase the available API request limit.

1. Open [GitHub token settings](https://github.com/settings/tokens).
2. Generate a token suitable for reading public information.
3. Open **Settings** in GitHub Search.
4. Paste the token and save it.

The application stores configuration at:

`~/.config/github-search/config.json`

The configuration file is saved with owner-only permissions where supported. **Never share your token, include it in screenshots, or commit it to GitHub.** A token is optional; do not grant permissions the application does not need.

## Data locations

| Data | Default location |
|---|---|
| Installed application | `/opt/github-search` |
| Settings and token | `~/.config/github-search/config.json` |
| Exported reports | `~/github-search-reports/` |
| Cloned repositories | `~/github/` |

## Project structure

~~~text
GitHub-Search/
├── README.md
├── LICENSE
├── install.sh
├── run.sh
├── remote-install.sh
├── doctor.sh
├── arcticfox_gui.py
├── arcticfox-cli.py
├── arcticfox_core.py
├── assets/
│   ├── arcticfox-icon.png
│   ├── moonlit-fox-splash.png
│   ├── moonlit-fox-splash.gif
│   ├── icon-v1.png
│   └── logo-v1.png
└── docs/
    ├── screenshot-main.png
    ├── screenshot-details.png
    └── screenshot-settings.png
~~~

## Troubleshooting

### GUI does not open

Install Python and Tkinter, then run the diagnostic script:

~~~bash
sudo apt update
sudo apt install -y python3 python3-tk
bash doctor.sh
~~~

You can also start the GUI directly to see any Python error:

~~~bash
python3 arcticfox_gui.py
~~~

### Tkinter is missing

~~~bash
sudo apt install -y python3-tk
~~~

### No display detected

The GUI needs a desktop session. If you are connected through SSH or using a headless environment, use:

~~~bash
python3 arcticfox-cli.py
~~~

### Git is missing

~~~bash
sudo apt install -y git
~~~

### Startup splash is missing

Check that this file exists in the project folder:

~~~text
assets/moonlit-fox-splash.png
~~~

If the application is installed, reinstall it from the project folder to copy the current assets:

~~~bash
sudo bash install.sh
~~~

### GitHub API rate limit reached

Wait for the limit to reset or add an optional token in **Settings**. Do not post your token in a public issue or screenshot.

### Launcher command not found

Open a new terminal and check that `/usr/local/bin` is in your PATH. You can also launch without installing:

~~~bash
bash run.sh
~~~

## Security and responsible use

GitHub Search uses the official GitHub REST API to retrieve information GitHub makes publicly available. It does not bypass private repository permissions. Respect GitHub's Terms of Service, API limits, and user privacy. Keep API tokens private and use the application responsibly.

## Version history

### v1.0

- GitHub Dark Pro interface redesign.
- Animated header, tab underline, search-mode control, and button hover effects.
- In-window 3-second startup splash with progress animation.
- Circular profile avatars and updated application artwork.
- GUI and terminal editions.
- GitHub user search, profile inspection, repository browsing, and cloning.
- Public gists and recent activity.
- TXT report saving and JSON export.
- Optional API token and configurable clone directory.
- Kali Linux installer, quick launcher, and diagnostic script.

## License

**GitHub Search is proprietary software.** All rights are reserved by the copyright holder. Viewing the source and personal evaluation are permitted. Copying, modifying, redistributing, sublicensing, or creating derivative works requires prior written permission.

See [LICENSE](LICENSE). This project is **not** distributed under the MIT License.

## Support

If you find a bug, open an [issue](https://github.com/arcticfox-cyber/GitHub-Search/issues). Include your Linux distribution, Python version, command used, and relevant error output. Remove tokens and other private information before sharing logs.

---

<div align="center">

**🦊 GITHUB SEARCH**

*Explore · Discover · Inspect*

Developed by [@arcticfox-cyber](https://github.com/arcticfox-cyber)

**Happy Searching.**

</div>
