import os
import pandas as pd
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
    chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
    chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems

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
    finally:
        driver.quit()

def save_image(image, company_name):
    # Ensure the sentiment_images directory exists
    output_dir = "company_images"
    os.makedirs(output_dir, exist_ok=True)

    # Save the image as {company_name}.png
    image_path = os.path.join(output_dir, f"{company_name}.png")
    image.save(image_path)
    print(f"Image saved: {image_path}")

# Read the Excel file and extract company names
excel_path = r"C:\projects\fortunafinal\Scripts\data new.xlsx"
sheet_name = "short"

try:
    df = pd.read_excel(excel_path, sheet_name=sheet_name)
    company_names = df["Company"].dropna().unique()

    for company_name in company_names:
        print(f"Processing: {company_name}")
        sentiment_image = fetch_sentiment_image(company_name)
        if sentiment_image:
            save_image(sentiment_image, company_name)

except FileNotFoundError:
    print(f"Excel file not found: {excel_path}")
except KeyError:
    print(f"Column 'Company' not found in sheet '{sheet_name}'")
except Exception as e:
    print(f"An error occurred: {str(e)}")
