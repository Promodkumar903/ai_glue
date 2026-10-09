@echo off
REM OIE AGENTS — Registry + verification
cd /d C:\Users\Administrator\ai_glue
call venv\Scripts\activate.bat

echo ============================================
echo OIE AGENTS — %date% %time%
echo ============================================

echo [1/3] Refreshing registry...
python OIE\oie_registry.py

echo [2/3] Verifying entities...
python OIE\verify_all.py

echo [3/3] Matching engine test...
python OIE\oie_requests.py

echo ============================================
echo AGENTS DONE — %date% %time%
echo ============================================