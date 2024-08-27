import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from utils import cached_forecast, cached_sentiment_image, load_ticker_company_map, load_css
import base64
from io import BytesIO
from PIL import Image


def render_tabs(selected_stock):
    load_css()
    ticker = yf.Ticker(selected_stock)
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Overview", "Financials", "Latest News", "Sentiment", "Forecast"])

    with tab1:
        render_overview(ticker)
    with tab2:
        render_financials(ticker)
    with tab3:
        render_latest_news(ticker)
    with tab4:
        render_sentiment(selected_stock)  # Use cached_forecast here
    with tab5:
        render_forecast(selected_stock)  # Use cached_sentiment_image here

def render_overview(ticker):
    load_css()
    info = ticker.info
    overview_content = f"""
    **Sector:** {info.get('sector', 'N/A')}

    **Industry:** {info.get('industry', 'N/A')}

    **Website:** {info.get('website', 'N/A')}

    **Company Overview:** {info.get('longBusinessSummary', 'N/A')}
    """
    st.markdown(overview_content)

def format_large_number(num):
    """Formats a number to 3 significant figures and adds a suffix (B, M, T)."""
    if isinstance(num, (int, float)):
        if abs(num) >= 1_000_000_000_000:  # Trillion
            return f"{num / 1_000_000_000_000:.3g} T"
        elif abs(num) >= 1_000_000_000:  # Billion
            return f"{num / 1_000_000_000:.3g} B"
        elif abs(num) >= 1_000_000:  # Million
            return f"{num / 1_000_000:.3g} M"
        else:  # Less than a million
            return f"{num:,.2f}"
    return num  # If num is 'N/A' or any other non-numeric value

def render_financials(ticker):
    load_css()
    info = ticker.info
    st.markdown("### Key Financials:")
    revenue = info.get('totalRevenue', 'N/A')
    earnings = info.get('netIncomeToCommon', 'N/A')
    eps = info.get('trailingEps', 'N/A')
    pe_ratio = info.get('trailingPE', 'N/A')
    gross_margin = info.get('grossMargins', 'N/A')
    profit_margin = info.get('profitMargins', 'N/A')
    market_cap = info.get('marketCap', 'N/A')

    # Calculate missing values if possible
    if gross_margin == 'N/A' and revenue != 'N/A' and info.get('grossProfit') != 'N/A':
        gross_margin = info['grossProfit'] / revenue

    if profit_margin == 'N/A' and revenue != 'N/A' and earnings != 'N/A':
        profit_margin = earnings / revenue

    # Format large numbers
    revenue = format_large_number(revenue)
    earnings = format_large_number(earnings)
    market_cap = format_large_number(market_cap)

    financials_html = f"""
    <table class="financials-table">
        <tr>
            <th>Revenue</th>
            <td>{revenue}</td>
        </tr>
        <tr>
            <th>Earnings</th>
            <td>{earnings}</td>
        </tr>
        <tr>
            <th>EPS</th>
            <td>{eps}</td>
        </tr>
        <tr>
            <th>PE Ratio</th>
            <td>{pe_ratio:.2f}</td>
        </tr>
        <tr>
            <th>Gross Margin</th>
            <td>{gross_margin:.2%}</td>
        </tr>
        <tr>
            <th>Profit Margin</th>
            <td>{profit_margin:.2%}</td>
        </tr>
        <tr>
            <th>Market Cap</th>
            <td>{market_cap}</td>
        </tr>
    </table>
    """
    st.markdown(financials_html, unsafe_allow_html=True)


def render_latest_news(ticker):
    load_css()
    news_data = ticker.news
    if news_data:
        st.markdown('<div class="news-grid">', unsafe_allow_html=True)
        for article in news_data[:6]:
            title = article['title']
            link = article['link']
            news_card_html = f"""
            <div class="news-card">
                <a href="{link}" target="_blank">
                    <div class="news-card-container">
                        <p class="news-card-title">{title}</p>
                        <p class="news-card-date">Date: {pd.to_datetime(article['providerPublishTime'], unit='s').strftime('%Y-%m-%d')}</p>
                    </div>
                </a>
            </div>
            """
            st.markdown(news_card_html, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.write("No news available for this stock.")

def render_forecast(selected_stock):
    load_css()
    with st.spinner('Running forecast...'):
        # Check if the data is available before attempting to forecast
        try:
            average_pred_price, last_actual_close, result, fig, df = cached_forecast(selected_stock)
            # Display the forecast results (whether recalculated or retrieved from session state)
            st.markdown("### Forecast Results")
            forecast_table = f"""
            <table class="financials-table">
                <tr>
                    <th>Average Forecasted Price (Next 5 Days)</th>
                    <td>{average_pred_price:.2f}</td>
                </tr>
                <tr>
                    <th>Last Actual Closing Price</th>
                    <td>{last_actual_close:.2f}</td>
                </tr>
                <tr>
                    <th>Forecast Result</th>
                    <td>{result}</td>
                </tr>
            </table>
            """
            st.markdown(forecast_table, unsafe_allow_html=True)
            st.plotly_chart(fig)
            
            # Display the Average True Range (ATR) value
            atr_value = ta.atr(
                df['High'],
                df['Low'],
                df['Adj Close'],
                length=14
            ).iloc[-1]

            st.markdown(f"### Average True Range (ATR): {atr_value:.2f}")

        except ValueError as e:
            st.error(f"Error generating forecast: {e}")
        except Exception as e:
            st.error(f"Unexpected error: {e}")


def render_sentiment(selected_stock):
    load_css()
    with st.spinner("Loading sentiment analysis..."):
        # Explanation of sentiment heatmap in an expandable section
        with st.expander("Understanding the Sentiment Heatmap", expanded=False):
            st.markdown("""
                <h3 style='font-size: 24px; font-weight: bold;'>Understanding the Sentiment Heatmap</h3>
                <p>A sentiment heatmap is a powerful tool used to visualize the emotional tone and intensity of text data, often sourced from social media posts, customer reviews, or other forms of written content. Here's how to interpret it:</p>

                <h4>1. Axes Explanation:</h4>
                <ul style='margin-left: 20px;'>
                    <li><strong>Horizontal Axis (X-Axis):</strong>
                        <ul style='margin-left: 20px;'>
                            <li>This axis measures the sentiment of the posts from negative (left) to positive (right).</li>
                            <li><strong>Left Side:</strong> Represents negative emotions like sadness, anger, or dissatisfaction.</li>
                            <li><strong>Right Side:</strong> Represents positive emotions like happiness, excitement, or satisfaction.</li>
                        </ul>
                    </li>
                    <li><strong>Vertical Axis (Y-Axis):</strong>
                        <ul style='margin-left: 20px;'>
                            <li>This axis measures the intensity or confidence level of the emotions.</li>
                            <li><strong>Top:</strong> Indicates high confidence or strong emotional responses.</li>
                            <li><strong>Bottom:</strong> Indicates low confidence or weaker emotional responses.</li>
                        </ul>
                    </li>
                </ul>

                <h4>2. Dot Interpretation:</h4>
                <ul style='margin-left: 20px;'>
                    <li><strong>Each Dot Represents a Post:</strong>
                        <ul style='margin-left: 20px;'>
                            <li>Each dot on the heatmap corresponds to a single social media post or text entry about the topic being analyzed.</li>
                            <li>The position of the dot shows both the sentiment (whether the post is positive or negative) and the confidence level of that sentiment (how strongly the emotion is expressed).</li>
                        </ul>
                    </li>
                    <li><strong>Color and Density:</strong>
                        <ul style='margin-left: 20px;'>
                            <li>The color or shade of the dots might vary, with darker or more intense colors often representing a higher concentration of similar sentiments.</li>
                            <li>A cluster of dots indicates that many posts share similar sentiments and emotional intensity.</li>
                        </ul>
                    </li>
                </ul>

                <h4>3. Clusters and Patterns:</h4>
                <ul style='margin-left: 20px;'>
                    <li><strong>Clusters:</strong>
                        <ul style='margin-left: 20px;'>
                            <li>Groups of dots that cluster together indicate a common sentiment or emotional response among many users.</li>
                            <li>For example, if many dots cluster on the right side, it suggests that most posts have a positive sentiment about the topic.</li>
                        </ul>
                    </li>
                    <li><strong>Outliers:</strong>
                        <ul style='margin-left: 20px;'>
                            <li>Dots that are isolated or far from the main clusters can represent outlier sentiments, such as unusually strong negative or positive emotions.</li>
                        </ul>
                    </li>
                </ul>
            """, unsafe_allow_html=True)
        
        # Load the ticker-company map dictionary by calling the function
        ticker_company_map = load_ticker_company_map()  # Now it returns the dictionary

        # Get the company name from the ticker-company map
        company_name = ticker_company_map.get(selected_stock, selected_stock)

        # Use the cached sentiment image function to fetch the sentiment image
        sentiment_image = cached_sentiment_image(company_name)

        if sentiment_image:
            # Convert the image to base64
            buffered = BytesIO()
            sentiment_image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()

            # Set the URL you want to redirect to when the image is clicked
            target_url = "https://www.csc2.ncsu.edu/faculty/healey/social-media-viz/production/"  # Replace with your desired URL

            # Display the clickable image
            st.markdown(f"""
                <a href="{target_url}" target="_blank">
                    <img src="data:image/png;base64,{img_str}" alt="Sentiment Analysis for {company_name}" style="width:100%; height:auto;"/>
                </a>
            """, unsafe_allow_html=True)
        else:
            st.warning("Sentiment analysis image could not be retrieved.")
