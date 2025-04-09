import os
import requests
import base64
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from tqdm import tqdm

def create_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def scroll_down(driver, scroll_pause_time=1, scroll_limit=3):
    last_height = driver.execute_script("return document.body.scrollHeight")
    for _ in range(scroll_limit):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause_time)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
        
def scrape_all_images(driver):
    try:
        images = driver.find_elements(By.TAG_NAME, 'img')
        image_urls = []
        for img in images:
            src = img.get_attribute('src') or img.get_attribute('data-src')
            if src and not src.startswith('data:image/gif'):
                width = int(img.get_attribute('width') or 0)
                height = int(img.get_attribute('height') or 0)
                if width >= 100 and height >= 100:
                    image_urls.append(src)
        return image_urls
    except Exception as e:
        print(f"Error scraping images: {e}")
        return []

def save_image(image_url, folder_name, file_name, retry_count=3):
    try:
        file_path = os.path.join(folder_name, f"{file_name}.jpg")

        if image_url.startswith('data:image/'):
            header, encoded = image_url.split(',', 1)
            image_data = base64.b64decode(encoded)
            with open(file_path, 'wb') as f:
                f.write(image_data)
        else:
            for attempt in range(retry_count):
                response = requests.get(image_url, timeout=10)
                if response.status_code == 200:
                    with open(file_path, 'wb') as f:
                        f.write(response.content)
                    return
                else:
                    print(f"Retry {attempt+1} failed for {image_url}")
                    time.sleep(1)
    except Exception as e:
        print(f"Error saving {file_name}: {e}")

def scrape_and_save_images(base_folder, search_term="", category=0, num_images=10):
    folder_name = "RawImgs"
    folder_path = os.path.join(base_folder, folder_name)

    os.makedirs(folder_path, exist_ok=True)
    driver = create_driver()
    driver.get(f"https://www.google.com/search?q={search_term}&tbm=isch")

    scroll_down(driver, scroll_pause_time=1, scroll_limit=3)

    image_urls = scrape_all_images(driver)[:num_images]
    print(f"Found {len(image_urls)} images for: '{search_term}'")

    for index, image_url in enumerate(tqdm(image_urls, desc="Downloading"), start=1):
        file_name = f"{category}_{index}"
        save_image(image_url, folder_path, file_name)

    driver.quit()
    print(f"Done! Images saved to: {folder_path}")

if __name__ == "__main__":
    base_folder = os.getcwd()
    scrape_and_save_images(base_folder, search_term="Pretty girl on the beach", category=0, num_images=100)
    scrape_and_save_images(base_folder, search_term="Hot girl in hoodie", category=1, num_images=100)

