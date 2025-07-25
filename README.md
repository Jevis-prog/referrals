Реферальная система с авторизацией по номеру телефона.

Описание проекта:

Данный проект реализует простую реферальную систему с авторизацией по номеру телефона. Пользователь вводит номер телефона,
получает 4-значный код для входа, и при первой авторизации ему присваивается уникальный 6-значный инвайт-код.
Пользователь может активировать чужой инвайт-код. В профиле отображается список пользователей,
которые ввели инвайт-код текущего пользователя.

Для установки всех зависимостей:

    pip install poetry
    poetry install

Для выполнения миграций:

    python manage.py migrate

Для запуска сервера:

    python manage.py runserver

Приложение можно тестировать через пользовательский интерфейс, по ссылке

http://localhost:8000/ui/phone/

Код от "СМС" можно будет увидеть в терминале.


Описание API:

1) Авторизация по номеру телефона
URL: /api/auth/request_code/

Метод: POST

Описание: Отправка номера телефона для начала авторизации. Генерируется и отправляется 4-значный код (эмуляция с задержкой).

Тело запроса:


```{
  "phone": "+79991234567"
}
```

Ответ:

```
{
  "detail": "Код отправлен"
}
```

2) Подтверждение кода авторизации
URL: /api/auth/verify_code/

Метод: POST

Описание: Подтверждение 4-значного кода, получение JWT токенов.

Тело запроса:

```
{
  "phone": "+79991234567",
  "code": "1234"
}
```

Ответ:


```
{
  "phone_number": "+79999877766",
  "invite_code": "C0aL3d",
  "access": "<JWT access token>",
  "refresh": "<JWT refresh token>"
}
```

3) Получение профиля пользователя
URL: /api/profile_back/

Метод: GET

Описание: Получение информации о профиле пользователя, включая его инвайт-код и активированный код,
а также список пользователей, которые ввели его код.

Тело запроса: нет

Ответ:
```
{
  "phone_number": "+79991234567",
  "invite_code": "A1B2C3",
  "invited_by_code": "Z9Y8X7",
  "invited_users": [
    "+79990001122",
    "+79990002233"
  ]
}
```
Авторизация: требуется, передавать в заголовке Authorization: Bearer <access token>

4) Ввод чужого инвайт-кода
URL: /api/profile_back/activate_invite/

Метод: POST

Описание: Активация чужого инвайт-кода пользователем (только 1 раз).

Тело запроса:


```
{
  "code": "Z9Y8X7"
}
```
Ответ:

```
{
  "detail": "Инвайт-код успешно активирован"
}

```
Авторизация: требуется, передавать в заголовке Authorization: Bearer <access token>