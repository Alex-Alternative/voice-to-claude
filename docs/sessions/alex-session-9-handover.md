# Alex Session 9 Handover — 2026-04-11

## Branch
`master` — fully pushed to origin (github.com/Moonhawk80/koda). 0 unpushed commits.

## What Was Built This Session

### 1. Environment Setup on New Machine
- Repo was cloned but venv was missing — created fresh venv and installed all deps
- `python -m venv venv` + `venv/Scripts/pip install -r requirements.txt packaging pywin32`
- `configure.py` has a Unicode banner that fails in cp1252 bash terminals — this is cosmetic only, config.json is already present with correct settings so configure.py does not need to be re-run
- Tests run via: `venv/Scripts/python -m pytest test_features.py` (96 passing)
- `test_stress.py` has a bare `sys.exit(0)` at module level that breaks pytest collection — run standalone only

### 2. Startup Shortcut Installed (`install_startup.bat`)
- `Koda.lnk` now exists at `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\`
- Target: `C:\Users\alexi\Projects\koda\start.bat`, WorkingDir: `C:\Users\alexi\Projects\koda`
- WindowStyle=7 (minimized — no console flash on login)
- Koda will now auto-start on every Windows login

### 3. GPU Detection + Power Mode (`hardware.py` — NEW)
New module handles all GPU detection logic:
- `detect_gpu()` — returns `"cuda_ready"`, `"nvidia_no_cuda"`, or `"none"`
  - Primary check: `ctranslate2.get_supported_compute_types("cuda")` — ground truth
  - Secondary check: `nvidia-smi` — detects GPU hardware even without CUDA runtime
- `try_install_cuda_packages()` — pip installs nvidia-cuda-runtime-cu12, nvidia-cublas-cu12, nvidia-cudnn-cu9, then re-tests
- `get_nvidia_gpu_name()` — returns friendly GPU name string for UI display
- `CUDA_DOWNLOAD_URL = "https://developer.nvidia.com/cuda-downloads"` — stable canonical URL

### 4. Power Mode Installer Step (`configure.py`)
Added `setup_performance()` as Step 1 of 9 (all other steps renumbered from 1-8 to 2-9):

**Bucket A (CUDA ready):** Shows side-by-side Standard vs Power Mode table, recommends Power Mode. User picks. Power Mode sets `large-v3-turbo` + `float16`.

**Bucket B (NVIDIA found, no CUDA):** Offers three choices:
1. Auto-install (~400MB download) — runs `try_install_cuda_packages()`, tests, offers Power Mode if success, shows URL + saves `ENABLE_POWER_MODE.txt` if failure
2. Show me how manually — saves `ENABLE_POWER_MODE.txt`, opens `nvidia.com/cuda-downloads` in browser
3. Skip — Standard Mode

**Bucket C (no GPU):** Completely silent — returns CPU defaults, user never sees a GPU screen.

If Power Mode is selected, `setup_model()` (Step 5) is skipped — model is already determined.

Added `compute_type` to the summary screen display.

### 5. `config.py` — compute_type default
Added `"compute_type": "int8"` to `DEFAULT_CONFIG` so the field always exists even for users who never ran the new installer.

### 6. voice.py — GPU-aware model loading with silent fallback
`load_whisper_model()` now reads `compute_type` from config:
- `float16` → `device="cuda"`
- `int8` → `device="cpu"`

If CUDA load fails at runtime (driver update, device removed, etc.):
- Logs warning, shows tray notification: "GPU unavailable — Koda switched to Standard Mode"
- Automatically retries with `small` / `cpu` / `int8`
- Updates in-memory config to prevent repeated failed GPU attempts
- Never crashes Koda

### 7. settings_gui.py — Performance section
New PERFORMANCE section added before HISTORY:
- Shows current mode: "Power Mode (NVIDIA GPU)" or "Standard Mode (CPU)"
- Status label (green text) shows live detection results
- **Check GPU** button — runs detection, reports what was found
- **Enable Power Mode** button (shown when on Standard) — runs auto-install path, saves config, prompts restart
- **Switch to Standard Mode** button (shown when on Power) — reverts to small/int8
- **Learn more** button — opens `nvidia.com/cuda-downloads` in browser
- Window height increased from 920px to 1020px

## Decisions Made

1. **URL to use for CUDA download:** `https://developer.nvidia.com/cuda-downloads` — hardcoded as a constant in both `hardware.py` and `configure.py`. This page has been stable for years and is NVIDIA's official selector. Never hardcode a versioned URL (e.g., /12.4) as those go stale.

2. **No permission needed from NVIDIA:** Mentioning NVIDIA/CUDA in the installer is nominative fair use — you're describing a technical requirement, not claiming a partnership. Only prohibited: using their logo/visual branding, claiming certification, or using "NVIDIA" in Koda's product name.

3. **ctranslate2 check is ground truth, nvidia-smi is secondary:** `nvidia-smi` detects hardware but doesn't prove CUDA runtime is available. ctranslate2's `get_supported_compute_types("cuda")` is the only reliable signal that GPU inference will actually work. If ctranslate2 says yes, it works. If only nvidia-smi says yes, it's Bucket B.

4. **Power Mode = large-v3-turbo + float16:** These two settings always travel together. Power Mode isn't just about compute_type — a user with GPU should also get a better model. Standard Mode = small + int8. These are the only two valid combinations. Mixed states (small + float16, large-v3-turbo + int8) are avoided.

5. **Automatic CUDA package install via pip:** Rather than always sending users to download a 3GB CUDA Toolkit, we first try `pip install nvidia-cuda-runtime-cu12 nvidia-cublas-cu12 nvidia-cudnn-cu9` (~400MB). This works for users who already have NVIDIA drivers. If it fails, we fall back to the URL + saved instructions file.

6. **ENABLE_POWER_MODE.txt saved to koda folder:** If a user dismisses the URL dialog, the instructions don't disappear. The text file stays in the koda folder as a persistent reminder with exact steps.

7. **Settings GUI doesn't auto-restart on mode switch:** Switching Power/Standard Mode in Settings saves config but requires a manual restart. Consistent with how model_size changes work elsewhere in the GUI.

8. **Bucket C is completely silent:** Users with no NVIDIA GPU never see a GPU screen. No disappointment, no confusion. The installer simply proceeds from the performance step (invisible) to Step 2 (microphone) seamlessly.

9. **GPU fallback in voice.py never crashes Koda:** If CUDA fails at runtime, Koda falls back gracefully to Standard Mode with a tray notification. This handles real scenarios: driver updates, hardware changes, moving the venv to a different machine.

## User Feedback & Corrections

1. **"will it have the URL of where to download whatever is needed on the prompts?"** — Confirmed yes. URLs auto-open in browser (not just displayed as text). Also saved to `ENABLE_POWER_MODE.txt` so they're never lost.

2. **"do we need permission from NVIDIA or whatever to mention them on an install process?"** — No. Nominative fair use. Mentioning NVIDIA/CUDA is standard industry practice (Steam, PyTorch, Blender etc. all do it). Only avoid: their logo, claiming endorsement, using their trademark in product names.

3. **"but make sure it is a user interface... like would you like the basic install or do you want to super power it with xyz"** — Drove the entire UX design: no technical jargon, "Standard Mode" vs "Power Mode" framing, side-by-side comparison table, friendly language throughout.

## Waiting On

1. **Soak test sleep/wake recovery** — the watchdog fix from session 8 has never been validated through a real sleep cycle. Run Koda, sleep the machine, wake it, check `debug.log` for:
   - `"Sleep/wake detected"` 
   - `"Full recovery complete"`
   This is the most important unvalidated fix in the codebase.

2. **Edge cases (Phase 8):**
   - RDP sessions — hotkey service behavior over remote desktop
   - Multi-monitor — overlay position and tray behavior
   - Bluetooth mic hot-swap — does audio stream recover?
   - USB mic disconnect/reconnect — same question

3. **GPU Power Mode real-world test** — Alex's machine has Intel UHD 770 (no NVIDIA), so the Power Mode path can't be tested here. Needs a user with an NVIDIA GPU to validate the full Bucket A and Bucket B flows.

## Next Session Priorities

### Phase 8 — Hardening
1. **Soak test sleep/wake** — launch Koda (`pythonw voice.py`), sleep machine, wake it, check `debug.log`
2. **RDP edge case** — connect via RDP, test hotkeys work through remote session
3. **Mic disconnect** — unplug USB mic while recording, verify graceful recovery

### Phase 7 Remainder
4. **Landing page / screenshots / demo video** — not started, lowest urgency of remaining items

### Backlog
5. Settings GUI dark theme polish
6. Wake word custom "Hey Koda" model (blocked on mic/training data — always was)

## Files Changed This Session

| File | Change |
|---|---|
| `hardware.py` | **NEW** — GPU detection, CUDA package install, GPU name lookup |
| `config.py` | Added `"compute_type": "int8"` to DEFAULT_CONFIG |
| `configure.py` | Added `setup_performance()` as Step 1 of 9, `_save_power_mode_instructions()`, renumbered all steps 1-8 → 2-9, `compute_type` in config dict and summary, added `import webbrowser` |
| `voice.py` | `load_whisper_model()` reads `compute_type`, GPU-aware load, silent CPU fallback with tray notification |
| `settings_gui.py` | Added PERFORMANCE section (Check GPU / Enable Power Mode / Learn more), helper methods `_check_gpu`, `_enable_power_mode`, `_disable_power_mode`, `_open_cuda_url`, window height 920→1020px |

*Note: commits acbf8e3, 4070f42, fb56e9d, ef59655 are session 9 work shipped earlier (repo URL update, sound files, hotkey recovery hardening, Prompt Assist detail extraction) — these were already complete when this session started.*

## Key Reminders

- **Kill ALL python/pythonw before restarting Koda:** `taskkill //f //im pythonw.exe` AND `taskkill //f //im python.exe`
- **Run from source:** `pythonw voice.py` — no installs during dev
- **Tests:** `venv/Scripts/python -m pytest test_features.py` — 96 passing. Do NOT use plain `python -m pytest` (system Python has no pytest)
- **Venv:** `C:\Users\alexi\Projects\koda\venv` — no `venv\Scripts\activate` in bash; use `venv/Scripts/python` and `venv/Scripts/pip` directly
- **configure.py UnicodeEncodeError** — cosmetic issue with box-drawing chars in cp1252 terminal. config.json is already correct, wizard doesn't need to be re-run
- **Hotkey rules:** ONLY `ctrl+alt+letter` or F-keys. No backtick, no Ctrl+Shift+Space, no Ctrl+Shift+P
- **Paste:** `keyboard.send("ctrl+v")` — NOT pyautogui
- **Sound:** `winsound` — NOT sounddevice
- **pyttsx3 COM threading:** init lazily in the thread that uses it, not at startup
- **mic_device = null** — never hardcode device indices
- **No NVIDIA GPU on this machine** — Intel UHD 770 only, Power Mode cannot be tested here
- **GitHub CLI:** `"C:\Program Files\GitHub CLI\gh.exe"`, auth as `Moonhawk80`
- **Repo:** github.com/Moonhawk80/koda (was Alex-Alternative/koda, transferred)
- **DO NOT suggest Product Hunt**
- **DO NOT build/install exe** — user wants to run from source until dev is done

## Migration Status
None — no database changes this session.

## Test Status
- **96 tests passing** (`test_features.py`) — unchanged from session start
- `test_stress.py` has bare `sys.exit(0)` at module level, breaks pytest collection — run standalone only
- No new tests written this session (GPU detection is hard to unit test without real hardware)
- GPU fallback path in voice.py is untested (needs real NVIDIA GPU to validate)

## Current Config State
```json
{
  "model_size": "small",
  "compute_type": "int8",
  "language": "en",
  "hotkey_dictation": "ctrl+space",
  "hotkey_command": "f8",
  "hotkey_prompt": "f9",
  "hotkey_correction": "f7",
  "hotkey_readback": "f6",
  "hotkey_readback_selected": "f5",
  "hotkey_mode": "hold",
  "mic_device": null,
  "sound_effects": true,
  "notifications": false,
  "noise_reduction": false
}
```
