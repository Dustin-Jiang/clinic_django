from django.test import TestCase
from django.test import LiveServerTestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from .models import Record, ClinicUser
import time

# Create your tests here.

# class BasicTest(StaticLiveServerTestCase):

#     @classmethod
#     def setUpClass(cls):
#         profile = webdriver.FirefoxProfile()
#         profile.set_preference('intl.accept_languages', 'zh-cn')
#         profile.update_preferences()                                                                                                                                             
#         cls.browser = webdriver.Firefox(profile)
#         cls.browser.implicitly_wait(10)
#         super().setUpClass()
    
#     @classmethod
#     def tearDownClass(cls):
#         cls.browser.quit()
#         super().tearDownClass

#     def test_regist(self):
#         browser = self.browser
#         browser.set_page_load_timeout(5)
#         try:
#             browser.get(self.live_server_url)
#         except:
#             pass
#         browser.find_element_by_id('username').send_keys('1120161730')
#         browser.find_element_by_id('password').send_keys('1120161730')
#         browser.find_element_by_class_name('btn-submit').click()
#         browser.find_element_by_css_selector("input[name=name]").send_keys('武上博')
#         browser.find_element_by_css_selector("input[name=phone]").send_keys('18801234123')
#         browser.find_element_by_css_selector('input[name=school]').send_keys('计算机学院')
#         browser.find_element_by_css_selector('button.success').click()

#         user = ClinicUser.objects.first()
#         self.assertEqual(user.username, '1120161730')
#         self.assertEqual(user.realname, '武上博')
#         self.assertEqual(user.phone_num, '18801234123')
#         self.assertEqual(user.school, '计算机学院')

#     def fill_reservation(self):
#         browser = self.browser
#         browser.get(self.live_server_url + '/student/#/reservation')

    
#     def test_reservation(self):
#         browser = self.browser
#         browser.get(self.live_server_url + '/student/#/reservation')

