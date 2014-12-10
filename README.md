# Getting started (Linux)

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