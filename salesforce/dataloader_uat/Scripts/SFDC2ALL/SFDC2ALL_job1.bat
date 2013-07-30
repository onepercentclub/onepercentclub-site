@echo off
for /f "tokens=1,2" %%u in ('date /t') do set d=%%v
for /f "tokens=1" %%u in ('time /t') do set t=%%u
if "%t:~1,1%"==":" set t=0%t%
set datestr=%d:~6,4%%d:~3,2%%d:~0,2%
set timestr=%t:~0,2%%t:~3,2%
set foldername=%datestr%-%timestr%

echo Cleansing log, input and output directories...

CALL %~dp0cleanse.bat

echo Now exporting data from Salesforce...
choice /T 3 /D y > nul
echo Processing Organizations...
CALL %~dp0export_Organizations\export_Organizations.bat

choice /T 3 /D y > nul
echo Processing Users...
CALL %~dp0export_Users\export_Users.bat

choice /T 3 /D y > nul
echo Processing Projects...
CALL %~dp0export_Projects\export_Projects.bat

choice /T 3 /D y > nul
echo Processing Projectbudgetlines...
CALL %~dp0export_Projectbudgetlines\export_Projectbudgetlines.bat

choice /T 3 /D y > nul
echo Processing Donations...
CALL %~dp0export_Donations\export_Donations.bat

choice /T 3 /D y > nul
echo Processing Vouchers...
CALL %~dp0export_Vouchers\export_Vouchers.bat

choice /T 3 /D y > nul
echo Processing Tasks...
CALL %~dp0export_Tasks\export_Tasks.bat

choice /T 3 /D y > nul
echo Processing Taskmembers...
CALL %~dp0export_Taskmembers\export_Taskmembers.bat

choice /T 3 /D y > nul

echo Moving output CSV files to output directories...
move /Y "%~dp0export_Organizations\write\export_Organizations.csv" "%~dp0..\..\Data\Output\SFDC2ALL_Organizations_%datestr%.csv"
move /Y "%~dp0export_Users\write\export_Users.csv" "%~dp0..\..\Data\Output\SFDC2ALL_Users_%datestr%.csv"
move /Y "%~dp0export_Projects\write\export_Projects.csv" "%~dp0..\..\Data\Output\SFDC2ALL_Projects_%datestr%.csv"
move /Y "%~dp0export_Projectbudgetlines\write\export_Projectbudgetlines.csv" "%~dp0..\..\Data\Output\SFDC2ALL_Projectbudgetlines_%datestr%.csv"
move /Y "%~dp0export_Donations\write\export_Donations.csv" "%~dp0..\..\Data\Output\SFDC2ALL_Donations_%datestr%.csv"
move /Y "%~dp0export_Vouchers\write\export_Vouchers.csv" "%~dp0..\..\Data\Output\SFDC2ALL_Vouchers_%datestr%.csv"
move /Y "%~dp0export_Tasks\write\export_Tasks.csv" "%~dp0..\..\Data\Output\SFDC2ALL_Tasks_%datestr%.csv"
move /Y "%~dp0export_Taskmembers\write\export_Taskmembers.csv" "%~dp0..\..\Data\Output\SFDC2ALL_Taskmembers_%datestr%.csv"


echo Archiving logs and input/ouput...
:MAKE_LOG
%~dp0..\..\Bin\7Z\7z.exe a -tzip -ssw %~dp0archive\%foldername%-SFDC2ALL_export_Organizations.zip %~dp0export_Organizations\read %~dp0export_Organizations\log %~dp0export_Organizations\write
%~dp0..\..\Bin\7Z\7z.exe a -tzip -ssw %~dp0archive\%foldername%-SFDC2ALL_export_Users.zip %~dp0export_Users\read %~dp0export_Users\log %~dp0export_Users\write
%~dp0..\..\Bin\7Z\7z.exe a -tzip -ssw %~dp0archive\%foldername%-SFDC2ALL_export_Projects.zip %~dp0export_Projects\read %~dp0export_Projects\log %~dp0export_Projects\write
%~dp0..\..\Bin\7Z\7z.exe a -tzip -ssw %~dp0archive\%foldername%-SFDC2ALL_export_Projectbudgetlines.zip %~dp0export_Projectbudgetlines\read %~dp0export_Projectbudgetlines\log %~dp0export_Projectbudgetlines\write
%~dp0..\..\Bin\7Z\7z.exe a -tzip -ssw %~dp0archive\%foldername%-SFDC2ALL_export_Donations.zip %~dp0export_Donations\read %~dp0export_Donations\log %~dp0export_Donations\write
%~dp0..\..\Bin\7Z\7z.exe a -tzip -ssw %~dp0archive\%foldername%-SFDC2ALL_export_Vouchers.zip %~dp0export_Vouchers\read %~dp0export_Vouchers\log %~dp0export_Vouchers\write
%~dp0..\..\Bin\7Z\7z.exe a -tzip -ssw %~dp0archive\%foldername%-SFDC2ALL_export_Tasks.zip %~dp0export_Tasks\read %~dp0export_Tasks\log %~dp0export_Tasks\write
%~dp0..\..\Bin\7Z\7z.exe a -tzip -ssw %~dp0archive\%foldername%-SFDC2ALL_export_Taskmembers.zip %~dp0export_Taskmembers\read %~dp0export_Taskmembers\log %~dp0export_Taskmembers\write


cd %~dp0
echo Finished!
GOTO PROCESS_END

:PROCESS_END

REM Exiting...