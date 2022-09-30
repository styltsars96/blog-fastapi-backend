"""
Blog backend application 'main' module.
"""
import uvicorn
from fastapi import FastAPI
from fastapi_sqlalchemy import DBSessionMiddleware

from app.routers import posts, users
from app.database import DATABASE_URL

app = FastAPI()

# DB session manager + avoid csrftokenError
app.add_middleware(DBSessionMiddleware, db_url=DATABASE_URL)

# Use below events for handling anything not created by middleware
# @app.on_event("startup")
# async def startup():
#     # Startup here ...


# @app.on_event("shutdown")
# async def shutdown():
#     # Cleanup here ...

app.include_router(users.router)
app.include_router(posts.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
