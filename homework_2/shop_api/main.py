from typing import List
from uuid import uuid4
from http import HTTPStatus

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, conint, confloat

app = FastAPI()

# Временное хранилище для корзин и товаров
carts = {}
items = {}


class Item(BaseModel):
    id: str
    name: str
    price: confloat(gt=0)
    deleted: bool = False


class CartItem(BaseModel):
    id: str
    name: str
    quantity: conint(gt=0)
    available: bool


class Cart(BaseModel):
    id: str
    items: List[CartItem] = []
    price: float = 0.0


@app.post('/cart', status_code=HTTPStatus.CREATED)
def create_cart():
    cart_id = str(uuid4())
    carts[cart_id] = Cart(id=cart_id)
    response = JSONResponse(
        content={'id': cart_id}, status_code=HTTPStatus.CREATED
    )
    response.headers['location'] = f'/cart/{cart_id}'
    return response


@app.get('/cart/{cart_id}')
def get_cart_by_id(cart_id):
    cart_id = str(cart_id)
    if cart_id not in carts:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Cart not found')
    return carts[cart_id]