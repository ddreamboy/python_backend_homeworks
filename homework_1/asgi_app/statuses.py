import json


def bad_request(message='Bad Request'):
    return {'status': 400, 'body': json.dumps({'error': message})}


def unprocessable_entity(message='Unprocessable Entity'):
    return {'status': 422, 'body': json.dumps({'error': message})}


def not_found(message='Not Found'):
    return {'status': 404, 'body': json.dumps({'error': message})}


def ok(message):
    return {'status': 200, 'body': json.dumps({'result': message})}
