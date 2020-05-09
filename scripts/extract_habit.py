import ast
import numpy as np
import collections
import matplotlib
import matplotlib.pyplot as plt
import mpld3
from datetime import datetime
from app import classes


class Insights:
    """
    Class to retrieve insights for a particular habit

    """

    def __init__(self, user_id, date, categories_file, habit_name, thresh):
        """

        :param user_id: user id
        :param date: beginning of the month to analyze
        :param categories_file:
        :param habit_name: string
        :param thresh: int
        """
        self.user_id = user_id
        self.date = date
        self.categories_file = categories_file
        self.habit_name = habit_name
        self.thresh = thresh
        self.transactions = self.get_habits_transactions()
        if self.transactions is not None:
            self.num = len(self.transactions)
            self.tot_amount = self.total_amount(self.transactions)
            self.avg_amount = self.average_amount(self.transactions)
            self.recommended = int(round(self.num * 0.8))
            self.yearly_saving = round((self.num - self.recommended) * 12 *
                                       self.avg_amount, 2)
            self.graph = self.num_per_day_graph(self.transactions)

    @staticmethod
    def parse_plaid_data(plaid_data):
        """
        Parse a string from plaid into python object
        :param plaid_data: name of the file (str)
        :return: list of dictionary
        """
        plaid_data = plaid_data.replace('\n', '')
        data = ast.literal_eval(plaid_data)
        return data

    def get_habits_transactions(self):
        """
        Return habits transactions if above the threshold and number
        of time spent on habit.
        Otherwise, return None.
        """
        data = open(self.categories_file).read()
        categories = self.parse_plaid_data(data)

        if self.habit_name == 'coffee':
            id_list = ['13005047',  # Cafe
                       '13005043'  # Coffee Shop
                       ]
        elif self.habit_name == 'lunch':
            # ids for restaurants
            id_restaurants = [x['category_id']
                              for x in categories['categories']
                              if 'Restaurants' in x['hierarchy']]
            # Ids to remove from restaurants
            id_to_remove = ['13005001',  # winery
                            '13005019',  # Juice Bar
                            '13005024',  # Ice Cream
                            '13005037',  # Distillery
                            '13005043',  # Coffee Shop
                            '13005047'  # Cafe
                            ]
            id_list = list(set(id_restaurants).difference(set(id_to_remove)))
        elif self.habit_name == 'transportation':
            id_list = ['22016000',  # Taxi
                       '22011000',  # Limos and Chauffeurs
                       '22006001'  # Ride share
                       ]
        else:
            # Not defined habit
            return None
        # Get the transactions from that user, for the specified month and
        # for the expenses from the category ids
        end_date = datetime(year=self.date.year, month=self.date.month + 1,
                            day=1)
        transactions = classes.Transaction.query.filter_by(
            user_id=self.user_id)\
            .filter((classes.Transaction.trans_date >= self.date) &
                    (classes.Transaction.trans_date < end_date) &
                    (classes.Transaction.category_id.in_(id_list))).all()
        ct = len(transactions)
        if ct < self.thresh:
            return None
        return transactions

    def num_per_day_graph(self, transactions):
        """
        Return the number of time user spent on habit on each day of the week
        :param transactions: list of transactions
        """
        map_day = {0: 'Mon', 1: 'Tues', 2: 'Wed', 3: 'Thurs',
                   4: 'Fri', 5: 'Sat', 6: 'Sun'}
        num_per_day = collections.Counter([x.trans_date.weekday()
                                           for x in transactions])
        for x in map_day.keys():
            if x not in num_per_day.keys():
                num_per_day[x] = 0
        sorted_num_per_day = sorted(num_per_day.items())
        day = [map_day[x[0]] for x in sorted_num_per_day]
        freq = [x[1] for x in sorted_num_per_day]
        matplotlib.use('Agg')
        fig = plt.figure(figsize=(6, 3))
        plt.bar(day, freq, align='center', alpha=0.5, color='#327AB7')
        plt.ylabel('Purchased {}'.format(self.habit_name))
        plt.xticks(ticks=np.arange(len(day)), labels=day)
        plt.title('Daily spending during the week')
        output = mpld3.fig_to_html(fig)
        plt.close()
        return output

    @staticmethod
    def total_amount(transactions):
        """
        Return the total amount spent on the habit.
        :param transactions: list of transactions
        """
        tot_amount = round(sum([float(x.trans_amount) for x in transactions]),
                           2)
        return tot_amount

    @staticmethod
    def average_amount(transactions):
        """
        Return the average spent on habit
        :param transactions: list of transactions
        """
        avg_amount = round(np.mean([float(x.trans_amount)
                                    for x in transactions]), 2)
        return avg_amount
