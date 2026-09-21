# @title Setup selenium
import os
import time
import tempfile
import shutil
import logging
import subprocess
import socket
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/webscraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Use these specific ports
WEBDRIVER_PORT = random.randint(4444, 4544)

def verify_chrome_installation():
    try:
        result = subprocess.run(['chrome', '--version'],
                              capture_output=True, text=True)
        logger.info(f"Chrome version: {result.stdout}")
        return True
    except:
        logger.error("Chrome verification failed")
        return False

def verify_chromedriver():
    chromedriver_path = '/usr/local/bin/chromedriver'
    try:
        result = subprocess.run([chromedriver_path, '--version'],
                              capture_output=True, text=True)
        logger.info(f"ChromeDriver version: {result.stdout}")
        st = os.stat(chromedriver_path)
        if not st.st_mode & 0o111:  # Check executable bit
            logger.warning("ChromeDriver not executable, fixing permissions...")
            os.chmod(chromedriver_path, 0o755)
            logger.info("Permissions updated")
        return True
    except:
        logger.error("ChromeDriver verification failed")
        return False

def verify_critical_path(_print=False):
    if _print:
        print(f"ChromeDriver exists: {os.path.exists('/usr/local/bin/chromedriver')}")
        print(f"Chrome exists: {os.path.exists('/usr/local/bin/chrome')}")

        print(f"ChromeDriver executable: {os.access('/usr/local/bin/chromedriver', os.X_OK)}")
        print(f"Chrome executable: {os.access('/usr/local/bin/chrome', os.X_OK)}")

    try:
        subprocess.run(["/usr/local/bin/chromedriver", "--version"], capture_output=True, text=True, check=True)
        if _print:
            print(
                subprocess.run(
                    ["/usr/local/bin/chromedriver", "--version"],
                    capture_output=True,
                    text=True
                ).stdout
            )
        subprocess.run(["/usr/local/bin/chrome", "--version"], check=True)
        if _print:
            print(
                subprocess.run(
                    ["/usr/local/bin/chrome", "--version"],
                    capture_output=True,
                    text=True
                ).stdout
            )
    except subprocess.CalledProcessError as e:
        print(f"Binary test failed: {e}")


def create_service():
    # 1. Verify chromedriver
    chromedriver_path = shutil.which('chromedriver') or '/usr/local/bin/chromedriver'
    if not os.path.exists(chromedriver_path):
        raise FileNotFoundError(f"ChromeDriver missing at {chromedriver_path}")

    # 2. Check port availability
    port = WEBDRIVER_PORT
    s = socket.socket()
    if s.connect_ex(('127.0.0.1', port)) == 0:
        port += 1
    s.close()

    # 3. Ensure log directory
    log_dir = tempfile.gettempdir()
    if not os.access(log_dir, os.W_OK):
        log_dir = '/tmp'

    # 4. Create service
    try:
        return Service(
            executable_path=chromedriver_path,
            port=port,
            service_args=[
                '--verbose',
                '--log-path=/tmp/chromedriver.log'
            ]
        )
    except Exception as e:
        print(f"Service creation failed: {str(e)}")
        return Service()  # Fallback to simplest config

def setup_selenium(debugging=False):
    try:
        logger.info("Initializing Selenium Chrome driver...")
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-notifications")
        options.add_argument("--remote-debugging-port=9222")

        # Disable automation flag
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.notifications": 2,  # Disable notifications
            "profile.default_content_setting_values.clipboard": 1,
            "profile.default_content_setting_values.clipboard_read": 1,
            "profile.default_content_setting_values.clipboard_write": 1
        })

        # Mimic a real browser's user agent
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

        if debugging:
            logger.info("Verifying ChromeDriver...")
            verifying_chromedriver = verify_chromedriver()
            logger.info(f"ChromeDriver verification: {verifying_chromedriver}")

        chromedriver_path = "/usr/local/bin/chromedriver"
        # os.chmod(chromedriver_path, 0o755)  # Make sure it's executable
        logger.info(f"Setting executable permission for {chromedriver_path}")

        service = create_service()
        logger.info("Service created")

        if debugging:
            verify_critical_path(_print=debugging)

        try:
            logger.info("Attempting Chrome initialization...")
            driver = webdriver.Chrome(
                options=options,
                service=service
            )
            logger.info("Successfully initialized Chrome driver!")
            return driver

        except Exception as e:
            logger.error(f"Initialization failed completely: {str(e)}")
            try:
                from subprocess import run
                run([chromedriver_path, "--version"], check=True)
                run(["/usr/local/bin/chrome", "--version"], check=True)
            except Exception as sub_e:
                logger.error(f"Subprocess check failed: {str(sub_e)}")
            raise

    except Exception as e:
        logger.error("Possible causes:")
        logger.error("- Missing or incompatible ChromeDriver")
        logger.error("- Chrome binary not found")
        logger.error("- Insufficient permissions")
        logger.error("- Missing system dependencies")
        raise RuntimeError(f"Failed to initialize WebDriver: {str(e)}")

def check_selenium_environment(debugging=False):
    try:
        driver = setup_selenium(debugging=debugging)
        driver.quit()
        print("Selenium environment check passed successfully. WebDriver initialised and terminated correctly.")
        return True
    except Exception as e:
        print(f"Selenium environment check failed: {e}")
        return False


# print(verify_chrome_installation())
# print(verify_chromedriver())
# print(verify_critical_path())
print(check_selenium_environment(debugging=True))
