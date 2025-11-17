<div align="center">

<h1>Warrior Rimer</h1>

<p>A lightweight top-down pixel shooting / survival game written in Python. Focused on simplicity, extensibility and learning value.</p>

<p>
  <img src="https://img.shields.io/badge/status-alpha-orange" alt="status" />
  <img src="https://img.shields.io/badge/python-3.7%2B-blue" alt="python" />
  <img src="https://img.shields.io/badge/license-MIT-green" alt="license" />
  <img src="https://img.shields.io/badge/platform-Windows-green" alt="platform" />
</p>

</div>

> Language: English | [中文说明](./README.md)

## 📌 Overview
Warrior Rimer is a local single-player shooter built with Python (likely using libraries listed in `requirements.txt`). You control a warrior moving around the map, firing weapons, switching gear, triggering buffs and unlocking achievements. The codebase aims to be readable and easy to extend.

Great for:
- Beginners learning a simple game loop & data persistence
- Developers wanting to add new levels, weapons, enemy logic
- Demonstrating packaging (PyInstaller + optional Inno Setup)

## ✨ Features
- Weapon switching (numeric keys 1 / 2 / 3)
- Movement & shooting (WASD + Space)
- Attack speed boost / buff (F key)
- Pause (M key)
- Achievement & statistics tracking: `achievement_data.json`, `game_data.json`
- One-click portable & installer build
- Clean separation between data files and logic

## 🧱 Tech / Dependencies
- Python 3.7+ (recommend 3.8–3.11 stable)
- Third-party packages: see `requirements.txt`
- Packaging: PyInstaller (`Warrior_Rimer.spec`)
- Installer: Inno Setup (`Warrior_Rimer.iss`, optional)

## 📂 Directory Structure (excerpt)
```
Warrior_RimerV1.0/
├─ start_game.py              # Game entry point (recommended for source run)
├─ main_game.py               # Main game loop / logic
├─ game_utils.py              # Shared utilities
├─ achievement_system.py      # Achievement system implementation
├─ achievement_data.json      # Achievement definitions / states
├─ game_data.json             # Current runtime game data
├─ game_data.clean.json       # Clean initial template
├─ pack.bat                   # One-click build script
├─ Warrior_Rimer.spec         # PyInstaller spec
├─ Warrior_Rimer.iss          # Inno Setup script
├─ music/                     # Audio assets (ensure wav files exist)
├─ Output/                    # Installer output
└─ build/                     # Temporary build artifacts
```

## 🚀 Quick Start
Clone (GitHub):
```bash
git clone https://github.com/m0n3rt/Warrior-RimerV1.0.git
cd Warrior-RimerV1.0
```
Install dependencies:
```bash
pip install -r requirements.txt
```
Run:
```bash
python start_game.py
```

## 🛠 Build & Distribution
Prerequisites:
- Windows
- Dependencies installed: `pip install -r requirements.txt`
- PyInstaller: `pip install pyinstaller`
- Optional: Inno Setup (add `iscc` to PATH)

One-click (PowerShell):
```powershell
cd "$PSScriptRoot"
./pack.bat
```
Script actions:
1. Reset `game_data.json` using `game_data.clean.json`
2. Clean old `build/` & `dist/`
3. Generate portable build via `Warrior_Rimer.spec` -> `dist/WarriorRimer/`
4. If `iscc` detected, compile installer `Warrior_Rimer.iss` -> `Output/Warrior_Rimer_Setup.exe`

Artifacts:
- Portable exe: `dist/WarriorRimer/WarriorRimer.exe`
- Installer: `Output/Warrior_Rimer_Setup.exe`

## ⬇️ Downloads & Updates
- Stable releases (recommended): check GitHub Releases tagged with `v*`
  - https://github.com/m0n3rt/Warrior-RimerV1.0/releases
- Nightly (pre-release): every push to `main` auto-updates a `nightly` pre-release with a portable zip and exe for quick testing.

## 🎮 Controls
| Action | Key |
|--------|-----|
| Move | W / A / S / D |
| Shoot | Space |
| Switch Weapons | 1 / 2 / 3 |
| Attack Speed Boost | F |
| Pause | M |

## 🏆 Achievement & Data System
Files:
- `achievement_data.json`: unlocked achievements and states
- `game_data.json`: current progress, score, attributes
- `game_data.clean.json`: initial clean template used when resetting or packaging

Recommendations:
- When adding new achievements, maintain field consistency and extend logic in `achievement_system.py`.
- Consider adding a version field for future migration.

## ❓ FAQ
1. No sound? Ensure `.wav` files exist in `music/` and are included in build.
2. Missing DLL on start? Install Visual C++ runtime or build with a Python version matching target machine.
3. Inno Setup skipped? Add install path to PATH or run `iscc Warrior_Rimer.iss` manually.
4. Modify initial save? Edit `game_data.clean.json` then run packaging script again.

## 🤝 Contributing
1. Fork & create branch: `feat/<feature-name>`
2. Write comments & minimal docs for new logic
3. Self-test (start game, switch weapons, pause)
4. Open Pull Request explaining motivation

Potential enhancements:
- Add unit tests (e.g. `pytest`)
- Code style tools (`ruff`, `flake8`)

## 🗺 Roadmap
- [ ] New enemy AI behavior patterns
- [ ] Difficulty progression system
- [ ] More weapons & status effects
- [ ] Save encryption / checksum
- [ ] Simple config file (resolution, volume)
- [ ] Multi-language (zh/en)

## 📄 License
This project is licensed under the MIT License. See the `LICENSE` file in the repository root. You are free to use, modify, distribute, and commercially utilize the code as long as the copyright notice and license text are retained.

## 🙏 Acknowledgements
- Python & related library maintainers
- Community tutorials & examples

## 🖼 Screenshots / Preview
(Placeholder – add gameplay, menu, achievement UI screenshots)
```
![Main Screen](docs/images/screenshot_main.png)
![Battle](docs/images/screenshot_battle.png)
```

## 🔖 Badge Ideas
- Build status (Gitee CI / GitHub Actions)
- Version tag
- Downloads (if releasing builds)

## 🧪 Testing (Planned)
Add:
- Function tests for core utilities (`game_utils.py`)
- Achievement edge cases (locked/unlocked transitions)

Basic test skeleton already exists in `tests/` using built-in `unittest`.
Run tests:
```bash
python -m unittest discover -s tests -p "test_*.py"
```

CI (GitHub Actions example) performs:
1. Dependency install
2. Unit tests
3. Optional PyInstaller build & artifact upload

You may replicate similar workflow on Gitee pipelines.

See `CHANGELOG.md` for release notes.

## 📬 Contact
Please open an Issue for bugs/features or reach out via profile email.

---
If this project helps you, please Star ⭐, Fork, and share with friends learning Python game development!

> Tip: Once license & screenshots are finalized, this README will be more complete.
