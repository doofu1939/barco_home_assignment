import unittest
import configparser
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

class checkWarranty(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        self.targetUrl = "https://www.barco.com/en/clickshare/support/warranty-info"
        self.driver.get(self.targetUrl)
        self.config = configparser.RawConfigParser()
        self.config.read('myConfig.cfg')

    def test_find_required_element(self):
        driver = self.driver
        intro = driver.find_element(By.CLASS_NAME, "c-warranty__intro")
        driver.implicitly_wait(5)
        serialNum = driver.find_element(By.ID, "SerialNumber")     
        driver.implicitly_wait(5)
        get_info_btn = driver.find_element(By.XPATH, '//button[normalize-space()="Get info"]')
        driver.implicitly_wait(5)

        assert intro.text == self.config.get("StringValue", "INTRO_TEXT")
        assert get_info_btn.text == self.config.get("StringValue", "BUTTON_TEXT")
        assert driver.find_element(By.LINK_TEXT, self.config.get("StringValue", "WARRANTY_POLICY"))

    def test_input_valid_serial_number_and_click(self):
        driver = self.driver
        valid_serial = self.config.get("SerialNumber", "VALID_SERIAL")
        driver.find_element(By.ID, "SerialNumber").send_keys(valid_serial)
        driver.find_element(By.XPATH, '//button[normalize-space()="Get info"]').click()
        try:
            result = WebDriverWait(driver, 10).until(
                         EC.presence_of_element_located((By.CLASS_NAME, "c-result-tile__dl"))
                     )
        finally:
            pass
        
        children = result.find_elements(By.XPATH, ".//*")
        result_mapping, i = {}, 0
        while i<len(children):
            if i%2 == 1:
                result_mapping[children[i-1].text] = children[i].text
            i+=1

        assert result_mapping[self.config.get("WarrantyInfo", "DESCRIPTION")] == "CLICKSHARE CX-50 SET NA"
        assert result_mapping[self.config.get("WarrantyInfo", "PART_NUMBER")] == "R9861522NA"
        assert result_mapping[self.config.get("WarrantyInfo", "INSTALLATION_DATE")] == "09/28/2020 00:00:00"
        assert result_mapping[self.config.get("WarrantyInfo", "WARRANTY_END_DATE")] == "09/27/2021 00:00:00"
        assert result_mapping[self.config.get("WarrantyInfo", "SERVICE_CONTRACT_END_DATE")] == "01/01/0001 00:00:00"
        assert driver.find_element(By.LINK_TEXT, self.config.get("StringValue", "WARRANTY_POLICY"))
        
    def test_input_too_short_serial_number_and_click(self):
        driver = self.driver
        too_short_serial = self.config.get("SerialNumber", "TOO_SHORT_SERIAL")
        driver.find_element(By.ID, "SerialNumber").send_keys(too_short_serial)
        driver.find_element(By.XPATH, '//button[normalize-space()="Get info"]').click()
        driver.implicitly_wait(5)

        assert self.config.get("StringValue", "MINIMUM_CHAR_REQUIRED") in driver.page_source
        assert driver.find_element(By.LINK_TEXT, self.config.get("StringValue", "WARRANTY_POLICY"))
        
    def test_empty_serial_number_and_click(self, empty_input = ""):
        driver = self.driver
        driver.find_element(By.ID, "SerialNumber").send_keys(empty_input)
        driver.find_element(By.XPATH, '//button[normalize-space()="Get info"]').click()
        driver.implicitly_wait(5)

        assert self.config.get("StringValue", "EMPTY_INPUT_NOTIFICATION") in driver.page_source
        assert driver.find_element(By.LINK_TEXT, self.config.get("StringValue", "WARRANTY_POLICY"))
        
    def test_invalid_serial_number_and_click(self):
        driver = self.driver
        invalid_input = self.config.get("SerialNumber", "INVALID_SERIAL_ALL_CHAR")
        driver.find_element(By.ID, "SerialNumber").send_keys(invalid_input)
        driver.find_element(By.XPATH, '//button[normalize-space()="Get info"]').click()
        driver.implicitly_wait(5)

        assert self.config.get("StringValue", "INVALID_INPUT_NOTIFICATION") in driver.page_source
        assert driver.find_element(By.LINK_TEXT, self.config.get("StringValue", "WARRANTY_POLICY"))
            
    def test_non_exist_serial_number_and_click(self):
        driver = self.driver
        non_exist = self.config.get("SerialNumber", "NON_EXISTING_SERIAL")
        driver.find_element(By.ID, "SerialNumber").send_keys(non_exist)
        driver.find_element(By.XPATH, '//button[normalize-space()="Get info"]').click()
        driver.implicitly_wait(5)

        assert driver.find_element(By.LINK_TEXT, self.config.get("StringValue", "WARRANTY_POLICY"))
            
    def tearDown(self):
        self.driver.close()

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(checkWarranty)
    unittest.TextTestRunner().run(suite)
    
    