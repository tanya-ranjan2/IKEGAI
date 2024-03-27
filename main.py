from fastapi import FastAPI
from AgentExecutor import agent_router
app=FastAPI(debug=True)
app.include_router(agent_router.router)

@app.get("/")
def index():
    return {"status":200}