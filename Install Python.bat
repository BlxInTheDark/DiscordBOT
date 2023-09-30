@echo off
setlocal enabledelayedexpansion

rem Python sürümünü ve indirme bağlantısını ayarlayın
set "python_version=3.11.5"
set "python_installer=python-%python_version%-amd64.exe"
set "python_url=https://www.python.org/ftp/python/%python_version%/%python_installer%"

rem Python kurulum dosyasını indirin
echo Python indiriliyor...
curl -o %python_installer% %python_url%

rem Python'ı kurun
echo Python kuruluyor...
%python_installer% /quiet InstallAllUsers=1 PrependPath=1 Include_launcher=0

rem Python kurulum dosyasını silin
del %python_installer%

rem pip ve bazı temel paketleri yükleyin
echo Temel paketler yükleniyor...
python -m ensurepip --default-pip
python -m pip install --upgrade pip
python -m pip install numpy matplotlib requests

echo Python kurulumu tamamlandı. Sistem yeniden başlatılacak...
pause

rem Bilgisayarı yeniden başlatın
shutdown /r /t 5
