from pymongo import MongoClient

class MongoDB(object):

    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client['factory']


    def addNews(self, news):
        collection = self.db['News']
        if not collection.find_one_and_replace({}, news):
            collection.insert_one(news)
        print('News added')

    def addSentiment(self, sentiment):
        collection = self.db['Sentiments']
        if not collection.find_one_and_replace({}, sentiment):
            collection.insert_one(sentiment)
        print('Sentiments added')

    def addRanking(self, ranking):
        collection = self.db['Ranking']
        collection.insert_one(ranking)
        print('Rank added')

    def addTraders(self, trader, name):
        collection = self.db['Traders']
        if not collection.find_one_and_replace({'name': name}, trader):
            collection.insert_one(trader)
        print('Trader added')

    def getRankedTraders(self):
        collection = self.db['Ranking']
        results = collection.find_one({})
        traders = []
        for trader in results['ranking']:
            traders.append(trader['name'])

        return traders


    def remove(self, collection):
        if collection == 'News':
            collection = self.db['News']
            collection.delete_many({})
            print('News removed')

        if collection == 'Ranking':
            collection = self.db['Ranking']
            collection.delete_many({})
            print('Ranking removed')

# mongo = MongoDB()
# mongo.getRankedTraders()

# TODO trader(mothly_return, year_return, rank, name, open trades(symbol, direction, takeprofit)
# TODO sentiment(symbol, type, strength)