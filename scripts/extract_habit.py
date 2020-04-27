import ast
import numpy as np
import collections
import matplotlib.pyplot as plt
from app import classes


def parse_plaid_data(plaid_data):
    """
    Parse a string from plaid into python object
    :param plaid_data: name of the file (str)
    :return: list of dictionary
    """
    plaid_data = plaid_data.replace('\n', '')
    data = ast.literal_eval(plaid_data)
    return data


def get_habits_transactions(user_id, date, habit_name, thresh,
                            categories_file):
    """
    Return habits transactions if above the threshold and number
    of time spent on habit.
    Otherwise, return None.
    :param user_id: user id
    :param date: beginning of the month to analyze
    :param habit_name: string
    :param thresh: int
    :param categories_file
    """
    data = open(categories_file).read()
    categories = parse_plaid_data(data)

    if habit_name == 'coffee':
        id_list = ['13005047',  # Cafe
                   '13005043'  # Coffee Shop
                   ]
    elif habit_name == 'lunch':
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
    elif habit_name == 'transportation':
        id_list = ['22016000',  # Taxi
                   '22011000',  # Limos and Chauffeurs
                   '22006001'  # Ride share
                   ]
    else:
        # Not defined habit
        return None
    # Get the transactions from that user, for the specified month and
    # for the expenses from the category ids
    transactions = classes.Transaction.query.filter_by(user_id=user_id)\
        .filter((classes.Transaction.trans_date >= date) &
                (classes.Transaction.category_id.in_(id_list))).all()
    ct = len(transactions)
    if ct < thresh:
        return None
    return transactions, ct


def num_per_day(transactions, habit_name):
    """
    Return the number of time user spent on habit on each day of the week
    :param transactions: list of transactions
    :param habit_name: str
    """
    map_day = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday',
               4: 'Friday', 5: 'Saturday', 6: 'Sunday'}
    num_per_day = collections.Counter([x.trans_date.weekday() for x in transactions])
    sorted_num_per_day = sorted(num_per_day.items())
    day = [map_day[x[0]] for x in sorted_num_per_day]
    freq = [x[1] for x in sorted_num_per_day]
    plt.bar(day, freq, align='center', alpha=0.5)
    plt.ylabel('Purchased {}'.format(habit_name))

    plt.show()


def total_amount(transactions):
    """
    Return the total amount spent on the habit.
    :param transactions: list of transactions
    """
    tot_amount = round(sum([float(x.trans_amount) for x in transactions]),
                       2)
    return tot_amount


def average_amount(transactions):
    """
    Return the average spent on habit
    :param transactions: list of transactions
    """
    avg_amount = round(np.mean([float(x.trans_amount) for x in transactions]),
                       2)
    return avg_amount
