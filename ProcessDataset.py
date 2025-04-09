from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time, os, requests
from PIL import Image
from io import BytesIO
import hashlib

QUERIES = [
    "beautiful asian woman full body",
    "girl in a hoodie photoshoot"
]

SAVE_DIR = "RawImgs"
IMAGES_PER_QUERY = 200

def setup_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--log-level=3')
    driver = webdriver.Chrome(options=options)
    return driver

def download_image(url, save_path):
    try:
        response = requests.get(url, timeout=5)
        image = Image.open(BytesIO(response.content))
        image.convert("RGB").save(save_path)
        return True
    except:
        return False

def scrape_images(query, driver, count=200):
    print(f"[+] Scraping: {query}")
    driver.get("https://www.google.com/imghp")
    box = driver.find_element(By.NAME, "q")
    box.send_keys(query)
    box.submit()

    time.sleep(2)
    for _ in range(10):  # Scroll to load more
        driver.execute_script("window.scrollBy(0,10000)")
        time.sleep(1)

    thumbnails = driver.find_elements(By.CSS_SELECTOR, "img.Q4LuWd")
    print(f"[i] Found {len(thumbnails)} thumbnails.")

    save_folder = os.path.join(SAVE_DIR, query.replace(" ", "_"))
    os.makedirs(save_folder, exist_ok=True)

    image_urls = set()
    for thumb in thumbnails:
        try:
            thumb.click()
            time.sleep(0.5)
            images = driver.find_elements(By.CSS_SELECTOR, "img.n3VNCb")
            for img in images:
                src = img.get_attribute("src")
                if src and "http" in src:
                    image_urls.add(src)
                if len(image_urls) >= count:
                    break
        except:
            continue
        if len(image_urls) >= count:
            break

    print(f"[✓] Downloading {len(image_urls)} images for '{query}'")

    for idx, url in enumerate(image_urls):
        filename = hashlib.md5(url.encode()).hexdigest() + ".jpg"
        save_path = os.path.join(save_folder, filename)
        download_image(url, save_path)

if __name__ == "__main__":
    driver = setup_driver()
    for q in QUERIES:
        scrape_images(q, driver, IMAGES_PER_QUERY)
    driver.quit()
