# Highlander – Windows Desktop Assistant

**Highlander** is a Windows desktop application powered by Google's Gemini AI. It uses each user's own Gemini API key to generate code, preview desktop screenshots on request, and type reviewed code visibly into the currently focused application.

## Included in This Release

- Windows desktop GUI built with Tkinter.
- Gemini AI text generation using Google's `google-genai` SDK.
- Per-user API key storage through Windows Credential Manager using `keyring`.
- Adjustable visible typing speed: 1–10 characters per second.
- Start and stop typing controls with a 5-second focus countdown.
- PyAutoGUI emergency failsafe (move the pointer to the top-left corner).
- Workspace folder creation and opening.
- Target-file creation and opening.
- Confirmed mouse movement to screen coordinates.
- Confirmed left-click and right-click controls.
- Optional screenshot capture and user-approved screenshot submission to Gemini for UI analysis.
- PyInstaller packaging.
- Inno Setup installer creation.
- GitHub Actions workflow for building Windows installers and publishing tagged releases.

## Requirements

- Windows 10 or Windows 11 (64-bit).
- Python 3.11 recommended.
- Inno Setup 6 for local installer creation.
- A personal Gemini API key from Google AI Studio.

## Run Highlander From Source

Open PowerShell in the project directory and run:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python src\main.py
```

## Build the Windows Installer Locally

1. Install Inno Setup 6: https://jrsoftware.org/isinfo.php
2. Run `build_windows.bat`.
3. Open `installer/Highlander.iss` in Inno Setup Compiler.
4. Compile the installer.
5. The installer output will be created in the `release` directory.

The intended installer filename is:

`Highlander_Setup.exe`

## Publish Highlander on GitHub

The project includes a GitHub Actions workflow located at:

`.github/workflows/release-windows.yml`

To publish a public Windows download:

1. Push the project files to the public GitHub repository:

   https://github.com/anjilacarson-cyber/Highlander

2. Open the repository's **Actions** tab and enable workflows if prompted.
3. Create and push a version tag:

```bash
git tag v1.0.0
git push origin v1.0.0
```

4. GitHub Actions should build the Windows installer.
5. Once the workflow succeeds, GitHub will publish the installer as a release asset.

### Public Download Page

https://github.com/anjilacarson-cyber/Highlander/releases

This will be the public page where users can find and download Highlander releases.

## End-User Installation Guide

1. Visit the Highlander Releases page.
2. Download `Highlander_Setup.exe`.
3. Run the installer and follow the installation wizard.
4. Launch Highlander using the desktop shortcut.
5. Obtain a personal Gemini API key from https://aistudio.google.com/app/apikey.
6. Enter the API key into Highlander.
7. Optionally select **Save key securely**.
8. Enter a coding task and generate code.
9. Review the generated code.
10. Open the intended target file in VS Code.
11. Click the insertion point and select **Type visibly**.

Each user must provide their own Gemini API key.

## Important Limitations and Safety

- Highlander is an initial desktop coding assistant, not a fully autonomous general-purpose computer-use agent.
- Gemini can analyze screenshots that the user explicitly submits, but it does not independently plan and execute arbitrary sequences of mouse and keyboard actions.
- Mouse movements and clicks are manually specified and confirmed.
- Highlander types into the currently focused application. The user must open the intended file and position the cursor.
- Typing speed is approximate. Keyboard layout, punctuation and non-ASCII characters can affect timing.
- Test with a disposable file before using Highlander on important work.
- Generated code is displayed for review and is never automatically executed.
- Screenshot analysis is optional and sends the captured image to Google's Gemini API. Avoid submitting screenshots containing passwords, private messages or sensitive information.
- API key storage relies on the operating system's credential backend. Users should protect their Windows accounts.
- The application is not code-signed. Windows SmartScreen may display an unknown-publisher warning until a code-signing certificate is obtained and applied.
- Do not use Highlander to misrepresent automated activity as human work or bypass application, workplace or platform rules.

## License

MIT License.

See the `LICENSE` file for the license terms.
