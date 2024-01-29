# Create your views here.
import yfinance as yf
import pandas as pd
import time
import logging
from datetime import datetime
from django.shortcuts import render
from django.http import JsonResponse

logging.basicConfig(filename='app.log', filemode='a', format='%(asctime)s - %(message)s', level=logging.INFO)

def get_data(tickers):
    try:
        return yf.download(tickers, period="1d", interval="5m")['Close']
    except Exception as e:
        logging.error(f"Error fetching data: {e}")
        return None


def calculate_change(data):
    if len(data) < 2:
        return 0
    return (data.iloc[-1] - data.iloc[0]) / data.iloc[0]

def calculate_probabilities(changes, total_stocks):
    up_count = (changes > 0.005).sum()
    down_count = (changes < -0.005).sum()
    flat_count = len(changes) - up_count - down_count
    up_prob = up_count / total_stocks
    down_prob = down_count / total_stocks
    flat_prob = flat_count / total_stocks
    return up_prob, down_prob, flat_prob

def investment_advice(up_prob, down_prob, flat_prob):
    advice = "No clear advice"
    threshold = 0.5

    if (up_prob > threshold and flat_prob < threshold) or (down_prob > threshold and flat_prob < threshold):
        advice = "Consider buying"
    elif up_prob < threshold and down_prob < threshold and flat_prob > threshold:
        advice = "Not recommended to enter the market"

    return advice, up_prob, down_prob, flat_prob

def stock_template_view(request):
    context = {'key': 'value'}
    return render(request, 'capture_trends/stock.html')

def stock_data_view(request):
    tickers = ['AAPL', 'MSFT', 'AMZN', 'NVDA', 'NFLX', 'GOOGL', 'TSLA', 'META', 'JPM', 'BRK-B', 'SPY', 'QQQ']  
    data = get_data(tickers)
    if data is None:
        logging.error('Failed to fetch data from API.')
        return JsonResponse({'error': 'Unable to fetch data'})

    changes = data.apply(calculate_change, axis=0)
    up_prob, down_prob, flat_prob = calculate_probabilities(changes, len(tickers))
    advice, up_prob, down_prob, flat_prob = investment_advice(up_prob, down_prob, flat_prob)

    # Prepare and log the information
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    changes_str = ', '.join([f"{ticker}: {change:.2%}" for ticker, change in changes.items()])
    probabilities_str = f"Up Probability: {up_prob:.2%}, Down Probability: {down_prob:.2%}, Flat Probability: {flat_prob:.2%}"
    log_message = f"{timestamp} - Investment Advice: {advice}. Changes: {changes_str}. Probabilities: {probabilities_str}"
    logging.info(log_message)

    json_data = {
        'changes': {ticker: change for ticker, change in changes.items()},
        'probabilities': {
            'up': up_prob,
            'down': down_prob,
            'flat': flat_prob
        },
        'advice': advice
    }

    return JsonResponse(json_data)




def display_changes(changes):
   # Display the change in each stock's value
   print(changes)


def main(tickers):
   while True:
       data = get_data(tickers)
       if data is None:
           time.sleep(60)
           continue
      
       # Apply the function along axis=0 (i.e., on each ticker's time series)
       changes = data.apply(calculate_change, axis=0)
       display_changes(changes)


       up_prob, down_prob, flat_prob = calculate_probabilities(changes, len(tickers))