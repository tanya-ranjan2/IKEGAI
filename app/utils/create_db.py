import pandas as pd 
import sqlite3 

class CreateDB : 
    """ 
    A class to convert a CSV file into a SQLite database. 
    """
    def __init__(
            self, csv_file: str, table_name: str, categorical_cols: list[str] = [], 
            numerical_cols: list[str] = []) -> None : 
        """
        Initialize the CreateDB with the CSV file, and table name 

        Parameters: 
        - csv_file (str): Path to the CSV file. 
        - table_name (str): Name of the table to be created in the database. 
        """
        self.csv_file = csv_file 
        self.db_name = '../database/sample_data.sqlite3' 
        self.table_name = table_name 
        self.df = pd.read_csv(self.csv_file) 
        self.categorical_cols = categorical_cols
        self.numerical_cols = numerical_cols

    def preprocess(self, uniform: bool = False) :  
        """
        strip the values and turn it into uniform case for categorical features
        """ 
        # categorical preprocessing 
        for col in self.categorical_cols :  
            self.df[col] = self.df[col].str.strip()
            if uniform :
                self.df[col] = self.df[col].str.lower() 
 
        print("preprocessing done...")
        self.df.to_csv("preprocessed.csv", index=False, encoding="utf-8")
        return self.df 

    def csv_to_sqlite(self) : 
        """
        Converts the CSV file into a SQLite database and stores it locally.
        """
        self.df = self.preprocess(uniform=True)
        conn = sqlite3.connect(self.db_name)
        self.df.to_sql(self.table_name, conn, if_exists= 'replace', index= False) 

        print('table created...')
        conn.close()


obj = CreateDB(
    csv_file = 'new_file.csv', table_name = 'published_purchase_order_v2', 
    categorical_cols=[
        "order_line_number", "material_number", "vendor_name", "unit_of_measure", 
        "purchasing_document_category", "category_l1", "category_l2", "category_l3"
    ]
) 
obj.csv_to_sqlite()