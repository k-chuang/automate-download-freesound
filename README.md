# Automating the Menial Tasks using Python Pt.2
[![Build Status](https://travis-ci.org/k-chuang/automate-download-freesound.svg?branch=master)](https://travis-ci.org/k-chuang/automate-download-freesound)
[![Coverage Status](https://coveralls.io/repos/github/k-chuang/automate-download-freesound/badge.svg?branch=master)](https://coveralls.io/github/k-chuang/automate-download-freesound?branch=master)

A cool Python automation project that automates the menial task of downloading hundreds of audio files on 
[Freesound](freesound.org) using Selenium, a web-browser automation tool.

# Description
Using Selenium and the Google chromedriver, this project will automate downloading audio files 
via a command line interface (CLI) application.

Inspired by [Automating the Boring Stuff](https://automatetheboringstuff.com/) by Al Sweigart.


# Setup
Make sure to install the chromedriver.exe via brew or from the [Google site](https://sites.google.com/a/chromium.org/chromedriver/downloads),
and set the location of the chromedriver on your SYSTEM PATH.

I installed the chromedriver via [brew](https://brew.sh/)(command is below), and naturally, brew installs packages to /usr/local/bin, which is already in your $PATH, so that is pretty convenient. You can always do an echo $PATH to make sure that /usr/local/bin is in it, and if it's not in your $PATH variable, then export it by editing either ~/.bash_profile or /etc/paths/.

    $ brew install chromedriver

After installing the chromedriver, here is rest of the setup:

    $ git clone https://github.com/k-chuang/automate-download-freesound.git
    $ cd automate-download-freesound
    $ virtualenv -p /usr/bin/python2.7 venv
    $ source venv/bin/activate
    $ pip install -r dev-requirements.txt
    $ pytest
 
# How to use

Run the command below for more information regarding the arguments (positional or optional, default values, description,   etc.)
 
    $ python automate_download_freesound.py --help
  
There is only one required argument, and that is the desired sounds you wish to download from [Freesound](http://freesound.org). You may list more than one sound, but make sure to separate each one by commas, and if the sound you want to download includes spaces, please put quotation marks around it to ensure a smooth experience.

    $ python automate_download_freesound.py "dogs barking,cats purring"

There are more features and arguments, including download path, file format, sample rate, and advanced filtering. These are all optional arguments, and are only there to help you with filtering for your needs.


# Scripts
[automate_download_freesound.py](https://github.com/k-chuang/automate-download-freesound/blob/master/automate_download_freesound.py) - the main CLI program that uses Selenium to automate downloading sound files from freesound
[test_automate_download_freesound.py](https://github.com/k-chuang/automate-download-freesound/blob/master/test_automate_download_freesound.py) - the tester program that runs through unit tests and test cases for the main CLI application. 

