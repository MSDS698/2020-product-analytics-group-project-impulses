import os
from datetime import datetime
from app import application, classes, db
from flask import redirect, render_template, url_for, request, flash, session
from flask_login import current_user, login_user, login_required, logout_user
from plaid.errors import ItemError
from plaid_methods.methods import get_accounts, get_transactions, \
    token_exchange
from plaid_methods import add_plaid_data as plaid_to_db
from plaid import Client
from plaid.api import Item
import pytz
import pandas as pd
import twilio.rest
from twilio.twiml.messaging_response import MessagingResponse
from scripts.coin_transaction import add_login_coin, add_saving_coin, \
    enter_lottery, lottery_drawing
from app.plotly_dashboard import plotly_saving_history, plotly_percent_saved
from scripts.extract_habit import Insights

ENV_VARS = {
    "PLAID_CLIENT_ID": os.environ["PLAID_CLIENT_ID"],
    "PLAID_PUBLIC_KEY": os.environ["PLAID_PUBLIC_KEY"],
    "PLAID_SECRET": os.environ["PLAID_SECRET"],
    "PLAID_ENV": os.environ["PLAID_ENV"],
    "TWILIO_ACCOUNT_SID": os.environ["TWILIO_ACCOUNT_SID"],
    "TWILIO_AUTH_TOKEN": os.environ["TWILIO_AUTH_TOKEN"],
    "SQLALCHEMY_DATABASE_URI": os.environ["SQLALCHEMY_DATABASE_URI"],
    "VERIFICATION_SID": os.environ["VERIFICATION_SID"]
}

# setup plaid client
client = Client(
    ENV_VARS["PLAID_CLIENT_ID"],
    ENV_VARS["PLAID_SECRET"],
    ENV_VARS["PLAID_PUBLIC_KEY"],
    ENV_VARS["PLAID_ENV"],
)

# setup twilio client
twilio_client = twilio.rest.Client(
    ENV_VARS["TWILIO_ACCOUNT_SID"],
    ENV_VARS["TWILIO_AUTH_TOKEN"])


@application.route("/index")
@application.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    return render_template("home.html")


@application.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    login_form = classes.LogInForm()
    if login_form.validate_on_submit():
        email = login_form.email.data
        password = login_form.password.data
        user = classes.User.query.filter_by(email=email).first()
        if user is not None and user.check_password(password):
            login_user(user)
            add_login_coin(user)
            return redirect(url_for("index"))
        else:
            flash('Invalid username and password combination')
    return render_template("login.html", form=login_form)


@application.route("/register", methods=["POST", "GET"])
def register():
    registration_form = classes.RegistrationForm()
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    if registration_form.validate_on_submit():
        first_name = registration_form.first_name.data
        last_name = registration_form.last_name.data
        email = registration_form.email.data
        phone = registration_form.phone.data
        password = registration_form.password.data

        # Make sure email and phone number are unique
        user_count = (classes.User.query.filter_by(email=email).count(
        ) + classes.User.query.filter_by(phone=phone).count())

        if len(phone) != 10:
            flash('Please enter a valid phone number')
        elif user_count != 0:
            flash('User already exists')
        else:
            user = classes.User(first_name, last_name, email, phone, password)
            db.session.add(user)
            db.session.commit()
            session['phone'] = phone
            return redirect(url_for('verify'))

    return render_template("register.html", form=registration_form)


@application.route('/verify', methods=('GET', 'POST'))
def verify():
    """Verify a user on registration with their phone number"""
    vsid = start_verification("+1"+str(session.get('phone')), "sms")
    if vsid is None:
        flash('Your phone number cannot be recognized \
        Please change it later.')
        return redirect(url_for("login"))
    else:
        if request.method == 'POST':
            phone = "+1"+str(session.get('phone'))
            code = request.form['code']
            return check_verification(phone, code)
    return render_template('verify.html')


def start_verification(to, channel='sms'):
    if channel not in ('sms', 'call'):
        channel = 'sms'

    service = ENV_VARS["VERIFICATION_SID"]
    verification = twilio_client.verify \
        .services(service) \
        .verifications \
        .create(to=to, channel=channel)
    return verification.sid


def check_verification(phone, code):
    service = ENV_VARS["VERIFICATION_SID"]
    if len(code) != 6:
        flash("The code you provided should be 6 digits, \
            Please try again.")
    else:
        try:
            verification_check = twilio_client.verify \
                .services(service) \
                .verification_checks \
                .create(to=phone, code=code)

            if verification_check.status == "approved":
                user_phone = session.get('phone')
                user = classes.User.query.filter_by(phone=user_phone).first()
                user.status = "verified"
                db.session.commit()

                flash('Your phone number has been verified! \
                    Please login to continue.')
                return redirect(url_for('login'))
            else:
                flash('The code you provided is incorrect. Please try again.')
        except Exception as e:
            flash("Error validating code: {}".format(e))

    return redirect(url_for('verify'))


@application.route('/create_habit', methods=["POST"])
@login_required
def create_habit():
    # add a new habit

    habit_form = classes.HabitForm()
    if habit_form.validate_on_submit():
        habit_name = habit_form.habit_name.data
        habit_category = habit_form.habit_category.data
        time_minute = habit_form.time_minute.data
        time_hour = habit_form.time_hour.data
        time_day_of_week = habit_form.time_day_of_week.data
        habit = classes.Habits(user=current_user,
                            habit_name=habit_name,
                            habit_category=habit_category,
                            time_minute=int(time_minute),
                            time_hour=int(time_hour),
                            time_day_of_week=time_day_of_week)

        db.session.add(habit)
        db.session.commit()
        return redirect(url_for("dashboard"))

    return redirect(url_for('dashboard'))


# @application.route("/dashboard", methods=["POST", "GET"])
# @login_required
# def dashboard():
#     # default values
#     flag_habits_edit = False

#     # get user session
#     user_id = current_user.id

#     # check if signed up in plaid
#     plaid_dict = classes.PlaidItems.query.filter_by(
#         user_id=user_id).first()

#     if plaid_dict:  # if signed up in plaid
#         # get data from the savings history table
#         pass

#     # get selected habits
#     if request.method == "POST":
#         habit_name = request.form.getlist("habit_name")
#         habit_category = request.form.getlist("habit_category")
#         time_hour_minute = request.form.getlist("time_hour_minute")
#         time_day_of_week = request.form.getlist("time_day_of_week")

#         # delete the user's habits
#         classes.Habits.query.filter_by(user_id=user_id).delete()

#         # add the latest habits back to db
#         for i in range(len(habit_name)):
#             habit = classes.Habits(user_id=user_id, habit_name=habit_name[i],
#                                    habit_category=habit_category[i],
#                                    time_minute=time_hour_minute[i][3:],
#                                    time_hour=time_hour_minute[i][:2],
#                                    time_day_of_week=time_day_of_week[i])
#             db.session.add(habit)
#             db.session.commit()
#         flag_habits_edit = True
#     habits = classes.Habits.query.filter_by(user_id=user_id).all()

#     return render_template("dashboard.html",
#                            user=current_user,
#                            habits=habits,
#                            flag_habits_edit=flag_habits_edit,
#                            plaid_public_key=client.public_key,
#                            plaid_environment=client.environment,
#                            plaid_products=ENV_VARS.get("PLAID_PRODUCTS",
#                                                        "transactions"),
#                            plaid_country_codes=ENV_VARS.
#                            get("PLAID_COUNTRY_CODES", "US")
#                            )


@application.route("/dashboard", methods=["POST", "GET"])
@login_required
def dashboard():
    # default values
    lottery_status = "Buy a lottery ticket before it ends!"

    # get lottery
    if request.method == "POST":
        buy_lottery = request.form.getlist("lottery_submit")
        checked_lottery = request.form.getlist("lottery_check")

        # if user try to buy the lottery tickets
        if buy_lottery[0] == 'buy':
            lottery_objs = classes.Lottery.query.filter(
                classes.Lottery.id.in_(checked_lottery)).all()
            cost = sum(lottery_obj.cost for lottery_obj in lottery_objs)
            if cost > int(current_user.coins):
                lottery_status = 'Not enough coins'
            else:
                lottery_status = 'You just bought a lottery ticket'
                for lottery_obj in lottery_objs:
                    enter_lottery(current_user, lottery_obj)

    # get the lottery that the user has bought
    bought_lottery_records = classes.UserLotteryLog.query.filter_by(
        user=current_user).all()

    # get all the available lottery records
    tz = pytz.timezone("America/Los_Angeles")
    current_time = datetime.now().astimezone(tz)
    available_lottery_records = classes.Lottery.query.filter(
        classes.Lottery.start_date <= str(current_time),
        classes.Lottery.end_date >= str(current_time)).all()

    # Dashboard tab
    # extract user's saving history from coins associated with "saving"
    user_id = current_user.id

    # using the login coins now for demo, since we don't have enough data for
    # the saving coins yet
    saving_date = classes.Coin.query.filter(
        classes.Coin.user_id == user_id,
        classes.Coin.description.in_(['login', 'registration'])) \
        .with_entities(classes.Coin.log_date).all()
    saving_coins = classes.Coin.query.filter(
        classes.Coin.user_id == user_id,
        classes.Coin.description.in_(['login', 'registration'])) \
        .with_entities(classes.Coin.coin_amount).all()
    savings_bar_plot, total_saving_coins = \
        plotly_saving_history(saving_date, saving_coins)

    # count how many times user has responded "Y" to save
    # here, description should be "saving" as well in the future
    num_saved = len(classes.Coin.query.filter_by(user_id=user_id,
                                                 description='login').all())
    # count number of total saving suggestions texts sent to user
    # total num = num of habits * days since user first signed up
    signup_tz = tz.localize(classes.User.query.filter_by(id=user_id).
                            with_entities(classes.User.signup_date).first()[
                                0])
    days = (datetime.now().astimezone(tz) - signup_tz).days
    num_total_suggestions = len(classes.Habits.query.
                                filter_by(user_id=user_id).all()) * days
    saving_percent_plot = plotly_percent_saved(num_saved,
                                               num_total_suggestions)
    # Retrieve spending habits for Insights
    categories_file = os.path.join(os.getcwd(), 'scripts', 'categories.json')

    # beginning_month = datetime(year=datetime.now().year,
    #                            month=datetime.now().month,
    #                            day=1)
    beginning_month = datetime(year=2019,
                               month=10,
                               day=1)
    insights_list = []
    thresholds = [8, 6, 2]
    for ind, habit_name in enumerate(['coffee', 'lunch', 'transportation']):
        insights = Insights(user_id, beginning_month, categories_file,
                            habit_name, thresholds[ind])
        if insights.transactions is not None:
            insights_list.append(insights)

    coin_log = classes.Coin.query.filter_by(user=current_user).order_by(
        classes.Coin.id.desc()).limit(6).all()

    return render_template("dashboard.html",
                           user=current_user,
                           coin_log=coin_log,
                           form=classes.HabitForm(),
                           lottery_status=lottery_status,
                           available_lottery_records=available_lottery_records,
                           bought_lottery_records=bought_lottery_records,
                           plaid_public_key=client.public_key,
                           plaid_environment=client.environment,
                           plaid_products=ENV_VARS.get("PLAID_PRODUCTS",
                                                       "transactions"),
                           plaid_country_codes=ENV_VARS.
                           get("PLAID_COUNTRY_CODES", "US"),
                           source_bar=savings_bar_plot,
                           source_pie=saving_percent_plot,
                           num_total_suggestions=num_total_suggestions,
                           num_saved=num_saved,
                           total_saving_coins=total_saving_coins,
                           insights=insights_list
                           )


@application.route('/find_insights')
@login_required
def find_insights():
    # time.sleep(3)
    insights_start_date = '2019-10-01'
    insights_end_date = '2019-11-01'
    df = pd.DataFrame([t.__dict__ for t in current_user.transaction])
    df.to_csv('test.csv')
    return df.to_markdown()


@application.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


@application.route("/delete_plaid_account", methods=["POST"])
def delete_plaid_account():
    account_id = request.form['accountId']
    # get account
    account = classes.Accounts.query.get(account_id)
    # get transactions associated with account
    transactions = classes.Transaction.query.\
        filter_by(account_id=account.id)

    accounts_with_plaid_id = classes.Accounts.query.\
        filter_by(plaid_id=account.plaid_id)\
        .count()
    # if only account associated with plaid id delete plaid id
    if accounts_with_plaid_id == 1:
        plaid_item = classes.PlaidItems.query.get(account.plaid_id)
        Item(client).remove(plaid_item.access_token)
        db.session.delete(plaid_item)

    for transaction in transactions:
        db.session.delete(transaction)
    db.session.delete(account)
    db.session.commit()

    return redirect(url_for('dashboard'))


@application.errorhandler(401)
def re_route(e):
    return redirect(url_for("login"))


@application.errorhandler(403)
def re_route(e):
    return redirect(url_for("index"))


@application.errorhandler(404)
def re_route(e):
    return redirect(url_for("index"))


@application.errorhandler(500)
def re_route(e):
    return redirect(url_for("index"))


@application.route("/access_plaid_token", methods=["POST", "GET"])
def access_plaid_token():
    try:
        public_token = request.form["public_token"]
        # extract selected account information from response
        selected_accounts_data = [
            key for key in request.form.keys() if key.startswith('accounts')]
        account_indices = set([int(field[9])
                               for field in selected_accounts_data])
        accounts = []

        for idx in account_indices:
            accounts.append(
                {'account_id': request.form[f'accounts[{idx}][id]'],
                 'name': request.form[f'accounts[{idx}][name]'],
                 'type': request.form[f'accounts[{idx}][type]'],
                 'subtype': request.form[f'accounts[{idx}][subtype]']}
            )

        existing_account_ids = [account_id for account in current_user.accounts
                                for account_id in account.account_plaid_id]

        for new_account in accounts:
            if new_account['account_id'] in existing_account_ids:
                flash("You have already added the account selected")
                redirect(url_for("dashboard"))

        response = token_exchange(client, public_token)
        item_id = response['item_id']
        access_token = response['access_token']

        # add plaid items
        plaid = classes.PlaidItems(user=current_user, item_id=item_id,
                                   access_token=access_token)
        db.session.add(plaid)
        db.session.commit()

        plaid_to_db.add_accounts(accounts, current_user, plaid)

        for account in current_user.accounts:
            transactions = get_transactions(
                client, '2019-10-01', '2019-11-01',
                access_token=account.plaid_item.access_token,
                account_id=account.account_plaid_id)
            plaid_to_db.add_transactions(transactions, current_user, account)

    except ItemError as e:
        outstring = f"Failure: {e.code}"
        print(outstring)
        return outstring

    return redirect(url_for("dashboard"))


@application.route("/send_message", methods=['GET', 'POST'])
def send_message():
    dow_dict = {'weekday': [0, 1, 2, 3, 4],
                'weekend': [5, 6],
                'everyday': [0, 1, 2, 3, 4, 5, 6]}

    habits = classes.Habits.query.all()

    for habit in habits:
        pst = pytz.timezone("America/Los_Angeles")
        now = datetime.now().astimezone(pst)
        if now.weekday() in dow_dict[habit.time_day_of_week] and \
                habit.time_minute == now.minute and \
                habit.time_hour == now.hour:
            body = f"Would you like to save $5 on {habit.habit_category} " + \
                   "today? Respond Y/N"
            twilio_client.messages.create(
                body=body,
                to=habit.user.phone,
                from_="+16462573594")

    # lottery drawing and send message to the winner
    lottery_drawing()

    return redirect(url_for("index"))


@application.route("/receive_message", methods=["POST"])
def receive_message():
    dow_dict = {'weekday': [0, 1, 2, 3, 4],
                'weekend': [5, 6],
                'everyday': [0, 1, 2, 3, 4, 5, 6]}

    pst = pytz.timezone("America/Los_Angeles")
    now = datetime.now().astimezone(pst)
    date = now.date()

    number = str(request.form['From'])[2:]
    response = request.form['Body']
    user_by_num = classes.User.query.filter_by(phone=number).first()
    name = user_by_num.first_name

    user_habits_num = len([habit for habit in user_by_num.habits
                           if now.weekday() in
                           dow_dict[habit.time_day_of_week]])

    save_num = len([save for save in user_by_num.coin
                    if save.log_date == date and save.description == "saving"])

    if save_num >= user_habits_num:
        resp = MessagingResponse()
        res_str_1 = f"Oops, I don't understand!"
        resp.message(res_str_1)
        return str(resp)

    else:
        if response.lower() == "y":
            add_saving_coin(user_by_num)
            resp = MessagingResponse()
            res_str_1 = f"Hi {name}, you save some money today! Hoorey!"
            resp.message(res_str_1)
            return str(resp)

        elif response.lower() == "n":
            resp = MessagingResponse()
            res_str_1 = f"Hi {name}, we understand, maybe next time!"
            resp.message(res_str_1)
            return str(resp)

        else:
            resp = MessagingResponse()
            res_str = f"Hi {name}, that's not a valid response, " + \
                      "please respond Y/N "
            resp.message(res_str)
            return str(resp)
