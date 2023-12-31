@echo off
setlocal

REM - This batch file will package (build, cook, and stage) your Unreal Engine project.

set PROJECT_NAME=%1
set PROJECT_PATH=%2
set BuildLocation=%3
set UNREAL_PATH=%~f4

REM - Set MAPS to the list of maps you want to cook, for example "MainMenuMap+FirstLevel+SecondLevel+TestMap" (DO NOT PUT SPACES ANYWHERE HERE!!!)
set MAPS=%5

if exist "%PROJECT_PATH%\%PROJECT_NAME%\%PROJECT_NAME%.uproject" goto Continue

echo.
echo Warning - %PROJECT_PATH%\%PROJECT_NAME%\%PROJECT_NAME%.uproject does not exist!
echo (edit this batch file in a text editor and set PROJECT_NAME to the name of your project)
echo.

pause

goto Exit

:Continue

if exist BUILD_EDITOR_FAILED.txt del BUILD_EDITOR_FAILED.txt
if exist BUILD_GAME_FAILED.txt del BUILD_GAME_FAILED.txt
if exist PACKAGING_FAILED.txt del PACKAGING_FAILED.txt

if NOT "%MAPS%"=="" (goto CheckInstalledBuild)

echo.
echo Warning - You don't have MAPS set, this will cause ALL content to be cooked!
echo (potentially making your packaged build larger than it needs to be)
echo.

:CheckInstalledBuild

REM - We need to check if this is an "Installed Build" (i.e. installed from the Epic Launcher) or a source code build (from GitHub).
if exist "%UNREAL_PATH%\Engine\Build\InstalledBuild.txt" (
    set INSTALLED=-installed
) else (
    set INSTALLED=
)

REM - Check if a .sln file exists for the project, if so, then it is a C++ project and you can build the game editor (otherwise it's a Blueprint project).
if exist "%PROJECT_PATH%\%PROJECT_NAME%\%PROJECT_NAME%.sln" (
    echo.
    echo %date% %time% Building Game Editor...
    echo.

    call "%UNREAL_PATH%\Engine\Build\BatchFiles\RunUAT.bat" BuildEditor -Project="%PROJECT_PATH%\%PROJECT_NAME%\%PROJECT_NAME%.uproject" -notools > %BuildLocation%/EditorBuildLog.txt
    if errorlevel 1 goto Error_BuildEditorFailed

    echo.
    echo %date% %time% Building Game...
    echo.

    call "%UNREAL_PATH%\Engine\Build\BatchFiles\RunUAT.bat" BuildGame -project="%PROJECT_PATH%\%PROJECT_NAME%\%PROJECT_NAME%.uproject" -platform=Win64 -notools -configuration=Shipping > %BuildLocation%/GameBuildLog.txt
    if errorlevel 1 goto Error_BuildGameFailed
)

echo %date% %time% Packaging the game...

REM - Note: "-clean" will clean and rebuild your game code (for C++ projects) and will clean the project's Saved\Cooked and Saved\StagedBuilds for every time this runs
REM - Note: If you don't wish to fully rebuild your game code each time you package, you can add "-nocompile" to skip compiling game code.
REM - Note: "-pak" will store all cooked content into a .pak file (using the UnrealPak tool).  Packaged games can (optionally) use encrypted .pak file for better security.
REM - Note: When you are ready to ship your game, change -configuration to just "-configuration=Shipping" (to prevent including Development and DebugGame executables in your shipped build).
REM - Note: When you are ready to ship your game, add "-nodebuginfo" to prevent the .pdb file from being added to the game's Binaries/Win64 folder.
REM - Note: Using "-createreleaseversion" allows you to create Patches and DLC later for your game if you wish.
REM - Note: You can use "-compressed" if you want to compress packages (this will make files smaller, but may take longer to load in game).

call "%UNREAL_PATH%\Engine\Build\BatchFiles\RunUAT.bat" BuildCookRun -project="%PROJECT_PATH%\%PROJECT_NAME%\%PROJECT_NAME%.uproject" %INSTALLED% -platform=Win64 -configuration=Shipping -map=%MAPS% -nocompileeditor -nodebuginfo -unattended -utf8output -clean -build -cook -stage -pak -prereqs -package -archive -archivedirectory="%BuildLocation%" -createreleaseversion=1.0 > %BuildLocation%/PackageBuildLog.txt
if errorlevel 1 goto Error_PackagingFailed

echo.
echo %date% %time% Done!

goto Exit


:Error_BuildEditorFailed
echo.
echo %date% %time% Error - Build Editor failed!
type NUL > BUILD_EDITOR_FAILED.txt
goto Exit

:Error_BuildGameFailed
echo.
echo %date% %time% Error - Build Game failed!
type NUL > BUILD_GAME_FAILED.txt
goto Exit

:Error_PackagingFailed
echo.
echo %date% %time% Error - Packaging failed!
type NUL > PACKAGING_FAILED.txt
goto Exit


:Exit
