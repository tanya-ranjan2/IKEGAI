from typing import Optional
from fastapi import APIRouter, UploadFile
from schemas.evaluation_schema import LLM_Intialization
from controllers.evaluate_llm import get_LLM_costing, get_scores, initialize_model
from utils.llmops import llmbuilder
from _temp.config import STORAGE_DRIVE
import os
import pandas as pd
from utils import APIconnector

router = APIRouter(prefix="/evaluate", tags=["evaluation_metrics"])
eval_metric = {}

############## not updated in User interface yet and need context to retrieve based on tool - to be discussed
@router.post("/uploadEvalMetric")
def create_upload_file(file: UploadFile, llm_evaluate: LLM_Intialization):
    df = pd.read_csv(file.file)
    for i, row in df.iterrows():
        input_prompt = row['input_prompt']
        actual_output = row['actual_output']
        expected_output = row['expected_output']
        custom_model = llmbuilder(llm_evaluate.model_name)
        #custom_model = initialize_model(llm_evaluate.model_name)
        status, scores, definitions, message_for_scores = get_scores(custom_model, input_prompt, 
                                actual_output, expected_output, 
                                llm_evaluate.retrieval_context, llm_evaluate.context)

        evaluation_scores = {
            "message": {"message_for_scores": message_for_scores},
            "status": status,
            "prompt" : input_prompt,
            "actual_output" : actual_output,
            "expected_output" : expected_output,
            "data": {"scores": scores, "definitions" : definitions, "model_name" : llm_evaluate.model_name},
        }
        
        res = APIconnector.send_eval(llm_evaluate.usecase_id, llm_evaluate.user_id,
                                     input_prompt, actual_output, expected_output,
                               None, None,
                               llm_evaluate.model_name, evaluation_scores)
        print("RESPONSE",res) 
    file.file.close()
    return res
    
    
    
'''
@router.post("/evaluate_LLM/")
async def evaluate_LLM(llm_evaluate: LLM_Intialization):
    
    custom_model = llmbuilder(llm_evaluate.model_name)
    #custom_model = initialize_model(llm_evaluate.model_name)
    status, scores, definitions, message_for_scores = get_scores(custom_model, llm_evaluate.input_prompt, 
                            llm_evaluate.actual_output, llm_evaluate.expected_output, 
                            llm_evaluate.retrieval_context, llm_evaluate.context)
    
    cost, status, message_for_cost = get_LLM_costing(llm_evaluate.prompt_token,
                                llm_evaluate.completion_token, llm_evaluate.model_name,)
    
    return {
        "message": {"message_for_scores": message_for_scores, "message_for_cost": message_for_cost},
        "status": status,
        "data": {"scores": scores, "cost": cost, 
                    "definitions" : definitions, "model_name" : llm_evaluate.model_name},
    }
'''