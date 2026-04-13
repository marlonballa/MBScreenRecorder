# 🎥 Screen Recorder

A simple, lightweight screen recorder and screenshot tool built with Python and Tkinter — no subscriptions, no bloat, just works.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey?logo=windows)

---

## Features

- 🎥 Record your screen and save as `.mp4`
- 📷 Take screenshots and save as `.png`
- 🗂️ All files saved automatically to `~/Gravações`
- ⚙️ Configurable FPS (5–30)
- 🖥️ Minimal interface — no distractions

---

## Requirements

- Python 3.8+
- Dependencies listed in `requirements.txt`

> Tkinter is included with Python — no extra install needed.

---

## Installation

```bash
# Clone the repository
git clone https://github.com/marlonballa/screen-recorder.git
cd screen-recorder

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## Usage

```bash
# Make sure venv is active
venv\Scripts\activate

# Run the app
python src/main.py
```

---

## Project Structure

```
screen-recorder/
├── src/
│   ├── core/
│   │   ├── capture.py       # Screenshot logic
│   │   └── recorder.py      # Video recording logic
│   ├── ui/
│   │   └── main_window.py   # Tkinter interface
│   └── main.py              # Entry point
├── assets/                  # Icons and images
├── tests/                   # Unit tests
├── requirements.txt
└── README.md
```

---

## Roadmap

- [x] Project structure & GitHub setup
- [ ] Core capture module (screenshot + recording)
- [ ] Tkinter interface
- [ ] Packaging as `.exe` with PyInstaller
- [ ] Inno Setup installer
- [ ] GitHub Actions CI/CD

---

## Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request.

---

## License

MIT © [marlonballa](https://github.com/marlonballa)
