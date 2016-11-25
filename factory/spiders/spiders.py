from scrapy import Spider
from scrapy.selector import Selector
from factory.items import NewsItem
import scrapy
from bs4 import BeautifulSoup
from selenium import webdriver
import time

class NewsSpider(Spider):
    ## returns sentiment on pairs and news
    name = "news"
    allowed_domains = ["http://www.forexfactory.com/"]
    start_urls = [
        "http://www.forexfactory.com/",
    ]



    def parse(self, response):


        table_content = {'day': '', 'content': []}
        data = []

        soup = BeautifulSoup(Selector(response).extract())
        table = soup.find('table', { "class" : "calendar__table" })

        rows = table.findAll('tr')
        for tr in rows:
            cols = tr.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            if len(cols) == 10:
                data.append([ele for ele in cols if ele])

        for row in data:
            if len(row) == 7:
                table_content['day'] = row[0]
                table_content['content'].append(
                    {'time': row[1], 'currency': row[2], 'event': row[3], 'actual': row[4], 'forecast': row[5],
                     'previous': row[6]})

            elif len(row) == 6:
                table_content['content'].append({'time': row[0], 'currency': row[1], 'event': row[2], 'actual': row[3],
                                                 'forecast': row[4], 'previous': row[5]})
            elif len(row) == 5:
                table_content['content'].append({'time': None, 'currency': row[0], 'event': row[1], 'actual': row[2],
                                                 'forecast': row[3], 'previous': row[4]})

        ##TODO write on mongodb
        for row in table_content['content']:
            print row





class TradesSpider(Spider):
    name = "leaderboard"
    allowed_domains = ["http://www.forexfactory.com/"]
    start_urls = [
        "http://www.forexfactory.com/trades.php",
    ]

    def __init__(self):
        self.driver = webdriver.Chrome(executable_path='/home/user/drivers/chromedriver')

    def parse(self, response):
        data = []
        ranking = []
        self.driver.get(response.url)
        nr_clicks = 3
        for i in range(1, nr_clicks):
            next = self.driver.find_element_by_xpath('//*[@id="flexBox_flex_trades/leaderboard_tradesLeaderboard"]/div/ul/li/a')
            next.click()
            time.sleep(2)

        soup = BeautifulSoup(self.driver.page_source)
        table = soup.find('table', {"class": "slidetable__table"})

        rows = table.findAll('tr')
        for tr in rows:
            cols = tr.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            # print ("cols", len(cols), cols)
            if len(cols) == 5:
                data.append([ele for ele in cols if ele])

        for pos in data:
            ranking.append({'rank': pos[0], 'title': pos[1], 'returns': pos[2], 'name': pos[3]})

        print ("ranking", len(ranking), ranking)
        while True:
            time.sleep(1)
