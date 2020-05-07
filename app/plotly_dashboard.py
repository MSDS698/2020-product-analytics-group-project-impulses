import plotly
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


def plotly_saving_history(saving_date, saving_coins):
    saving_coins_sum = [saving_coins[0][0]]
    for i, coin in enumerate(saving_coins[1:]):
        saving_coins_sum.append(saving_coins_sum[i] + coin[0])
    df = pd.DataFrame(saving_date, saving_coins_sum).reset_index()
    df.columns = ['coins', 'date']
    fig = px.line(df, x="date", y="coins")
    fig.update_layout(xaxis_title=None,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey')
    output = plotly.offline.plot(fig, include_plotlyjs=False,
                                 output_type='div')
    return output, saving_coins_sum[-1]


def plotly_percent_saved(num_saved, num_total_suggestions):
    labels = ['Saved', 'Unsaved']
    values = [num_saved, num_total_suggestions - num_saved]

    # pull is given as a fraction of the pie radius
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, pull=[0.2, 0])])
    output = plotly.offline.plot(fig, include_plotlyjs=False,
                                 output_type='div')
    return output


if __name__ == "__main__":
    plotly_saving_history(saving_date, saving_coins_sum)
    plotly_percent_saved(num_saved, num_total_suggestions)
