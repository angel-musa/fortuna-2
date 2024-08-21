# Fortuna - Stock Analysis and Forecasting App 💸

Fortuna is a Streamlit-based application designed to help users analyze stocks, forecast future prices, and perform sentiment analysis based on social media data. The app features a user-friendly interface with various tools and functionalities to assist with investment decisions.

## Features

- **Stock Overview**: Get detailed information about a stock, including its sector, industry, website, and a company overview.
- **Financials**: View key financial metrics such as revenue, earnings, EPS, PE ratio, and profit margins.
- **Latest News**: Stay updated with the latest news articles related to the selected stock.
- **Forecast**: Forecast future stock prices using machine learning models, and visualize the results with interactive plots.
- **Sentiment Analysis**: Analyze the sentiment of social media posts related to a specific stock. The sentiment images are updated automatically every hour and stored in the GitHub repository.

## How It Works

### 1. Authentication
The app features a login system where users can log in to access their personalized watchlist. After logging in, users can add stocks to their watchlist and view the corresponding stock data.

### 2. Stock Data Rendering
Users can select a stock from the available list, and the app will render detailed information about the stock, including financial data, news articles, and forecasted prices.

### 3. Sentiment Analysis
The sentiment analysis tool searches for a company's sentiment image within a folder called `company_images` in the repository. These images are generated by the `image_fetcher.py` script, which runs every hour on a local machine, fetching the latest sentiment data and saving the images to the `sentiment_images` folder. The folder is then automatically pushed to the GitHub repository.

### 4. Automated Sentiment Image Fetcher
The `image_fetcher.py` script runs every hour using a scheduled task on the local machine. It reads company names from an Excel file (`data new.xlsx`, sheet `short`), fetches sentiment images using a headless browser, and saves the images as `{company_name}.png` in the `sentiment_images` folder. The updated images are then committed and pushed to the GitHub repository.

### 5. Watchlist Functionality
Users can add stocks to their watchlist, which is saved in a database (`watchlist.db`). The watchlist is loaded upon login, allowing users to easily manage and view their favorite stocks.

## Installation

To run this app locally, follow these steps:

1. **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/fortuna-app.git
    cd fortuna-app
    ```

2. **Create a virtual environment and activate it:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4. **Set up your configuration:**
   - Edit the `config.yaml` file with your user credentials, cookie settings, and other configurations.

5. **Run the app:**
    ```bash
    streamlit run main.py
    ```

## Automated Image Fetching

The sentiment images are updated automatically every hour through a scheduled task on a local machine. Here’s how you can set up the automation:

1. **Set up a Scheduled Task (Windows):**
   - Open Task Scheduler and create a new task.
   - Set the trigger to run every hour.
   - Set the action to run the `image_fetcher.py` script, which should be located in the same directory as your app.

2. **Ensure Git Access:**
   - Make sure your script has access to push updates to your GitHub repository. You can use SSH keys or store credentials securely.

## Usage

- **Login:** Log in to access personalized features.
- **Stock Selection:** Choose a stock from the list to view its detailed analysis.
- **Watchlist:** Add and manage your favorite stocks in the watchlist.
- **Sentiment Analysis:** View the sentiment heatmap for the selected stock, which is updated every hour.


