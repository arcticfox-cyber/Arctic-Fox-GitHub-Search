 <div align="center">

# 🔴 ARCTIC FOX

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=800&size=27&pause=1000&color=FF3333&center=true&vCenter=true&width=650&lines=ARCTIC+FOX;GITHUB+SEARCH+TOOL;EXPLORE+GITHUB+PROFILES;DISCOVER+PUBLIC+REPOSITORIES" alt="Arctic Fox Animated Heading" />

### GitHub Account & Repository Inspector

<p>
  <img src="https://img.shields.io/badge/VERSION-3.0-red?style=for-the-badge" />
  <img src="https://img.shields.io/badge/PLATFORM-KALI%20LINUX-blue?style=for-the-badge&logo=kalilinux" />
  <img src="https://img.shields.io/badge/BUILT%20WITH-PYTHON-yellow?style=for-the-badge&logo=python" />
</p>

<p>
  <a href="https://github.com/arcticfox-cyber/Arctic-Fox-GitHub-Search-v3.0">
    <img src="https://img.shields.io/badge/GitHub-Repository-black?style=for-the-badge&logo=github" />
  </a>
</p>

**Explore. Discover. Inspect.**

A powerful terminal-based GitHub account and repository inspection tool.

</div>

---

## 📖 About Arctic Fox

**Arctic Fox GitHub Search v3.0** is a Python-based command-line tool designed to explore GitHub accounts and inspect publicly available repository information.

With a simple command, you can search any GitHub username, view profile information, discover public repositories, inspect repository statistics, clone repositories, explore public Gists and generate detailed text reports.

Arctic Fox uses the official GitHub REST API to retrieve publicly available information.

Designed for Kali Linux, Linux users, developers and cybersecurity enthusiasts.

## 🖥️ GUI Edition Guide

Want to use the graphical interface instead of the terminal version?

- **[Open the GUI README](README-GUI.md)** — setup, launch instructions, installation, troubleshooting and GUI-specific fixes.
- **[View the GUI README on GitHub](https://github.com/arcticfox-cyber/Arctic-Fox-GitHub-Search-v3.0/blob/main/README-GUI.md)**

The main README below continues to document the terminal edition. The separate GUI guide is attached here so both guides are easy to find from the repository's main page.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔍 Username Search | Search GitHub accounts by username |
| 👤 Profile Inspector | View public profile information |
| 📦 Repository Explorer | List public repositories |
| ⭐ Star Statistics | Display repository stars |
| 🍴 Fork Statistics | Display repository forks |
| 💻 Language Detection | Show repository programming languages |
| 🏷️ Topics | Display repository topics |
| 📥 Repository Cloning | Clone repositories using Git |
| 🌐 Browser Support | Open profiles and repositories |
| 📝 Report Generator | Generate detailed text reports |
| 📚 Gist Explorer | Display public Gists |
| 🏢 Organization Explorer | Display associated organizations |
| ⚙️ Settings | Configure API token and clone directory |
| 🎨 Animated Interface | Colored terminal interface and loading animations |

## 🖥️ How It Works

<div align="center">

<img src="https://img.shields.io/badge/01-ENTER%20GITHUB%20USERNAME-red?style=for-the-badge" />

<br>⬇️<br>

<img src="https://img.shields.io/badge/02-CONNECT%20TO%20GITHUB%20API-black?style=for-the-badge" />

<br>⬇️<br>

<img src="https://img.shields.io/badge/03-FETCH%20PUBLIC%20INFORMATION-blue?style=for-the-badge" />

<br>⬇️<br>

<img src="https://img.shields.io/badge/04-EXPLORE%20REPOSITORIES-purple?style=for-the-badge" />

<br>⬇️<br>

<img src="https://img.shields.io/badge/05-CLONE%20%2F%20SAVE%20REPORT-green?style=for-the-badge" />

</div>

1. Launch Arctic Fox using `af`.
2. Enter the GitHub username.
3. The tool requests publicly available information from GitHub.
4. Profile information and repositories are displayed.
5. Select a repository to clone, inspect or open in a browser.
6. Save a report containing the collected information.

## ⚙️ Requirements

Before installing Arctic Fox, make sure you have:

- Kali Linux or another Linux distribution.
- Python 3.
- Git.
- Internet connection.

Install the required packages:

```bash
sudo apt update
sudo apt install python3 git -y
```

**Note:** The provided Python script uses standard Python libraries. No additional Python packages are required.

## 📥 Installation

### Step 1 — Clone the Repository

```bash
git clone https://github.com/arcticfox-cyber/Arctic-Fox-GitHub-Search-v3.0.git
```

### Step 2 — Enter the Project Directory

```bash
cd Arctic-Fox-GitHub-Search-v3.0
```

### Step 3 — Install Requirements

```bash
sudo apt update
sudo apt install python3 git -y
```

### Step 4 — Give Execution Permission

```bash
chmod +x arcticfox.py
```

### Step 5 — Install Arctic Fox System-Wide

```bash
sudo install -m 755 arcticfox.py /usr/local/bin/arcticfox
```

### Step 6 — Create the `af` Command

```bash
sudo ln -sf /usr/local/bin/arcticfox /usr/local/bin/af
```

### Step 7 — Launch Arctic Fox

```bash
af
```

<details>
<summary><b>⚡ Quick Installation (All Commands Together)</b></summary>

```bash
git clone https://github.com/arcticfox-cyber/Arctic-Fox-GitHub-Search-v3.0.git

cd Arctic-Fox-GitHub-Search-v3.0

sudo apt update

sudo apt install python3 git -y

chmod +x arcticfox.py

sudo install -m 755 arcticfox.py /usr/local/bin/arcticfox

sudo ln -sf /usr/local/bin/arcticfox /usr/local/bin/af

af
```

</details>

## 🚀 Usage

### 1. Start Arctic Fox

```bash
af
```

Enter the GitHub username when prompted.

```text
username > arcticfox-cyber
```

### 2. Direct Username Search

You can search directly without opening the interactive username prompt.

```bash
af arcticfox-cyber
```

### 3. Search Any GitHub Account

```bash
af octocat
```

Replace `octocat` with the username you want to inspect.

### 4. Open Settings

Inside the main interface, enter:

```text
s
```

### 5. Exit Arctic Fox

```text
q
```

## 📊 Profile Information

Arctic Fox displays publicly available GitHub profile information, including:

- Username
- Full name
- Account type
- Bio
- Company
- Location
- Website or blog
- Twitter username
- Public email, if available
- Account creation date
- Last profile update
- Public repository count
- Public Gist count
- Followers
- Following
- GitHub profile URL
- Associated organizations

## 📦 Repository Explorer

Arctic Fox lists public repositories belonging to the searched account.

Repository information includes:

- Repository name
- Full repository name
- Stars
- Forks
- Primary programming language
- Last updated date
- Description
- Topics
- Fork status
- Archived status

The current script retrieves a maximum of 600 repositories.

### Repository Actions

After selecting a repository, the following menu appears:

```text
[1] Clone
[2] Details
[3] Browser
[0] Back
```

**[1] Clone**

Clone the selected repository using Git.

**[2] Details**

Display detailed repository information:

- Full name
- Stars
- Forks
- Watchers
- Language
- License
- Creation date
- Last push date
- Repository size
- Topics
- Homepage
- Description

**[3] Browser**

Open the selected repository on GitHub.

## 📝 Report Generator

Arctic Fox includes a report generation feature.

Save the collected information by entering:

```text
s
```

The generated report includes:

- GitHub profile information
- Repository information
- Stars and forks
- Programming languages
- Repository descriptions
- Repository topics
- Public Gists
- Recent public activity

Reports are automatically saved inside:

```text
~/arctic-fox-reports/
```

Example report:

```text
arctic-fox-reports/
│
└── octocat-20261102-163000.txt
```

## 🔑 GitHub API Token (Optional)

Arctic Fox works without a GitHub API token.

However, configuring a token can increase your available GitHub API rate limit.

### Generate a GitHub Token

Visit:

https://github.com/settings/tokens

Generate a token with the appropriate public repository access scope if using a classic token.

### Configure Your Token

Start Arctic Fox:

```bash
af
```

Open settings:

```text
s
```

Select:

```text
[1] Token set/clear
```

Paste your GitHub token and save it.

### Configuration Location

```text
~/.config/arctic-fox/config.json
```

The configuration file is saved with restricted permissions (`600`).

**Security:** Never share your personal GitHub API token with anyone.

## ⚙️ Settings Menu

Arctic Fox provides the following settings:

```text
[1] Token set/clear
[2] Clone dir
[0] Back
```

**Token set/clear:** Configure or remove your GitHub API token.

**Clone dir:** Change the directory where repositories will be cloned.

## 📂 Project Structure

```text
Arctic-Fox-GitHub-Search-v3.0/
│
├── arcticfox.py
│
└── README.md
```

Additional configuration and report directories are created in your home directory.

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python 3 | Main programming language |
| GitHub REST API | GitHub account and repository information |
| Git | Repository cloning |
| JSON | API responses and configuration |
| ANSI Escape Codes | Terminal colors and animation |
| Linux | Operating environment |

## ⚠️ Important Notes

- An active internet connection is required.
- GitHub API rate limits may apply.
- A GitHub token is optional.
- Only publicly available GitHub information is retrieved by the normal profile and repository features.
- Private repository contents are not accessed.
- Git must be installed for cloning repositories.
- The `xdg-open` or `termux-open-url` command is needed for supported browser opening.
- The repository listing is limited to 600 repositories.
- Reports are stored locally on your system.

## 🛡️ Responsible Use

Arctic Fox is intended for educational purposes, GitHub profile exploration and public repository inspection.

Always respect GitHub's Terms of Service, API usage limits and user privacy.

Use this tool responsibly and only for legitimate purposes.

## 🤝 Contributing

Contributions and improvements are welcome!

1. Fork this repository.
2. Create a new branch.
3. Make your changes.
4. Test your code.
5. Submit a Pull Request.

## 🐛 Bug Reports

Found a bug or have an idea for improvement?

Open an issue in the GitHub repository:

https://github.com/arcticfox-cyber/Arctic-Fox-GitHub-Search-v3.0/issues

## ⭐ Support the Project

If you like Arctic Fox, please consider giving the repository a ⭐ Star.

Your support motivates further development and improvements.

---

<div align="center">

# 🔴 ARCTIC FOX 🦊

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=700&size=20&pause=1000&color=FF3333&center=true&vCenter=true&width=500&lines=EXPLORE+GITHUB;DISCOVER+REPOSITORIES;STAY+FROSTY" alt="Arctic Fox Footer Animation" />

**Developed by [@arcticfox-cyber](https://github.com/arcticfox-cyber)**

[![GitHub](https://img.shields.io/badge/GitHub-arcticfox--cyber-black?style=for-the-badge&logo=github)](https://github.com/arcticfox-cyber)

**Explore. Discover. Inspect.**

*Stay Frosty. Stay Curious.*

</div>
