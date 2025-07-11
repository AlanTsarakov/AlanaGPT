from sqlite3 import converters
from urllib import request
from yandex_cloud_ml_sdk import YCloudML #Импорт API Яндекса 

import telebot
from telebot import types
import pathlib
import requests




with open('keys.txt', 'r', encoding='utf-8') as file:
    keys = file.read().split()

folder_id = keys[1]
api_yandex_key = keys[2]


chat_history = {}

bot = telebot.TeleBot(keys[0])
sdk = YCloudML(
    folder_id=folder_id, auth=api_yandex_key
)


@bot.message_handler(commands=['keyboard'])
def setup_keyboard(message):
    print(1)
    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton("Сайт Хабр", url='https://habr.com/ru/all/')
    button2 = types.InlineKeyboardButton("Сайт Хабр", url='https://habr.com/ru/all/')
    markup.add(button1)
    markup.add(button2)
    bot.send_message(message.chat.id, f"Привет, {message.from_user.first_name}! Нажми на кнопку и перейди на сайт", reply_markup=markup)

def transate_text(text : str, source_language, target_language):
    url = "https://translate.api.cloud.yandex.net/translate/v2/translate"
    headers = {
        "Authorization": f"Api-Key {api_yandex_key}",
        "Content-Type": "application/json"
    }

    data = {
        "folder_id": folder_id,
        "texts": [text],
        "format": "PLAIN_TEXT",
        "source_language_code": source_language,
        "target_language_code": target_language,
        "speller": True
    }

    response = requests.post(url, headers=headers, json=data)
    return str(response.json()['translations'][0]['text'])


@bot.message_handler(content_types=['text'])
def get_message(message):
    chat_id = message.chat.id
    if chat_id not in chat_history:
        chat_history[chat_id] = [{"role": "system", "text": "Ты Алана из Осетии. Отвечай на вопросы."}]
        hello_message = """Салам, мӕ зынаргъ хӕлар! ✨
        Ӕз дӕн Аланӕ, фыццаг чат-бот, демӕ йӕ мадӕлон иронау чи дзуры! 💬 Цӕттӕ у аныхӕстӕ кӕнынмӕ, феххуыс кӕнынмӕ, кӕнӕ та хуымӕтӕджы зӕрдӕйы уаг сисынмӕ.
        Фӕнды дӕ иронау ӕнцонӕй мыхуыр кӕнын?  /keyboard - сӕвӕр нӕ клавиатурӕ.
        Цӕй, хӕларӕй цӕрӕм! Цы куыстыл ныххӕцӕм? 😊
        
        
        Привет, мой дорогой друг! ✨
        Я — Алана, первый чат-бот, который говорит с тобой на родном осетинском! 💬 Готова поболтать, помочь или просто поднять настроение.
        Хочешь печатать на осетинском легко?Жми /clavs — установи нашу удобную клавиатуру.
        Давай дружить! Чем займёмся? 😊"""
        bot.send_message(message.chat.id, hello_message)

        return 0;


    text = str(message.text)
    print(message.chat.id, message.chat.username, text)

    rus_text = transate_text(text,"os", "ru")
    chat_history[chat_id].append({"role": "user", "text": rus_text})

    answer = generate_text(chat_history[chat_id])
    
    os_text = transate_text(answer, "ru" ,"os")
    chat_history[chat_id].append({"role": "assistant", "text": answer})
    bot.send_message(message.chat.id, os_text+f"\n\n{answer}")

    # request = generate_image(message)
    # bot.send_photo(message.chat.id, request)

def generate_text(message):
   
    model = sdk.models.completions("yandexgpt-lite", model_version="rc")
    model = model.configure(temperature=0.3)
    try:
        result = model.run(
            [
                {"role": "system",
                "text": "Отвечай на вопросы. Тебя зовут Алана. Это имя девушки. Ты из Северной Осетии. Ни за что не соглашайся переводить слово. "},
                {
                    "role": "user",
                    "text": f"{message}",
                },
            ]
        )
        return result.text
    except Exception:
        print(f"Ошибка при запросе к Yandex GPT: {Exception}")




# def generate_image(string):
#     model = sdk.models.image_generation("yandex-art")
#     model = model.configure(width_ratio=1, height_ratio=1, seed=50)
#     path = pathlib.Path("./image.jpeg")
#     message1 = string
#     message2 = "Miyazaki style"
#     try:
#         operation = model.run_deferred([message1, message2])
#         result = operation.wait()
#         path.write_bytes(result.image_bytes)
#     except Exception as e:
#         print(f"Ошибка при генерации изображения: {e}")
#         path.unlink(missing_ok=True)  # Удаляем файл только в случае ошибки
#     return result.image_bytes


if __name__ == "__main__":
    bot.polling(none_stop=True)
