<div align="center">

# 🦊 ARCTIC FOX — GITHUB SEARCH

### Explore GitHub. Discover developers. Inspect public repositories.

<p>
  <img src="https://img.shields.io/badge/VERSION-5.0.3-8296FF?style=for-the-badge" alt="Version 5.0.3" />
  <img src="https://img.shields.io/badge/PLATFORM-KALI%20LINUX-6C63FF?style=for-the-badge&logo=kalilinux&logoColor=white" alt="Kali Linux" />
  <img src="https://img.shields.io/badge/PYTHON-3.x-9AB7FF?style=for-the-badge&logo=python&logoColor=white" alt="Python 3" />
  <img src="https://img.shields.io/badge/INTERFACE-GUI-8B7BFF?style=for-the-badge" alt="Graphical interface" />
</p>

**A desktop GUI for searching GitHub users and exploring publicly available profile and repository information.**

[Repository](https://github.com/arcticfox-cyber/Arctic-Fox-GitHub-Search) · [Report a Bug](https://github.com/arcticfox-cyber/Arctic-Fox-GitHub-Search/issues)

</div>

---

## ✨ About

**Arctic Fox GitHub Search** is a Python desktop application for discovering GitHub accounts and inspecting public repository information through a graphical interface.

Search for a GitHub username, review the profile, browse repositories, and open repository pages without having to work entirely from the terminal.

The interface uses a dark midnight palette with moonlit blue and violet accents. On launch, the application displays the included Moonlit Fox splash artwork for approximately **3 seconds**, then opens the main GUI.

> This project is intended for Kali Linux and other Linux desktop environments with Python 3 and Tkinter.

## 🚀 Features

| Feature | Description |
|---|---|
| 🔎 GitHub user search | Search for a public GitHub account by username |
| 👤 Profile information | View available public profile details |
| 🖼️ Profile avatars | Display GitHub profile images when the image format is supported |
| 📦 Repository explorer | Browse public repositories for the searched account |
| ⭐ Repository statistics | Inspect available stars, forks, and language information |
| 🌐 GitHub links | Open profiles and repositories on GitHub |
| 🎨 Dark GUI | Midnight blue, ice-blue, and violet visual theme |
| 🌙 Startup splash | Displays the included Moonlit Fox artwork for around 3 seconds |
| ⚙️ Linux support | Designed for Kali Linux and compatible Linux desktop environments |

*The information shown depends on what GitHub makes publicly available and the API response.*

## 🖥️ Interface

The application opens with the Moonlit Fox splash artwork and then displays the main Arctic Fox GUI.

The splash image is included in the project assets. Keep the `assets` directory alongside the application files when running the tool.

## 📋 Requirements

- Kali Linux or another Linux distribution with a desktop environment
- Python 3
- Tkinter
- Git (if you want to clone repositories)
- Internet connection

Install the system packages on Kali Linux / Debian:

```bash
sudo apt update
sudo apt install python3 python3-tk python3-pip git -y
```

### Optional image support

Pillow improves compatibility when displaying GitHub avatars and scaling the splash artwork:

```bash
python3 -m pip install --user Pillow
```

The application includes fallback handling for environments where Pillow is not installed. Image decoding support can vary with the installed Tk version.

## 📥 Installation

Clone the repository:

```bash
git clone https://github.com/arcticfox-cyber/Arctic-Fox-GitHub-Search.git
cd Arctic-Fox-GitHub-Search
```

From the extracted application folder, install the requirements above and launch using the provided launcher:

```bash
chmod +x run.sh
./run.sh
```

You can also start the GUI directly from its project directory:

```bash
python3 arcticfox_gui.py
```

> If the repository checkout you downloaded does not contain `run.sh` or `arcticfox_gui.py` at its current directory level, first enter the directory containing those files. Keep the application assets folder in the same project directory.

## 🔍 How to Use

1. Start Arctic Fox.
2. Enter the GitHub username you want to search for.
3. Review the profile information and avatar when available.
4. Browse the account's public repositories.
5. Open a profile or repository on GitHub when you need more details.

## 🧰 Troubleshooting

### The GUI does not open

Install Tkinter and try launching from a terminal to see the error:

```bash
sudo apt install python3-tk -y
python3 arcticfox_gui.py
```

### The splash screen is blank

- Make sure the `assets` folder is present beside the application files.
- Confirm that `moonlit-fox-splash.gif` is inside `assets/`.
- Run the application from a terminal and check for Tk image-loading errors.

### GitHub avatar is missing

- Check your internet connection.
- Confirm the GitHub profile has an avatar image available.
- Install Pillow for broader PNG, JPEG, and WebP image decoding:

```bash
python3 -m pip install --user Pillow
```

### Search results are missing or incomplete

- Check your internet connection.
- Verify the GitHub username spelling.
- GitHub API rate limits may affect how much information can be retrieved.
- Some profile or repository information may not be publicly available.

## 🔐 Privacy & Responsible Use

Arctic Fox is designed to inspect publicly available GitHub information. Respect GitHub's Terms of Service, API rate limits, and the privacy of other users.

- Do not use the tool to access information you are not authorized to view.
- Never publish or share personal access tokens.
- Keep any locally stored credentials private.
- Search results are subject to GitHub API availability and rate limits.

## 🛠️ Built With

- **Python 3** — application logic
- **Tkinter** — desktop GUI
- **GitHub REST API** — public GitHub information
- **Pillow (optional)** — broader image decoding and image scaling
- **Git** — repository cloning

## 📌 Version Notes

### v5.0.3

- Improved startup splash handling for Linux/Tk environments.
- Uses a Tk-native GIF splash asset to avoid inconsistent PNG decoding.
- Maps the main window before displaying the splash to avoid a blank startup screen.
- Keeps a visible fallback label if the splash artwork cannot be loaded.
- Retains the moonlit blue/violet visual direction.

## 🐛 Bug Reports & Suggestions

If you encounter a problem or have a suggestion, please open an issue:

[**Arctic Fox GitHub Search — Issues**](https://github.com/arcticfox-cyber/Arctic-Fox-GitHub-Search/issues)

When reporting a bug, include:
- Your Linux distribution and desktop environment
- Python and Tk versions
- The command you used to launch the application
- The terminal error output (remove any private tokens first)

## 📜 License & Project Use

Arctic Fox is a proprietary project. Viewing and personal evaluation are permitted. Copying, modifying, redistributing, or creating derivative versions requires prior written permission from the project owner.

Do not remove project branding or claim the project or its artwork as your own.

---

<div align="center">

## 🦊 ARCTIC FOX

**Explore. Discover. Inspect.**

Developed by [@arcticfox-cyber](https://github.com/arcticfox-cyber)

[![GitHub](https://img.shields.io/badge/GitHub-arcticfox--cyber-111827?style=for-the-badge&logo=github)](https://github.com/arcticfox-cyber)

*Stay Frosty.*

</div>
