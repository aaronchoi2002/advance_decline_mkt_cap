import yfinance as yf
import pandas as pd
import streamlit as st
from language import languages
import mplfinance as mpf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import time




# Define the ticker symbol
#df = pd.read_csv("C:/Users/aaron/OneDrive/文档/web_app/advance_decline/sp500_adj_close.csv")

@st.cache_data
def download_stock_data(tickers, start_date, symbol, dummy):
    df = yf.download(tickers, start=start_date)["Adj Close"]
    df = df.T
    df = pd.merge(symbol.set_index('tickers'), df, left_index=True, right_index=True)
    df = df.T
    df = df.dropna(axis=1, how='all')
    df_dow = yf.download("^GSPC", start="2013-01-01")

    return df, df_dow


def assign_stock_return_labels(neutral_threshold_percent, df_diff):
    df_diff_sign = df_diff.applymap(
        lambda x: 'positive' if x > neutral_threshold_percent else (
            'negative' if x < -neutral_threshold_percent else (
                'neutral' if -threshold_percent <= x <= neutral_threshold_percent else 'no data')))
    return df_diff_sign

def process_df(df):
    df_sign = assign_stock_return_labels(threshold_percent, df)
    positive_counts = df_sign[df_sign == 'positive'].count(axis=1)
    neutral_counts = df_sign[df_sign == 'neutral'].count(axis=1)
    negative_counts = df_sign[df_sign == 'negative'].count(axis=1)
    no_data_counts = df_sign[df_sign == 'no data'].count(axis=1)

    # Creating a DataFrame to show the counts
    df_counts = pd.DataFrame({
        'positive_returns': positive_counts,
        'neutral_returns': neutral_counts,
        'negative_returns': negative_counts,
        'no_data': no_data_counts
    })

    return df_counts

def calculate_metrics(df):
    """Calculate the total, AD, positive percentage and positive neutral percentage.

    Args:
    df (DataFrame): Input DataFrame with 'positive_returns', 'neutral_returns', 'negative_returns' columns.

    Returns:
    df (DataFrame): DataFrame with new columns 'total', 'AD', 'positive_percentage', 'positive_neutral_percentage'.
    """
    df["total"] = df["positive_returns"]+ df["negative_returns"]
    df["AD"] = df["positive_returns"] - df["negative_returns"]
    df["positive_percentage"] = round((df["positive_returns"] / df["total"])*100,2)
    return df




# Data cleaning 
tickers = pd.read_csv('S&P_500.csv')
symbol = tickers["Symbol"]
symbol_list = symbol.tolist()
symbol = symbol.to_frame(name="tickers")
# Current time as a dummy input
dummy = 0  
df, df_dow= download_stock_data(symbol_list, "2013-01-01", symbol, dummy)

selected_language = st.sidebar.selectbox("Choose a language", options=['English', '簡體', '繁體'])
threshold_percent = st.sidebar.number_input(f"{languages['Neutral_Threshold(%)'][selected_language]}", min_value=0.0, max_value=10.0, value=0.0, step=0.1)
if st.sidebar.button(f"{languages['refresh'][selected_language]}"):
    dummy = time.time() # Current time as a dummy input
    df, df_dow= download_stock_data(symbol_list, "2013-01-01", symbol, dummy)
st.title(f"{languages['title'][selected_language]}")

# Calculating the price difference
df_diff = df.pct_change() * 100
df_dow["pct"] = df_dow["Adj Close"].pct_change() * 100

# Separating the dataframe 'df_diff' into smaller dataframes based on the ranking of market cap.
df_top_33 = df_diff.iloc[:, :13]
df_top_33_50 = df_diff.iloc[:, 13:37]
df_top_50_66 = df_diff.iloc[:, 37:85]
df_top_66 = df_diff.iloc[:, 85:]


# Apply the 'process_df' function to each of the created dataframes
df_counts = process_df(df_diff)
df_counts_33 = process_df(df_top_33)
df_counts_33_50 = process_df(df_top_33_50)
df_counts_50_66 = process_df(df_top_50_66)
df_counts_66 = process_df(df_top_66)


st.subheader(languages['today'][selected_language])


df_counts = calculate_metrics(df_counts)
df_counts_33 = calculate_metrics(df_counts_33)
df_counts_33_50 = calculate_metrics(df_counts_33_50)
df_counts_50_66 = calculate_metrics(df_counts_50_66)
df_counts_66 = calculate_metrics(df_counts_66)



st.write(df_counts["AD"].index[-1])
Col1, Col2, Col3  = st.columns(3)
with Col1:
    st.metric(label=languages['S&P500'][selected_language], value=f"{round(df_dow['pct'].iloc[-1],2)}%")

with Col2:
    st.metric(label=languages['AD'][selected_language], value=df_counts["AD"].iloc[-1])

with Col3:
    st.metric(label=languages['positive_percentage'][selected_language], value=f'{df_counts["positive_percentage"].iloc[-1]}%')





st.write("_______________")

Col1, Col2, Col3, Col4 = st.columns(4)
with Col1:
    st.metric(label=languages['Positive Return'][selected_language], value=df_counts["positive_returns"].iloc[-1])

with Col2:
    st.metric(label=languages['Neutral Returns'][selected_language], value=df_counts["neutral_returns"].iloc[-1])

with Col3:
    st.metric(label=languages['Negative Returns'][selected_language], value=df_counts["negative_returns"].iloc[-1])

with Col4:
    st.metric(label=languages['No Data'][selected_language], value=df_counts["no_data"].iloc[-1])


st.write("_______________")
st.subheader(languages['market_cap'][selected_language])
st.write(languages["number_of_stocks_up"][selected_language])
Col1, Col2, Col3, Col4 = st.columns(4)
with Col1:
    st.metric(label=languages['AD_33'][selected_language], value=f'{df_counts_33["positive_percentage"].iloc[-1]}%')

with Col2:
    st.metric(label=languages['AD_33_50'][selected_language], value=f'{df_counts_33_50["positive_percentage"].iloc[-1]}%')

with Col3:
    st.metric(label=languages['AD_50_66'][selected_language], value=f'{df_counts_50_66["positive_percentage"].iloc[-1]}%')

with Col4:
    st.metric(label=languages['AD_66'][selected_language], value=f'{df_counts_66["positive_percentage"].iloc[-1]}%')



st.markdown("""<hr style="border-top: 2px solid black; border-bottom: 2px solid black;">""", unsafe_allow_html=True)
st.subheader(languages['chart'][selected_language])
Col1, Col2 = st.columns(2)
with Col1:
    trade_day = st.number_input(f"{languages['Trading days covered'][selected_language]}", min_value=1.0, max_value=2800.0, value=60.0, step=1.0)
    # Get last 30 days data
    df_last_days = df_counts.tail(int(trade_day))
    df_last_days_33 = df_counts_33.tail(int(trade_day))
    df_last_days_33_50 = df_counts_33_50.tail(int(trade_day))
    df_last_days_50_66 = df_counts_50_66.tail(int(trade_day))
    df_last_days_66 = df_counts_66.tail(int(trade_day))


with Col2:
    average = st.number_input(f"{languages['Average Days'][selected_language]}", min_value=1.0, max_value=60.0, value=10.0, step=1.0)
    #Get the average of the last 30 days
    df_last_days["positive_percentage_average"] = df_last_days["positive_percentage"].rolling(int(average)).mean()
    df_last_days_33["positive_percentage_average"] = df_last_days_33["positive_percentage"].rolling(int(average)).mean()
    df_last_days_33_50["positive_percentage_average"] = df_last_days_33_50["positive_percentage"].rolling(int(average)).mean()
    df_last_days_50_66["positive_percentage_average"] = df_last_days_50_66["positive_percentage"].rolling(int(average)).mean()
    df_last_days_66["positive_percentage_average"] = df_last_days_66["positive_percentage"].rolling(int(average)).mean()


# Calculate difference
df_last_days_33['diff'] = df_last_days_33['positive_percentage_average'] - df_last_days_66['positive_percentage_average']

# Create line charts
st.write(df_last_days.index[0])


df_dow = df_dow.tail(int(trade_day))

#Create subplots
fig = make_subplots(rows=3, cols=1)

#Add candlestick chart
fig.add_trace(go.Candlestick(x=df_dow.index, 
                             open=df_dow['Open'], 
                             high=df_dow['High'], 
                             low=df_dow['Low'], 
                             close=df_dow['Close'], 
                             name='S&P 500'), row=1, col=1)

# Add line charts
fig.add_trace(go.Scatter(x=df_last_days.index, y=df_last_days['positive_percentage_average'], mode='lines', name=languages['positive_percentage'][selected_language]), row=2, col=1)
fig.add_trace(go.Scatter(x=df_last_days_33.index, y=df_last_days_33['positive_percentage_average'], mode='lines', name=languages['AD_33'][selected_language]), row=2, col=1)
fig.add_trace(go.Scatter(x=df_last_days_33_50.index, y=df_last_days_33_50['positive_percentage_average'], mode='lines', name=languages['AD_33_50'][selected_language]), row=2, col=1)
fig.add_trace(go.Scatter(x=df_last_days_50_66.index, y=df_last_days_50_66['positive_percentage_average'], mode='lines', name=languages['AD_50_66'][selected_language]), row=2, col=1)
fig.add_trace(go.Scatter(x=df_last_days_66.index, y=df_last_days_66['positive_percentage_average'], mode='lines', name=languages['AD_66'][selected_language]), row=2, col=1)
fig.add_trace(go.Scatter(x=df_last_days_33.index, y=df_last_days_33['diff'], mode='lines', name='Difference'), row=3, col=1)

# Update layout
fig.update_layout(height=800, width=1200, title_text="^GSPC Prices and Average Percentages")
fig.update_layout(xaxis_rangeslider_visible=False)
fig.update_layout(hovermode="x unified")  # add line


#Show the plot in Streamlit
st.plotly_chart(fig)