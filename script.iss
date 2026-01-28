[Setup]
AppName=APZ-Tool
AppVersion=1.0
DefaultDirName={pf}\APZ-Tool
DefaultGroupName=APZ-Tool
UninstallDisplayIcon={app}\APZ-Tool.exe
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
OutputDir=.
OutputBaseFilename=APZ-Tool-Setup

[Files]
Source: "H:\Code\APZ_Tool\dist\APZ-Tool.exe"; DestDir: "{app}"

[Icons]
Name: "{group}\APZ-Tool"; Filename: "{app}\APZ-Tool.exe"
Name: "{commondesktop}\APZ-Tool"; Filename: "{app}\APZ-Tool.exe"; Tasks: desktopicon

[Tasks]
Name: desktopicon; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"

[Run]
Filename: "{app}\APZ-Tool.exe"; Description: "Launch APZ-Tool"; Flags: nowait postinstall skipifsilents