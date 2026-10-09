@echo off
REM OIE Daily Auto-Run Script
cd /d C:\Users\Administrator\ai_glue
call venv\Scripts\activate.bat

echo ============================================
echo OIE DAILY RUN — %date% %time%
echo ============================================

echo.
echo [1/3] Fetching new jobs...
python OIE\oie_new_only.py

echo.
echo [2/3] Deduplicating...
python OIE\oie_dedup_title.py

echo.
echo [3/3] Updating categories...
python OIE\oie_categories.py

echo.
echo ============================================
echo DONE — %date% %time%
echo ============================================