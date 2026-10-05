from tests.test_main import client
from main import app
from fastapi import status
from router.auth import get_current_user
from database import SessionLocal
from models import Transactions
from datetime import date


def override_get_current_user():
    return {
        'id': 1,
        'username': 'testuser'
    }


app.dependency_overrides[get_current_user] = override_get_current_user


def test_transaction():

    db = SessionLocal()

    # remove old test data if it exists
    db.query(Transactions).filter(
        Transactions.id == 99
    ).delete()

    transaction = Transactions(
        id=99,
        title='Testing',
        amount=500,
        type='expense',
        category='Food',
        date=date.today(),
        owner_id=1
    )

    db.add(transaction)
    db.commit()


def test_read_transactions():

    response = client.get('/transactions')

    assert response.status_code == status.HTTP_200_OK


def test_read_specific_transaction():

    response = client.get('/transactions/99')

    assert response.status_code == status.HTTP_200_OK


def test_create_transaction():

    db = SessionLocal()

    # remove old test data if it exists
    db.query(Transactions).filter(
        Transactions.id == 100
    ).delete()
    db.commit()

    request_data = {
        "title": "Test Transaction",
        "amount": 100,
        "type": "expense",
        "category": "Food",
        "date": str(date.today())
    }

    response = client.post(
        '/transactions/create',
        json=request_data
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
        'message': 'Transactions create successfully'
    }


def test_update_transaction():

    request_data = {
        "title": "Updated Transaction"
    }

    response = client.put(
        '/transactions/edit/99',
        json=request_data
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        'message': 'To do updated successfully'
    }


def test_delete_transaction():

    response = client.delete(
        '/transactions/delete/99'
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        'message': 'Transactions deleted successfully'
    }