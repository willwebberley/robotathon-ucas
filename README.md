# Visit Day Robotathon
## Cardiff School of Computer Science & Informatics

A webapp used as a small introduction to basic Python programming for visiting applicants to the School of Computer Science & Informatics at Cardiff University.

The app is based around the Python [robot game](https://robotgame.net), and includes a modified version of the game's `rgkit` module.

## Resetting the app
To delete the app data ready for a new visit day, then make a `GET` request (using your browser or otherwise) to `/delete_all_data`.


## Installation and running guide 

### Installation on managed School machines
The School's system managers have information required to install the app on locally-managed machines. Below is a quick setup guide for this (assuming Mint/Ubuntu) on host `openday.cs.cf.ac.uk`:

Install system dependencies:
```
# apt-get install nginx python-pip python-dev tmux
```

Install Python dependencies:
```
# pip install flask elo uwsgi
```

Create a user (if you need one) that can run the apps:
```
# useradd apps 
# mkdir /home/apps 
# chown apps /home/apps
```

Download the app (as user `apps`):
```
$ cd ~
$ git clone https://github.com/flyingsparx/robotathon-ucas.git
```

Configure the webserver by adding the server block below to `/etc/nginx/nginx.conf`:
```
server{
        listen 80;
        server_name ucas.openday.cs.cf.ac.uk;
        location /static {
                root /home/apps/robotathon-ucas;
        }
        location / {
                uwsgi_pass 127.0.0.1:8188;
                include /etc/nginx/uwsgi_params;
        }
}
```

Start the webserver:
```
# service nginx start
```

Run the app (as user `apps`):
```
$ cd ~/robotathon-ucas
$ ./start.sh
```

You may prefer to run `start.sh` inside a multiplexer (such as the installed `tmux`) for manageability.

The app is now available at [ucas.openday.cs.cf.ac.uk](http://ucas.openday.cs.cf.ac.uk).


### General installation
Follow these instructions for ad-hoc installations of the app.

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
