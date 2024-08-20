import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image
import io
import time

# Function to fetch sentiment analysis image
def fetch_sentiment_image(company_name):
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Ensure the browser runs headless
    chrome_options.add_argument("--disable-gpu")  # Disable GPU
    chrome_options.add_argument("--window-size=1920,1080")  # Set the window size to ensure everything is visible

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # Open the website
        url = "https://www.csc2.ncsu.edu/faculty/healey/social-media-viz/production/"
        driver.get(url)

        # Wait for the search input to be present
        search_box = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#query-inp"))
        )

        # Input the company name
        search_box.clear()
        search_box.send_keys(company_name)

        # Submit the form by clicking the 'Query' button
        query_button = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#query-btn"))
        )
        query_button.click()

        # Wait for 30 seconds to ensure the posts are fully loaded
        time.sleep(30)

        # Locate the image using the provided selector
        image_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#post-canvas"))
        )

        # Capture the image from the element
        image_data = image_element.screenshot_as_png

        # Return the image data
        return Image.open(io.BytesIO(image_data))

    except TimeoutException as e:
        st.error("Failed to load the sentiment analysis image. The element might not be present or the page took too long to load.")
        driver.save_screenshot("debug_screenshot.png")
        st.image("debug_screenshot.png", caption="Debug Screenshot")
    finally:
        driver.quit()