from selenium import selenium
import unittest
import os

class GeneralTests(unittest.TestCase):
    seleniumHost = 'localhost'
    seleniumPort = str(4444)
    browserStartCommand = "*firefox"
    browserURL = "http://localhost:8000"

    def setUp(self):
        self.selenium = selenium(self.seleniumHost, self.seleniumPort,
                                 self.browserStartCommand, self.browserURL)
        self.selenium.start()

    def login(self):
        selenium = self.selenium
        selenium.open("/")
        selenium.click("login")
        selenium.wait_for_page_to_load(5000)
        selenium.type("email", "selenium@example.com")
        selenium.click("submit-login")
        selenium.wait_for_page_to_load(5000)

    def add_program(self):
        selenium = self.selenium
        selenium.answer_on_next_prompt("fib1")
        selenium.click("add_button")
        selenium.wait_for_page_to_load(5000)

    def del_program(self):
        selenium = self.selenium
        selenium.answer_on_next_prompt("fib1")
        selenium.click("del_button")
        selenium.wait_for_page_to_load(5000)

    def get_details(self):
        selenium = self.selenium
        selenium.click('xpath=//a[text()="example"]')
        selenium.wait_for_page_to_load(5000)

    def test_login(self):
        selenium = self.selenium
        self.login()
        self.failUnless(selenium.is_text_present("example"))
        self.failUnless(selenium.is_text_present("On this page"))
        self.failUnless(selenium.is_text_present("Add Program"))
        self.failUnless(selenium.is_text_present("Del Program"))

    def test_add_program(self):
        selenium = self.selenium
        self.login()
        self.add_program()
        self.failUnless(selenium.is_text_present("example"))
        self.failUnless(selenium.is_text_present("fib1"))

    def test_del_program(self):
        selenium = self.selenium
        self.login()
        self.del_program()
        self.failUnless(selenium.is_text_present("example"))
        self.failUnless(not selenium.is_text_present("fib1"))

    def test_get_details(self):
        selenium = self.selenium
        self.login()
        self.get_details()
        self.failUnless(selenium.is_element_present("run"))
        self.failUnless(selenium.is_element_present("reset"))
        self.failUnless(selenium.is_element_present("update"))

    def test_run(self):
        selenium = self.selenium
        self.login()
        for i in range(0,10):
            selenium.open("/run/example/")
            self.failUnless(not selenium.is_text_present("Request information"))
            self.failUnless(selenium.is_text_present("registers"))
            self.failUnless(selenium.is_text_present("output"))



    def tearDown(self):
        self.selenium.stop()

if __name__ == "__main__":
    unittest.main()




