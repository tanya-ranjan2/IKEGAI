import requests

def get_usecase_details(uid):
    res=requests.get(f"https://ikegai.southindia.cloudapp.azure.com/solution-manager/v1/useCase/usecase-by-id?id={uid}")
    print(res.json())
    if res.status_code==200:
        return res.json()['data']
    elif res.status_code==500:
        res=requests.get(f"https://ikegai.southindia.cloudapp.azure.com/solution-manager/v1/useCase/?id={uid}")
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
        "prompt_token": prompt_token,
        "completion_token": completion_token,
        "model_name": model_name
    }
    res=requests.post(f"https://ikegai.southindia.cloudapp.azure.com/solution-manager/evaluate/evaluate_LLM/",json=data)
    return {"status":res.status_code}
    

if __name__=="__main__":
    print(get_usecase_details('TEST123'))