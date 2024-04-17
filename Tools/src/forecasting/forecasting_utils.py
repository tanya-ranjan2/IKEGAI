import pymongo 
import pandas as pd
from prophet import Prophet
import plotly.express as px 
import plotly.graph_objects as go

def preprocess(filter_data: list[tuple], feature_parameters: dict) -> pd.DataFrame : 
    filter_data = eval(filter_data)
    all_features = [feature_parameters["feature"]]
    all_features.sort()   
    df = pd.DataFrame(filter_data, columns=['date'] + all_features)
    df["date"] = pd.to_datetime(df['date']).dt.date
    df = df.sort_values(by='date') 
    return df 
    
def forecast_using_prophet_utils(filter_data: list[tuple], feature_parameters: dict) -> str : 
    try :
        print('inside forecasting --> ', feature_parameters)
        data = preprocess(filter_data, feature_parameters)

        print(data.tail())

        data.rename(columns = {'date' : 'ds', feature_parameters['feature'] : 'y'}, inplace = True)
        model = Prophet()
        
        model.fit(data[['ds', 'y']])
        future = model.make_future_dataframe(periods = feature_parameters["days_to_forecast"])
        forecast = model.predict(future)
        
        forecast_df = pd.DataFrame(forecast[['ds', 'yhat']])
        forecast_df.columns = ['date', feature_parameters['feature']]

        print(forecast_df.tail())

        print("before modify --> ", forecast_df)
        if feature_parameters["forecasting_date_type"] == "month" or feature_parameters["forecasting_date_type"] == "months" : 
            forecast_df = forecast_df.groupby(pd.Grouper(key="date", freq="M")).sum()
        if feature_parameters["forecasting_date_type"] == "year" or feature_parameters["forecasting_date_type"] == "years": 
            forecast_df = forecast_df.groupby(pd.Grouper(key="date", freq="Y")).sum()
        print("after modify --> ", forecast_df)
        forecast_df.reset_index(inplace=True)

        table_creation = forecast_df 
        chart_creation = forecast_df.to_dict()
        chart_config = {
            "type": "line",  
            "columns": [{"x-axis":["date"], "y-axis":[feature_parameters['feature']]}],  
            "options": {} 
        }
        return table_creation, chart_creation, chart_config 
    except : 
        return "couldn't process with Prophet", None, None
