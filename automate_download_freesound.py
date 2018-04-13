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


def verify_authentication(user_info):
    '''A function to check if login credentials are valid (True) or not valid (False)
    :param user_info: a namedtuple with login credentials: user.email, user.password
    :return: boolean value depending on if login credentials are valid
    '''
    driver = webdriver.Chrome()
    driver = login(driver, user_info.email, user_info.password)

    if re.match("https://freesound.org/home/login/", driver.current_url):
        driver.quit()
        return False
    else:
        print("Login successful!")
        driver.quit()
        return True


def login(driver, user, pass_w):
    ''' Simulate logging into freesound.org

    :param driver: a chrome driver instance
    :param user: the user's email login
    :param pass_w: the user's password
    :return: the same chrome driver instance
    '''
    driver.get("https://freesound.org/home/login/?next=/search/")
    username = driver.find_element_by_xpath('//*[@id="id_username"]')
    username.send_keys(user)
    password = driver.find_element_by_xpath('//*[@id="id_password"]')
    password.send_keys(pass_w)
    loginSelect = driver.find_element_by_xpath('//*[@id="content_full"]/form/input[2]')
    loginSelect.send_keys(Keys.RETURN)
    return driver


def setup(full_path):
    '''Function to set up default download directory and Chrome Options

    :param full_path: absolute path to download to
    :return: a chrome driver instance
    '''
    chromeOptions = webdriver.ChromeOptions()
    prefs = {"download.default_directory": full_path}
    chromeOptions.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(chrome_options=chromeOptions)
    return driver


def enter_search_subject(driver, search_subject):
    '''Function to go to the freesound site, and enter in the desired sound
    :param driver: a chrome driver instance
    :param search_subject: a string containing the desired sound
    :return: a chrome driver instance
    '''
    driver.get("https://freesound.org")
    search_bar = driver.find_element_by_xpath('//*[@id="search"]/form/fieldset/input[1]')
    search_bar.send_keys(search_subject)
    search_bar.send_keys(Keys.RETURN)
    return driver


def filter_by_attribute(driver, attribute_name, attribute_value):
    '''Filter by attribute depending on name and value

    :param driver: a chrome driver instance
    :param attribute_name: a string that is either samplerate or fileformat
    :param attribute_value: a string containing the attributes value
    :return: a chrome driver instance
    '''
    if attribute_name == 'samplerate':
        message = "The sample rate you provided is not supported... Defaulting to sample rate of 48000."
        default_value = "48000"
    elif attribute_name == 'fileformat':
        message = "The file format you provided is not supported... Defaulting to the file format of wav."
        default_value = "wav"

    try:
        # Check if sample rate is valid search choice
        sampling_rate = driver.find_element_by_link_text(str(attribute_value))
        sampling_rate.send_keys(Keys.RETURN)
    except NoSuchElementException:
        print(message)
        sampling_rate = driver.find_element_by_link_text(default_value)
        sampling_rate.send_keys(Keys.RETURN)
    return driver


def advanced_filtering(driver):
    '''Function to do more advanced filtering of sound files. Advanced search for
    only search subject in tags, file name, or file description.

    :param driver: a chrome driver instance
    :return: a chrome driver instance
    '''

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

    max_duration = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, '//*[@id="filter_duration_max"]')))
    max_duration.clear()
    max_duration.send_keys("60")

    new_advanced_search = driver.find_elements_by_xpath('//*[@id="search_submit"]')
    new_advanced_search[1].send_keys(Keys.RETURN)
    return driver


def find_next_page(driver):
    '''Function that determines whether or not there is a next page.

    :param driver: a chrome driver instance
    :return: a boolean value, True if there is a next page, and False if we are at the last page
    '''
    try:
        # Try to find a next page button
        new_page = driver.find_element_by_xpath('//*[@id="content_full"]/div[2]/ul/li[2]/a')
        new_page.send_keys(Keys.RETURN)
        return True
    except NoSuchElementException:
        # This means we are at last page
        return False


def wait_for_downloads(full_path):
    '''Function that waits for downloads, and will only return True
    when chrome downloads in full_path are finished.

    :param full_path: the absolute path to the folder where audio files are downloaded
    :return: a boolean value, True if downloads are done, False if not done
    '''
    unfinished_files = glob.glob(full_path + "/*.crdownload")
    if unfinished_files:
        return False
    else:
        return True


def simulate_download(sound, download_path, user, pass_w, args):
    '''A function used to automate downloading of sound files via Selenium.

    :param sound: a string of the desired sound to download
    :param download_path: a path of the desired download path
    :param args: a Namespace object with attributes such as file format, sample rate, and advanced filtering
    :return: count of number of downloads
    '''
    full_path = os.path.join(download_path, sound)

    if not os.path.exists(full_path):
        # make a directory for the files to go to
        os.makedirs(full_path)

    download_count = 0
    driver = setup(full_path)
    search_subject = sound
    try:

        driver = login(driver, user, pass_w)

        driver = enter_search_subject(driver, search_subject)
        if args.samplerate is not None:
            driver = filter_by_attribute(driver, 'samplerate', args.samplerate)
        if args.file_format is not None:
            driver = filter_by_attribute(driver, 'fileformat', args.file_format)

        if args.advanced_filter:
            # Advanced search for only search subject in tags or file name
            driver = advanced_filtering(driver)
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
                download_count += 1
                driver.back()
                # Redefine links to avoid stale element error
                links = driver.find_elements_by_class_name("title")
            if not find_next_page(driver):
                break

        # Wait for the rest of the downloads to finish
        while not wait_for_downloads(full_path):
            time.sleep(5)

        # Close all open browsers associated with driver instance and garbage collect driver instance
        driver.quit()

    except TimeoutException:
        print("Time out exception... Page took too long to load...")
        sys.exit(1)

    return download_count


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
                        default=os.path.expanduser("~") + "/Downloads/",
                        help='Optional argument to specify the download path where files will go. '
                             'Default will be your standard Downloads folder. '
                             'Works for both MacOS and Windows environments.')

    parser.add_argument('--file-format',
                        dest='file_format',
                        type=str,
                        default=None,
                        choices=[None, "wav", "flac", "aiff", "ogg", "mp3", "m4a"],
                        help='Enter the desired audio file format. '
                             'Default will be all available audio file formats with no filtering. '
                             'The available options are wav, aiff, flac, ogg, m4a, and mp3.')

    parser.add_argument('--sample-rate',
                        dest='samplerate',
                        type=int,
                        choices=[None, 11025, 16000, 22050, 44100, 48000, 88200, 96000],
                        default=None,
                        help='Enter the desired sample rate of the file. '
                             'Default will be all of the available sample rates with no filtering. '
                             'The available options are 11025, 22050, 44100, 48000, 88200, and 96000.')

    parser.add_argument('--advanced-filter',
                        dest='advanced_filter',
                        type=bool,
                        default=False,
                        help='Enter True if you want to initiate advanced filtering to limit audio files. '
                             'Only audio files with tags, filenames, and descriptions '
                             'containing your search item will be downloaded.')

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

    if not os.path.exists(download_path):
        print("The download destination directory specified does not exist... Defaulting to Downloads folder.")
        download_path = os.path.expanduser("~") + "/Downloads/"

    user_info = authenticate()
    credentials_flag = verify_authentication(user_info)

    if not credentials_flag:
        print("The credentials you entered were not correct. Please re-run the script. Exiting program...")
        sys.exit(1)

    for elem in sounds:
        download_count = simulate_download(elem, download_path, user_info.email, user_info.password, args)
        output_path = os.path.join(download_path, elem)
        print("Downloaded %d files of \"%s\" at %s" %
              (download_count, elem, output_path))

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
