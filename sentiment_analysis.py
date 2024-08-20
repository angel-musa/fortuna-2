import streamlit as st
from PIL import Image
import io
import requests
from bs4 import BeautifulSoup

# Function to fetch sentiment analysis image
def fetch_sentiment_image(company_name):
    try:
        # Base URL for the sentiment analysis website
        url = "https://www.csc2.ncsu.edu/faculty/healey/social-media-viz/production/"

        # Send a GET request to the website
        response = requests.get(url)
        
        if response.status_code != 200:
            st.error("Failed to load the sentiment analysis website.")
            return None

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Simulate entering the company name in the search box
        search_box = soup.find("input", {"id": "query-inp"})
        if not search_box:
            st.error("Search box not found on the page.")
            return None

        # Simulate the process that would occur when inputting the company name
        # This approach assumes a basic GET request is sufficient, which may need to be adjusted
        # based on the actual website's form handling.
        form_data = {'query': company_name}
        response = requests.post(url, data=form_data)
        
        # Parse the new content with the search results
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the sentiment analysis image
        image_element = soup.find("img", {"id": "post-canvas"})
        if not image_element:
            st.error("Sentiment analysis image not found.")
            return None

        # Get the image URL and fetch the image
        image_url = url + image_element['src']
        image_response = requests.get(image_url)
        
        if image_response.status_code != 200:
            st.error("Failed to load the sentiment analysis image.")
            return None

        # Convert the image to a PIL Image object and return it
        image = Image.open(io.BytesIO(image_response.content))
        return image

    except Exception as e:
        st.error("An error occurred while fetching the sentiment analysis image.")
        st.error(str(e))
        return None
