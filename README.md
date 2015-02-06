# Visit Day Robotathon
## Cardiff School of Computer Science & Informatics

A webapp used as a small introduction to basic Python programming for visiting applicants to the School of Computer Science & Informatics at Cardiff University.

The app is based around the Python [robot game](https://robotgame.net), and includes a modified version of the game's `rgkit` module.

## Running the app
Install the app and dependencies as described further below. 


### Recommended: If using UWSGI and a webserver (e.g. Nginx)
Start the app by running the included file:
```
$ ./start.sh
```

This will create any required directories and get things ready. You may find it useful to run this script inside of something like `tmux` or `screen` for easy management.

### Otherwise
Start the app by running the application directly and create required directorie(s):
```
$ mkdir robots
$ python application.py
```

## Resetting the app
To delete the app data ready for a new visit day, then make a `GET` request (using your browser or otherwise) to `/delete_all_data`.


## Installation guide 
The School's system managers have information required to install the app on locally-managed machines. For other installations, you may like to follow the guide below.

This guide assumes you have pip installed. On Ubuntu (and probably other Debian-based distros) you can use apt-get
to install this:

`sudo apt-get install python-pip`

To keep things isolated, install virtulenv:

`sudo pip install virtualenv`

Next, clone the repository and enter the directory that is made:

`cd robotathon-ucas`

Create the robotathon virtual environment. This assumes you have the Python 2.7 binary in /usr/bin/.

`virtualenv -p /usr/bin/python2.7 robotathon`

Activate the environment. This should change your shell prompt to indicate you're using the venv.

`source robotathon/bin/activate`

Install the dependencies using pip:

`pip install flask elo`

Run the web-server:

`python application.py`

Open your browser and visit `http://127.0.0.1:8088/`. If everything worked, you should see the Welcome page.
