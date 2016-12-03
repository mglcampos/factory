from mongodb import MongoDB
import operator

class ProcessData():

    def __init__(self):
        self.mongo = MongoDB()

    def tradedCurrencies(self):
        pairs = {}
        pairs['currencies'], pairs['currency'] = self.mongo.getTradersCurrencies()
        inOrder = []
        temp = {}
        for pair in pairs['currencies']:
            temp[pair] = pairs['currencies'][pair]['total']

        for i in range (0,len(pairs['currency'])):
            max_pair = max(temp.iteritems(), key=operator.itemgetter(1))[0]
            inOrder.append(max_pair)
            del temp[max_pair]


        for i in range(0, len(pairs['currency'])):
            print(inOrder[i], pairs['currencies'][inOrder[i]])

p = ProcessData()
p.tradedCurrencies()