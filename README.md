# MCQ Screen Assistant

A fast, minimal, AI-powered desktop application for solving multiple-choice questions from any part of your screen.

**❌ NO API KEY NEEDED!** Runs completely free using Ollama (local AI).

## Features

- **Global Hotkey**: Press `Ctrl+Shift+X` anywhere to activate
- **Region Selection**: Click and drag to select any MCQ on screen
- **OCR Processing**: Extracts text using Tesseract with preprocessing
- **Local AI-Powered**: Uses Ollama (free, open-source models)
- **Clean UI**: Modern, semi-transparent popup with fade animations
- **Fast**: Optimized for <3 second response time
- **Background Operation**: No visible window, runs silently
- **100% Free**: No API costs, no subscriptions

## Quick Start

### 1. Prerequisites

- **Python 3.8+** - [Download Python](https://www.python.org/downloads/)
- **Tesseract OCR** - Required for text extraction
- **Ollama** - Free local AI (no API key needed!)

### 2. Install Ollama (Local AI) - 3 Minutes ⚡

**✅ STEP 1: Download Ollama**
1. Go to: https://ollama.ai
2. Download for your OS (Windows/Mac/Linux)
3. Install it

**✅ STEP 2: Start Ollama**
- Windows: Click the Ollama icon (runs in background)
- It starts on `http://localhost:11434`

**✅ STEP 3: Pull a Model (one-time download)**
Open Command Prompt and run:
```cmd
ollama pull mistral
```
(First time: ~2-3 minutes. After that: instant)

**Done!** Ollama is now ready. It will stay running in the background.

### 3. Install Tesseract OCR - 5 Minutes ⚡

1. Go to: https://github.com/UB-Mannheim/tesseract/wiki
2. Download: `tesseract-ocr-w64-setup-5.3.3.20231005.exe` (or latest version)
3. Run and install to: `C:\Program Files\Tesseract-OCR\` (default)
4. Verify (open Command Prompt):
   ```cmd
   "C:\Program Files\Tesseract-OCR\tesseract.exe" --version
   ```

### 4. Install Python Dependencies

Navigate to the project folder in Command Prompt and run:

```cmd
pip install -r requirements.txt
```

### 5. Run the Application

```cmd
python main.py
```

Or use the batch script:
```cmd
run.bat
```

**You're done! No API key needed!** 🎉

## Usage

| Action | Hotkey |
|--------|--------|
| **Activate Selection** | `Ctrl+Shift+X` |
| **Exit App** | `Ctrl+Shift+Q` |
| **Cancel Selection** | `Esc` |

**Workflow:**
1. Press `Ctrl+Shift+X`
2. Click and drag to select an MCQ on screen
3. A popup appears with the answer in ~2 seconds
4. Popup auto-dismisses after 3 seconds
5. Press `Ctrl+Shift+X` again to select another MCQ

## Available Models

In `main.py`, change `OLLAMA_MODEL` to:

| Model | Speed | Accuracy | Memory | Recommended |
|-------|-------|----------|--------|-------------|
| `mistral` | ⚡ Fast | 🟩 Good | 4GB | ✅ YES |
| `llama2` | ⚡ Fast | 🟩 Good | 4GB | ✅ YES |
| `neural-chat` | ⚡ Fast | 🟩 Good | 4GB | ✅ YES |
| `orca-mini` | ⚡ Very Fast | 🟨 Fair | 2GB | For weak PCs |
| `mistral-large` | 🐢 Slow | 🟩🟩 Better | 8GB | Better accuracy |

To use a different model:
```cmd
ollama pull llama2
```

Then in `main.py`:
```python
class Config:
    OLLAMA_MODEL = "llama2"
```

## Building Standalone Executable

### Step 1: Install PyInstaller

```cmd
pip install pyinstaller
```

### Step 2: Build Using the Script

```cmd
build.bat
```

Or manually:
```cmd
pyinstaller --onefile --noconsole --name MCQAssistant main.py
```

The executable will be at: `dist/MCQAssistant.exe`

### Step 3: Run on Any Computer

Just make sure:
1. ✅ Ollama is installed and running
2. ✅ Tesseract is installed
3. ✅ Model is pulled (`ollama pull mistral`)

Then run `MCQAssistant.exe` - no installation needed!

## Configuration

Edit `main.py`:

```python
class Config:
    HOTKEY = "ctrl+shift+x"           # Activation hotkey
    EXIT_HOTKEY = "ctrl+shift+q"      # Exit hotkey
    POPUP_DURATION_MS = 3000          # Popup shows for 3 seconds
    OLLAMA_URL = "http://localhost:11434"  # Ollama server
    OLLAMA_MODEL = "mistral"          # Model to use
    TESSERACT_PATH = None             # Auto-detect (or set custom)
```

## Troubleshooting

### ❌ "Cannot connect to Ollama"
- Make sure Ollama is installed and running
- Run in Command Prompt: `ollama serve` (if it stops)
- Or click the Ollama icon in system tray

### ❌ "Model not found"
- Pull the model: `ollama pull mistral`
- Check available models: `ollama list`

### ❌ "Tesseract not found"
- Ensure installed in `C:\Program Files\Tesseract-OCR\`
- Or set `Config.TESSERACT_PATH` in `main.py`

### ❌ "Hotkey not working"
- Run Command Prompt as **Administrator**
- Check for conflicts with other apps

### ❌ "OCR extracts wrong text"
- Select a cleaner, higher-contrast region
- Try selecting a slightly larger area
- Ensure text is not rotated >15°

### ⚠️ "Slow response time"
- First request: 5-10 seconds (model loading)
- Subsequent: 1-3 seconds (normal)
- Using slow model? Try `orca-mini` or `neural-chat`

## Performance Tips

1. **First Run**: Ollama loads the model into VRAM (~2-5 seconds)
2. **Subsequent Runs**: Fast (~1-2 seconds) until you close the app
3. **Keep Ollama Running**: Leave it open for best performance
4. **Use Mistral**: Fastest model with good accuracy

## Project Structure

```
mcq_assistant/
├── main.py              # Entry point & config
├── screen_capture.py    # Region selection
├── ocr_processor.py     # Text extraction (Tesseract)
├── ai_handler.py        # Ollama API calls
├── ui_overlay.py        # UI & animations
├── config.py            # Configuration options
├── requirements.txt     # Python dependencies
├── MCQAssistant.spec    # PyInstaller config
├── run.bat              # Quick run script
├── build.bat            # Build executable script
└── README.md            # This file
```

## Comparison: Claude vs Ollama

| Feature | Claude API | Ollama Local |
|---------|-----------|--------------|
| **Cost** | $0.003/1K request | FREE |
| **Speed** | ~2-3 seconds | 1-3 seconds |
| **Privacy** | Cloud (not private) | Local (100% private) |
| **Accuracy** | Excellent | Very good |
| **Setup** | Need API key | Just download |
| **Internet Required** | YES | NO |
| **Best For** | Production apps | Personal use |

## License

MIT License - Use freely!

## Credits

- **OCR**: [Tesseract](https://github.com/tesseract-ocr/tesseract)
- **AI**: [Ollama](https://ollama.ai)
- **Screen Capture**: [python-mss](https://github.com/BoboTiG/python-mss)
- **UI**: [PyQt5](https://www.riverbankcomputing.com/software/pyqt/)

---

**Enjoy solving MCQs faster!** 🚀
