@echo off
for /f "tokens=1,2" %%u in ('date /t') do set d=%%v
for /f "tokens=1" %%u in ('time /t') do set t=%%u
if "%t:~1,1%"==":" set t=0%t%
set datestr=%d:~6,4%%d:~3,2%%d:~0,2%
set timestr=%t:~0,2%%t:~3,2%
set foldername=%datestr%-%timestr%

echo Cleansing log, input and output directories...

CALL %~dp0cleanse.bat

echo Moving input CSV files to read directories...
IF NOT EXIST %~dp0..\..\Data\Input\BLUE2SFDC_Organizations_%datestr%.csv GOTO ERROR_FNF_END
IF NOT EXIST %~dp0..\..\Data\Input\BLUE2SFDC_Users_%datestr%.csv GOTO ERROR_FNF_END
IF NOT EXIST %~dp0..\..\Data\Input\BLUE2SFDC_Projects_%datestr%.csv GOTO ERROR_FNF_END
IF NOT EXIST %~dp0..\..\Data\Input\BLUE2SFDC_Projectbudgetlines_%datestr%.csv GOTO ERROR_FNF_END
IF NOT EXIST %~dp0..\..\Data\Input\BLUE2SFDC_Donations_%datestr%.csv GOTO ERROR_FNF_END
IF NOT EXIST %~dp0..\..\Data\Input\BLUE2SFDC_Tasks_%datestr%.csv GOTO ERROR_FNF_END
IF NOT EXIST %~dp0..\..\Data\Input\BLUE2SFDC_Taskmembers_%datestr%.csv GOTO ERROR_FNF_END
move /Y %~dp0..\..\Data\Input\BLUE2SFDC_Organizations_%datestr%.csv %~dp0upsert_Organizations\read\upsert_Organizations.csv
move /Y %~dp0..\..\Data\Input\BLUE2SFDC_Users_%datestr%.csv %~dp0upsert_Users\read\upsert_Users.csv
move /Y %~dp0..\..\Data\Input\BLUE2SFDC_Projects_%datestr%.csv %~dp0upsert_Projects\read\upsert_Projects.csv
move /Y %~dp0..\..\Data\Input\BLUE2SFDC_Projectbudgetlines_%datestr%.csv %~dp0upsert_Projectbudgetlines\read\upsert_Projectbudgetlines.csv
move /Y %~dp0..\..\Data\Input\BLUE2SFDC_Donations_%datestr%.csv %~dp0upsert_Donations\read\upsert_Donations.csv
move /Y %~dp0..\..\Data\Input\BLUE2SFDC_Tasks_%datestr%.csv %~dp0upsert_Tasks\read\upsert_Tasks.csv
move /Y %~dp0..\..\Data\Input\BLUE2SFDC_Taskmembers_%datestr%.csv %~dp0upsert_Taskmembers\read\upsert_Taskmembers.csv

echo Now uploading input data to Salesforce...
choice /T 3 /D y > nul
echo Processing Organizations...
CALL %~dp0upsert_Organizations\upsert_Organizations.bat

choice /T 3 /D y > nul
echo Processing Users...
CALL %~dp0upsert_Users\upsert_Users.bat

choice /T 3 /D y > nul
echo Processing Projects...
CALL %~dp0upsert_Projects\upsert_Projects.bat

choice /T 3 /D y > nul
echo Processing Projectbudgetlines...
CALL %~dp0upsert_Projectbudgetlines\upsert_Projectbudgetlines.bat

choice /T 3 /D y > nul
echo Processing Donations...
CALL %~dp0upsert_Donations\upsert_Donations.bat

choice /T 3 /D y > nul
echo Processing Tasks...
CALL %~dp0upsert_Tasks\upsert_Tasks.bat

choice /T 3 /D y > nul
echo Processing Taskmembers...
CALL %~dp0upsert_Taskmembers\upsert_Taskmembers.bat

choice /T 3 /D y > nul


echo Archiving logs and input/ouput...
:MAKE_LOG
%~dp0..\..\Bin\7Z\7z.exe a -tzip -ssw %~dp0archive\%foldername%-BLUE2SFDC_upsert_Organizations.zip %~dp0upsert_Organizations\read %~dp0upsert_Organizations\log %~dp0upsert_Organizations\write
%~dp0..\..\Bin\7Z\7z.exe a -tzip -ssw %~dp0archive\%foldername%-BLUE2SFDC_upsert_Users.zip %~dp0upsert_Users\read %~dp0upsert_Users\log %~dp0upsert_Users\write
%~dp0..\..\Bin\7Z\7z.exe a -tzip -ssw %~dp0archive\%foldername%-BLUE2SFDC_upsert_Projects.zip %~dp0upsert_Projects\read %~dp0upsert_Projects\log %~dp0upsert_Projects\write
%~dp0..\..\Bin\7Z\7z.exe a -tzip -ssw %~dp0archive\%foldername%-BLUE2SFDC_upsert_Projectbudgetlines.zip %~dp0upsert_Projectbudgetlines\read %~dp0upsert_Projectbudgetlines\log %~dp0upsert_Projectbudgetlines\write
%~dp0..\..\Bin\7Z\7z.exe a -tzip -ssw %~dp0archive\%foldername%-BLUE2SFDC_upsert_Donations.zip %~dp0upsert_Donations\read %~dp0upsert_Donations\log %~dp0upsert_Donations\write
%~dp0..\..\Bin\7Z\7z.exe a -tzip -ssw %~dp0archive\%foldername%-BLUE2SFDC_upsert_Tasks.zip %~dp0upsert_Tasks\read %~dp0upsert_Tasks\log %~dp0upsert_Tasks\write
%~dp0..\..\Bin\7Z\7z.exe a -tzip -ssw %~dp0archive\%foldername%-BLUE2SFDC_upsert_Taskmembers.zip %~dp0upsert_Taskmembers\read %~dp0upsert_Taskmembers\log %~dp0upsert_Taskmembers\write


cd %~dp0
echo Finished successfully!
GOTO PROCESS_END

:ERROR_FNF_END
echo An error occurred during execution: a required input file was not found...

:PROCESS_END

REM Exiting...