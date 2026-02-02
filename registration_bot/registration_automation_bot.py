import os
import time
import random
import string
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

class RegistrationBot:
    def __init__(self, base_url, scenario_type='standard', service_type='type_a', enable_screenshots=False, screenshot_path=None):
        """
        scenario_type: 'standard' or 'premium'
        service_type: 'type_a', 'type_b', 'other'
        enable_screenshots: boolean
        screenshot_path: folder path for reports
        """
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        self.driver.maximize_window()
        self.base_url = base_url
        self.wait = WebDriverWait(self.driver, 15)
        self.scenario_type = scenario_type
        self.service_type = service_type
        
        self.screenshot_enabled = enable_screenshots
        self.screenshot_folder = screenshot_path if screenshot_path else "test_reports"
        
        if self.screenshot_enabled:
            self.setup_screenshot_folder()
        
        self.used_codes = set()
        self.registration_count = 0
        
    def setup_screenshot_folder(self):
        """Creates directory for test artifacts"""
        try:
            if not os.path.exists(self.screenshot_folder):
                os.makedirs(self.screenshot_folder)
                print(f"✓ Directory created: {self.screenshot_folder}")
        except Exception as e:
            print(f"✗ Failed to create directory: {e}")
            self.screenshot_enabled = False
        
    def take_screenshot(self, step_name):
        """Saves a screenshot with timestamp"""
        if self.screenshot_enabled:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            reg_id = f"id{self.registration_count:03d}"
            filename = os.path.join(self.screenshot_folder, f"{reg_id}_{step_name}_{timestamp}.png")
            self.driver.save_screenshot(filename)
            print(f"📸 Screenshot saved: {filename}")
    
    def generate_unique_id(self):
        """Generates a unique format: 2 letters + 6 digits"""
        while True:
            letters = ''.join(random.choice(string.ascii_uppercase) for _ in range(2))
            numbers = ''.join(random.choice(string.digits) for _ in range(6))
            code = letters + numbers
            if code not in self.used_codes:
                self.used_codes.add(code)
                return code
    
    def click_virtual_keyboard(self, char):
        """Interaction with custom on-screen UI keyboard"""
        try:
            if char == ' ':
                # Selector for spacebar button
                xpath = "//button[contains(@class, 'spacebar-class')]" 
            else:
                xpath = f"//button[text()='{char}' or text()='{char.lower()}' or text()='{char.upper()}']"
            
            button = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            button.click()
            time.sleep(random.uniform(0.1, 0.3))
            return True
        except Exception as e:
            print(f"✗ UI Key '{char}' not found: {e}")
            return False
    
    def type_text_via_ui(self, text):
        """Types text using the on-screen keyboard simulation"""
        print(f"⌨ Typing: '{text}'")
        for char in text:
            if not self.click_virtual_keyboard(char):
                return False
        return True
    
    def click_next(self):
        """Universal 'Next' button handler"""
        try:
            next_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'NEXT')]")))
            next_btn.click()
            time.sleep(1.5)
            return True
        except Exception as e:
            print(f"✗ 'Next' button error: {e}")
            return False

    # --- REGISTRATION STEPS ---

    def step_1_user_type(self):
        print(f"\n--- STEP 1: User Type Selection [Reg #{self.registration_count}] ---")
        self.driver.get(self.base_url)
        time.sleep(1)
        
        btn_text = "STANDARD_USER" if self.scenario_type == 'standard' else "PREMIUM_USER"
        success = self.wait_and_click_text(btn_text)
        if success: self.take_screenshot("user_type_selected")
        return success

    def step_2_service_selection(self):
        print("\n--- STEP 2: Service Selection ---")
        service_map = {'type_a': 'SERVICE_ALPHA', 'type_b': 'SERVICE_BETA'}
        btn_text = service_map.get(self.service_type, 'DEFAULT_SERVICE')
        
        success = self.wait_and_click_text(btn_text)
        if success: self.take_screenshot("service_selected")
        return success

    def step_3_time_slot(self):
        print("\n--- STEP 3: Time Slot Selection ---")
        try:
            # Finding available time buttons
            slots = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "button.time-slot-btn")))
            if slots:
                slots[0].click()
                print(f"✓ Time slot selected: {slots[0].text}")
                self.take_screenshot("time_selected")
                return True
            return False
        except Exception as e:
            print(f"✗ Time selection error: {e}")
            return False

    def step_4_fill_data(self):
        """Automated form filling with random data"""
        print("\n--- STEP 4: Form Data Entry ---")
        
        # 1. Unique ID
        if not self.type_text_via_ui(self.generate_unique_id()): return False
        self.click_next()
        
        # 2. Random Name
        name = random.choice(string.ascii_uppercase) + " " + random.choice(string.ascii_uppercase)
        if not self.type_text_via_ui(name): return False
        self.click_next()
        
        # 3. Email
        if not self.type_text_via_ui("test@example.com"): return False
        self.click_next()
        
        self.take_screenshot("form_completed")
        return True

    def wait_and_click_text(self, text):
        try:
            btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, f"//button[contains(text(), '{text}')]")))
            btn.click()
            return True
        except:
            return False

    def run_full_cycle(self):
        try:
            if not self.step_1_user_type(): return False
            if not self.step_2_service_selection(): return False
            if not self.step_3_time_slot(): return False
            if not self.step_4_fill_data(): return False
            
            print("\n✅ Registration completed successfully!")
            self.take_screenshot("final_success")
            time.sleep(5)
            return True
        except Exception as e:
            print(f"❌ Critical failure: {e}")
            return False

    def close(self):
        self.driver.quit()

# --- EXECUTION BLOCK ---
if __name__ == "__main__":
    URL = "https://demo-queue-system.io"
    PATH = "./test_results"
    
    bot = RegistrationBot(URL, scenario_type='standard', enable_screenshots=True, screenshot_path=PATH)
    try:
        bot.run_full_cycle()
    finally:
        bot.close()
