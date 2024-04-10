from fastapi import FastAPI
from AgentExecutor import agent_router
'''
__import__('pysqlite3')
import sys
sys.modules['sqlite3']= sys.modules.pop('pysqlite3')
'''
app=FastAPI(
    debug=True,
)
app.include_router(agent_router.router)

@app.get("/")
def index():
    return {"status":200}