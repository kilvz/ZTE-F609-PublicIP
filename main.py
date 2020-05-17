import time
import json
import re
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options

logging.basicConfig(filename='publicip.log', format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S', filemode='a')
logger = logging.getLogger()
logger.setLevel(logging.INFO)
userlog = logging.StreamHandler()
userlog.setLevel(logging.INFO)
logger.addHandler(userlog)

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--window-size=1024x768')
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--allow-insecure-localhost')
chrome_options.add_argument('--acceptInsecureCerts')

public = False
retry = 0
driver = webdriver.Chrome(chrome_options=chrome_options, executable_path='/srv/torrent/downloads/publicip/chromedriver')

def login(user, password):
	driver.find_element(By.ID, "Frm_Username").send_keys(user)
	driver.find_element(By.ID, "Frm_Password").send_keys(password)
	driver.find_element(By.ID, "LoginId").click()
	logger.info("Logged in")

def checkip():
	wait = WebDriverWait(driver, 10)
	wait.until(EC.frame_to_be_available_and_switch_to_it(1))
	driver.find_element(By.ID, "Fnt_mmStatu").click()
	driver.find_element(By.ID, "smWanStatu").click()
	driver.find_element(By.ID, "ssmETHWANv46Conn").click()
	ip = driver.find_element(By.ID, "TextPPPIPAddress0").get_attribute("value")
	status = driver.find_element(By.ID, "TextPPPConStatus0").get_attribute("value")
	logger.info("WAN IP is %s, status %s", ip, status)
	private = re.compile("10\..")
	isprivate = bool(re.match(private,ip))
	logger.info("Private IP is %s", isprivate)
	return isprivate, status

def alwayson():
	wait = WebDriverWait(driver, 10)
	wait.until(EC.frame_to_be_available_and_switch_to_it(1))
	driver.find_element(By.ID, "mmNet").click()
	driver.find_element(By.ID, "smWANConn").click()
	driver.find_element(By.ID, "ssmETHWAN46Con").click()
	driver.find_element(By.ID, "Frm_WANCName0").click()
	dropdown = driver.find_element(By.ID, "Frm_WANCName0")
	dropdown.find_element(By.XPATH, "//option[. = 'omci_ipv4_pppoe_1']").click()
	driver.find_element(By.ID, "Frm_ConnTrigger").click()
	dropdown = driver.find_element(By.ID, "Frm_ConnTrigger")
	dropdown.find_element(By.XPATH, "//option[. = 'Always On']").click()
	driver.find_element(By.CSS_SELECTOR, "#Frm_ConnTrigger > option:nth-child(1)").click()
	driver.find_element(By.ID, "Btn_DoEdit").click()
	logger.info("Changed connection trigger to Always On")
	time.sleep(2)

def manual():
	wait = WebDriverWait(driver, 10)
	wait.until(EC.frame_to_be_available_and_switch_to_it(1))
	driver.find_element(By.ID, "mmNet").click()
	driver.find_element(By.ID, "smWANConn").click()
	driver.find_element(By.ID, "ssmETHWAN46Con").click()
	driver.find_element(By.ID, "Frm_WANCName0").click()
	dropdown = driver.find_element(By.ID, "Frm_WANCName0")
	dropdown.find_element(By.XPATH, "//option[. = 'omci_ipv4_pppoe_1']").click()
	ismanual = driver.find_element(By.ID, "Frm_ConnTrigger").get_attribute("value")
	if ismanual == "AlwaysOn":
		driver.find_element(By.ID, "Frm_ConnTrigger").click()
		dropdown = driver.find_element(By.ID, "Frm_ConnTrigger")
		dropdown.find_element(By.XPATH, "//option[. = 'Manual']").click()
		driver.find_element(By.CSS_SELECTOR, "#Frm_ConnTrigger > option:nth-child(3)").click()
		driver.find_element(By.ID, "Btn_DoEdit").click()
		logger.info("Connection trigger changed to manual")
		time.sleep(2)
	else:
		logger.info("Connection trigger is already manual")

user = "user"
password = "chrisg661"
driver.get("https://192.168.1.1/")
login(user, password)

while public == False:
	isprivate, status = checkip()
	if ((isprivate == False) and (status == "Connected")):
		logger.info("WAN IP is Public, aborting")
		driver.find_element(By.LINK_TEXT, "Logout").click()
		logger.info("Logged out")
		public = True
		break
	else:
		manual()
		time.sleep(2)
		alwayson()
		time.sleep(5)
	logger.info("Connection retry %s", retry)
	retry += 1

logger.info("JOB DONE with %s try!", retry)
logger.info("|-----------------------------------------|")
driver.close()
driver.quit()
quit()