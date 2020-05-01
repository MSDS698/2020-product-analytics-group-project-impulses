import ast
import numpy as np
import collections
import plotly
import plotly.graph_objects as go
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
            self.graph = self.num_per_day(self.transactions)

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
        transactions = classes.Transaction.query.filter_by(
            user_id=self.user_id)\
            .filter((classes.Transaction.trans_date >= self.date) &
                    (classes.Transaction.category_id.in_(id_list))).all()
        ct = len(transactions)
        if ct < self.thresh:
            return None
        return transactions

    def num_per_day(self, transactions):
        """
        Return the number of time user spent on habit on each day of the week
        :param transactions: list of transactions
        """
        map_day = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday',
                   4: 'Friday', 5: 'Saturday', 6: 'Sunday'}
        num_per_day = collections.Counter([x.trans_date.weekday()
                                           for x in transactions])
        sorted_num_per_day = sorted(num_per_day.items())
        day = [map_day[x[0]] for x in sorted_num_per_day]
        freq = [x[1] for x in sorted_num_per_day]
        fig = go.Figure(data=[go.Bar(x=day, y=freq)],
                        layout=go.Layout(title='Purchased {}'.format(self.habit_name))
                        )
        output = plotly.offline.plot(fig, include_plotlyjs=False,
                                     image_width='100%',
                                     image_height='100%',
                                     output_type='div')
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
        avg_amount = round(np.mean([float(x.trans_amount) for x in transactions]),
                           2)
        return avg_amount
