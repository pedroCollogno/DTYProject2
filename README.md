# Welcome to the Thales AI Demonstrator !

## Getting Started

First of all, these instructions will get you a copy of the project up and running on your local machine.

### Prerequisites

This projects runs with python. If you haven't got python on your machine, install it ! (https://www.python.org/downloads/).

> Note : On Windows, you will need python3.5 64 bits. Else, you will not be able to install `tensorflow`. Here's a link of a working version : https://www.python.org/downloads/release/python-354/. On Mac you can work with Python 3.5 or 3.6, even though 3.5 is recommended.

This project also uses WebSockets managed by the Django Framework. In order for those to work, you will need a `Redis` server instance running on your computer.

|                           Windows                           |                Mac (Or other UNIX OS)                |
| :---------------------------------------------------------: | :--------------------------------------------------: |
|  Using `Redis` on Windows is quite tricky, so you have to use a specific release for it to work with Django Channels. If you don't have it, download the archive from GitHub, it is available [HERE](https://github.com/MicrosoftArchive/redis/releases/tag/win-3.0.504). Then, extract the `Redis-x64-3.0.504.zip` archive in another folder located wherever you want. (In `C:\Program Files\Redis` for example). Once that is done, you can either add the folder path to the PATH environment variable ([instructions below](##add-redis-to-path)). If you do not want to add it to your path, you can modify the [start file](./win_scripts/start.bat) in any text editor, and the path to `Redis` folder to the last line. (Change from `redis-server` to `C:\"Program Files"\Redis\redis-server` for example) | Simply download Redis from here (https://redis.io/). Detailed installation instructions can be found at https://redis.io/download/#installation. |

This projects client side runs using `NodeJS` and `NPM`. If you haven't got those on your machine, install both of them ! 
- Instructions to install both : https://www.npmjs.com/get-npm

### Installing the project

The first thing you will have to do, even before installing the project, is decide where you will want to save the data you collect and the models you compile.
It can be anywhere you choose, you just have to specify the path to these folders in the `config.json` file, at the root of the project.

Then, you have to install our custom `ml_tools` package. To do that, you have two steps to follow:

- Update the `config.json` file in the `ml_tools/src` folder
- Install the package

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

## Add Redis to PATH

To access it, press `WIN+R` and execute `sysdm.cpl`. Then, in Advanced System Properties check environment variables. Finally, in PATH variable, add a new path, being the path to geckodriver. For example, add `C:\Program Files\Redis` to path if `redis-server.exe` is in this Redis folder
