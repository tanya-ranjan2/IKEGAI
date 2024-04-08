import requests

def get_usecase_details(uid):
    res=requests.get(f"https://ikegai.southindia.cloudapp.azure.com/solution-manager/v1/useCase/?id={uid}")
    if res.status_code==200:
        return res.json()['data']
    else:
        return {"status":res.status_code}
    
    
if __name__=="__main__":
    print(get_usecase_details('US123'))