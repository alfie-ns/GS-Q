# Formatting Functions ----------------------------------------------------------
def supports_formatting():
    return sys.stdout.isatty()

def format_text(text, format_code):
    if supports_formatting():
        return f"\033[{format_code}m{text}\033[0m"
    return text

def bold(text):
    return format_text(text, "1")

def blue(text):
    return format_text(text, "34")

def red(text):
    return format_text(text, "31")

def green(text):
    return format_text(text, "32")


#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Dependencies ------------------------------------------------------------------
import sys, os, time
from dotenv import load_dotenv
import openai
import gs_quant.timeseries as ts
from gs_quant.timeseries import Window
from gs_quant.markets.securities import Stock, SecurityMaster
from gs_quant.markets.portfolio import Portfolio
import pandas as pd
import numpy as np

# Load environment variables
load_dotenv()

# Set up OpenAI API key
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_client = openai.OpenAI(api_key=openai_api_key)

# Formatting Functions ----------------------------------------------------------
# (Formatting functions remain unchanged)

# Investment Analysis Functions -------------------------------------------------
def generate_sample_data(n_observations=1000):
    return ts.generate_series(n_observations)

def calculate_volatility(series, window=22):
    return ts.volatility(series, Window(window, 0))

def analyse_timeseries(series):
    vol = calculate_volatility(series)
    return {
        "mean": series.mean(),
        "std_dev": series.std(),
        "last_value": series.iloc[-1],
        "last_volatility": vol.iloc[-1]
    }

def get_stock_data(ticker, start_date, end_date):
    stock = Stock(ticker, SecurityMaster.get(ticker))
    return stock.price.loc[start_date:end_date]

def calculate_returns(prices):
    return prices.pct_change().dropna()

def sharpe_ratio(returns, risk_free_rate=0.02):
    return (returns.mean() - risk_free_rate) / returns.std()

def recommend_investments(tickers, start_date, end_date):
    stocks = [Stock(ticker, SecurityMaster.get(ticker)) for ticker in tickers]
    portfolio = Portfolio(stocks)
    performance = portfolio.price.loc[start_date:end_date]
    returns = calculate_returns(performance)
    
    recommendations = []
    for ticker in tickers:
        stock_returns = returns[ticker]
        sharpe = sharpe_ratio(stock_returns)
        recommendations.append((ticker, sharpe))
    
    recommendations.sort(key=lambda x: x[1], reverse=True)
    return recommendations

# AI Response Function ----------------------------------------------------------
def ai_response(user_input, investment_data, analysis):
    prompt = f"""You are an AI investment assistant with access to financial data and analysis tools. The user has provided the following input: "{user_input}"
    
    Current investment data status: {"Available" if investment_data is not None else "Not generated"}
    
    Analysis results: {analysis if analysis else "Not available"}
    
    You can perform the following actions:
    1. Generate sample data
    2. Analyze time series data
    3. Get real stock data for specific tickers
    4. Calculate returns and Sharpe ratios
    5. Recommend investments based on performance

    Respond in a helpful and professional manner, providing investment insights and recommendations when possible. If the user's request requires any of the above actions, indicate that you'll perform them and explain the results."""

    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": prompt}]
    )

    ai_message = response.choices[0].message.content
    
    # Check if AI suggests performing any actions
    if "generate sample data" in ai_message.lower():
        investment_data = generate_sample_data()
        ai_message += f"\n\nI've generated sample investment data for you."
    
    if "analyze time series data" in ai_message.lower() and investment_data is not None:
        analysis = analyse_timeseries(investment_data)
        ai_message += f"\n\nHere's the analysis of the time series data:\n"
        ai_message += f"Mean Value: {analysis['mean']:.4f}\n"
        ai_message += f"Standard Deviation: {analysis['std_dev']:.4f}\n"
        ai_message += f"Last Value: {analysis['last_value']:.4f}\n"
        ai_message += f"Last Volatility (22-day window): {analysis['last_volatility']:.4f}"
    
    if "get real stock data" in ai_message.lower():
        # For demonstration, we'll use a fixed set of tickers and date range
        tickers = ['AAPL', 'GOOGL', 'MSFT']
        start_date = '2023-01-01'
        end_date = '2023-12-31'
        try:
            stock_data = {ticker: get_stock_data(ticker, start_date, end_date) for ticker in tickers}
            ai_message += f"\n\nI've retrieved real stock data for {', '.join(tickers)} from {start_date} to {end_date}."
        except Exception as e:
            ai_message += f"\n\nI encountered an error while trying to retrieve stock data: {str(e)}"
    
    if "recommend investments" in ai_message.lower():
        tickers = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'FB']
        start_date = '2023-01-01'
        end_date = '2023-12-31'
        try:
            recommendations = recommend_investments(tickers, start_date, end_date)
            ai_message += f"\n\nBased on the Sharpe ratio, here are my investment recommendations:\n"
            for ticker, sharpe in recommendations[:3]:
                ai_message += f"{ticker}: Sharpe Ratio = {sharpe:.2f}\n"
        except Exception as e:
            ai_message += f"\n\nI encountered an error while trying to generate investment recommendations: {str(e)}"

    return ai_message

# Main Function -----------------------------------------------------------------
def main():
    investment_data = None
    analysis = None

    while True:
        os.system('clear')
        print(bold(blue("\nAI Investment Analysis Assistant\n")))

        user_input = input(bold("You: ")).strip()

        if user_input.lower() == 'exit':
            os.system('clear')
            print("\nExiting...")
            time.sleep(1.5)
            os.system('clear')
            sys.exit()

        response = ai_response(user_input, investment_data, analysis)
        print(bold(red("\nAI: ")) + response)

        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
