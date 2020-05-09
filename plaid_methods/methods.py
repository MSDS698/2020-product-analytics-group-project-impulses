import plaid
from plaid.errors import APIError, ItemError, PlaidError
import requests

import os
from typing import List
import time


def get_transactions(
    client: plaid.Client, start_date: str, end_date: str,
    access_token: str, account_id: str
) -> List[dict]:
    """
    Returns transactions associated with access_token
    :param [client]: plaid client object that encapsulates plaid keys
    :type [client]: [plaid.Client]

    :param [start_date]: string in the format "YYYY-MM-DD"
                         that defines the start
    date of the window to retrieve transactions from
    :type [start_date]: [string]

    :param [end_date]: string in the format "YYYY-MM-DD" that defines the end
    date of the window to retrieve transactions from
    :type [end_date]: [string]

    :param [access_token]:  access token to use to retrieve transactions
    :type [access_token]: [string]

    :param [account_id]:  account id of the transactions you want to retrieve
    :type [account_id]:[list[string]]
    """
    timeout = 5
    while True:
        try:
            response = client.Transactions.get(
                access_token, start_date=start_date, end_date=end_date,
                account_ids=[account_id]
            )

            transactions = response["transactions"]

            while len(transactions) < response["total_transactions"]:
                response = client.Transactions.get(
                    access_token,
                    start_date=start_date,
                    end_date=end_date,
                    offset=len(transactions),
                    account_ids=[account_id]
                )
                transactions.extend(response["transactions"])
            break
        except ItemError as e:
            if e.code == "NO_PRODUCT_READY":
                if timeout == 0:
                    return e.code
                else:
                    time.sleep(.5)
                    timeout = timeout - 1

        except APIError as e:
            return e.code
    return transactions


def get_accounts(client: plaid.Client, access_token: str) -> List[dict]:
    """
    Returns account information
    :param [client]: plaid client object that encapsulates plaid keys
    :type [client]: [plaid.Client]

    :param [access_token]:  access token to use to retrieve transactions
    :type [access_token]: [string]
    """
    try:
        response = client.Accounts.get(access_token)
    except APIError as e:
        return e.code
    return response["accounts"]


def token_exchange(client: plaid.Client, public_token: str) -> dict:
    """
    Returns account information
        :param [client]: plaid client object that encapsulates plaid keys
        :type [client]: [plaid.Client]

        :param [public_token]:  public token recieved from Plaid Link
        :type [public_token]: [string]
    """
    try:
        response = client.Item.public_token.exchange(public_token)
    except PlaidError as e:
        return e.code

    return response
