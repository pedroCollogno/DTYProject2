
cd ../ml_tools
python ./setup.py install > nul
cd ../back_django
python src/manage.py runserver