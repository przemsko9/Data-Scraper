from selenium.webdriver import Chrome
from selenium.webdriver import ChromeOptions
from selenium.webdriver.chrome.service import Service
from pip._internal.network.session import user_agent


def set_driver():
    # Selenium Chrome browser setup
    options = ChromeOptions()
    chrome_prefs = {"profile.default_content_setting_values": {"images": 2}}
    options.experimental_options["prefs"] = chrome_prefs
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument('user-agent={0}'.format(user_agent))
    options.headless = True
    service = Service('D:\Python\Python Projects\Clothes Scraping\chromedriver\chromedriver.exe')
    driver = Chrome(service=service, options=options)
    driver.set_page_load_timeout(1000)
    driver.set_window_size(1800, 1000)

    return driver
