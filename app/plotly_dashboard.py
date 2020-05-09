import plotly
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import pytz

TZ = pytz.timezone("America/Los_Angeles")


def select_past_week(saving_date):
    this_week_cnt = 0
    last_week_cnt = 0
    for dates in saving_date:
        if (datetime.now().astimezone(TZ).date() - dates[0]).days <= 7:
            this_week_cnt += 1
        elif (datetime.now().astimezone(TZ).date() - dates[0]).days <= 14:
            last_week_cnt += 1
    if last_week_cnt == 0:
        percentage = 0
    else:
        percentage = round((this_week_cnt - last_week_cnt) /
                           last_week_cnt * 100)
    return percentage, this_week_cnt * 10


def plotly_saving_history(saving_date, saving_coins):
    if len(saving_coins) != 0:
        saving_coins_sum = [(saving_date[0][0], saving_coins[0][0])]
        for i, coin in enumerate(saving_coins[1:]):
            saving_coins_sum.append(
                (saving_date[i + 1][0], saving_coins_sum[i][1] + coin[0]))

        saving_dict = dict(saving_coins_sum)
        base = datetime.now().astimezone(TZ).date()
        first_date = saving_coins_sum[0][0]
        latest_date = saving_coins_sum[-1][0]
        date_list = [(base - timedelta(days=x)) for x in range(0, 7)]
        for dates in date_list:
            if dates > latest_date:
                saving_dict[dates] = saving_dict[latest_date]
            elif dates < first_date:
                saving_dict[dates] = 0
        df = pd.DataFrame(saving_dict.items(), columns=['date', 'coins']) \
            .sort_values('date')

        fig = go.Figure(data=go.Scatter(x=df.date, y=df.coins,
                                        line=dict(color='#327AB7', width=4)))

        fig.update_layout(
            xaxis_range=[datetime.now().astimezone(TZ) - timedelta(days=7),
                         datetime.now().astimezone(TZ)])
        fig.update_layout(xaxis_title=None,
                          paper_bgcolor='rgba(0,0,0,0)',
                          plot_bgcolor='rgba(0,0,0,0)')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey')
        output = plotly.offline.plot(fig, include_plotlyjs=False,
                                     output_type='div')
        return output
    else:
        return 'No savings yet'


def plotly_percent_saved(num_saved, num_total_suggestions):
    labels = ['Saved', 'Unsaved']
    values = [num_saved, num_total_suggestions - num_saved]

    # pull is given as a fraction of the pie radius
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, pull=[0.2, 0])])
    fig.update_traces(marker=dict(colors=['#327AB7', 'grey']))
    output = plotly.offline.plot(fig, include_plotlyjs=False,
                                 output_type='div')
    return output


if __name__ == "__main__":
    plotly_saving_history(saving_date, saving_coins_sum)
    plotly_percent_saved(num_saved, num_total_suggestions)
