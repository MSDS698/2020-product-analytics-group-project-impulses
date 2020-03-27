import psycopg2
import datetime


class SimulatedInvestmentPlatform:

    def __init__(self, user_id, amount, date):
        """

        :param user_id: user id (int)
        :param amount: amount of saving or amount user is withdrawing (float)
        :param date: date of transaction (datetime.date or str)
        """
        self.user_id = user_id
        self.amount = amount
        self.date = date

    @staticmethod
    def connect_database():
        """
        Connect to the postgres database.
        :return: connection
        """
        connection = psycopg2.connect(user="masteruser",
                                      password="productimpulses",
                                      host="maindb.cuwtgivgs05r.us-west-1.rds.amazonaws.com",
                                      port="5432",
                                      database="postgres")
        return connection

    @staticmethod
    def close_connection(cursor, connection):
        """
        Close the connection.
        :param cursor:
        :param connection:
        """
        cursor.close()
        connection.close()

    def update_savings(self):
        """
        Update the savings_history table when the user save money
        """
        if isinstance(self.date, str):
            # If the date is in string format, convert it to date format
            self.date = datetime.datetime.strptime(self.date, '%Y-%m-%d').date()
        connection = self.connect_database()
        cursor = connection.cursor()
        query_balance = f"""SELECT total_savings 
                            FROM dw.savings_history 
                            WHERE user_id={self.user_id} 
                            ORDER BY update_date DESC LIMIT 1"""
        cursor.execute(query_balance)
        balance = cursor.fetchone()
        if balance:
            balance = float(balance[0]) + self.amount
        else:
            balance = self.amount
        now = datetime.datetime.date(datetime.datetime.now())
        current_date = psycopg2.Date(now.year, now.month, now.day)
        transaction_date = psycopg2.Date(self.date.year, self.date.month, self.date.day)
        add_saving = f"""INSERT INTO dw.savings_history (user_id, amount, total_savings, transfer_date, update_date)
                         VALUES ({self.user_id}, {self.amount}, {balance}, {transaction_date}, {current_date})"""
        cursor.execute(add_saving)
        connection.commit()
        self.close_connection(cursor, connection)

    def user_withdraw(self):
        """
        Update the savings_history table when the user withdraw money
        """
        self.update_savings()
