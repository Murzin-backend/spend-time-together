from fastapi import FastAPI
from app.api.routes import api_router
from app.di.containers import DIContainer

app = FastAPI(
    title="Spend Time Together",
    description="Backend API for Spend Time Together application",
    version="0.1.0"
)

container = DIContainer()
container.wire(packages=["app.api"])

app.container = container
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
