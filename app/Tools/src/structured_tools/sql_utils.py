import json
import os
import re
import sqlite3
import uuid

import pandas as pd
from _temp.config import OpenAIConfig
from pydantic import BaseModel
from sqlmodel import Session, select, create_engine, text
from pathlib import Path
from dataclasses import asdict
from openai import AzureOpenAI

client = AzureOpenAI(**asdict(OpenAIConfig()))

class UsecaseDetailsT(BaseModel):
    name:str 
    db_uri:str
    filepath:str
    db_type:str

class PromptMaker:
    def __init__(self, prompt_text: str, name=None,db_uri=None,filepath=None,db_type=None) -> None:
        self.prompt = prompt_text
        self.engine = "LH-GPT"
        self.form_answer_flag = False
        self.usecase_details = UsecaseDetailsT(name=name, db_uri=db_uri,filepath=filepath,db_type=db_type)

        self.get_usecase_details()

    def get_usecase_details(self): 
        self.usecase_name = self.usecase_details.name

    def get_response_from_openai(self, messages: list):
        model_response = client.chat.completions.create(
            # engine=self.engine,
            # messages=messages,
            # temperature=0,
            # max_tokens=4000,
            model="LH-GPT",
            messages=messages
        )
      
        print(model_response.choices[0].message.content)
        print(100*"+")

        return model_response.choices[0].message

    def get_sql_code_from_model_response(self, resp: str):
        # print(resp)

        # if "```" in resp:
        #     pattern = r"```(.*?)```"
        #     # extract the code block using regex
        #     code_block = re.findall(pattern, resp, re.DOTALL)[0].strip()
        if "SELECT" in resp:
            pattern = r"SELECT(.*?);"
            code_block = (
                "SELECT " + re.findall(pattern, resp, re.DOTALL)[0].strip() + ";"
            )
        else:
            return resp

        # print(resp, code_block)
        return code_block
    
    def get_charts_from_model_response(self, resp: str):
        # Extract the JSON from the string 
        # 
        try:
            if '```' in resp  :  
                json_string = resp.split('```')[0] 
            else :
                # Extract the JSON string from the given string  
                # Use regular expressions to extract the JSON string  
                json_string = re.search(r'\{.*\}', resp, re.DOTALL).group() 
                # json_string = resp
            json_data = json.loads(json_string)  
            print('j0-json string',json_string)
            print('j0- json_data',json_data)
            # Print the JSON data  
            # Get the value of the type key from the chart object  
            chart_config = json_data.get('chart',{})
            print('j0- chart_config',chart_config)

            # Print the chart type value  
            return chart_config
        except Exception as e:
            try:
                # json_string = resp.split('```')[1] 
                # Extract the JSON string between the two sets of backticks  
                pattern = re.compile('```(.*?)```', re.DOTALL)
                match = pattern.search(resp)
                json_string = match.group(1)

                # json_string = resp
                print("J1",json_string)
                json_data = json.loads(json_string)  

                # Print the JSON data  
                # Get the value of the type key from the chart object  
                chart_config = json_data.get('chart',{})

                # Print the chart type value  
                return chart_config
            except Exception as e:
                import traceback
                print(e.args[0])
                traceback.print_exc()
                return {}


    def execute_query(self, query, use_pandas: bool = False):
        print("Executing Query....")
        try:

            engine = create_engine(self.usecase_details.db_uri)
            if use_pandas:
                resp = pd.read_sql_query(query, engine)

            else:
                conn = Session(engine)
                out = conn.exec(text(query))
                resp = out.all()    
                conn.close()

            self.form_answer_flag = True
            return resp
        except Exception as e:
            print("SQL Error", e)
            pass
        return query

    def get_data_definition(self):

        return Path(self.usecase_details.filepath).read_text()
       

    def form_answer(self, data: str):  # sourcery skip: remove-unnecessary-cast
        print("Forming Answer....")
        context = """
        Your role is to answer that sounds conversational for the given below data which is executed by sqlite query below is the given prompt followed by its output.
        please set conversational for it.
        """
        prompt = self.prompt + str(data)
        messages = [
            {"role": "system", "content": context},
            {"role": "user", "content": prompt},
        ]
        model_resp = self.get_response_from_openai(messages=messages)
        return model_resp.content

    def add_context_to_data_definition(
        self, data_definition: str, extra_instructions: str = "Please respond in proper mentioned format only for all consecutive users prompt", db_type = "SQLite"
    ):
        base_instruct = """
        Design an AI system that can generate SQL queries and recommend relevant charts based on natural language queries. The system should use the provided tables and columns and ensure that all generated queries are applicable for a #db_type# database.  
        
        If the AI system is unable to generate a valid #db_type# query for a given input, it should provide a clear and concise explanation for why the query was invalid in a non-technical language.  
        
        After generating the appropriate SQL query, the system should suggest charts and chart types based on the query results, along with the required columns to be used. Users should be prompted with the following question: 
        "What type of chart would you like to see? Here are some options: bar chart, line chart, scatter plot, pie chart. Please let me know your preference."  
        
        JSON Schema:  
        {  
        "query": "",  
        "chart": {  
            "type": "",  
            "columns": [],  
            "options": {}  
        },  
        "error": ""  
        }  
        
        Please provide the SQL query and chart recommendation in the format specified above. If the query is invalid, please include an explanation for the error in the "error" field.  
        
        Example Input:  
        "What were the total sales for each product category in the last quarter?"  
        
        Expected Output:  
        {  
        "query": "SELECT category, SUM(sales) AS total_sales FROM sales WHERE date >= '2022-07-01' AND date <= '2022-09-30' GROUP BY category;",  
        "chart": {  
            "type": "bar",  
            "columns": [{"x-axis":["category"], "y-axis":["total_sales"]}],  
            "options": {}  
        },  
        "error": ""  
        }  
        
        Example Input:  
        "Which employees had the highest sales in the last month?"  
        
        Expected Output:  
        {  
        "query": "SELECT employee_id, SUM(sales) AS total_sales FROM sales WHERE date >= '2022-09-01' AND date <= '2022-09-30' GROUP BY employee_id ORDER BY total_sales DESC LIMIT 10;",  
        "chart": {  
            "type": "line",  
            "columns":  [{"x-axis":["employee_id"], "y-axis":["total_sales"]}],  
            "options": {}  
        },  
        "error": ""  
        }  

        
        Find the Sqlite table schema details below this can help you understand the meaning of tables and their relations:
        
        """.replace("#db_type#", db_type)

        return base_instruct + "\n" + data_definition + "\n" + extra_instructions

    def get_schema_representation(self):
        """Get the database schema in a JSON-like format"""

        # Query to get all table names
        query = "SELECT name FROM sqlite_master WHERE type='table';"
        tables = self.execute_query(query=query)

        db_schema = {}

        for table in tables:
            table_name = table[0]

            # Query to get column details for each table
            query = f"PRAGMA table_info({table_name});"
            columns = self.execute_query(query=query)

            column_details = {column[1]: column[2] for column in columns}
            db_schema[table_name] = column_details

        # print(f"{db_schema=}")
        self.form_answer_flag = False
        return db_schema

    def get_prompt_answer(self, id: str = None):
        psm = PromptSessionManager(id=id)

        if psm.max_prompt_limit_reached():
            raise Exception("Limit Reached")

        try:
            sql_query = None
            tabular_answer = None
            raw_table = []
            answer = None
            chart_config = {}
            # if _message := psm.get_updated_current_session_prompt(
            #     prompt=self.prompt
            # ):
            #     messages = _message
            # else:
            data_def = self.get_data_definition()
            extra_instruction = "Please respond in proper mentioned json format only"
            context = self.add_context_to_data_definition(
                data_definition=data_def,
                extra_instructions=extra_instruction,
                db_type=self.usecase_details.db_type,
            )
            messages = [
                {"role": "system", "content": context},
                {"role": "user", "content": self.prompt},
            ]

            model_resp = self.get_response_from_openai(messages=messages)
            print(model_resp)
            # psm.save_current_session_prompt_and_resp(messages=messages, resp=model_resp)   #removed for ikegai

            sql_query = self.get_sql_code_from_model_response(model_resp.content)
            print(sql_query)
            chart_config = self.get_charts_from_model_response(model_resp.content)
            tabular_answer = self.execute_query(sql_query, use_pandas=True)
            print(tabular_answer)
            tabular_answer=tabular_answer.dropna()
            if self.form_answer_flag & len(tabular_answer) > 16000:
                answer = tabular_answer
            else:
                answer = self.form_answer(tabular_answer) if self.form_answer_flag else None
        except Exception as e:
            print(e)
            tabular_answer = f"Failed:{e}"
        finally:

            if isinstance(tabular_answer,pd.DataFrame):
                print("converting...")
                raw_table = tabular_answer.to_dict(orient="tight")
                tabular_answer = tabular_answer.to_dict()
            return {
                "chart_config": chart_config,
                "tabular_answer": tabular_answer,
                "raw_table":raw_table,
                "answer": answer,
                "session_id": psm.get_session_id(),
            }
        


class PromptSessionManager:
    def __init__(self, id: str = None) -> None:
        self.prompt_limit = 15
        self.id = uuid.uuid4() if id is None else id

        # print(f"{self.id=}")

        self.prompt_store_path = f"prompt_store/{self.id}.json"
        self.content: list = None
        self.read_saved_prompt_file()

    def get_session_id(self):
        return self.id

    def max_prompt_limit_reached(self):
        return len(self.content) > self.prompt_limit - 1 if self.content else False

    def read_saved_prompt_file(self):
       
        try:
            _content = Path(self.prompt_store_path).read_text()
            self.content = json.loads(_content)
            return True
        except Exception:
            return False

    def save_current_session_prompt_and_resp(self, messages: list, resp: dict):
      
        messages.append(resp)
        if not os.path.exists("prompt_store"):
            os.makedirs("prompt_store")
        with open(self.prompt_store_path, "w+") as f:
            f.write(json.dumps(messages))

    def get_updated_current_session_prompt(self, prompt: str):
        
        if not self.content:
            return False
        _prompt = (
            "Generate the Updated json including this requirement with relevant charts recomendation and output json only\n"
            + prompt
        )
        # _prompt = prompt
        self.content.append({"role": "user", "content": _prompt})
        return self.content





# if __name__=="__main__":
#     PromptMaker(prompt_text="what are my top spends?",
#             name="my-usecase",
#             db_uri="sqlite:///usecases/Spend-Analytics-Platform/db/Spend-Analytics-Platform.db",
#             filepath="usecases/Spend-Analytics-Platform/defination/spend_analytics.txt",
#             db_type="sqlite").get_prompt_answer()