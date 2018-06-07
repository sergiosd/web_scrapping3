# -*- coding: utf-8 -*-
"""
Editor de Spyder

Este es un archivo temporal
"""
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
from datetime import datetime, date, timedelta


class Selenium_Driver:
    """Creation and management of a Selenium chrome driver"""
    def __init__(self, web_page, chrome_options=None):
        if chrome_options:
            self.driver = webdriver.Chrome(chrome_options=chrome_options)
        else:
            self.driver = webdriver.Chrome()
        self.driver.get(web_page)

    def get_cookies(self):
        return self.driver.get_cookies()

    def delete_all_cookies(self):
        self.driver.delete_all_cookies()

    def check_page_title(self, title):
        if not self.driver:
            raise ValueError("webdriver is not initialitated")
        try:
            assert title in self.driver.title
            return 0
        except AssertionError:
            return self.driver.title

    def send_keys(self, xpath_str, keys, elementToBeClosed=False):
        if not self.driver:
            raise ValueError("webdriver is not initialitated")
        try:
            element = self.driver.find_element_by_xpath(xpath_str)
            element.send_keys(keys)
            if elementToBeClosed:
                element.clear()
        except Exception as e:
            print('Error while sending keys "{keys}". Error reported:\n{err}'.
                  format(keys=keys, err=e))
            return 1
        else:
            return 0

    def send_n_keys(self, xpath_str, keys, n, elementToBeClosed=False):
        if not self.driver:
            raise ValueError("webdriver is not initialitated")
        try:
            element = self.driver.find_element_by_xpath(xpath_str)
            for count in range(n):
                element.send_keys(keys)
            if elementToBeClosed:
                element.clear()
        except Exception as e:
            print('Error while sending keys "{keys}". Error reported:\n{err}'.
                  format(keys=keys, err=e))
            return 1
        else:
            return 0

    def send_click(self, xpath_str, elementToBeClosed=False):
        if not self.driver:
            raise ValueError("webdriver is not initialitated")
        try:
            element = self.driver.find_element_by_xpath(xpath_str)
            element.click()
            if elementToBeClosed:
                element.clear()
        except Exception as e:
            print('Error while sending click. Error reported:\n{err}'.
                  format(err=e))
            return 1
        else:
            return 0

    def get_element(self, xpath_str):
        return self.driver.find_element_by_xpath(xpath_str)

    def get_elements(self, xpath_str):
        return self.driver.find_elements_by_xpath(xpath_str)

    def close_driver(self):
        self.driver.close()

    def wait_for_element_ID(self, id_str, wait_time):
        try:  # this block implements a wait for the load of the table element
            # after 5 seconds a timeout is error is produced
            WebDriverWait(self.driver, wait_time).until(
                    EC.presence_of_element_located((By.ID, id_str)))
        except Exception as e:
            raise e
        time.sleep(1)

    def wait_for_element_XPath(self, xpath_str, wait_time):
        try:  # this block implements a wait for the load of the table element
            # after 5 seconds a timeout is error is produced
            WebDriverWait(self.driver, wait_time).until(
                    EC.presence_of_element_located((By.XPATH, xpath_str)))
        except Exception as e:
            raise e
        time.sleep(1)


class Finance_Yahoo_Navigation(Selenium_Driver):
    """Manage navigation in yahoo.finance.page using Chrome"""

    def __init__(self, delete_cookies=True, chrome_options=None,
                 decimal_point=','):
        self.dp = decimal_point
        super().__init__("https://finance.yahoo.com", chrome_options)
        if type(self.check_page_title("Yahoo Finance")) is str:
            if "Oath" in self.driver.title:
                self.send_keys("//input[@value='OK']", Keys.RETURN)
            else:
                raise ValueError("Unknown page {page},"
                                 " please check opened browser".
                                 format(page=self.driver.title))
            # do another check after closing oath page
            if type(self.check_page_title("Yahoo Finance")) is str:
                self.driver.refresh()
                raise ValueError("Unknown page {page},"
                                 " please check opened browser".
                                 format(page=self.driver.title))
        if delete_cookies:
            self.delete_all_cookies()

    def select_ticker(self, ticker):
        self.ticker = ticker
        self.send_keys("//input[@name='p']", ticker + Keys.RETURN)
        self.summ_table_elements = None

    def select_tab(self, tab_id):
        tab_dic = {"Summary": "1", "Historical Data": "9", "Analysis": "10",
                   "Statistics": "4"}
        tab_str = "//*[@id='quote-nav']/ul/li[" + tab_dic[tab_id] + "]/a"
        self.wait_for_element_XPath(tab_str, 60)
        self.send_keys(tab_str, Keys.ENTER)

    def get_current_price(self, click_summary_tab_first=False):
        if click_summary_tab_first:
            self.select_tab("Summary")
        xpath_str = "//*[@id='Lead-2-QuoteHeader-Proxy']" \
                    "/div[@id='quote-header-info']/div[3]/div[1]/div/span[1]"
        xpath_str = "//*[@id='quote-header-info']/div[3]/div[1]/div/span[1]"
        self.wait_for_element_XPath(xpath_str, 60)
        element = self.get_element(xpath_str)
        try:
            return float(element.text.replace('.', self.dp))
        except:
            return None

    def get_company_name(self, click_summary_tab_first=False):
        if click_summary_tab_first:
            self.select_tab("Summary")
        xpath_str = '//*[@id="quote-header-info"]/div[2]/div[1]/div[1]/h1'
        self.wait_for_element_XPath(xpath_str, 60)
        element = self.get_element(xpath_str)
        return element.text

    def _get_summary_table(self, click_summary_tab_first=False):
        if click_summary_tab_first:
            self.select_tab("Summary")
        xpath_str = "//*[@id='quote-summary']" \
                    "//div[@data-test='right-summary-table']/table/tbody//tr"
        self.wait_for_element_XPath(xpath_str, 60)
        self.summ_table_elements = self.get_elements(xpath_str)

    def _get_analysis_table(self, table_name, click_analysis_tab_first=False):
        if click_analysis_tab_first:
            self.select_tab("Analysis")
        xpath_str = "//*[th='" + table_name + "']/../../tbody//tr"
        self.wait_for_element_XPath(xpath_str, 10)
        return self.get_elements(xpath_str)

    def _get_statistics_table(self, click_statistics_tab_first=False):
        if click_statistics_tab_first:
            self.select_tab("Statistics")
        xpath_str = "//*[h2='Valuation Measures']//table//tr"
        self.wait_for_element_XPath(xpath_str, 10)
        return self.get_elements(xpath_str)

    def get_dividend_yield(self, click_summary_tab_first=False):
        if not self.summ_table_elements:
            self._get_summary_table(click_summary_tab_first)
        dividend = self.summ_table_elements[5].text.replace('%',
                                                            '(').split('(')[1]
        try:
            return float(dividend.replace('.', self.dp))/100
        except:
            return None

    def get_ex_dividend_date(self, click_summary_tab_first=False):
        if not self.summ_table_elements:
            self._get_summary_table(click_summary_tab_first)
        return self.summ_table_elements[6].text.split()[2]

    def get_market_cap(self, click_summary_tab_first=False):
        if not self.summ_table_elements:
            self._get_summary_table(click_summary_tab_first)
        try:
            return float(self.summ_table_elements[0]
                    .text.split()[2].replace('B', '').replace('.', self.dp))
        except:
            return None

    def _calculate_timeframe_dates(self, current_day, days):
        start_lapse = timedelta(days=days+15)
        end_lapse = timedelta(days=days-15)
        self.start_date = current_day-start_lapse
        self.end_date = current_day-end_lapse

    def _get_quotes_table(self):
        xpath_date = '//*[@id="Col1-1-HistoricalDataTable-Proxy"]' \
                     '/section/div[2]/table/tbody//tr'  # to get all the table
        return self.driver.find_elements_by_xpath(xpath_date)

    def get_ndays_quotes(self, ndays, click_historical_data_first=False):
        if click_historical_data_first:
            self.select_tab("Historical Data")
        self._calculate_timeframe_dates(date.today(), ndays)

        # Open the timeframe window
        time_frame_xpath = '//*[@id="Col1-1-HistoricalDataTable-Proxy"]' \
                           '/section' \
                           '//input[@data-test="date-picker-full-range"]'
        self.wait_for_element_XPath(time_frame_xpath, 60)
        self.send_click(time_frame_xpath)

        # Select start date field and introduce start_date
        self.send_n_keys('//*[@id="Col1-1-HistoricalDataTable-Proxy"]'
                         '/section//input[@name="startDate"]', Keys.DELETE, 10)
        self.send_keys('//*[@id="Col1-1-HistoricalDataTable-Proxy"]/'
                       'section//input[@name="startDate"]',
                       self.start_date.strftime("%m/%d/%Y"))

        # Select end date field and introduce end_date
        self.send_n_keys('//*[@id="Col1-1-HistoricalDataTable-Proxy"]'
                         '/section//input[@name="endDate"]',
                         Keys.BACKSPACE, 10)
        self.send_keys('//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section'
                       '//input[@name="endDate"]',
                       self.end_date.strftime("%m/%d/%Y"))

        # Validate timeframe
        try:
            # Check if error message is present
            element = self.driver.find_element_by_xpath(
                    '//*[@id="Col1-1-HistoricalDataTable-Proxy"]'
                    '/section/div[1]/div[1]/div[1]/span[2]/div/span[3]')
        except Exception as e:
            # Dates validated, error message is not present
            # Applying introduced timeframes
            self.send_click('//*[@id="Col1-1-HistoricalDataTable-Proxy"]'
                            '/section/div[1]/div[1]/div[1]/span[2]/div'
                            '/div[3]/button[1]')
            self.send_click('//*[@id="Col1-1-HistoricalDataTable-Proxy"]'
                            '/section/div[1]/div[1]/button')
        else:
            # Dates not validated, error reported
            # Closing timeframe window
            self.send_click('//*[@id="Col1-1-HistoricalDataTable-Proxy"]'
                            '/section/div[1]/div[1]/div[1]/span[2]/div'
                            '/div[3]/button[2]')
            return None

        # Get the quotes
        five_years_date = date.today()-timedelta(days=ndays)
        five_years_date_str = five_years_date.strftime("%b %d, %Y")
        quotes_table = self._get_quotes_table()
        while quotes_table:
            for element in quotes_table:
                try:
                    if five_years_date_str in element.text:
                        try:
                            return float(element.text.split()[7]
                                     .replace('.', self.dp))
                        except:
                            return None
                except Exception as e:
                    pass
            five_years_date = five_years_date - timedelta(days=1)
            five_years_date_str = five_years_date.strftime("%b %d, %Y")
        return None

    def get_EPS_surprise(self, click_analysis_tab_first=False):
        elements = self._get_analysis_table("Earnings History",
                                            click_analysis_tab_first)
        try:
            eps_estimated = float(elements[0].
                                  text.split()[5].replace('.', self.dp))
            eps_actual = float(elements[1].
                               text.split()[5].replace('.', self.dp))
            return (eps_actual - eps_estimated) / eps_estimated
        except Exception as e:
            print("Error while catching EPS of ticker {}".format(self.ticker))
            return None

    def get_growth_estimated(self, click_analysis_tab_first=False):
        elements = self._get_analysis_table("Growth Estimates",
                                            click_analysis_tab_first)
        growth = []
        try:
            # Next quarter
            growth.append(float(elements[1].text.split()[2]
                                .replace('%', '').replace('.', self.dp))/100)
            # this year
            growth.append(float(elements[2].text.split()[2]
                                .replace('%', '').replace('.', self.dp))/100)
            # this year
            growth.append(float(elements[3].text.split()[2]
                                .replace('%', '').replace('.', self.dp))/100)
            return growth
        except Exception as e:
            print("Error while catching growth of ticker {}".
                  format(self.ticker))
        return None

    def get_analysts_rating(self, click_analysis_tab_first=False):
        # scroll down the window to load the data analyst area
        self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")
        xpath_str = "//div[@class='analyst-opinion-container" \
                    " slider-indicator-container']/div"
        self.wait_for_element_XPath(xpath_str, 60)
        # scroll up the window to let activate tab selection and others
        self.driver.execute_script("window.scrollTo(0, 0)")
        try:
            return float(self.get_element(xpath_str).text.replace('.',
                                                                  self.dp))
        except:
            return None

    def get_target_price(self, click_analysis_tab_first=False):
        xpath_str = "//section[@data-test='price-targets']/div"
        elements = self.get_elements(xpath_str)
        for element in elements:
            if 'Average' in element.text:
                try:
                    return float(element.text.split()[3].replace('.', self.dp))
                except:
                    return None

    def get_PE(self, click_statistics_tab_first=False):
        elements = self._get_statistics_table(click_statistics_tab_first)
        try:
            for element in elements:
                if "Trailing P/E" in element.text:
                    return float(element.text.split()[2].replace('.', self.dp))
        except Exception as e:
            print("Error while catching PE of ticker {}".format(self.ticker))
        return None

    def get_PEG(self, click_statistics_tab_first=False):
        elements = self._get_statistics_table(click_statistics_tab_first)
        try:
            for element in elements:
                if "PEG Ratio" in element.text:
                    return float(element.text.split()[6].replace('.', self.dp))
        except Exception as e:
            print("Error while catching PEG of ticker {}".format(self.ticker))
        return None
