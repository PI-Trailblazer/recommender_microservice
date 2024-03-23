from requests import Session
from app.api import deps
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import jwt
from app import crud

router = APIRouter()
