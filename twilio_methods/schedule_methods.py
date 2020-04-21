import time
import pytz
import twilio.rest
import pandas as pd
from datetime import datetime
from twilio import twiml

def dow_list(dow):
    if len(dow) == 1 and dow != "*":
        return [int(dow)]
    elif "-" in dow:
        return [days for days in range(int(dow[0]), int(dow[-1])+1)]
    elif "," in dow:
        return list(map(int, dow.split(",")))
    elif dow == "*":
        return [days for days in range(7)]
    elif dow == "weekday":
        return [days for days in range(5)]
    elif dow == "weekend":
        return [6,7]

def habit_today(df_habit, df_user):

    pst = pytz.timezone("America/Los_Angeles")
    now = datetime.now().astimezone(pst)

    df_today = df_habit.loc[(df_habit["time_hour"]>=now.hour)&
                            (df_habit["time_minute"]>=now.minute)&
                            [now.weekday()+1 in lst \
                             for lst in df_habit.time_day_of_week.apply(dow_list)]]

    df_output = pd.merge(df_today, df_user, how="left", on=["user_id"])
    return df_output
    