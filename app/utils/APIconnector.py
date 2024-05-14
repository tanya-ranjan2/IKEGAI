import requests
from _temp import config
def get_usecase_details(uid):
    res=requests.get(config.API_GET_DETAILS_FULL.format(uid=uid))
    if res.status_code==200:
        return res.json()['data']
    elif res.status_code==500:
        res=requests.get(config.API_GET_DETAILS_PARTIAL.format(uid=uid))
        return res.json()['data']
    else:
        return {"status":res.status_code}
    
    
def send_eval(uid,user_id,query,responce,ground_truth,prompt_token,completion_token,model_name):
    data={
        "usecase_id": uid,
        "user_id": user_id,
        "prompt":query,
        "llm_response": responce,
        "ground_truth": ground_truth,
        "prompt_token": str(prompt_token),
        "completion_token": str(completion_token),
        "model_name": model_name
    }
    print(data)
    res=requests.post(f"https://ikegai.southindia.cloudapp.azure.com/solution-manager/evaluate/evaluate_LLM/",json=data)
    return {"status":res.status_code}
    

if __name__=="__main__":
    print(get_usecase_details('TEST123'))