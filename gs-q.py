#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Dependencies ------------------------------------------------------------------
import sys, os, time
from dotenv import load_dotenv

# GS Quant API dependencies
import gs_quant.timeseries as ts
from gs_quant.timeseries import Window

# Formatting dependencies
import textwrap
import datetime

# Load environment variables
load_dotenv()

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

# Main Function -----------------------------------------------------------------
def main():
    while True:
        os.system('clear')
        print(bold(blue("\nInvestment Analysis Tool\n")))

        print("Generating sample investment data...")
        investment_data = generate_sample_data()

        print(bold(green("\nSample data generated successfully!")))
        print("\nAnalysing investment data...")
        
        analysis = analyse_timeseries(investment_data)
        
        print(f"\nAnalysis Results:")
        print(f"Mean Value: {analysis['mean']:.4f}")
        print(f"Standard Deviation: {analysis['std_dev']:.4f}")
        print(f"Last Value: {analysis['last_value']:.4f}")
        print(f"Last Volatility (22-day window): {analysis['last_volatility']:.4f}")

        while True:
            action = input(bold("\nWhat would you like to do? (analyse/exit): ")).strip().lower()

            if action == 'exit':
                os.system('clear')
                print("\nExiting...")
                time.sleep(1.5)
                os.system('clear')
                sys.exit()

            elif action == 'analyse':
                window = int(input("Enter the number of days for volatility calculation (default is 22): ") or 22)
                vol = calculate_volatility(investment_data, window)
                print(f"\n{window}-day Volatility (last 5 values):")
                print(vol.tail())

            else:
                print(red("Invalid choice. Please enter 'analyse' or 'exit'."))

if __name__ == "__main__":
    main()