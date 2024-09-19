import json
from typing import Any, Dict
from math import factorial
from .statuses import bad_request, unprocessable_entity, not_found, ok


def fibonacci(n: int) -> int:
    if n in [0, 1]:
        return n
    else:
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b


async def handler_factorial(query_string):
    try:
        n = int(query_string.split('=')[-1])
        if n < 0:
            return bad_request()
        return ok(factorial(n))
    except Exception as e:
        return unprocessable_entity()


async def handler_fibonacci(path):
    try:
        n = int(path.split('/')[-1])
        if n < 0:
            return bad_request()
        return ok(fibonacci(n))
    except Exception as e:
        return unprocessable_entity()


async def handler_mean(body):
    print(body)
    try:
        numbers = body

        if not isinstance(numbers, list) or (
            not all(isinstance(n, (int, float)) for n in numbers)
        ):
            raise TypeError
        elif not len(numbers):
            return bad_request()

        result = sum(numbers) / len(numbers)

        return ok(result)
    except TypeError:
        return unprocessable_entity()


async def route(path, method, query_string, body):
    if method == 'GET':
        if path == '/factorial':
            return await handler_factorial(query_string)
        elif '/fibonacci' in path:
            return await handler_fibonacci(path)
        elif path == '/mean':
            return await handler_mean(body)
        else:
            return not_found()
    else:
        return not_found()


async def http_handler(scope, recieve, send):
    path = scope['path']
    method = scope['method']
    query_string = scope['query_string'].decode()

    try:
        body = await recieve()
        body = json.loads(body['body'].decode())
    except Exception as e:
        body = None

    response = await route(path, method, query_string, body)

    await send(
        {
            'type': 'http.response.start',
            'status': response['status'],
            'headers': [(b'content-type', b'application/json')],
        }
    )
    await send(
        {
            'type': 'http.response.body',
            'body': json.dumps(response['body']).encode(),
        }
    )


async def app(scope: Dict[str, Any], receive: Any, send: Any) -> None:
    if scope['type'] == 'http':
        await http_handler(scope, receive, send)
