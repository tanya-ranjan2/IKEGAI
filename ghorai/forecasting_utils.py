import pandas as pd
from prophet import Prophet
import plotly.express as px 

def preprocess(filter_data: list[tuple], feature_parameters: dict) -> pd.DataFrame :
    # data = eval(filter_data)
    all_features = feature_parameters["exogenous_variable"] + [feature_parameters["feature"]]
    all_features.sort()
    print(filter_data)
    df = pd.DataFrame(filter_data)
    # df["date"] = pd.to_datetime(df['date'])
    # df = df.sort_values(by='date')
    return df 
    
def forecast_using_prophet(filter_data: list[tuple], feature_parameters: dict) -> str : 
    data = preprocess(filter_data, feature_parameters)
    data.rename(columns = {'date' : 'ds', feature_parameters['feature'] : 'y'}, inplace = True)
    model = Prophet()
    
    model.fit(data[['ds', 'y']])
    future = model.make_future_dataframe(periods = feature_parameters["days_to_forecast"])
    forecast = model.predict(future)
    
    forecast_df = pd.DataFrame(forecast[['ds', 'yhat']])
    forecast_df.columns = ['date', feature_parameters['feature']]

    fig = px.line(forecast_df, x='date', y= feature_parameters['feature'], title='Time Series with Rangeslider')

    fig.update_xaxes(rangeslider_visible=True)
    fig.write_html("plots/new_file.html")

    # return forecast_df
    return "success"