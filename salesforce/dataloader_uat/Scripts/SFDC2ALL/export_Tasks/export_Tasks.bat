SET DLPATH="%~dp0..\..\..\Bin\DataLoader20"
SET DLCONF="%~dp0config"
SET DLDATA="%~dp0write"
for %%i in ("%~dp0.") do set CURDIRNAME=%%~nxi
cd %~dp0
call %DLPATH%\_jvm\bin\java.exe -cp %DLPATH%\DataLoader.jar -Xms256m -Xmx512m -Dsalesforce.config.dir=%DLCONF% com.salesforce.dataloader.process.ProcessRunner process.name=%CURDIRNAME%
