import os
from datetime import datetime
from app import application, classes, db
from flask import redirect, render_template, url_for, request, flash
from flask_login import current_user, login_user, login_required, logout_user
from plaid.errors import ItemError
from plaid_methods.methods import get_accounts, get_transactions, \
    token_exchange
from plaid_methods import add_plaid_data as plaid_to_db
from plaid import Client


ENV_VARS = {
    "PLAID_CLIENT_ID": os.environ["PLAID_CLIENT_ID"],
    "PLAID_PUBLIC_KEY": os.environ["PLAID_PUBLIC_KEY"],
    "PLAID_SECRET": os.environ["PLAID_SECRET"],
    "PLAID_ENV": os.environ["PLAID_ENV"]
}

# setup plaid client
client = Client(
    ENV_VARS["PLAID_CLIENT_ID"],
    ENV_VARS["PLAID_SECRET"],
    ENV_VARS["PLAID_PUBLIC_KEY"],
    ENV_VARS["PLAID_ENV"],
)


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
    if login_coin_date is None:  # first time login
        coin_amount = 10
    elif (datetime.now().date() - login_coin_date).days > 0:  # daily login
        coin_amount = 2
    else:
        return
    new_coin = classes.Coin(user=user, coin_amount=coin_amount,
                            log_date=datetime.now(),
                            description="login")
    user.coins += coin_amount
    db.session.add(new_coin)
    db.session.commit()


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
            return "Not a valid user"
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

        # User information does not already exist in DB
        if user_count == 0:
            user = classes.User(first_name, last_name, email, phone, password)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for("login"))
    return render_template("register.html", form=registration_form)


@application.route("/dashboard", methods=["POST", "GET"])
@login_required
def dashboard():
    # default values
    transactions = ''
    habit_form = classes.HabitForm()
    flag_habits_edit = False

    # get user session
    user_id = current_user.id

    # check if signed up in plaid
    plaid_dict = classes.PlaidItems.query.filter_by(
        user_id=user_id).first()

    if plaid_dict:  # if signed up in plaid
        print('dashboard: already signed up plaid')
        item_id = plaid_dict.item_id
        access_token = plaid_dict.access_token

        # get transaction data
        transactions = classes.Transaction.query.filter_by(user_id=user_id).all()

        # transactions = get_transactions(
        #     client, '2019-10-01', '2019-11-01',
        #     access_token=access_token,
        #     account_id=current_user.accounts[0].account_plaid_id)

    # get user session
    user_id = current_user.id

    # get selected habits
    if request.method == "POST":
        habit_name = request.form.getlist("habit_name")
        habit_category = request.form.getlist("habit_category")
        time_hour_minute = request.form.getlist("time_hour_minute")
        time_day_of_week = request.form.getlist("time_day_of_week")

        if habit_name:
            # delete the user's habits
            classes.Habits.query.filter_by(user_id=user_id).delete()

            # add the latest habits back to db
            for i in range(len(habit_name)):
                print(habit_name[i])
                print(time_day_of_week[i])
                print(time_hour_minute[i])
                habit = classes.Habits(user_id=user_id, habit_name=habit_name[i],
                                       habit_category=habit_category[i],
                                       time_minute=time_hour_minute[i][3:],
                                       time_hour=time_hour_minute[i][:2],
                                       time_day_of_week=time_day_of_week[i])
                print('asdd')
                db.session.add(habit)
                db.session.commit()
                print('dfsfsdf')
            flag_habits_edit = True
            print('flag_habits_edit: ', flag_habits_edit)
            # return redirect(url_for("dashboard") + '#habits-tab-md')
    habits = classes.Habits.query.filter_by(user_id=user_id).all()

    return render_template("dashboard.html",
                           user=current_user,
                           transactions=transactions,
                           habits=habits,
                           flag_habits_edit=flag_habits_edit,
                           form=habit_form,
                           plaid_public_key=client.public_key,
                           plaid_environment=client.environment,
                           plaid_products=ENV_VARS.get("PLAID_PRODUCTS",
                                                       "transactions"),
                           plaid_country_codes=ENV_VARS.
                           get("PLAID_COUNTRY_CODES", "US")
                           )


@application.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


@application.route("/access_plaid_token", methods=["POST", "GET"])
def access_plaid_token():
    try:
        public_token = request.form["public_token"]
        # extract selected account information from response
        selected_accounts_data = [
            key for key in request.form.keys() if key.startswith('accounts')]
        account_indicies = set([int(field[9])
                                for field in selected_accounts_data])
        accounts = []

        for idx in account_indicies:
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
