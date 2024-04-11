import os
from datetime import datetime

import uvicorn
from fastapi import FastAPI

# from __version__ import __version__ as version
from AgentExectutor import agent_router
from usecase_manager.api import usecases

app = FastAPI(
    title="IKE.GAI Services",
    # version=version,
    description=f"""---
*Service Running From: {datetime.now().strftime("%d %h %Y, %H:%M:%S")}*
    """,
     redoc_url=None,
    contact={"name": "KPMG GenAi Development Team"},
)




app.include_router(agent_router.router)
app.include_router(usecases.router) 



@app.get("/")
def index():
    return {"status":200}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


