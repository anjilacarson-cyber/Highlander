# Gemini Desktop Operator

A Windows desktop application that uses each user's own Gemini API key to generate code, preview desktop screenshots on request, and type reviewed code visibly into the currently focused application.

## Included in this first distributable release

- Windows GUI built with Tkinter.
- Gemini text generation using Google's `google-genai` SDK (default model: `gemini-3.8-flash`).
- Per-user API key storage through the Windows Credential Manager using `keyring`.
- Adjustable visible typing speed: 1–10 characters per second.
- Start/stop typing controls and a 5-second focus countdown.
- PyAutoGUI emergency failsafe (move pointer to the top-left corner).
- Workspace folder creation/opening and target-file creation/opening.
- Confirmed mouse movement to screen coordinates and confirmed left/right clicks.
- Optional screenshot capture and explicit user-approved screenshot submission to Gemini for UI analysis.
- PyInstaller and Inno Setup packaging.
- GitHub Actions workflow to build the Windows installer and publish tagged releases.

## Requirements for developers/builders

- Windows 10/11 x64
- Python 3.11 recommended
- Inno Setup 6 for local installer creation
- A Gemini API key from Google AI Studio

## Run from source

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python src\main.py
```

## Build a Windows installer locally

1. Install Inno Setup 6: https://jrsoftware.org/isinfo.php
2. Run `build_windows.bat`.
3. Open `installer/GeminiDesktopOperator.iss` in Inno Setup Compiler and compile it.
4. The installer output is created in the `release` directory.

## Publish a public download link using GitHub Releases

This repository includes `.github/workflows/release-windows.yml`.

1. Create a new public repository on GitHub named `Gemini-Desktop-Operator`.
2. Upload/push the contents of this project folder to the repository.
3. In GitHub, open **Actions** and enable workflows if prompted.
4. Create and push a version tag:

```bash
git tag v1.0.0
git push origin v1.0.0
```

5. GitHub Actions builds the Windows installer and attaches it to a public Release.
6. Share the repository's Releases page:
   `https://github.com/YOUR-USERNAME/Gemini-Desktop-Operator/releases`

Replace `YOUR-USERNAME` with the actual GitHub account name. This URL becomes a public download page after the release is published.

## End-user installation

1. Download `Gemini_Desktop_Operator_Setup.exe` from the GitHub Releases page.
2. Run the installer and follow the wizard.
3. Launch Gemini Desktop Operator from the desktop shortcut.
4. Get a personal API key at https://aistudio.google.com/app/apikey.
5. Paste the key into the app and optionally choose **Save key securely**.
6. Enter a coding task, generate code, review it, open the target file in VS Code, click the insertion point, and choose **Type visibly**.

## Important limitations and safety

- This is a first distributable release, not a fully autonomous general-purpose computer-use agent. Gemini can analyze an explicitly submitted screenshot, but it does not independently plan and execute arbitrary sequences of mouse/keyboard actions. Mouse movement and clicks are manually specified and confirmed.
- It types into the currently focused application only. The user must open the intended target file and place the cursor.
- The typing speed is an approximate character rate; keyboard layout, punctuation, and non-ASCII characters can affect timing. Test with a disposable file before using it on important work.
- Generated code is shown for review and is never automatically executed.
- Screenshot analysis is opt-in and sends the captured image to Google's Gemini API. Do not submit screenshots containing secrets, private messages, or sensitive data.
- API key storage relies on the operating system credential backend. Users should protect their Windows account.
- The application has not been code-signed. Windows SmartScreen may show an unknown-publisher warning until the publisher obtains and applies a code-signing certificate.
- Do not use the application to misrepresent automated activity as human work or to bypass an app's recording, platform, or workplace rules.

## License

MIT License. Add a LICENSE file with the license terms before public distribution if you intend to publish this as open-source software.
