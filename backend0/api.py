#!/bin/env python3

from fastapi import FastAPI, APIRouter

app = FastAPI()
routers = APIRouter()

app.servers

app.include_router(routers)
