from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field

from . import accounts

router = APIRouter()


def user_for(request: Request, *, admin: bool = False) -> dict:
    user = request.state.user
    if not user:
        raise HTTPException(401, "Sign in to continue.")
    if admin and user["role"] != "admin":
        raise HTTPException(403, "Only the admin can manage accounts.")
    return user


def set_session(response: Response, request: Request, user_id: str) -> None:
    accounts.revoke_session(request.cookies.get(accounts.COOKIE))
    response.set_cookie(accounts.COOKIE, accounts.new_session(user_id),
                        max_age=accounts.SESSION_SECONDS, httponly=True,
                        secure=request.state.secure_cookie, samesite="lax", path="/")


class Login(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=256)


class Password(BaseModel):
    password: str = Field(min_length=12, max_length=256)
    current_password: str = Field(default="", max_length=256)


class NewAccount(BaseModel):
    username: str = Field(min_length=3, max_length=32)
    password: str = Field(min_length=12, max_length=256)


class AccountStatus(BaseModel):
    disabled: bool


@router.get("/api/auth/me")
def me(request: Request):
    user = request.state.user
    return {"user": accounts.public_user(user) if user else None,
            "loginRequired": request.state.login_required,
            "ownerLoginAvailable": request.state.shared_auth.enabled,
            "hasPassword": bool(user and user["password_hash"])}


@router.post("/api/auth/login")
def login(payload: Login, request: Request, response: Response):
    try:
        user = accounts.authenticate(payload.username, payload.password,
                                     request.client.host if request.client else "unknown")
    except accounts.LoginLimited as error:
        raise HTTPException(429, str(error)) from error
    if not user:
        raise HTTPException(401, "Incorrect username or password.")
    set_session(response, request, user["id"])
    return {"user": accounts.public_user(user)}


@router.post("/api/auth/logout")
def logout(request: Request, response: Response):
    accounts.revoke_session(request.cookies.get(accounts.COOKIE))
    # A marker prevents the shared NSY cookie (or local mode) from signing the
    # owner straight back in after an explicit study-app logout.
    response.set_cookie(accounts.COOKIE, "signed-out", max_age=accounts.SESSION_SECONDS,
                        httponly=True, secure=request.state.secure_cookie, samesite="lax", path="/")
    return {"ok": True}


@router.get("/api/auth/owner")
def owner_login(request: Request):
    auth = request.state.shared_auth
    if auth.enabled and not auth.valid_token(request.cookies.get(auth.cookie_name)):
        return RedirectResponse(auth.login_redirect("/api/auth/owner"), status_code=303)
    if request.state.login_required and not auth.enabled:
        return RedirectResponse("/login", status_code=303)
    response = RedirectResponse("/", status_code=303)
    set_session(response, request, "owner")
    return response


@router.post("/api/auth/password")
def change_password(payload: Password, request: Request, response: Response):
    user = user_for(request)
    if user["password_hash"] and not accounts.password_matches(payload.current_password, user["password_hash"]):
        raise HTTPException(400, "Current password is incorrect.")
    accounts.set_password(user["id"], payload.password)
    set_session(response, request, user["id"])
    return {"ok": True}


@router.get("/api/admin/accounts")
def list_accounts(request: Request):
    user_for(request, admin=True)
    return {"accounts": accounts.list_users()}


@router.post("/api/admin/accounts", status_code=201)
def create_account(payload: NewAccount, request: Request):
    user_for(request, admin=True)
    try:
        return accounts.create_user(payload.username, payload.password)
    except ValueError as error:
        raise HTTPException(400, str(error)) from error


@router.post("/api/admin/accounts/{user_id}/password")
def reset_password(user_id: str, payload: Password, request: Request):
    user_for(request, admin=True)
    if user_id == "owner":
        raise HTTPException(400, "Use Change my password for your own account.")
    try:
        accounts.set_password(user_id, payload.password, must_change=True)
    except ValueError as error:
        raise HTTPException(404, str(error)) from error
    return {"ok": True}


@router.patch("/api/admin/accounts/{user_id}")
def account_status(user_id: str, payload: AccountStatus, request: Request):
    user_for(request, admin=True)
    try:
        accounts.set_disabled(user_id, payload.disabled)
    except ValueError as error:
        raise HTTPException(400, str(error)) from error
    return {"ok": True}
