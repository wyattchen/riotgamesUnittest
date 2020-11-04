import unittest 
import requests
from views import getLOLinfo, getMatchList, add_record


class TestLeagueFunctions(unittest.TestCase):
    def test_getLOLinfo(self):

        assert isinstance(getLOLinfo(), dict)

    def test_getMatchList(self):

        assert isinstance(getMatchList(), dict)


    