from fastapi import FastAPI
from AgentExecutor import agent_router
from fastapi.middleware.cors import CORSMiddleware
'''
__import__('pysqlite3')
import sys
sys.modules['sqlite3']= sys.modules.pop('pysqlite3')
'''
import chromadb

app=FastAPI(
    debug=True,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(agent_router.router)

@app.get("/")
def index():
    return {"status":200}