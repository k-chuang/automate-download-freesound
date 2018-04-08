"""
Unit tests for test_automate_download_freesound.py
Run with:
$ pytest test_automate_download_freesound.py -v
"""
import unittest
import automate_download_freesound


class CommandLineTests(unittest.TestCase):

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

    def test_main(self):
        '''
        Test for main function to exit if no arguments provided
        '''
        with self.assertRaises(SystemExit):
            automate_download_freesound.main(['automate_download_freesound.py'])