@echo off
REM SnapFlow - Push to GitHub Script
REM 
REM Before running this script:
REM 1. Create a GitHub repository at: https://github.com/new
REM 2. Name it: snapflow
REM 3. Get your repository URL (it will look like: https://github.com/YOUR_USERNAME/snapflow.git)
REM 4. Edit this file and replace YOUR_USERNAME with your actual GitHub username

echo.
echo ========================================
echo SnapFlow - GitHub Push Setup
echo ========================================
echo.

REM Replace YOUR_USERNAME with your actual GitHub username
set GITHUB_USERNAME=YOUR_USERNAME
set REPO_NAME=snapflow

echo Current directory: %CD%
echo.

REM Check if git is installed
where git >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Git is not installed or not in PATH
    echo Please install Git from: https://git-scm.com/download/win
    pause
    exit /b 1
)

echo Git found!
echo.

REM Initialize git repository if not already initialized
if not exist ".git" (
    echo Initializing Git repository...
    git init
    echo.
) else (
    echo Git repository already initialized.
    echo.
)

REM Add all files
echo Adding files to git...
git add .
echo.

REM Commit
echo Committing files...
git commit -m "Initial commit: SnapFlow v1.0.0 - Lightning-fast database snapshot manager"
echo.

REM Rename branch to main
echo Renaming branch to main...
git branch -M main
echo.

REM Add remote
echo Adding GitHub remote...
git remote remove origin 2>nul
git remote add origin https://github.com/%GITHUB_USERNAME%/%REPO_NAME%.git
echo.

echo ========================================
echo Ready to push!
echo ========================================
echo.
echo Repository URL: https://github.com/%GITHUB_USERNAME%/%REPO_NAME%.git
echo.
echo IMPORTANT: Make sure you:
echo 1. Created the repository on GitHub
echo 2. Replaced YOUR_USERNAME in this script with your actual username
echo.
echo Press any key to push to GitHub...
pause >nul

echo.
echo Pushing to GitHub...
git push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo SUCCESS! Project pushed to GitHub!
    echo ========================================
    echo.
    echo Your repository: https://github.com/%GITHUB_USERNAME%/%REPO_NAME%
    echo.
) else (
    echo.
    echo ========================================
    echo ERROR: Push failed
    echo ========================================
    echo.
    echo Possible reasons:
    echo 1. Repository not created on GitHub
    echo 2. Wrong username in script
    echo 3. Authentication required
    echo 4. No internet connection
    echo.
    echo If you need to authenticate:
    echo - GitHub will prompt for your credentials
    echo - You may need a Personal Access Token instead of password
    echo - Create token at: https://github.com/settings/tokens
    echo.
)

pause
