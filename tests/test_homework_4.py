import pytest
from http import HTTPStatus
from fastapi.testclient import TestClient
from homework_4.demo_service.api.main import create_app


@pytest.fixture(scope='module')
def client():
    app = create_app()
    with TestClient(app) as client:
        yield client


def test_user_register(client):
    try:
        response = client.post(
            '/user-register',
            json={
                'username': 'nagibator228',
                'name': 'Mister Beast',
                'birthdate': '2024-04-24',
                'role': 'user',
                'password': 'qwerty123',
            },
        )
        assert response.status_code == HTTPStatus.OK, (
            f'Expected status 200, but got {response.status_code}'
        )
        assert response.json() == {
            'uid': 2,
            'username': 'nagibator228',
            'name': 'Mister Beast',
            'birthdate': '2024-04-24T00:00:00',
            'role': 'user'
        }, f'Response JSON does not match expected: {response.json()}'

    except Exception as e:
        pytest.fail(f'Test failed with exception: {str(e)}')


@pytest.mark.parametrize(
    'body, status', [
    (
        {
            'username': 'nagibator228',
            'name': 'Mister Beast',
            'birthdate': '2024-04-24',
            'role': 'user',
            'password': 'qwerty123',
        }, HTTPStatus.BAD_REQUEST
        ),
    (
        {
            'username': 'normis',
            'name': 'Vanya Ivanov',
            'birthdate': '2024-04-24',
            'role': 'user',
            'password': 'omagad',
        }, HTTPStatus.BAD_REQUEST
        ),
    (
        {
            'username': 'nagibator228',
            'name': 'Mister Beast',
            'birthdate': '24-04-2024',
            'role': 'user',
            'password': 'qwerty123',
        }, HTTPStatus.UNPROCESSABLE_ENTITY
        ),
])
def test_user_register_invalid(client, body, status):
    response = client.post('/user-register', json=body)
    assert response.status_code == status


def test_user_get_by_uid(client):
    response = client.post(
        '/user-get',
        params={'id': 2},
        auth=('nagibator228', 'qwerty123')
    )
    assert response.status_code == HTTPStatus.OK, (
        f'Expected status 200, but got {response.status_code}'
    )
    assert response.json() == {
        'uid': 2,
        'username': 'nagibator228',
        'name': 'Mister Beast',
        'birthdate': '2024-04-24T00:00:00',
        'role': 'user'
    }


def test_user_get_by_username(client):
    response = client.post(
        '/user-get',
        params={'username': 'nagibator228'},
        auth=('nagibator228', 'qwerty123')
    )
    assert response.status_code == HTTPStatus.OK, (
        f'Expected status 200, but got {response.status_code}'
    )
    assert response.json() == {
        'uid': 2,
        'username': 'nagibator228',
        'name': 'Mister Beast',
        'birthdate': '2024-04-24T00:00:00',
        'role': 'user'
    }


def test_user_get_both_id_and_username(client):
    response = client.post(
        '/user-get',
        params={'id': 2, 'username': 'nagibator228'},
        auth=('nagibator228', 'qwerty123')
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST, (
        f'Expected status 400, but got {response.status_code}'
    )


def test_user_get_neither_id_nor_username(client):
    response = client.post(
        '/user-get',
        auth=('nagibator228', 'qwerty123')
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST, (
        f'Expected status 400, but got {response.status_code}'
    )


def test_user_get_unauthorized(client):
    response = client.post(
        '/user-get',
        params={'id': 2}
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED, (
        f'Expected status 401, but got {response.status_code}'
    )


def test_user_get_not_found(client):
    response = client.post(
        '/user-get',
        params={'id': 999},
        auth=('nagibator228', 'qwerty123')
    )
    assert response.status_code == HTTPStatus.NOT_FOUND, (
        f'Expected status 404, but got {response.status_code}'
    )


def test_user_promote_as_admin(client):
    response = client.post(
        '/user-register',
        json={
            'username': 'bab_nick',
            'name': 'Gena Bookin',
            'birthdate': '2024-04-24',
            'role': 'user',
            'password': 'qwerty123',
        },
    )
    assert response.status_code == HTTPStatus.OK, (
        f'Expected status 200, but got {response.status_code}'
    )
    user_id = response.json()['uid']

    response = client.post(
        '/user-promote',
        params={'id': user_id},
        auth=('admin', 'superSecretAdminPassword123')
    )
    assert response.status_code == HTTPStatus.OK, (
        f'Expected status 200, but got {response.status_code}'
    )

    response = client.post(
        '/user-get',
        params={'id': user_id},
        auth=('admin', 'superSecretAdminPassword123')
    )
    assert response.status_code == HTTPStatus.OK, (
        f'Expected status 200, but got {response.status_code}'
    )
    assert response.json()['role'] == 'admin', (
        f'Expected role must be admin, but got {response.json()["role"]}'
    )


def test_user_promote_as_non_admin(client):
    response = client.post(
        '/user-register',
        json={
            'username': 'turbopushka',
            'name': 'Zapoi Pivovarov',
            'birthdate': '2024-04-24',
            'role': 'user',
            'password': 'qwerty123',
        },
    )
    assert response.status_code == HTTPStatus.OK, (
        f'Expected status 200, but got {response.status_code}'
    )
    user_id = response.json()['uid']

    response = client.post(
        '/user-promote',
        params={'id': user_id},
        auth=('nagibator228', 'qwerty123')
    )
    assert response.status_code == HTTPStatus.FORBIDDEN, (
        f'Expected status 403, but got {response.status_code}'
    )


def test_user_promote_non_existent_user(client):
    response = client.post(
        '/user-promote',
        params={'id': 999},
        auth=('admin', 'superSecretAdminPassword123')
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST, (
        f'Expected status 400, but got {response.status_code}'
    )


def test_get_user_with_invalid_id(client):
    response = client.post(
        '/user-get',
        params={'id': 'invalid'},
        auth=('nagibator228', 'qwerty123')
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, (
        f'Expected status 422, but got {response.status_code}'
    )


def test_promote_user_with_invalid_id(client):
    response = client.post(
        '/user-promote',
        params={'id': 'invalid'},
        auth=('admin', 'superSecretAdminPassword123')
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, (
        f'Expected status 422, but got {response.status_code}'
    )


def test_value_error_handler(client):
    response = client.post(
        '/user-get',
        params={'id': 1, 'username': 'testuser'},
        auth=('admin', 'superSecretAdminPassword123')
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {"detail": "both id and username are provided"}


def test_grant_admin_user_not_found(client):
    response = client.post(
        '/user-promote',
        params={'id': 999},
        auth=('admin', 'superSecretAdminPassword123')
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {"detail": "user not found"}


def test_invalid_credentials(client):
    response = client.post(
        '/user-get',
        params={'id': 2},
        auth=('invalid_user', 'invalid_password')
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED, (
        f'Expected status 401, but got {response.status_code}'
    )


def test_promote_non_existent_user(client):
    response = client.post(
        '/user-promote',
        params={'id': 999},
        auth=('admin', 'superSecretAdminPassword123')
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST, (
        f'Expected status 400, but got {response.status_code}'
    )
    assert response.json() == {"detail": "user not found"}
