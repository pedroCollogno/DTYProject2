# Welcome to the Django Backend of this project !

## Getting Started

First of all, these instructions will get you a copy of the project up and running on your local machine.

### Prerequisites

This projects runs with python. If you haven't got python on your machine, install it ! (https://www.python.org/downloads/).

> Note : On Windows, you will need python3.5 64 bits. Else, you will not be able to install `tensorflow`. On Mac you can work with python3.5 or 3.6, even though 3.5 is recommended.

This project also uses WebSockets managed by the Django Framework. In order for those to work, you will need a `Redis` server instance running on your computer. Simply download Redis from here (https://redis.io/) and run `redis-server` in your terminal.

### Installing the project

The first thing you will have to do, even before installing the project, is decide where you will want to save the data you collect and the models you compile.
It can be anywhere you choose, you just have to specify the path to these folders in the `config.json` file, at the root of the project.

Now that you have done that, the first step is to install all requirements listed in `requirements.txt`.
```
pip install -r requirements.txt
# pip3 install -r requirements.txt   / if you're using python 3
```

Then, you have to install our custom `ml_tools` package. To do that, you have two steps to follow:
* Update the `config.json` file in the `ml_tools/src` folder
* Install the package

For the second step, just go to the `ml_tools` folder in your terminal and run the following command : 
```
python setup.py install
# python3 setup.py install / if you're using python 3
```

## Start the server up

To start the server, simply run this in your terminal :
```
python src/manage.py runserver
```

You're ready to go !