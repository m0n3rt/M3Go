@echo off
setlocal enableextensions
set "ROOT=%~dp0"

echo [1/4] Resetting save data to defaults...
if exist "%ROOT%game_data.clean.json" (
	copy /Y "%ROOT%game_data.clean.json" "%ROOT%game_data.json" >nul
) else (
	echo {"high_score":0,"history":[],"saved_game":null} > "%ROOT%game_data.json"
)

echo [2/4] Cleaning previous build artifacts...
if exist "%ROOT%build" rmdir /s /q "%ROOT%build"
if exist "%ROOT%dist" rmdir /s /q "%ROOT%dist"
if not exist "%ROOT%Output" mkdir "%ROOT%Output" >nul 2>&1

echo [3/4] Building game with PyInstaller...
pyinstaller "%ROOT%Warrior_Rimer.spec"
if errorlevel 1 (
	echo PyInstaller build failed. Aborting.
	exit /b 1
)

echo [4/4] Building installer with Inno Setup (if available)...
where iscc >nul 2>&1
if %errorlevel%==0 (
	iscc "%ROOT%Warrior_Rimer.iss"
) else (
	echo Inno Setup compiler (iscc) not found in PATH. Skipping installer step.
	echo Portable build is ready at "%ROOT%dist\WarriorRimer".
)

echo Done.
exit /b 0