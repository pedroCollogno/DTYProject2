cd ..
xcopy config.json back_django\config.json
xcopy config.json front\config.json
xcopy config.json ml_tools\src\config.json
pip install Twisted-18.9.0-cp35-cp35m-win_amd64.whl

cd back_django
pip install -r requirements.txt

cd ../ml_tools
pip install -r requirements.txt
python setup.py install

cd ../front
npm install
