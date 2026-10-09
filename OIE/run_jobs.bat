@echo off
REM OIE JOBS — Daily job crawl
cd /d C:\Users\Administrator\ai_glue
call venv\Scripts\activate.bat

echo ============================================
echo OIE JOBS — %date% %time%
echo ============================================

echo [1/4] Fetching new jobs...
python OIE\oie_new_only.py

echo [2/4] Deduplicating...
python OIE\oie_dedup_title.py

echo [3/4] Categorizing...
python OIE\oie_categories.py

echo [4/4] Verification...
python OIE\oie_verification.py

echo ============================================
echo JOBS DONE — %date% %time%
echo ============================================