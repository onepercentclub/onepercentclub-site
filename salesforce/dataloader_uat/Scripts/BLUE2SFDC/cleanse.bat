@echo off
del /Q %~dp0upsert_Organizations\read\*.csv 2>NUL
del /Q %~dp0upsert_Organizations\log\*.csv 2>NUL
del /Q %~dp0upsert_Organizations\write\*.csv 2>NUL
copy /Y nul %~dp0upsert_Organizations\log\sdl.log 2>NUL
del /Q %~dp0upsert_Users\read\*.csv 2>NUL
del /Q %~dp0upsert_Users\log\*.csv 2>NUL
del /Q %~dp0upsert_Users\write\*.csv 2>NUL
copy /Y nul %~dp0upsert_Users\log\sdl.log 2>NUL
del /Q %~dp0upsert_Projects\read\*.csv 2>NUL
del /Q %~dp0upsert_Projects\log\*.csv 2>NUL
del /Q %~dp0upsert_Projects\write\*.csv 2>NUL
copy /Y nul %~dp0upsert_Projects\log\sdl.log 2>NUL
del /Q %~dp0upsert_Projectbudgetlines\read\*.csv 2>NUL
del /Q %~dp0upsert_Projectbudgetlines\log\*.csv 2>NUL
del /Q %~dp0upsert_Projectbudgetlines\write\*.csv 2>NUL
copy /Y nul %~dp0upsert_Projectbudgetlines\log\sdl.log 2>NUL
del /Q %~dp0upsert_Donations\read\*.csv 2>NUL
del /Q %~dp0upsert_Donations\log\*.csv 2>NUL
del /Q %~dp0upsert_Donations\write\*.csv 2>NUL
copy /Y nul %~dp0upsert_Donations\log\sdl.log 2>NUL
del /Q %~dp0upsert_Tasks\read\*.csv 2>NUL
del /Q %~dp0upsert_Tasks\log\*.csv 2>NUL
del /Q %~dp0upsert_Tasks\write\*.csv 2>NUL
copy /Y nul %~dp0upsert_Tasks\log\sdl.log 2>NUL
del /Q %~dp0upsert_Taskmembers\read\*.csv 2>NUL
del /Q %~dp0upsert_Taskmembers\log\*.csv 2>NUL
del /Q %~dp0upsert_Taskmembers\write\*.csv 2>NUL
copy /Y nul %~dp0upsert_Taskmembers\log\sdl.log 2>NUL