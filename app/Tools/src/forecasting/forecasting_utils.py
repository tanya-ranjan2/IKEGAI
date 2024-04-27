import pymongo 
import pandas as pd
import numpy as np
from prophet import Prophet
import plotly.express as px 
import plotly.graph_objects as go
from memory_profiler import profile
from sklearn.metrics import mean_absolute_error, mean_squared_error, mean_squared_log_error

class AccuracyMetrics : 
    def __init__(self, y_true, y_pred) : 
        self.y_true = y_true 
        self.y_pred = y_pred 
    
    def MAE(self) : 
        return mean_absolute_error(self.y_true, self.y_pred)
    
    def MSE(self) : 
        return mean_squared_error(self.y_true, self.y_pred)
    
    def RMSE(self) : 
        return np.sqrt(mean_squared_error(self.y_true, self.y_pred))
    
    # ! might give inf if any y_true value is 0
    def MAPE(self) :    
        return np.mean(np.abs((self.y_true - self.y_pred)/self.y_true)) * 100
    
    def forecast_bias(self) : 
        return np.mean(self.y_true - self.y_pred)
    
    # ! will give error for negative values
    def MSLE(self) : 
        return mean_squared_log_error(y_true=self.y_true, y_pred=self.y_pred)
    
# @profile
def preprocess(filter_data: list[list], feature_parameters: dict) -> pd.DataFrame :  
    filter_data = eval(filter_data)
    all_features = [feature_parameters["feature"]]
    all_features.sort()   
    df = pd.DataFrame(filter_data, columns=['date'] + all_features)
    df["date"] = pd.to_datetime(df['date']).dt.date
    df = df.sort_values(by='date') 
    return df 
    
# @profile
def forecast_using_prophet_utils(filter_data: list[tuple], feature_parameters: dict) -> str : 
    try : 
        data = preprocess(filter_data, feature_parameters)
        data.rename(columns = {'date' : 'ds', feature_parameters['feature'] : 'y'}, inplace = True)
        
        model = Prophet()
        model.fit(data[['ds', 'y']])
        future = model.make_future_dataframe(periods = feature_parameters["days_to_forecast"])
        forecast = model.predict(future)
        
        forecast_df = pd.DataFrame(forecast[['ds', 'yhat']])
        forecast_df.columns = ['date', feature_parameters['feature']]

        print("actual data tail --> ", data.tail())

        #? accuracy checking  
        # accuracy is calculated based on minimum between the available raw data, 
        # days to forecast and number of days available in forecasted data except the future dates   
        min_range = min(
            feature_parameters["days_to_forecast"], 
            len(forecast_df)-feature_parameters["days_to_forecast"], 
            len(data), 100
        ) 
 
        accuracy_obj = AccuracyMetrics(
            y_true = np.array(data['y'][-min_range:]), 
            y_pred = np.array(forecast_df[feature_parameters['feature']][:min_range])
        )

        accuracy_metrics = {
            "MSE" : accuracy_obj.MSE(), 
            "MAE" : accuracy_obj.MAE(), 
            "RMSE" : accuracy_obj.RMSE(), 
            "MAPE" : accuracy_obj.MAPE(), 
            "forecast_bias" : accuracy_obj.forecast_bias(),
            "MSLE" : accuracy_obj.MSLE()
        }

        to_chop = feature_parameters["days_to_forecast"]
        if feature_parameters["forecasting_date_type"] == "month" or feature_parameters["forecasting_date_type"] == "months" : 
            forecast_df = forecast_df.groupby(pd.Grouper(key="date", freq="M")).sum()
            to_chop = feature_parameters["forecasting_date"]
        if feature_parameters["forecasting_date_type"] == "year" or feature_parameters["forecasting_date_type"] == "years": 
            forecast_df = forecast_df.groupby(pd.Grouper(key="date", freq="Y")).sum()
            to_chop = feature_parameters["forecasting_date"]
        
        print("predicted data after modification --> ", forecast_df.tail())
        forecast_df.reset_index(inplace=True)

        table_creation = forecast_df 
        chart_creation = forecast_df.to_dict()
        chart_config = {
            "type": "line",  
            "columns": [{"x-axis":["date"], "y-axis":[feature_parameters['feature']]}],  
            "options": {} 
        }

        return table_creation, chart_creation, chart_config, accuracy_metrics, to_chop
    except : 
        return "couldn't process with Prophet", None, {}, {}, -1