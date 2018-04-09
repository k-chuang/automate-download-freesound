#!/bin/env python2.7

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
import getpass
import re
import glob
import os
import time
from collections import namedtuple
import argparse
import sys


def authenticate():
    '''A function used to retrieve login credentials to authenticate for freesound.org.

    :return: a namedtuple containing user login credentials with two attributes, an email and a password
    '''
    Credentials = namedtuple('Credentials', ['email', 'password'])
    user = raw_input("Please enter your email/username for freesound.org: \n")
    password = getpass.getpass()
    user_info = Credentials(email=user, password=password)
    return user_info


def simulate_download(sound, download_path, user, pass_w, args):
    '''A function used to automate downloading of sound files via Selenium.

    :param sound: a string of the desired sound to download
    :param download_path: a path of the desired download path
    :param args: a Namespace object with attributes such as file format, sample rate, and advanced filtering
    :return: None
    '''
    full_path = os.path.join(download_path, sound)

    # If the directory we are trying to write to already exists
    if os.path.exists(full_path):
        # dont write to it and exit the program
        print("The requested directory already exists at %s" % full_path)
        exit(1)
    else:
        # make a directory for the files to go to
        os.makedirs(full_path)

    # Seting download path within Chrome options
    chromeOptions = webdriver.ChromeOptions()
    prefs = {"download.default_directory": full_path}
    chromeOptions.add_experimental_option("prefs", prefs)
    search_subject = sound
    driver = webdriver.Chrome(chrome_options=chromeOptions)

    try:

        driver.get("https://freesound.org/home/login/?next=/search/")
        username = driver.find_element_by_xpath('//*[@id="id_username"]')
        username.send_keys(user)
        password = driver.find_element_by_xpath('//*[@id="id_password"]')
        password.send_keys(pass_w)
        loginSelect = driver.find_element_by_xpath('//*[@id="content_full"]/form/input[2]')
        loginSelect.send_keys(Keys.RETURN)

        # Checking if login credentials are correct before moving out, if not exit the script
        if re.match("https://freesound.org/home/login/", driver.current_url):
            print("The login credentials you provided were incorrect. Please re-run the script. Exiting now...")
            driver.quit()
            exit(1)

        # Go to the freesound site, and enter in the desired sound
        driver.get("https://freesound.org")
        search_bar = driver.find_element_by_xpath('//*[@id="search"]/form/fieldset/input[1]')
        search_bar.send_keys(search_subject)
        search_bar.send_keys(Keys.RETURN)

        try:
            # Check if sample rate is valid search choice
            sampling_rate = driver.find_element_by_link_text(str(args.samplerate))
            sampling_rate.send_keys(Keys.RETURN)

        except NoSuchElementException:
            print("The sample rate you provided is not supported... Defaulting to sample rate of 48000.")
            sampling_rate = driver.find_element_by_link_text("48000")
            sampling_rate.send_keys(Keys.RETURN)

        try:
            # Check if file format is valid search choice
            file_format = driver.find_element_by_link_text(args.file_format)
            file_format.send_keys(Keys.RETURN)
        except NoSuchElementException:
            print("The file format you provided is not supported... Defaulting to the file format of wav. ")
            file_format = driver.find_element_by_link_text("wav")
            file_format.send_keys(Keys.RETURN)

        if args.advanced_filter:
            # Advanced search for only search subject in tags or file name
            driver.find_element_by_css_selector('a[onclick*=showAdvancedSearchOption').click()
            tag_element = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.NAME, 'a_tag')))
            tag_element.click()

            file_element = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.NAME, 'a_filename')))
            file_element.click()

            description_element = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.NAME, 'a_description')))
            description_element.click()

            new_advanced_search = driver.find_elements_by_xpath('//*[@id="search_submit"]')
            new_advanced_search[1].send_keys(Keys.RETURN)

        driver.implicitly_wait(1)

        while True:
            # Gather all links on the page
            links = driver.find_elements_by_class_name("title")
            # Loop through all links on this page to download
            for j in range(len(links)):

                links[j].send_keys(Keys.RETURN)

                # Finding the download button
                download_link = driver.find_element_by_xpath('//*[@id="download_button"]')
                download_link.send_keys(Keys.RETURN)
                driver.back()
                # Redefine links to avoid stale element error
                links = driver.find_elements_by_class_name("title")

            try:
                # Try to find a next page button
                new_page = driver.find_element_by_xpath('//*[@id="content_full"]/div[2]/ul/li[2]/a')
                new_page.send_keys(Keys.RETURN)
            except NoSuchElementException:
                # The next page element does not exist, meaning we are at the last page, so break out of the loop
                break

        # Wait for the rest of the downloads to finish
        while True:
            unfinished_files = glob.glob(full_path + "/*.crdownload")
            if not unfinished_files:
                break
            else:
                time.sleep(5)

        # Close all open browsers associated with driver instance and garbage collect driver instance
        driver.quit()

    except TimeoutException:
        print("Time out exception... Page took too long to load...")
        exit(1)


def list_of_sounds(arguments):
    '''Create a type for string arguments separated by commas, and generate a list from it.

    :param arguments: a string of arguments separated by commas from command line
    :return: a list of string arguments
    :raises ArgumentTypeError: an exception that comes from improper argument type
    '''
    try:
        # Remove spaces between commas (if user happens to have spaces)
        no_space = re.sub(r'\s*,\s*', ',', arguments)
        sound_list = map(str, no_space.split(','))
        sound_list = filter(None, sound_list)
        return sound_list
    except:
        raise argparse.ArgumentTypeError("List of sounds must be separated by commas (no spaces).")


def parse_args(argv):
    '''

    :param argv: string of sys arguments passed to command line
    :return: arguments parsed out of sys.argv
    '''
    parser = argparse.ArgumentParser(description='Download audio files from Freesound.org!')
    parser.add_argument('sounds',
                        type=list_of_sounds,
                        default=None,
                        help='Enter sound(s) you would like to download '
                             'separated by commas and no spaces. If desired sound '
                             'contains two or more words, please enclose sound list in parenthesis'
                             'to prevent errors. (i.e. "dog barking,cats purring,birds chirping")')

    parser.add_argument('--download-dir',
                        dest='downloadpath',
                        default=None,
                        help='Optional argument to specify the download path where files will go. '
                             'Default will be your standard Downloads folder. '
                             'Works for both MacOS and Windows environments.')

    parser.add_argument('--file-format',
                        dest='file_format',
                        type=str,
                        default="wav",
                        choices=["wav", "flac", "aiff", "ogg", "mp3", "m4a"],
                        help='Enter the desired audio file format. Default will be wav files. '
                             'The available options are wav, aiff, flac, and mp3.')

    parser.add_argument('--sample-rate',
                        dest='samplerate',
                        type=int,
                        choices=[11025, 16000, 22050, 44100, 48000, 88200, 96000],
                        default=48000,
                        help='Enter the desired sample rate of the file. Default will be 48000. '
                             'The available options are 11025, 22050, 44100, 48000, 88200, and 96000.')

    parser.add_argument('--advanced-filter',
                        dest='advanced_filter',
                        type=bool,
                        default=False,
                        help='Enter True if you want to initiate advanced filtering to limit audio files. '
                             'Only audio files with tags or filenames containing your search item will be downloaded.')

    # If no arguments provided, return help message
    if len(argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    return parser.parse_args(argv[1:])


def main(argv):
    args = parse_args(argv)

    # To be clear:
    sounds = args.sounds
    download_path = args.downloadpath

    if not download_path or not os.path.exists(download_path):
        print("The download destination directory specified does not exist... Defaulting to Downloads folder.")
        download_path = os.path.expanduser("~") + "/Downloads/"

    user_info = authenticate()

    for elem in sounds:
        simulate_download(elem, download_path, user_info.email, user_info.password, args)
        output_path = os.path.join(download_path, elem)
        print("Finished downloading %s at %s" % (elem, output_path))

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
