; Inno Setup script for Scores (Windows).
;
; Per-user install (no administrator rights) into %LocalAppData%, so the in-app
; updater can download and run a new installer without elevation - the same
; per-user model WeatherFast uses and QuickMail gets from Velopack.
;
; The version is passed by the CI build with /DMyAppVersion=x.y.z; it defaults to
; 0.0.0 for local test compiles.
;
; Build locally (after `python build.py` at the repo root):
;   "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" /DMyAppVersion=0.8.0 installer\scores.iss

#ifndef MyAppVersion
  #define MyAppVersion "0.0.0"
#endif
#define MyAppName "Scores"
#define MyAppPublisher "Kelly Ford"
#define MyAppExeName "Scores.exe"
#define MyAppURL "https://github.com/kellylford/Scores"

[Setup]
; Stable AppId so upgrades replace the prior install (never change this GUID).
AppId={{4B0F6C2E-9D71-4A18-8E52-2C6B7A5F1D93}
; The running app holds this named mutex (see hold_app_mutex in
; services/updater.py); it lets Setup detect a running copy and wait for it to
; close before replacing the executable an in-app update is trying to update.
AppMutex=ScoresRunning
CloseApplications=yes
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
DefaultDirName={localappdata}\Programs\Scores
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir=Output
OutputBaseFilename=Scores-{#MyAppVersion}-Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\{#MyAppExeName}
VersionInfoVersion={#MyAppVersion}
VersionInfoProductName={#MyAppName}
LicenseFile=..\LICENSE

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional icons:"; Flags: unchecked

[Files]
; The PyInstaller one-dir build output (produced by build.py at the repo root):
; the executable plus its _internal support folder. One-dir, not one-file - see
; the note in build.py for why the installer must not package a one-file build.
Source: "..\dist\Scores\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autostartmenu}\Scores"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\Scores"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch Scores"; Flags: nowait postinstall skipifsilent

[Code]
// Force-close any Scores process still holding the installed executable.
// (Comments here use // rather than braces: Inno's brace comments do not nest,
// so an {app}-style constant inside one would terminate it early.)
//
// AppMutex and CloseApplications are not sufficient when the running copy is a
// one-file build - which every install upgrading from a pre-installer release
// is. Those run a bootloader parent plus a Python child, and only the child
// creates ScoresRunning, so once it exits the mutex is gone even though the
// parent may still be alive holding Scores.exe open on the bootloader's "Failed
// to remove temporary directory" dialog. Restart Manager cannot shift that
// either: a process whose message loop has already ended does not act on the
// WM_CLOSE that CloseApplications sends. Without this, setup fails with
// "DeleteFile failed; code 5. Access is denied."
//
// Killing it is safe here: in that state the application has finished its work
// and is only displaying a shutdown warning. A genuinely running instance is
// still caught earlier by AppMutex, which prompts the user first.
function PrepareToInstall(var NeedsRestart: Boolean): String;
var
  ResultCode: Integer;
begin
  Result := '';  // never block the install - a lock still surfaces as a file error
  Exec(ExpandConstant('{sys}\taskkill.exe'), '/F /IM Scores.exe', '',
       SW_HIDE, ewWaitUntilTerminated, ResultCode);
  // 128 = "no such process", the normal case. Give Windows a moment either way
  // so the handle is released before the file copy starts.
  Sleep(500);
end;
