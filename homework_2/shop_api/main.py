from typing import List, Optional, Dict

from fastapi import FastAPI, HTTPException, Query, Response, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, confloat, conint


app = FastAPI()
