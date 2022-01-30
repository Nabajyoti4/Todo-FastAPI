import sys
sys.path.append('..')

from typing import Optional
from fastapi import Depends, HTTPException, status, APIRouter
import models
from schemas import CreateUser
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta, datetime
from jose import jwt, JWTError
from config import settings

SECRET_KEY=settings.secret_key
ALGORITHM=settings.algorithm

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

models.Base.metadata.create_all(bind=engine)

oauth_bearer = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={401: {"description": "Unauthorized"}}
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_password_hash(password):
    """Generate Hash Password from plain password

    Args:
        password (Str): Plain text

    Returns:
        [Str]: Hash password
    """
    return bcrypt_context.hash(password)

def verify_password(plain_password, hashed_password):
    """Verify password from plain text

    Args:
        plain_password (Str): Plain text
        hashed_password (Str): Hash password

    Returns:
        Bool: True or False
    """
    return bcrypt_context.verify(plain_password, hashed_password)

def authenticate_user(db, username: str, password: str):
    """Authenticate user based on given username and password

    Args:
        db (Session): Database session
        username (Str): Username
        password (str): Plain text password

    Returns:
        Dict: User data
    """
    user = db.query(models.Users).filter(models.Users.username == username).first()
    
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False

    return user

def create_access_token(username: str, user_id : int, expires_delta: Optional[timedelta] = None):
    """Gegenerate JWT token

    Returns:
        Str: Jwt token
    """
    encode = {"sub": username,
            "id": user_id}
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    encode.update({
        "exp": expire
    })
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
    


@router.post('/create/user')
async def create_new_user(create_user: CreateUser, db: Session = Depends(get_db)):
    """
    Create a new user
    """
    try:
        create_user_model = models.Users()
        create_user_model.username = create_user.username
        create_user_model.email = create_user.email
        create_user_model.first_name = create_user.first_name
        create_user_model.last_name = create_user.last_name
        
        hash_password = get_password_hash(create_user.password)
        create_user_model.hashed_password = hash_password
        create_user_model.is_active = True

        db.add(create_user_model)
        db.commit()

        return {
            "message": "User created successfully"
        }
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")



@router.post("/login/access-token")
async def login_for_access_token(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
    ):
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    
    if not user:
        raise token_exception()
    access_token_expires = timedelta(minutes=20)
    access_token = create_access_token(
         user.username,user.id, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


async def get_current_user(token: str = Depends(oauth_bearer)):
    """Get the user deatils from the JWT token

    Args:
        token (str, optional): [description]. Defaults to Depends(oauth_bearer).

    Raises:
        HTTPException: If user details not found in token
        HTTPException: If token is not valid

    Returns:
        str: User details
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        if username is None or user_id is None:
            raise get_user_exception()
        return {
            "username": username,
            "id": user_id
        }
    except JWTError:
        raise get_user_exception()

# Exceptions
def get_user_exception():
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return credentials_exception

def token_exception():
    token_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate token, Incorrect token , username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return token_exception