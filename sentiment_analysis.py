import streamlit as st
from PIL import Image
import os

# Function to fetch sentiment analysis image from local repository
def fetch_sentiment_image(company_name):
    # Define the path to the image file within the company_images folder
    image_dir = "company_images"
    image_path = os.path.join(image_dir, f"{company_name}.png")

    # Check if the image file exists
    if os.path.exists(image_path):
        # Open the image using PIL
        image = Image.open(image_path)
        return image
    else:
        st.error(f"Sentiment analysis image for {company_name} not found.")
        return None
