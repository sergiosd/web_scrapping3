# -*- coding: utf-8 -*-
"""
Created on Sun Jun  3 14:51:25 2018

@author: meltus
"""
from web_scrapping_lib import Finance_Yahoo_Navigation
from datetime import datetime
import pandas as pd

fyn = None


def get_ticker_data(ticker, open_webpage=True, verbose=True,
                    decimal_point=','):
    global fyn

    results = {}
    if open_webpage:
        # OPEN finance.yahoo.com ACCEPTING Oath PAGE IF NEEDED
        fyn = Finance_Yahoo_Navigation(delete_cookies=False,
                                       decimal_point=decimal_point)

    # INTRODUCE TICKER
    results['ticker'] = ticker
    results['DateTime'] = datetime.now().strftime("%m/%d/%y")
    fyn.select_ticker(ticker)
    if verbose:
        print("---------{}---------".format(ticker))
        print("{}".format(results['DateTime']))

    # GET CURRENT PRICE AND COMPANY NAME
    results['Price'] = fyn.get_current_price(click_summary_tab_first=False)
    results['Company'] = fyn.get_company_name(click_summary_tab_first=False)
    if verbose:
        print("Current price = {}".format(results['Price']))
        print("Company = {}".format(results['Company']))

    # COLLECT SUMMARY DATA
    results['dividend_yield'] = \
        fyn.get_dividend_yield(click_summary_tab_first=True)
    results['ex_dividend_date'] =\
        fyn.get_ex_dividend_date(click_summary_tab_first=False)
    results['market_cap'] = \
        fyn.get_market_cap(click_summary_tab_first=False)
    if verbose:
        print("Dividend Yield: {}".format(results['dividend_yield']))
        print("ex_dividend_date: {}".format(results['ex_dividend_date']))
        print("market_cap: {}".format(results['market_cap']))

    # GET ANALYSTS RATING
    results['analysts_rating'] = fyn.get_analysts_rating()
    if verbose:
        print("Analysts rating: {}".format(results['analysts_rating']))

    # GET TARGET PRICE
    results['target_price'] = fyn.get_target_price()
    try:
        results['target_ratio'] = results['Price'] / results['target_price']
    except:
        results['target_ratio'] = None
    if verbose:
        print("Target price: {}".format(results['target_price']))

    # GET HISTORICAL DATA
    results['five_years_close'] = fyn.get_ndays_quotes(
            ndays=365*5, click_historical_data_first=True)
    results['one_year_close'] = fyn.get_ndays_quotes(
            ndays=365, click_historical_data_first=False)
    results['one_month_close'] = fyn.get_ndays_quotes(
            ndays=30, click_historical_data_first=False)
    try:
        results['five_y_trend'] = results['Price'] / \
               results['five_years_close']
    except:
        results['five_y_trend'] = None
    try:
        results['one_y_trend'] = results['Price'] / results['one_year_close']
    except:
        results['one_y_trend'] = None
    try:
        results['one_m_trend'] = results['Price'] / results['one_month_close']
    except:
        results['one_m_trend'] = None
    if verbose:
        print("Five years ago close: {}".format(results['five_years_close']))
        print("One year ago close: {}".format(results['one_year_close']))
        print("One month ago close: {}".format(results['one_month_close']))
        print("Five years trend: {}".format(results['five_y_trend']))
        print("One year trend: {}".format(results['one_y_trend']))
        print("One month trend: {}".format(results['one_m_trend']))

    # GET LAST EPS SURPRISE INDEX
    results['eps_surprise'] = fyn.get_EPS_surprise(
            click_analysis_tab_first=True)
    if verbose:
        print("Last EPS surprise: {}".format(results['eps_surprise']))

    # GET GROWTH ESTIMATES
    growth = fyn.get_growth_estimated(click_analysis_tab_first=False)
    if growth:
        results['growth_next_quarter'] = growth[0]
        results['growth_this_year'] = growth[1]
        results['growth_next_year'] = growth[2]
    else:
        results['growth_next_quarter'] = results['growth_this_year'] = \
               results['growth_next_year'] = None
    if verbose:
        print("Growth next quarter: {}".format(results['growth_next_quarter']))
        print("Growth this year: {}".format(results['growth_this_year']))
        print("Growth next year: {}".format(results['growth_next_year']))

    # GET VALUATION MEASURES
    results['PE'] = fyn.get_PE(click_statistics_tab_first=True)
    results['PEG'] = fyn.get_PEG(click_statistics_tab_first=False)
    if verbose:
        print("PE: {}".format(results['PE']))
        print("PEG: {}".format(results['PEG']))
    return results

if __name__ == '__main__':
    tickers_df = pd.read_csv("tickers.csv", sep=";")
    columns = ['ticker', 'Company', 'DateTime', 'Price', 'dividend_yield',
               'analysts_rating', 'target_price', 'target_ratio',
               'PE', 'PEG', 'eps_surprise', 'growth_next_quarter',
               'growth_this_year', 'growth_next_year', 'market_cap',
               'ex_dividend_date', 'five_years_close', 'one_year_close',
               'one_month_close', 'five_y_trend', 'one_y_trend',
               'one_m_trend']
    result = get_ticker_data(tickers_df.loc[0, 'Tickers'], open_webpage=True,
                             decimal_point=".")
    results = pd.DataFrame(data=result, index=[0])
    results.to_csv("results.csv", mode="a", sep=";", columns=columns,
                   index=False, encoding='latin1', header=True, na_rep="")
    tickers_df = tickers_df.drop(tickers_df.index[0])
    for ticker in tickers_df['Tickers']:
        result = get_ticker_data(ticker, open_webpage=False)
        # results = results.append(result, ignore_index=True)
        results = pd.DataFrame(data=result, index=[0])
        results.to_csv("results.csv", mode="a", sep=";", columns=columns,
                       index=False, encoding='latin1', header=False)
    fyn.close_driver()
