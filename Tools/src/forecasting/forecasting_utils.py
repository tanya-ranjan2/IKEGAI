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
    df["date"] = pd.to_datetime(df['date'])
    df = df.sort_values(by='date')
    # print
    return df 
    
def forecast_using_prophet_utils(filter_data: list[tuple], feature_parameters: dict, mongo_store: bool = False) -> str : 
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

        #fig = px.line(
        #        forecast_df, x ='date', y = feature_parameters['feature'], 
        #        title = 'Time Series with Rangeslider', markers = True
        #    )

        #fig.update_xaxes(rangeslider_visible=True)
        #fig.write_html("plots/new_file.html")


        # if mongo_store : 
        #     client = pymongo.MongoClient("mongodb+srv://ikegai:ikegai%40123456@cluster0.l2apier.mongodb.net")
        #     db = client["ikegai"]
        #     forecasting_plot_collection = db["plots"]

        #     with open('path/new_file.html', 'r') as file :
        #         html_content = file.read()

        #     html_doc = {
        #         "html_content" : html_content
        #     }

        #     result = forecasting_plot_collection.insert_one(html_doc)

        return forecast_df
        # return "success"
    except : 
        return "couldn't process with Prophet"