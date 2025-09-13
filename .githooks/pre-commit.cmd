@echo off
setlocal ENABLEDELAYEDEXPANSION

for /f "delims=" %%F in ('git diff --cached --name-only') do (
  set "f=%%F"
  REM الگوهای ممنوع
  echo !f! | findstr /R /C:"^DataBase/" >nul && goto :blocked
  echo !f! | findstr /R /C:".*\.mdf$" >nul && goto :blocked
  echo !f! | findstr /R /C:".*\.ldf$" >nul && goto :blocked
  echo !f! | findstr /R /C:".*\.sqlite[0-9]*$" >nul && goto :blocked
  echo !f! | findstr /R /C:".*\.bak$" >nul && goto :blocked
  echo !f! | findstr /R /C:".*\.log$" >nul && goto :blocked
)
exit /b 0

:blocked
echo ✖ Commit blocked: %%F matches a forbidden pattern
echo → Remove from index:  git rm --cached "%%F"
exit /b 1
