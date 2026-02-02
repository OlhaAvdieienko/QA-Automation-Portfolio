import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def open_incognito_windows(url, credentials_list):
    """
    Automates login into multiple accounts simultaneously in incognito mode.
    Useful for testing multi-user environments or system load.
    """
    drivers = []
    chrome_options = Options()
    chrome_options.add_argument("--incognito")
    chrome_options.add_experimental_option("detach", True)

    # Automatic driver management
    service = Service(ChromeDriverManager().install())
    wait_time = 15

    for idx, creds in enumerate(credentials_list):
        print(f"\nProcessing account {idx + 1}: {creds['login']}")

        driver = webdriver.Chrome(service=service, options=chrome_options)
        drivers.append(driver) 
        wait = WebDriverWait(driver, wait_time)

        try:
            driver.get(url)
            print(f"   Opened: {url}")

            # Locating and filling the Company field
            company_field = wait.until(EC.element_to_be_clickable((By.ID, "Company")))
            company_field.clear()
            company_field.send_keys(creds["company"])

            # Locating and filling the Login field
            login_field = wait.until(EC.element_to_be_clickable((By.ID, "Login")))
            login_field.clear()
            login_field.send_keys(creds["login"])

            # Locating and filling the Password field
            password_field = wait.until(EC.element_to_be_clickable((By.ID, "Password")))
            password_field.clear()
            password_field.send_keys(creds["password"])

            print("   Form fields populated successfully")

            # Login button interaction via XPATH
            login_button = wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[@type='submit' and contains(@class,'btn-primary')]")
                )
            )
            login_button.click() 
            print("   Login action performed")

        except Exception as e:
            print(f"   ERROR for {creds['login']}: {str(e)}")

        time.sleep(1)

    input("\nPress Enter to close all browser windows...")
    
    for d in drivers:
        try:
            d.quit()
        except:
            pass
    print("All sessions closed.")

# === TEST DATA (Placeholders) ===
credentials_list = [
    {"company": "test_corp_1", "login": "qa_user_1", "password": "secure_password123"},
    {"company": "test_corp_1", "login": "qa_user_2", "password": "secure_password123"},
    {"company": "test_corp_1", "login": "qa_user_3", "password": "secure_password123"}
]

# === EXECUTION ===
if __name__ == "__main__":
    # URL is hidden for privacy. Replace with your testing environment URL.
    TARGET_URL = "https://your-testing-environment.io/login" 
    open_incognito_windows(TARGET_URL, credentials_list)
