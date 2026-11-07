@echo off
setlocal
cd /d "%~dp0"
call build_lotto_exe.bat
if errorlevel 1 exit /b 1
call build_launcher_gui_exe.bat
if errorlevel 1 exit /b 1
call build_launcher_projects_exe.bat
if errorlevel 1 exit /b 1
echo Alle drei EXE-Dateien wurden erstellt.
pause
