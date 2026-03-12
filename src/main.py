# -*- coding: utf-8 -*-

import os
from model_utils import load_model, make_inference
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel


# Описание структуры входных данных
class Instance(BaseModel):
    hour: int
    month: int
    precipitation: float
    pressure: float
    humidity: float
    wind_speed: float
    latitude: float
    longitude: float
    height: float


# Создаем экземпляр FastAPI приложения
app = FastAPI()

# Настраиваем авторизацию через Bearer Token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth")

# Получаем путь к модели из переменной окружения
model_path: str = os.getenv("MODEL_PATH")

# Если путь к модели не задан — сервис не запускается
if model_path is None:
    raise ValueError("The environment variable $MODEL_PATH is empty!")


# Функция проверки токена
async def is_token_correct(token: str) -> bool:
    dummy_correct_token = "00000"
    return token == dummy_correct_token


# Проверка токена перед доступом к защищенному endpoint
async def check_token(token: str = Depends(oauth2_scheme)) -> None:
    if not await is_token_correct(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Endpoint для проверки работоспособности сервиса
@app.get("/healthcheck")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


# Основной endpoint инференса
@app.post("/predictions")
async def predictions(
    instance: Instance,
    token: str = Depends(check_token)
) -> dict[str, float]:

    # Загружаем модель
    model = load_model(model_path)

    # Выполняем предсказание
    result = make_inference(
        model,
        instance.dict()
    )

    return result
