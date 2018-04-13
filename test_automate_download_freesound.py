"""
Unit tests for test_automate_download_freesound.py
Run with:
$ pytest
"""

import unittest
import mock
import automate_download_freesound
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from collections import namedtuple
import pytest
import os
import shutil


class FreeSoundLoginElementsTest(unittest.TestCase):
    '''Using the setUpClass() and tearDownClass() methods along with the @classmethod decorator.
    These methods enable us to set the values at the class level rather than at method level.
    The values initialized at class level are shared between the test methods.'''
    @classmethod
    def setUpClass(cls):
        cls.driver = webdriver.Chrome()
        cls.driver.get("https://freesound.org/home/login/?next=/")

    def test_login_username(self):
        self.assertTrue(self.is_element_present(By.XPATH, '//*[@id="id_username"]'))

    def test_password(self):
        self.assertTrue(self.is_element_present(By.XPATH, '//*[@id="id_password"]'))

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def is_element_present(self, how, what):
        '''
        Helper method to confirm the presence of an element on page
        :params how: By locator type
        :params what: locator value
        '''
        try:
            self.driver.find_element(by=how, value=what)
        except NoSuchElementException:
            return False
        return True


class FreeSoundSearchByTextTest(unittest.TestCase):
    '''Using the setUpClass() and tearDownClass() methods along with the @classmethod decorator.
    These methods enable us to set the values at the class level rather than at method level.
    The values initialized at class level are shared between the test methods.'''
    @classmethod
    def setUpClass(cls):
        cls.driver = webdriver.Chrome()
        cls.driver.get("https://freesound.org/")

    def test_search_by_text(self):
        '''
        Test to see that the number of elements within the first page of a search item is 15.
        '''
        # get the search textbox
        self.search_field = self.driver.find_element_by_name("q")
        self.search_field.clear()
        # enter search keyword and submit
        self.search_field.send_keys("dogs barking")
        self.search_field.submit()
        # get the list of elements which are displayed after the search
        # currently on result page using find_elements_by_class_name method
        lists = self.driver.find_elements_by_class_name("title")
        self.assertEqual(15, len(lists))

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def is_element_present(self, how, what):
        '''
        Helper method to confirm the presence of an element on page
        :params how: By locator type
        :params what: locator value
        '''
        try:
            self.driver.find_element(by=how, value=what)
        except NoSuchElementException:
            return False
        return True


class FreeSoundSearchTest(unittest.TestCase):
    '''Using the setUpClass() and tearDownClass() methods along with the @classmethod decorator.
    These methods enable us to set the values at the class level rather than at method level.
    The values initialized at class level are shared between the test methods.'''
    @classmethod
    def setUpClass(cls):
        cls.driver = webdriver.Chrome()
        cls.driver.get("https://freesound.org/search/?q=")

    def test_for_number_of_elements(self):
        # get the list of elements which are displayed after the search
        # currently on result page using find_elements_by_class_name method
        lists = self.driver.find_elements_by_class_name("title")
        self.assertEqual(15, len(lists))

    def test_for_file_format(self):
        '''
        Test to find attribute of file format
        '''
        self.assertTrue(self.is_element_present(By.XPATH, '//*[@id="sidebar"]/h3[3]'))

    def test_for_wav_file_format(self):
        '''
        Test to find specific wav format
        '''
        self.assertTrue(self.is_element_present(By.LINK_TEXT, 'wav'))

    def test_for_samplerate(self):
        '''
        Test to find attribute of samplerate
        '''
        self.assertTrue(self.is_element_present(By.XPATH, '//*[@id="sidebar"]/h3[4]'))

    def test_for_specific_samplerate(self):
        '''
        Test to find specific 48000 sample rate
        '''
        self.assertTrue(self.is_element_present(By.LINK_TEXT, '48000'))

    def test_for_advanced_filter(self):
        '''
        Test for advanced filter button
        '''
        self.assertTrue(self.is_element_present(
            By.CSS_SELECTOR, 'a[onclick*=showAdvancedSearchOption'))

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def is_element_present(self, how, what):
        '''
       Helper method to confirm the presence of an element on page
       :params how: By locator type
       :params what: locator value
       '''
        try:
            self.driver.find_element(by=how, value=what)
        except NoSuchElementException:
            return False
        return True


class FreeSoundAdvancedFilter(unittest.TestCase):
    '''Using the setUpClass() and tearDownClass() methods along with the @classmethod decorator.
    These methods enable us to set the values at the class level rather than at method level.
    The values initialized at class level are shared between the test methods.'''
    @classmethod
    def setUpClass(cls):
        cls.driver = webdriver.Chrome()
        cls.driver.get("https://freesound.org/search/?q=")
        cls.driver.find_element_by_css_selector('a[onclick*=showAdvancedSearchOption').click()

    def test_fail_filter_item(self):
        with self.assertRaises(NoSuchElementException):
            self.driver.find_element_by_id('10000')

    def test_tags_filter_item(self):
        tag_element = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.NAME, 'a_tag')))
        tag_element.click()
        self.assertTrue(tag_element.is_selected())

    def test_filenames_filter_item(self):
        file_element = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.NAME, 'a_filename')))
        file_element.click()
        self.assertTrue(file_element.is_selected())

    def test_description_filter_item(self):
        description_element = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.NAME, 'a_description')))
        description_element.click()
        self.assertTrue(description_element.is_selected())

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def is_element_present(self, how, what):
        '''
        Helper method to confirm the presence of an element on page
       :params how: By locator type
       :params what: locator value
       '''
        try:
            self.driver.find_element(by=how, value=what)
        except NoSuchElementException:
            return False
        return True


class SimulateDownloadIntegrationTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.email = os.environ['FREESOUND_EMAIL']
        cls.password = os.environ['FREESOUND_PASSWORD']
        cls.download_path = os.path.expanduser("~") + "/Downloads/"
        shutil.rmtree(os.path.join(cls.download_path, 'toaster pop set'), ignore_errors=True)
        shutil.rmtree(os.path.join(cls.download_path, 'tiger'), ignore_errors=True)
        shutil.rmtree(os.path.join(cls.download_path, 'glass breaking'), ignore_errors=True)

    def test_simulate_download_basic(self):
        '''
        Testing with no filters, just the one positional argument
        '''

        args = automate_download_freesound.parse_args(['automate_download_freesound.py', 'toaster pop set'])
        download_count = automate_download_freesound.simulate_download(
            args.sounds[0], self.download_path, self.email, self.password, args)
        self.assertEqual(download_count, 2)
        update_download_path = os.path.join(self.download_path, 'toaster pop set')
        self.assertEqual(len(os.listdir(update_download_path)), download_count)

    def test_simulate_download_optional_arguments(self):
        '''
         Testing with optional filter arguments
        '''

        args = automate_download_freesound.parse_args(
            ['automate_download_freesound.py', 'tiger',
             '--sample-rate', '48000', '--file-format', 'mp3'])
        download_count = automate_download_freesound.simulate_download(
            args.sounds[0], self.download_path, self.email, self.password, args)
        self.assertEqual(download_count, 2)
        update_download_path = os.path.join(self.download_path, 'tiger')
        self.assertEqual(len(os.listdir(update_download_path)), download_count)

    def test_simulate_download_advanced_filters(self):
        '''
        Testing with optional arguments and advanced filters
        '''
        args = automate_download_freesound.parse_args(
            ['automate_download_freesound.py', 'glass breaking',
             '--sample-rate', '48000', '--file-format', 'flac', '--advanced-filter', 'True'])
        download_count = automate_download_freesound.simulate_download(
            args.sounds[0], self.download_path, self.email, self.password, args)
        self.assertEqual(download_count, 3)
        update_download_path = os.path.join(self.download_path, 'glass breaking')
        self.assertEqual(len(os.listdir(update_download_path)), download_count)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(os.path.join(cls.download_path, 'toaster pop set'), ignore_errors=True)
        shutil.rmtree(os.path.join(cls.download_path, 'tiger'), ignore_errors=True)
        shutil.rmtree(os.path.join(cls.download_path, 'glass breaking'), ignore_errors=True)


class FreeSoundLoginAuthenticationTest(unittest.TestCase):

    @mock.patch('getpass.getpass')
    @mock.patch('__builtin__.raw_input')
    def test_authenticate(self, input, getpass):
        input.return_value = 'example@gmail.com'
        getpass.return_value = 'MyPassword'
        Credentials = namedtuple('Credentials', ['email', 'password'])
        user_info = Credentials(email=input.return_value, password=getpass.return_value)
        self.assertEqual(automate_download_freesound.authenticate(), user_info)

    @mock.patch('getpass.getpass')
    @mock.patch('__builtin__.raw_input')
    def test_verify_authentication_fail(self, input, getpass):
        '''
        Test verify authentication to make sure fail
        '''
        input.return_value = 'example@gmail.com'
        getpass.return_value = 'MyPassword'
        Credentials = namedtuple('Credentials', ['email', 'password'])
        user_info = Credentials(email=input.return_value, password=getpass.return_value)
        self.assertFalse(automate_download_freesound.verify_authentication(user_info))

    @mock.patch('getpass.getpass')
    @mock.patch('__builtin__.raw_input')
    def test_verify_authentication_pass(self, input, getpass):
        '''
         Test verify authentication to make sure pass
        '''
        input.return_value = os.environ['FREESOUND_EMAIL']
        getpass.return_value = os.environ['FREESOUND_PASSWORD']
        Credentials = namedtuple('Credentials', ['email', 'password'])
        user_info = Credentials(email=input.return_value, password=getpass.return_value)
        self.assertTrue(automate_download_freesound.verify_authentication(user_info))


class CommandLineArgumentsTests(unittest.TestCase):

    def test_parse_args_sound_one(self):
        '''
        Basic test to test for the sound positional argument of parse_args()
        '''
        args = automate_download_freesound.parse_args(['automate_download_freesound.py', 'dogs'])
        self.assertEqual(args.sounds, ['dogs'])
        self.assertEqual(args.downloadpath, os.path.expanduser("~") + "/Downloads/")
        self.assertEqual(args.file_format, None)
        self.assertEqual(args.samplerate, None)
        self.assertFalse(args.advanced_filter)

    def test_parse_args_sound_two(self):
        '''
        Test for multiple arguments that include spaces, but separated by commas
        '''
        args = automate_download_freesound.parse_args(
            ['automate_download_freesound.py', "dogs barking loud, birds chirping loud"])
        self.assertEqual(args.sounds, ['dogs barking loud', 'birds chirping loud'])
        self.assertEqual(args.downloadpath, os.path.expanduser("~") + "/Downloads/")
        self.assertEqual(args.file_format, None)
        self.assertEqual(args.samplerate, None)
        self.assertFalse(args.advanced_filter)

    def test_parse_args_sound_three(self):
        '''
        Test for leading/extra commas as input
        '''
        args = automate_download_freesound.parse_args(
            ['automate_download_freesound.py', "dogs,cats,birds,"])
        self.assertEqual(args.sounds, ['dogs', 'cats', 'birds'])
        self.assertEqual(args.downloadpath, os.path.expanduser("~") + "/Downloads/")
        self.assertEqual(args.file_format, None)
        self.assertEqual(args.samplerate, None)
        self.assertFalse(args.advanced_filter)

    def test_parse_args_format_pass(self):
        args = automate_download_freesound.parse_args(
            ['automate_download_freesound.py', "dogs,cats,birds,", "--file-format", "wav"])
        assert args.file_format in [None, "wav", "flac", "aiff", "ogg", "mp3", "m4a"]

    def test_parse_args_format_fail(self):
        '''Test to see if there is a command line syntax error of wth error code 2
        '''
        with self.assertRaises(SystemExit) as err:
            automate_download_freesound.parse_args(
                ['automate_download_freesound.py', "dogs,cats,birds,", "--file-format", "mp5"])
        self.assertEqual(err.exception.code, 2)

    def test_parse_args_samplerate_pass(self):
        args = automate_download_freesound.parse_args(
            ['automate_download_freesound.py', "dogs,cats,birds,", "--sample-rate", "48000"])
        assert int(args.samplerate) in [None, 11025, 16000, 22050, 44100, 48000, 88200, 96000]

    def test_parse_args_samplerate_fail(self):
        '''Test to see if there is a command line syntax error of wth error code 2
        '''
        with self.assertRaises(SystemExit) as err:
            automate_download_freesound.parse_args(
                ['automate_download_freesound.py', "dogs,cats,birds,", "--sample-rate", "2500"])
        self.assertEqual(err.exception.code, 2)

    def test_parse_args_download_path_pass(self):
        args = automate_download_freesound.parse_args(
            ['automate_download_freesound.py', "dogs,cats,birds,"])
        self.assertEqual(args.downloadpath, os.path.expanduser("~") + "/Downloads/")

    def test_main(self):
        '''
        Test for main function to exit with error code 1 and provide help if no arguments provided
        '''
        with self.assertRaises(SystemExit) as err:
            automate_download_freesound.main(['automate_download_freesound.py'])
        self.assertEqual(err.exception.code, 1)
