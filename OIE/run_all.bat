@echo off
REM OIE MASTER — All verticals
cd /d C:\Users\Administrator\ai_glue

echo ============================================
echo OIE MASTER RUN — %date% %time%
echo ============================================

echo.
echo ### RUNNING JOBS ###
call OIE\run_jobs.bat

echo.
echo ### RUNNING STUDIES ###
call OIE\run_studies.bat

echo.
echo ### RUNNING AGENTS ###
call OIE\run_agents.bat

echo.
echo ============================================
echo OIE ALL DONE — %date% %time%
echo ============================================