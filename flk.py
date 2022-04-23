import json
import re
import random

import flask
from flask import request
from flask_cors import CORS, cross_origin
import sqlite3

conn = sqlite3.connect("users.db", check_same_thread=False)
cur = conn.cursor()
conn.commit()
app = flask.Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


def get_example(user_id):
    cur.execute("SELECT * FROM users where user_id = ?", (user_id,))
    user = cur.fetchone()
    if user is None:
        cur.execute("INSERT INTO users (user_id, stage, balls) values (?, -1, 0)", (user_id,))
        conn.commit()
        cur.execute("SELECT * FROM users where user_id = ?", (user_id,))
        user = cur.fetchone()
    return user


def set_stage(new_stage, user_id):
    cur.execute("UPDATE users SET stage = ? where user_id = ?", (new_stage, user_id))
    conn.commit()


def set_balls(new_balls, user_id):
    cur.execute("UPDATE users SET balls = ? where user_id = ?", (new_balls, user_id))
    conn.commit()


@app.post("/webhook")
@cross_origin()
def webhook():
    stage = -1
    request_body = json.loads(request.data)
    derived_session_fields = ['session_id', 'user_id', 'message_id']
    text_standart = "Команда не распознана."
    tts_standart = "Я не распозна+ю такую команду."
    text = text_standart
    tts = tts_standart
    categories = ["Gamedev", "Java", "Mobile", "PHP", "Back End", "Маруся", "Чат боты", "Mini Apps"]
    user = get_example(request_body['session']["user_id"])

    if re.search("вездеход", request_body["request"]["command"].lower()):
        tts = "Привет вездек+одерам!"
        text = "Привет вездекодерам!"
        stage = -1

    if re.search("категория", request_body["request"]["command"].lower()):
        tts = "Ты хочешь узнать какую категорию взять на вездек+оде? Ну давай попробуем!"
        text = "Я задам 8 простых вопросов и по ним мы поймем куда тебе стоит двигаться :)\nСкажи жду вопросы, если хочешь начать :0"
        stage = -1

    if re.search("жду вопросы", request_body["request"]["command"].lower()):
        tts = "Хорошо. Первый вопрос: Java - какой язык? Динамичный или статичный?"
        text = "Java - динамичный или статичный язык?"
        stage = 1
        set_balls(0, request_body['session']["user_id"])

    if re.search("статичный", request_body["request"]["command"].lower()) or (
            re.search("далее", request_body["request"]["command"].lower()) and user[2] == -1):
        tts = "Действительно. Он статичный. Второй вопрос: Какой язык используется в Unity"
        text = "Какой язык используется в юнити? (C++, Python, C#, Java)"
        stage = 2

    if re.search("c#", request_body["request"]["command"].lower()) or (
            re.search("далее", request_body["request"]["command"].lower()) and user[2] == 1):
        tts = "Ессесно. Си шарп. Третий вопрос: Какой метод взаимодействия с сервером используется в марусе"
        text = "Какой метод взаимодействия с сервером используется в марусе (Longpoll, Callback, Webhooks, data-scrapper)"
        stage = 3

    if re.search("webhooks", request_body["request"]["command"].lower()) or (
            re.search("далее", request_body["request"]["command"].lower()) and user[2] == 2):
        tts = "Ты прав. Это действительно вебхуки. Следующий вопрос: в PHP слабая типизация или сильная?"
        text = "В PHP слабая типизация или сильная?"
        stage = 4

    if re.search("слабая", request_body["request"]["command"].lower()) or (
            re.search("далее", request_body["request"]["command"].lower()) and user[2] == 3):
        tts = "Думаю да, слабая. Пятый вопрос: Какой фреймворк JAVA чаще всего используется на Android?"
        text = "Какой фреймворк JAVA чаще всего используется на Android? (Flutter, Kotlin, Spring)"
        stage = 5

    if re.search("spring", request_body["request"]["command"].lower()) or (
            re.search("далее", request_body["request"]["command"].lower()) and user[2] == 4):
        tts = "Возможно вопрос был не совсем корректен, но ты ответил верно :) Шестой вопрос: На каком порту стоит HTTPS протокол?"
        text = "На каком порту стоит HTTPS протокол?"
        stage = 6

    if re.search("443", request_body["request"]["command"].lower()) or (
            re.search("далее", request_body["request"]["command"].lower()) and user[2] == 5):
        tts = "Ты прав. А HTTP на 80. Седьмой вопрос: Какой из способов взаимодействия VK с сервером отправляет на сервер обновления?"
        text = "Какой из способов взаимодействия VK с сервером отправляет на сервер обновления (Longpoll, Callback, Webhooks, data-scrapper)?"
        stage = 7

    if re.search("callback", request_body["request"]["command"].lower()) or (
            re.search("далее", request_body["request"]["command"].lower()) and user[2] == 6):
        tts = "Да. Это callback. Последний вопрос: Что нужно для создания приложений VK MINI APPS?"
        text = "Что нужно для создания приложений VK MINI APPS (Много деняк, связи, просто желание)?"
        stage = 8

    if re.search("просто желание", request_body["request"]["command"].lower()) or (
            re.search("далее", request_body["request"]["command"].lower()) and user[2] == 7):
        rand_resh = categories[random.randint(0, len(categories) - 1)]
        tts = f"<speaker audio=marusia-sounds/game-win-2> Да. Это полностью бесплатно. Ты прошел тест. Думаю, тебе стоит выбрать категорию: {rand_resh}. Ты набрал {user[3]} баллов."
        text = f"<speaker audio=marusia-sounds/game-win-2> Да. Это полностью бесплатно. Ты прошел тест. Тебе стоит выбрать категорию: {rand_resh}. Ты набрал {user[3]} баллов."
        return {"response": {"text": text, "tts": tts, "end_session": False,
                             "card": {
                                 "type": "Link",
                                 "url": ["https://vk.com/app7543093_404016892"],
                                 "title": "Регистрируйся!",
                                 "text": f"Напомню, тебе лучше выбрать: {rand_resh}",
                                 "image_id": 457239017
                             }},
                "session": {derived_key: request_body['session'][derived_key] for derived_key in
                            derived_session_fields},
                "version": request_body['version']
                }
    if user[2] >= 0:
        if text_standart == text:
            text = "А вот и нет! -1 балл. Для следующего вопроса просто напиши: 'далее'"
            tts = "Ты не угадал. <speaker audio=marusia-sounds/game-loss-1> Это задание я тебе не защитаю."
        else:
            if not re.search("далее", request_body["request"]["command"].lower()):
                tts = "<speaker audio=marusia-sounds/game-win-1>" + tts
                set_balls(user[3] + 1, request_body['session']["user_id"])
                set_stage(stage, request_body['session']["user_id"])
    else:
        set_stage(stage, request_body['session']["user_id"])
    return {"response": {"text": text, "tts": tts, "end_session": False},
            "session": {derived_key: request_body['session'][derived_key] for derived_key in derived_session_fields},
            "version": request_body['version']
            }


app.run(debug=True)
