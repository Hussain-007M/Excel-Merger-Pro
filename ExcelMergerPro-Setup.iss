#define MyAppName "Excel Merger Pro"
#ifndef MyAppVersion
  #define MyAppVersion "3.4.0-beta.2"
#endif
#define MyAppExeName "ExcelMergerPro-Release.exe"

[Setup]
AppId={{A66AB126-B570-4239-BBDF-E729E8B1F3B2}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher=Excel Merger Pro
DefaultDirName={localappdata}\Programs\ExcelMergerPro
DefaultGroupName={#MyAppName}
PrivilegesRequired=lowest
OutputDir=installer_output
OutputBaseFilename=ExcelMergerPro-Setup-{#MyAppVersion}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
SetupIconFile=ExcelMergerPro.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
ArchitecturesAllowed=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked

[Files]
Source: "dist\ExcelMergerPro-Release\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent
