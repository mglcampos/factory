import datetime
import time
from bs4 import BeautifulSoup

import scrapy
from scrapy import Spider
from scrapy.spiders import CrawlSpider
from selenium import webdriver

from factory.mongodb import MongoDB


class NewsSpider(Spider):
    ## returns sentiment on pairs and news
    name = "main"
    allowed_domains = ["http://www.forexfactory.com/"]
    start_urls = [
        "http://www.forexfactory.com/",
    ]

    def __init__(self):
        self.driver = webdriver.Chrome(executable_path='/home/user/drivers/chromedriver')
        # self.driver = webdriver.PhantomJS()

    def parse(self, response):

        self.driver.get(response.url)
        next = self.driver.find_element_by_xpath(
            '//*[@id="flexBox_flex_trades/positions_tradesPositionsCopy1"]/div[4]/ul/li/a')
        next.click()
        time.sleep(3)

        table_content = {'day': '', 'content': []}
        data = []
        sentiments_table = {'day': '', 'sentiments': []}
        content = {}
        # soup = BeautifulSoup(Selector(response).extract())
        # table = soup.find('table', { "class" : "calendar__table" })
        #
        #
        # rows = table.findAll('tr')
        # for tr in rows:
        #     # cols = tr.find_all('td')
        #     # cols = [ele.text.strip() for ele in cols]
        #     # # print('table_content', cols)
        #     # ##TODO fix this
        #     #
        #     # data.append([ele for ele in cols if ele])
        #
        #     print("ROW -- -- ---", tr.find('td', {"class" : "calendar__cell calendar__currency currency"}))

        # for row in data:
        #     if len(row) >3:
        #         pass

            # if len(row) == 7:
            #     table_content['day'] = row[0]
            #     table_content['content'].append(
            #         {'time': row[1], 'currency': row[2], 'event': row[3], 'actual': row[4], 'forecast': row[5],
            #          'previous': row[6]})
            #
            # elif len(row) == 6:
            #     table_content['content'].append({'time': row[0], 'currency': row[1], 'event': row[2], 'actual': row[3],
            #                                      'forecast': row[4], 'previous': row[5]})
            # elif len(row) == 5:
            #     table_content['content'].append({'time': None, 'currency': row[0], 'event': row[1], 'actual': row[2],
            #                                      'forecast': row[3], 'previous': row[4]})
            #     print('table_content', table_content['content'][:-1])

        data = []

        soup = BeautifulSoup(self.driver.page_source)
        sentiments = soup.find('div', {"class": "flexBox trades_positions traders trades_positions--traders trades_positions--ishomepage trades_positions--more"})
        divs = sentiments.findAll('table', {"class": "trades_position"})

        for div in divs:
            tr = div.find('tr')
            currency = tr.find('a', {"class": "currency"})

            li = div.findAll('li')
            sentiments= [ele.text.strip() for ele in li]
            content['symbol'] = currency.text.strip()
            content['Long_Traders'] = sentiments[0].split(' ')
            content['Long_Traders'] = [content['Long_Traders'][0], content['Long_Traders'][1]]
            content['Short_Traders'] = sentiments[1].split(' ')
            content['Short_Traders'] = [content['Short_Traders'][2],content['Short_Traders'][0]]
            x = dict(content)
            data.append(x)


        sentiments_table['day'] = datetime.datetime.now()
        sentiments_table['sentiments'] = data
        mongo = MongoDB()
        if table_content['content']:
            mongo.addNews(table_content)
        if sentiments_table:
            mongo.addSentiment(sentiments_table)

        # TODO maybe remove this
        time.sleep(2)
        self.driver.close()





class RankingSpider(Spider):
    name = "ranking"
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
        if len(ranking) == 99:
            dict = {'ranking': ranking}
            mongo = MongoDB()
            mongo.remove('Ranking')
            mongo.addRanking(dict)


class TradersSpider(CrawlSpider):

    name = "traders"
    allowed_domains = ["*"]
    start_urls = [
        "http://www.forexfactory.com/",
    ]

    def __init__(self):
        self.driver = webdriver.Chrome(executable_path='/home/user/drivers/chromedriver')

    def start_requests(self):

        self.mongo = MongoDB()
        traders = self.mongo.getRankedTraders()
        print ('traders', len(traders), traders)
        for trader in traders:
            # next_page = response.urljoin(trader)
            next_page = "http://www.forexfactory.com/" + trader
            print ('next_page', next_page)
            yield scrapy.Request(next_page, callback=self.parse)

    def parse(self, response):
        print("URL-------------------", response.url)
        data = {'returns': [], 'trades': []}
        self.driver.get(response.url)
        time.sleep(3)
        soup = BeautifulSoup(self.driver.page_source)
        status = soup.find('th', {"class": "crunched slidetable__header slidetable__header--fixed"})
        if status:
            status = status.text.strip()
            print('STATUS --------------------------------------------------------- ', status)
            if status == 'Open Trades':
                table = soup.find('table', {"class": "memberinfo__explorers slidetable__table"})
                # soup = soup.find('tbody')
                rows = soup.findAll('tr')
                for tr in rows:
                    cols = tr.find_all('td')
                    cols = [ele.text.strip() for ele in cols]
                    print("pre len(cols) == 22", len(cols))
                    if len(cols) > 19:
                        open_trades = cols
                        # print('Open trades', open_trades[0])
                        print(" len(cols) == 22",len(open_trades[0]))
                        if len(open_trades[0]) > 2:
                            trade = open_trades[0].split(' ')
                            if len(trade) > 2:
                                print('trade', trade)
                                currency = trade[0]
                                direction = trade[1]
                                value = trade[2]
                                ##TODO change takeProfit
                                trades = dict({'currency': currency, 'direction' : direction, 'value' : value ,'takeProfit' : open_trades[16]})
                                print('Open trades', trades)
                                data['trades'].append(trades)

                    elif len(cols) == 12:
                        returns = cols
                        # print('Returns', returns)
                        data['returns'].append({'period': returns[0], 'percentage' : returns[2], 'pips':returns[6], 'entry/exit' : returns[8]})


                name = response.url.split('.com/')
                name = name[1]
                print ('open_trades', len(cols), data['trades'])
                print ('returns', len(cols), data['returns'])
                trader = {'name': name, 'returns': data['returns'], 'open_trades': data['trades'], 'last_updated' : datetime.datetime.now()}

                self.mongo.addTraders(trader, name)



