from fastapi import APIRouter
from typing import Dict, Any

from app.services.pdos.pdos import (
    add_user_to_network,
    send_user_test_tokens,
)
from app.settings import settings

router = APIRouter()


@router.post("/auth/register-wallet-user")
def register_wallet_user(body: Dict[Any, Any]):
    public_key= body["publicKey"]
    return add_user_to_network(public_key)


@router.post("/register")
def register_user(body: Dict[Any, Any]):
    public_key= body["publicKey"]
    n_user_account = add_user_to_network(public_key)
    send_user_test_tokens(public_key)
    return n_user_account