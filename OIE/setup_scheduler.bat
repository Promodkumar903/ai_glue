@echo off
REM Setup Windows Task Scheduler for OIE Daily Run
REM Run this file AS ADMINISTRATOR (right-click → Run as administrator)

echo ============================================
echo Setting up OIE Scheduled Tasks
echo ============================================

REM Delete existing tasks (if any)
schtasks /Delete /TN "AI_Glue_OIE_Daily" /F 2>nul
schtasks /Delete /TN "AI_Glue_OIE_Studies" /F 2>nul
schtasks /Delete /TN "AI_Glue_OIE_Agents" /F 2>nul

echo.
echo [1/3] Jobs task — Daily 6:00 AM
schtasks /Create /TN "AI_Glue_OIE_Daily" /TR "C:\Users\Administrator\ai_glue\OIE\run_jobs.bat" /SC DAILY /ST 06:00 /F

echo.
echo [2/3] Studies task — Daily 6:30 AM
schtasks /Create /TN "AI_Glue_OIE_Studies" /TR "C:\Users\Administrator\ai_glue\OIE\run_studies.bat" /SC DAILY /ST 06:30 /F

echo.
echo [3/3] Agents task — Weekly Sunday 7:00 AM
schtasks /Create /TN "AI_Glue_OIE_Agents" /TR "C:\Users\Administrator\ai_glue\OIE\run_agents.bat" /SC WEEKLY /D SUN /ST 07:00 /F

echo.
echo ============================================
echo SETUP COMPLETE
echo ============================================
echo.
echo Tasks scheduled:
echo   - AI_Glue_OIE_Daily      (Daily 6:00 AM)
echo   - AI_Glue_OIE_Studies    (Daily 6:30 AM)
echo   - AI_Glue_OIE_Agents     (Weekly Sunday 7:00 AM)
echo.
echo Verify with: schtasks /Query /TN "AI_Glue_OIE_Daily"
echo.
pause