:: This batch script is intended to facilitate the installation of the perquisites required to run CPD
:: by Julien SATTI @ LIF

:: Check environment for Python and pip
python --version 2>NUL
pip --version 2>NUL
if errorlevel 1 goto errorNoPython

:: Reaching here means Python and pip are installed and therefore can proceed with the installation of libraries
goto librariesInstall

:: Install Python if not detected
:errorNoPython
:: Try native install for Windows (experimental)
python3.exe
if errorlevel 0
    goto librariesInstall
else
:: Open Python website if experimental install failed
    echo Python is not installed on your system.
    echo Now opening the download URL.
    start "" "https://www.python.org/downloads/windows/"

:: Set Python version found and install libraries
:librariesInstall
for /f "delims=" %%V in ('python -V') do @set ver=%%V
echo Congrats, %ver% is installed...

:: Install pywin32
pip install pywin32

:: Install aead
pip install aead

:: End
goto:eof