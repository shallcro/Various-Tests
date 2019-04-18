@ECHO OFF

:_START
CLS
TYPE C:\BDPL\scripts\bdpl.txt
ECHO.
ECHO.
ECHO.

setlocal EnableDelayedExpansion
IF NOT EXIST Z: (
  REM Get username
  SET /P _name="Enter your IU username: "
 
  REM get server
  REM SET /P _server=<C:\BDPL\resources\server.txt

  REM Connect to shared drive
  NET USE Z: \\156.56.241.173\bdpl /user:ads\!_name! *
)

IF NOT EXIST Z: (
  PAUSE
  GOTO _START
) ELSE (
  CLS
)


TYPE C:\BDPL\scripts\bdpl.txt
python C:\BDPL\scripts\python3\bdpl_ingest_20190329.pyw




