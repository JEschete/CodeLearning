from fastapi import FastAPI
import Code.FastAPI.Lecture6_Project3.models as models
from Code.FastAPI.Lecture6_Project3.database import engine


app = FastAPI()
models.Base.metadata.create_all(bind=engine)

