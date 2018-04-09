"""
Unit tests for test_automate_download_freesound.py
Run with:
$ pytest test_automate_download_freesound.py -v
"""
import unittest
import automate_download_freesound
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException


class FreeSoundOrgLoginTest(unittest.TestCase):
    '''using the setUpClass() and tearDownClass() methods along with the @classmethod decorator.
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
        """
        Helper method to confirm the presence of an element on page
        :params how: By locator type
        :params what: locator value
        """
        try:
            self.driver.find_element(by=how, value=what)
        except NoSuchElementException:
            return False
        return True


class FreeSoundSearchByTextTest(unittest.TestCase):
    '''using the setUpClass() and tearDownClass() methods along with the @classmethod decorator.
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
        """
        Helper method to confirm the presence of an element on page
        :params how: By locator type
        :params what: locator value
        """
        try:
            self.driver.find_element(by=how, value=what)
        except NoSuchElementException:
            return False
        return True


class FreeSoundSearchTest(unittest.TestCase):
    '''using the setUpClass() and tearDownClass() methods along with the @classmethod decorator.
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
        """
        Helper method to confirm the presence of an element on page
        :params how: By locator type
        :params what: locator value
        """
        try:
            self.driver.find_element(by=how, value=what)
        except NoSuchElementException:
            return False
        return True


class FreeSoundOrgAdvancedFilter(unittest.TestCase):
    '''using the setUpClass() and tearDownClass() methods along with the @classmethod decorator.
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
        """
        Helper method to confirm the presence of an element on page
        :params how: By locator type
        :params what: locator value
        """
        try:
            self.driver.find_element(by=how, value=what)
        except NoSuchElementException:
            return False
        return True

class SimulateDownloadIntegrationTest(unittest.TestCase):

    pass


class CommandLineArgumentsTests(unittest.TestCase):

    def test_parse_args_sound_one(self):
        '''
        Basic test to test for the sound positional argument of parse_args()
        '''
        args = automate_download_freesound.parse_args(['automate_download_freesound.py', 'dogs'])
        self.assertEqual(args.sounds, ['dogs'])
        self.assertEqual(args.downloadpath, None)
        self.assertEqual(args.file_format, 'wav')
        self.assertEqual(args.samplerate, 48000)
        self.assertFalse(args.advanced_filter)

    def test_parse_args_sound_two(self):
        '''
        Test for multiple arguments that include spaces, but separated by commas
        '''
        args = automate_download_freesound.parse_args(
            ['automate_download_freesound.py', "dogs barking loud, birds chirping loud"])
        self.assertEqual(args.sounds, ['dogs barking loud', 'birds chirping loud'])
        self.assertEqual(args.downloadpath, None)
        self.assertEqual(args.file_format, 'wav')
        self.assertEqual(args.samplerate, 48000)
        self.assertFalse(args.advanced_filter)

    def test_parse_args_sound_three(self):
        '''
        Test for leading/extra commas as input
        '''
        args = automate_download_freesound.parse_args(
            ['automate_download_freesound.py', "dogs,cats,birds,"])
        self.assertEqual(args.sounds, ['dogs', 'cats', 'birds'])
        self.assertEqual(args.downloadpath, None)
        self.assertEqual(args.file_format, 'wav')
        self.assertEqual(args.samplerate, 48000)
        self.assertFalse(args.advanced_filter)

    def test_parse_args_format_one(self):
        args = automate_download_freesound.parse_args(
            ['automate_download_freesound.py', "dogs,cats,birds,", "--file-format", "wav"])
        assert args.file_format in ["wav", "flac", "aiff", "ogg", "mp3", "m4a"]

    def test_parse_args_format_two(self):
        with self.assertRaises(SystemExit):
            automate_download_freesound.parse_args(
                ['automate_download_freesound.py', "dogs,cats,birds,", "--file-format", "mp5"])

    def test_parse_args_samplerate_one(self):
        args = automate_download_freesound.parse_args(
            ['automate_download_freesound.py', "dogs,cats,birds,", "--sample-rate", "48000"])
        assert int(args.samplerate) in [11025, 16000, 22050, 44100, 48000, 88200, 96000]

    def test_parse_args_samplerate_two(self):
        with self.assertRaises(SystemExit):
            automate_download_freesound.parse_args(
                ['automate_download_freesound.py', "dogs,cats,birds,", "--sample-rate", "2500"])

    def test_main(self):
        '''
        Test for main function to exit if no arguments provided
        '''
        with self.assertRaises(SystemExit):
            automate_download_freesound.main(['automate_download_freesound.py'])
