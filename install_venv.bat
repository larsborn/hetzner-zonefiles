mkdir temp
cd temp
wget --no-check-certificate "http://pypi.python.org/packages/source/v/virtualenv/virtualenv-1.11.4.tar.gz"
"C:\Program Files\7-Zip\7z.exe" e *.tar.gz
"C:\Program Files\7-Zip\7z.exe" e *.tar -y
cd ..
python temp\virtualenv.py py_env
rm -rf temp
