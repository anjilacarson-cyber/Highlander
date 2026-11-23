#define MyAppName "Gemini Desktop Operator"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Gemini Desktop Operator"
#define MyAppExeName "GeminiDesktopOperator.exe"

[Setup]
AppId={{B6E3D6C9-17D4-4C20-9F34-21A6E43D1A20}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\Gemini Desktop Operator
DefaultGroupName={#MyAppName}
OutputDir=..\release
OutputBaseFilename=Gemini_Desktop_Operator_Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=lowest
UninstallDisplayIcon={app}\{#MyAppExeName}

[Files]
Source: "..\dist\GeminiDesktopOperator.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch Gemini Desktop Operator"; Flags: postinstall nowait skipifsilent
