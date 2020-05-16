# This PowerShell script is intended to facilitate the installation of the perquisites required to run Chromium Password Decrypter
# Author: Julien SATTI @ LIF
# Version-control: https://git.duework.org/julien/cpdecrypt

Write-Host "== CPD Requirements Installation Helper =="
Write-Host "	== by Julien SATTI @ LIF =="

# Fonction main appelant les autres fonction
function Main {
    # Check environment for Python 3.8.3
    $p = &{python -V} 2>&1
    $version = if($p -is [System.Management.Automation.ErrorRecord]) {
        # Python isn't installed
        Write-Host "`nPython 3.8.3 was not found on your system:"
        Install-Python383
        Main
    }  else {
        Write-Host "`n$p was found on your system:"
        # A version of Python is installed
        # Check if this version is Python 3.8.3
        if($p -eq "Python 3.8.3") {
	    Write-Host " -"$p" is the required version, nothing to do..."
            Install-Libraries
        } else {
            Install-Python383
            Main
        }
    }
}

# Fonction dédiée à l'installation de Python 3.8.3 (testé avec pywin32)
function Install-Python383 {
    # Based on https://stackoverflow.com/questions/45825618/downloading-and-installing-python-via-a-batch-file
    # This is the link to download Python 3.8.3 from Python.org
    # See https://www.python.org/downloads/
    $pythonUrl = "https://www.python.org/ftp/python/3.8.3/python-3.8.3-amd64.exe"

    # This is the directory that the exe is downloaded to
    $tempDirectory = "C:\tmp_cpdecrypt\"

    # Installation Directory
    # Some packages look for Python here
    $targetDir = "C:\Python38"

    Write-Host " - Downloading Python 3.8.3 from the source..."
    # create the download directory and get the exe file
    $pythonNameLoc = $tempDirectory + "python383.exe"
    New-Item -ItemType directory -Path $tempDirectory -Force | Out-Null
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    (New-Object System.Net.WebClient).DownloadFile($pythonUrl, $pythonNameLoc)

    # These are the silent arguments for the install of python
    # See https://docs.python.org/3/using/windows.html
    $Arguments = @()
    $Arguments += "/i"
    $Arguments += 'InstallAllUsers="1"'
    $Arguments += 'TargetDir="' + $targetDir + '"'
    $Arguments += 'DefaultAllUsersTargetDir="' + $targetDir + '"'
    $Arguments += 'AssociateFiles="1"'
    $Arguments += 'PrependPath="1"'
    $Arguments += 'Include_doc="1"'
    $Arguments += 'Include_debug="1"'
    $Arguments += 'Include_dev="1"'
    $Arguments += 'Include_exe="1"'
    $Arguments += 'Include_launcher="1"'
    $Arguments += 'InstallLauncherAllUsers="1"'
    $Arguments += 'Include_lib="1"'
    $Arguments += 'Include_pip="1"'
    $Arguments += 'Include_symbols="1"'
    $Arguments += 'Include_tcltk="1"'
    $Arguments += 'Include_test="1"'
    $Arguments += 'Include_tools="1"'
    $Arguments += 'Include_launcher="1"'
    $Arguments += 'Include_launcher="1"'
    $Arguments += 'Include_launcher="1"'
    $Arguments += 'Include_launcher="1"'
    $Arguments += 'Include_launcher="1"'
    $Arguments += 'Include_launcher="1"'
    $Arguments += "/passive"

    # Install Python
    Write-Host " - Installing Python 3.8.3, please follow the instructions on screen..."
    Start-Process $pythonNameLoc -ArgumentList $Arguments -Wait

    Verification-Python383
}

# Fonction dédié à la vérification de la bonne installation et à l'arrêt en cas d'échec
function Verification-Python383 {
    # Check environment for Python 3.8.3
    $p = &{python -V} 2>&1
    $version = if(($p -is [System.Management.Automation.ErrorRecord]) -or ($p -eq "Python 3.8.3")) {
        Write-Host " - Python 3.8.3 installation failed!"
        Write-Host "`nProgram incomplete, please re-run it and make sure to follow instructions on screen!`n"
	pause
	exit
    } else {
        Write-Host " - Python 3.8.3 is now installed!"
    }
}

# Fonction dédiée à l'installation des deux librairies nécessaires
function Install-Libraries {
    # Upgrading pip
    Write-Host " - Upgrading pip..."
    python -m pip install --upgrade pip 1>$null

    # Install required libraries using pip
    # Install pywin32
    Write-Host " - Installing pywin32..."
    python -m pip install pywin32 1>$null

    # Install aead
    Write-Host " - Installing aead..."
    python -m pip install aead 1>$null
}

# Lancement de la fonction principale et fin
Main
Write-Host "`nProgram complete, you should now be able to run cpdecrypt!`n"
pause