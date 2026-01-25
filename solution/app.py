import uvicorn
from fastapi import FastAPI
from solution.repositories import init_db, create_admin_user
from solution.api import users_router, fraudrules_router

app = FastAPI()
app.include_router(users_router)
app.include_router(fraudrules_router)

@app.get('/api/v1/ping')
def ping():
    return {"status": "ok"}


@app.on_event("startup")
async def startup_event():
    await init_db()
    await create_admin_user()

# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)


