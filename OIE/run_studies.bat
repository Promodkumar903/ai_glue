@echo off
REM OIE STUDIES — Universities + Scholarships + Hostels
cd /d C:\Users\Administrator\ai_glue
call venv\Scripts\activate.bat

echo ============================================
echo OIE STUDIES — %date% %time%
echo ============================================

echo [1/5] Universities refresh...
python OIE\oie_study_universities.py

echo [2/5] More countries...
python OIE\oie_study_more_unis.py

echo [3/5] Scholarships...
python OIE\oie_study_scholarships.py

echo [4/5] Hostels...
python OIE\oie_study_hostels.py

echo [5/5] Country policies...
python OIE\oie_study_free_edu.py

echo ============================================
echo STUDIES DONE — %date% %time%
echo ============================================