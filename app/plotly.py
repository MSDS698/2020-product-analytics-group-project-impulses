import plotly
import plotly.express as px
import pandas as pd


def plotly_saving_history(saving_date, saving_coins_sum):
    df = pd.DataFrame(saving_date, saving_coins_sum).reset_index()
    df.columns = ['coins', 'date']

    fig = px.bar(df, x="date", y="coins")
    output = plotly.offline.plot(fig, include_plotlyjs=False,
                                 output_type='div')
    return (output)


if __name__ == "__main__":
    plotly_saving_history(saving_date, saving_coins_sum)