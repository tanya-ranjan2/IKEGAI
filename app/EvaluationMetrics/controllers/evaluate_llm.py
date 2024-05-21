from typing import Optional
from langchain_openai import AzureChatOpenAI
from langchain.evaluation import load_evaluator
from datasets import Dataset
import json
from ragas import evaluate
from ragas.metrics import faithfulness, context_recall, context_precision
from ..metric_info import MetricsInfo

class ModelEvaluationMetrics:
    def __init__(self, custom_model, input_prompt, actual_output, 
                 expected_output= None, retrieval_context= None, context = None):
        self.input= input_prompt
        self.actual_output=actual_output
        self.expected_output = expected_output
        self.retrieval_context = retrieval_context
        self.context = context
        self.custom_model = custom_model
        
    def get_relevancy_score(self, relevancy_criteria):
        evaluator = load_evaluator("score_string", criteria=relevancy_criteria, llm=self.custom_model)
        eval_result = evaluator.evaluate_strings(prediction=self.actual_output, input=self.input)
        return eval_result
    
    def get_toxicity_score(self, toxicity_criteria):
        evaluator = load_evaluator("score_string", criteria=toxicity_criteria, llm=self.custom_model)
        eval_result = evaluator.evaluate_strings(prediction=self.actual_output, input=self.input)
        return eval_result
    
    def get_bias_score(self, bias_criteria):
        evaluator = load_evaluator("score_string", criteria=bias_criteria, llm=self.custom_model)
        eval_result = evaluator.evaluate_strings(prediction=self.actual_output, input=self.input)
        return eval_result
    
    def get_coherence_score(self, coherence_criteria):
        evaluator = load_evaluator("score_string", criteria=coherence_criteria, llm=self.custom_model)
        eval_result = evaluator.evaluate_strings(prediction=self.actual_output, input=self.input)
        return eval_result
    
    def get_fluency_score(self, fluency_criteria):
        evaluator = load_evaluator("score_string", criteria=fluency_criteria, llm=self.custom_model)
        eval_result = evaluator.evaluate_strings(prediction=self.actual_output, input=self.input)
        return eval_result
    
    def get_contextualrelevancy_score(self, contextualrelevancy_criteria):
        evaluator = load_evaluator("labeled_score_string", criteria=contextualrelevancy_criteria, llm=self.custom_model)
        eval_result = evaluator.evaluate_strings(prediction=self.actual_output, 
                                                 reference=self.retrieval_context, input=self.input)
        return eval_result
    
    def get_correctness_score(self, correctness_criteria):
        evaluator = load_evaluator("labeled_score_string", criteria=correctness_criteria, llm=self.custom_model)
        eval_result = evaluator.evaluate_strings(prediction=self.actual_output, 
                                                 reference=self.expected_output, input=self.input)
        return eval_result
    
    def get_similarity_score(self, similarity_criteria):
        evaluator = load_evaluator("labeled_score_string", criteria=similarity_criteria, llm=self.custom_model)
        eval_result = evaluator.evaluate_strings(prediction=self.actual_output, 
                                                 reference=self.expected_output, input=self.input)
        return eval_result
    
    def get_hallucination_score(self, hallucination_criteria):
        evaluator = load_evaluator("labeled_score_string", criteria=hallucination_criteria, llm=self.custom_model)
        eval_result = evaluator.evaluate_strings(prediction=self.actual_output, 
                                                 reference=self.context, input=self.input)
        return eval_result
    
    def get_groundness_score(self, groundness_criteria):
        evaluator = load_evaluator("labeled_score_string", criteria=groundness_criteria, llm=self.custom_model)
        eval_result = evaluator.evaluate_strings(prediction=self.actual_output, 
                                                 reference=self.context, input=self.input)
        return eval_result
    
    def get_faithfulness_score(self):
        response_dataset = Dataset.from_dict({
            "question" : [self.input],
            "answer" : [self.actual_output],
            "contexts" : self.context,
            "ground_truth" : [self.expected_output]
        })  
        metrics = [faithfulness]
        result = evaluate(response_dataset, metrics,llm=self.custom_model)
        eval_result = {'score' : result['faithfulness']}
        return eval_result
    
    def get_context_recall_score(self):  
        response_dataset = Dataset.from_dict({
            "question" : [self.input],
            "answer" : [self.actual_output],
            "contexts" : self.context,
            "ground_truth" : [self.expected_output]
        })
        
        metrics = [context_recall]
        result = evaluate(response_dataset, metrics,llm=self.custom_model)
        eval_result = {'score' : result['context_recall']}
        return eval_result
    
    def get_context_precision_score(self):
        response_dataset = Dataset.from_dict({
            "question" : [self.input],
            "answer" : [self.actual_output],
            "contexts" : self.context,
            "ground_truth" : [self.expected_output]
        })
          
        metrics = [context_precision]
        result = evaluate(response_dataset, metrics,llm=self.custom_model)
        eval_result = {}
        eval_result['score'] = result['context_precision']
        return eval_result    
    
def get_scores(custom_model, input_prompt, actual_output, expected_output, 
                           retrieval_context, context):
    scores = {}
    definitions = {}
    try:
        print('Entered to get evaluation scores')
        metrics = MetricsInfo().get_metric_info()
        if custom_model != None:
            model_evaluation = ModelEvaluationMetrics(custom_model, input_prompt, actual_output, expected_output, 
                            retrieval_context, context)

            if (input_prompt is not None) and (actual_output is not None):
                # 5 metrics to be returned
                metric_type = 'type1' 
                
            if (input_prompt is not None) and (actual_output is not None) and (context is not None):
                # 7 metrics to be returned
                metric_type =  ['type1', 'type2']
                
            if (input_prompt is not None) and (actual_output is not None) and (expected_output is not None):
                # 7 metrics to be returned
                metric_type = ['type1', 'type3']
                
            if (input_prompt is not None) and (actual_output is not None) and (retrieval_context is not None) and (context is not None):
                # 9 metrics to be returned
                metric_type = ['type1', 'type2', 'type4']
            
            if (input_prompt is not None) and (actual_output is not None) and (expected_output is not None) and (retrieval_context is not None) and (context is not None):
                # 13 metrics to be returned
                metric_type = ['type1', 'type2', 'type3', 'type4', 'type5']
                
            selected_metrics = []
            for key, val in metrics.items():
                if val['metric_type'] in metric_type:
                    selected_metrics.append(key)
            
            print('Total metrics to be evaluated : ', len(selected_metrics),', which are :', selected_metrics) 
            
            for metric in selected_metrics:
                if "criteria" in metrics[metric]:
                    criteria = metrics[metric]['criteria']
                    result = getattr(model_evaluation, "get_%s_score" % metric)(criteria)
                else:
                    result = getattr(model_evaluation, "get_%s_score" % metric)()
                scores[metric] = result
                
                definitions[metric] = metrics[metric]['definition']
                
            status = True
            message = 'Successfully evaluated model evaluation metrics!'
        else:
            status= False
            message = 'Please provide correct model.Something went wrong with model'
        
    except Exception as e:
        status = False
        message = "Something went wrong! Exception : "+ str(e)
    
    return status, scores, definitions, message

def initialize_model(model_name):
    model_details = {'azureopenai' : {
                            "api_key" : "312ff50d6d954023b8748232617327b6",
                            "azure_endpoint" : "https://openai-lh.openai.azure.com/",
                            "azure_deployment" : "test",
                            "api_version" :"2024-02-15-preview"
                }}

    ## Custom model
    custom_model = AzureChatOpenAI(deployment_name=model_details[model_name]['azure_deployment'], 
                                    api_key=model_details[model_name]['api_key'],
                                    azure_endpoint=model_details[model_name]['azure_endpoint'], 
                                    api_version=model_details[model_name]['api_version'])
    return custom_model

class LLM_Costing:
    def __init__(self):
        self.openai_cost = {
            "azureopenai": {
                "input_price": 0.0010 / 1000,
                "output_price": 0.0020 / 1000,
            },
            "gpt-4-1106-preview": {
                "input_price": 0.01 / 1000,
                "output_price": 0.03 / 1000,
            },
            "gpt-4-0613": {"input_price": 0.03 / 1000, "output_price": 0.06 / 1000},
            "gpt-4-32k-0613": {"input_price": 0.06 / 1000, "output_price": 0.12 / 1000},
        }

    def get_costing(self, prompt_token, completion_token, model_name):
        input_price = self.openai_cost[model_name]["input_price"]
        output_price = self.openai_cost[model_name]["output_price"]
        total_input_price = round((float(prompt_token) * input_price), 4)
        total_output_price = round((float(completion_token) * output_price), 4)
        total_price = total_input_price + total_output_price
        return total_input_price, total_output_price, total_price


def get_LLM_costing(prompt_token, completion_token, model_name):
    cost = {}
    status = False
    try:
        llm_cost = LLM_Costing()
        total_input_price, total_output_price, total_price = llm_cost.get_costing(
            prompt_token, completion_token, model_name
        )
        cost = {
            "total_input_price": total_input_price,
            "total_output_price": total_output_price,
            "total_price": total_price,
        }
        status = True
        message = "Successfully found out the LLM Costing."

    except Exception as e:
        message = "Something went wrong! Exception : " + str(e)

    return cost, status, message