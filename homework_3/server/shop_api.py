
from typing import List, Optional, Dict

from fastapi import FastAPI, HTTPException, Query, Response, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, confloat, conint
from prometheus_client import Counter, Gauge, Histogram, Summary, generate_latest, REGISTRY


app = FastAPI()

# Метрики
request_counter = Counter('requests_total', 'Total number of requests')
error_counter = Counter('errors_total', 'Total number of errors')
request_duration_histogram = Histogram('request_duration_seconds', 'Histogram of request duration in seconds')


class UpdateItem(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None

    model_config = {
        'extra': 'forbid'
    }


class NewItem(BaseModel):
    name: str
    price: confloat(gt=0)  # type: ignore


class Item(BaseModel):
    id: int
    name: str
    price: confloat(gt=0)  # type: ignore
    deleted: bool = False


class CartItem(BaseModel):
    id: int
    name: str
    quantity: conint(gt=0)  # type: ignore
    available: bool


class Cart(BaseModel):
    id: int
    items: List[CartItem] = []
    price: float = 0.0


carts: Dict[int, Cart] = {}
items: Dict[int, Item] = {}

cart_id_counter = 0
item_id_counter = 0


@app.get('/')
def read_root():
    '''
    Возвращает приветственное сообщение
    '''
    request_counter.inc()
    return JSONResponse(
        content={'message': 'Привет, World !'}
    )


@app.post('/item', status_code=status.HTTP_201_CREATED)
def create_item(item: NewItem, response: Response):
    '''
    Создает новый товар и возвращает его
    '''
    global item_id_counter
    item_id_counter += 1
    new_item = Item(
        id=item_id_counter,
        name=item.name,
        price=item.price,
        deleted=False
    )
    items[item_id_counter] = new_item
    response.headers['location'] = f'/item/{item_id_counter}'

    request_counter.inc()

    return new_item.model_dump()


@app.post('/cart', status_code=status.HTTP_201_CREATED)
def create_cart(response: Response):
    '''
    Создает новую корзину и возвращает её ID
    '''
    global cart_id_counter
    cart_id_counter += 1
    cart_id = cart_id_counter
    carts[cart_id] = Cart(id=cart_id)
    response.headers['location'] = f'/cart/{cart_id}'
    
    request_counter.inc()

    return {'id': cart_id}


@app.post('/cart/{cart_id}/add/{item_id}', status_code=status.HTTP_200_OK)
def add_item_to_cart(cart_id: int, item_id: int):
    '''
    Добавляет товар в корзину по ID корзины и ID товара
    '''
    if cart_id not in carts:
        error_counter.inc()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Такой корзины нету :('
        )
    if item_id not in items:
        error_counter.inc()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail='Такого товара нету :('
        )

    cart = carts[cart_id]
    item = items[item_id]

    if item.deleted:
        error_counter.inc()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Этот товар недоступен :('
        )

    existing_item = next(
        (
            cart_item for cart_item in cart.items if cart_item.id == item_id
        ), 
        None
    )
    
    if existing_item:
        existing_item.quantity += 1
    else:
        cart_item = CartItem(
            id=item.id,
            name=item.name,
            quantity=1,
            available=not item.deleted
        )
        cart.items.append(cart_item)

    cart.price += item.price
    
    request_counter.inc()
    
    return JSONResponse(
        content={'message': 'Товар добавлен в корзину'}
    )


@app.get('/cart/{cart_id}')
def get_cart_by_id(cart_id: int):
    '''
    Возвращает корзину по её ID.
    '''
    if cart_id not in carts:
        error_counter.inc()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Такой корзины нету :('
        )
        
    request_counter.inc()
    
    return carts[cart_id]


@app.get('/cart')
def get_carts(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, gt=0),
    min_price: float | None = Query(None, ge=0),
    max_price: float | None = Query(None, ge=0),
    min_quantity: int | None = Query(None, ge=0),
    max_quantity: int | None = Query(None, ge=0)
):
    '''
    Возвращает список корзин с возможностью фильтрации и пагинации
    '''
    filtered_carts = [
        cart for cart in carts.values()
        if (min_price is None or cart.price >= min_price) and
           (max_price is None or cart.price <= max_price) and
           (min_quantity is None or sum(item.quantity for item in cart.items) >= min_quantity) and
           (max_quantity is None or sum(item.quantity for item in cart.items) <= max_quantity)
    ]
    
    request_counter.inc()
    
    return filtered_carts[offset:offset + limit]


@app.get('/item/{id}')
def get_item_by_id(id: int):
    '''
    Возвращает товар по его ID
    '''
    if id not in items:
        error_counter.inc()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Такого товара нету :('
        )
        
    if items[id].deleted:
        error_counter.inc()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Товар удален'
        )
    
    request_counter.inc()
    
    return items[id]


@app.get('/item')
def get_item(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, gt=0),
    min_price: float | None = Query(None, ge=0),
    max_price: float | None = Query(None, ge=0),
    show_deleted: bool = Query(False)
):
    '''
    Возвращает список товаров с возможностью фильтрации и пагинации.
    '''
    filtered_items = [
        item for item in items.values()
        if (min_price is None or item.price >= min_price) and
           (max_price is None or item.price <= max_price) and
           (show_deleted or not item.deleted)
    ]
    
    request_counter.inc()
    
    return filtered_items[offset:offset + limit]


@app.put('/item/{id}')
def put_item_by_id(id: int, new_item: NewItem):
    '''
    Полностью обновляет товар по его ID.
    '''
    if id not in items.keys():
        error_counter.inc()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Товара не существует. Только замена существующего :('
        )
        
    item = items[id]
    item.name = new_item.name
    item.price = new_item.price

    request_counter.inc()
    
    return item


@app.patch('/item/{id}')
def patch_item_by_id(id: int, update_item: UpdateItem):
    '''
    Частично обновляет товар по его ID.
    '''
    if id not in items:
        error_counter.inc()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Товара не существует. Только замена существующего :('
        )

    item = items[id]

    if item.deleted:
        error_counter.inc()
        raise HTTPException(
            status_code=status.HTTP_304_NOT_MODIFIED,
            detail='Товар удален'
        )

    if update_item.name is not None:
        item.name = update_item.name
    if update_item.price is not None:
        item.price = update_item.price

    request_counter.inc()
    
    return item


@app.delete('/item/{id}')
def delete_item(id: int):
    '''
    Удаляет товар по его ID
    '''
    if id not in items:
        error_counter.inc()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Такого товара нету :('
        )
    item = items[id]
    item.deleted = True
    
    request_counter.inc()
    
    return {'message': 'Товар удален'}


@app.get('/metrics')
def metrics():
    '''
    Возвращает метрики
    '''
    request_counter.inc()
    return Response(generate_latest(REGISTRY), media_type='text/plain')
