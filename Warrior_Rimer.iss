[Setup]
AppId={{E0B3A5A1-3B7C-4A9D-8F1E-0F8D9C7A3B2D}}
AppName=Warrior Rimer
AppVersion=1.0
;AppVerName=Warrior Rimer 1.0
AppPublisher=Your Game Studio
DefaultDirName={autopf}\Warrior Rimer
DisableProgramGroupPage=yes
;PrivilegesRequired=lowest
OutputBaseFilename=WarriorRimer_Setup
OutputDir=Output
Compression=lzma
SolidCompression=yes
WizardStyle=modern
SetupIconFile=warrior_rimer.ico

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\WarriorRimer\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\Warrior Rimer"; Filename: "{app}\WarriorRimer.exe"
Name: "{autodesktop}\Warrior Rimer"; Filename: "{app}\WarriorRimer.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\WarriorRimer.exe"; Description: "{cm:LaunchProgram,Warrior Rimer}"; Flags: nowait postinstall skipifsilent