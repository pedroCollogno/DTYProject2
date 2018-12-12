# Welcome to the React Frontend of this project !

## Getting Started

First of all, these instructions will get you a copy of the project up and running on your local machine.

### Prerequisites

This projects runs using `NodeJS` and `NPM`. If you haven't got those on your machine, install both of them ! 
- Instructions to install both : https://www.npmjs.com/get-npm


### Installing the project

The first thing you will have to do, even before installing the project, is decide where you will want to save the data you collect and the models you compile.
It can be anywhere you choose, you just have to specify the path to these folders in the `config.json` file, at the root of the project. 

Now that you have done that, the first step is to install all external packages needed for our project to work.
```
npm install
```

## Start the server up

There you are, ready to go !
To start the server, simply run this in your terminal :
```
npm start
```
Or use the bash `start_front` bash script at the root of the project.

> **Note:** If you're in development, you might want to use `gulp` at this part of the process instead of `npm start`. The gulp script actually updates and compiles the `.scss` files in the project. Running the `start_front` script does the trick, since it uses gulp as a project dependency, and not a globally installed package.

## Using the app

To visit the app, open a browser on http://localhost:4200/

You should get a view like this :

<img src="../assets/welcome_screen.png" />

To get the details on how to use the demonstrator once it's up and running, checkout the [User Manual](../USER_MANUAL.md)