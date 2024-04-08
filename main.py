from fastapi import FastAPI
from AgentExecutor import agent_router
app=FastAPI(
    debug=True,
    root_path="/agent",
    docs_url='/docs'
    )
app.include_router(agent_router.router)

@app.get("/")
def index():
    return {"status":200}