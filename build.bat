for %%f in (%cd%) do set addon=%%~nxf
TITLE Building %addon%

python build.py

python list_channels.py

pause