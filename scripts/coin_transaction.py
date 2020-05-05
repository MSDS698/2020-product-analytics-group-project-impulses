import random
import pytz
from datetime import datetime
from app import classes, db


# helper function to update user coins when logging in
def add_login_coin(user):
    """Update user coins when logging in.

    When the user is logged in for the first time, 10 coins will be added
    as a sign-up bonus. For regular user login, 2 coins are rewarded daily.

    If any changes occur, a new coin transaction will be added to coin
    table and the coins column in user table will also be updated.
    """
    login_coin_date = db.session.query(db.func.max(classes.Coin.log_date)) \
        .filter_by(user=user, description="login").scalar()
    tz = pytz.timezone("America/Los_Angeles")
    if login_coin_date is None:  # first time login
        coin_amount = 10
        description = "registration"
    elif (datetime.now().astimezone(tz).date() - login_coin_date).days > 0:
        # daily login
        coin_amount = 2
        description = "login"
    else:
        return
    new_coin = classes.Coin(user=user, coin_amount=coin_amount,
                            log_date=datetime.now().astimezone(tz).date(),
                            description=description)
    user.coins += coin_amount
    db.session.add(new_coin)
    db.session.commit()


# helper function to update user coins when replying "yes" to saving texts
def add_saving_coin(user):
    """Update user coins when replying "yes" to saving texts.

    When the user replies "yes" to saving text messages, 10 coins will be
    added. A new coin transaction will be added to coin table and the coins
    column in user table will also be updated.
    """
    tz = pytz.timezone("America/Los_Angeles")
    new_coin = classes.Coin(user=user, coin_amount=10,
                            log_date=datetime.now().astimezone(tz).date(),
                            description="saving")
    user.coins += 10
    db.session.add(new_coin)
    db.session.commit()


# helper function to update user coins when entering a lottery
def enter_lottery(user, lottery):
    """Update user coins when buying an entry to a lottery.

    When the user buys an entry to a lottery, coins corresponding to the
    lottery cost will be deducted from the total number of coins that the
    user has.

    A new coin transaction will be added to coin table and the coins column
    in user table will also be updated. The user_lottery_log table will also
    be updated.
    """
    # check if the user has bought the lottery before
    lottery_log = classes.UserLotteryLog.query.filter_by(
        user=user, lottery=lottery).first()
    if lottery_log:
        lottery_log.entries += 1
    else:  # the user buys the lottery for the first time
        new_lottery_log = classes.UserLotteryLog(user=user, lottery=lottery)
        db.session.add(new_lottery_log)

    # update the user's coins
    tz = pytz.timezone("America/Los_Angeles")
    new_coin = classes.Coin(user=user, coin_amount=-lottery.cost,
                            log_date=datetime.now().astimezone(tz).date(),
                            description="lottery")
    user.coins -= lottery.cost
    db.session.add(new_coin)
    db.session.commit()


# lottery drawing function
def lottery_drawing():
    """Draw the winner for lotteries that have ended.

    First check which lotteries have ended without the winner drawn.
    Then choose the winner, send message to the winner, and update
    the lottery table.
    """
    tz = pytz.timezone("America/Los_Angeles")
    current_time = datetime.now().astimezone(tz)
    lottery_to_draw = classes.Lottery.query.filter(
        classes.Lottery.winner_user_id.is_(None),
        classes.Lottery.end_date <= str(current_time)).all()

    for lottery in lottery_to_draw:
        participants = classes.UserLotteryLog.query.filter_by(
            lottery=lottery).all()
        participants = [p.user_id for p in participants
                        for _ in range(p.entries)]

        if participants:
            lottery.winner_user_id = winner = random.choice(participants)
            # send message to the winner
            body = f"Congratulations! You've won the lottery for " \
                   + f"{lottery.lottery_name}!"
            twilio_client.messages.create(
                body=body,
                to=classes.User.query.filter_by(id=winner).first().phone,
                from_="+16462573594")
        else:
            lottery.winner_user_id = -1
    db.session.commit()
