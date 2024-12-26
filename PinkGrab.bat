@echo off
echo Installing required Python modules...

pip install customtkinter
pip install pillow
pip install requests
pip install pycryptodome
pip install pypiwin32
pip install pysqlite3

echo All required modules have been installed.

python pgrb.py

pause