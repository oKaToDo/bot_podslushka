import vk_api
import vk
from vk_api.upload import VkUpload
from vk_api.longpoll import VkLongPoll, VkEventType
from PIL import Image, ImageDraw, ImageFont
import random
import os

vk_sess = vk_api.VkApi(token='32e1c4d8d1360ced570756d0a743f65bb494a8f489dd3a8300c414e2698cacf472ba5b7c48ca2c2622371')
longpoll = VkLongPoll(vk_sess)
api = vk.API(vk_sess)
uploader = VkUpload(vk_sess)
last_text = ''
attachments = []
not_command = False

schedule = {
    'понедельник': [f'{c + 1} - {i}' for c, i in enumerate(
        ["География", "Русский язык", "Литература", "Практикум", "Алгебра", "Химия", "Английский язык"])],
    'вторник': [f'{c + 1} - {i}' for c, i in
                enumerate(["Геометрия", "Алгебра", "Родной язык (русский)", "История", "Английский язык", "Физика"])],
    'среда': [f'{c + 1} - {i}' for c, i in enumerate(
        ["Алгебра", "Обществознание", "История", "Английский язык", "География", "Физ-ра", "Биология"])],
    'четверг': [f'{c + 1} - {i}' for c, i in
                enumerate(["Геометрия", "Физ-ра", "Английский язык", "Физика", "Химия", "Алгебра", "Литература"])],
    'пятница': [f'{c + 1} - {i}' for c, i in enumerate(
        ["Информатика", "Английский язык", "Практикум по математике", "Биология", "Русский язык", "Литература"])]
}


def send_msg(id, text):
    vk_sess.method('messages.send',
                   {'user_id': id, 'message': text, 'random_id': 0, 'attachment': ','.join(attachments)})


def send_schedule(text):
    send_msg(id, '\n'.join(schedule[text]))


def edit_photo(id, text):
    global attachments
    image = f'static/pictures/{random.choice([i for i in range(1, 10)])}.jpg'
    image1 = Image.open(image)
    image1 = image1.resize((500, 600))
    draw_text = ImageDraw.Draw(image1)
    font = ImageFont.truetype('static/3952.ttf', size=25)
    w, h = draw_text.textsize(text, font=font)
    draw_text.text(
        (int(((500 - w) / 2)), 560),
        text,
        font=font,
        fill='#ffffff')
    image1.save('static/pictures/photo_to_user.jpg')
    image1_path = 'static/pictures/photo_to_user.jpg'

    upload_image = uploader.photo_messages(photos=image1_path)[0]
    attachments.append(f'photo{upload_image["owner_id"]}_{upload_image["id"]}')
    os.remove('static/pictures/photo_to_user.jpg')


for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        attachments = []
        id = event.user_id
        if event.text:
            text = event.text.lower()

            if text == 'расписание':
                send_msg(id, 'Введи день и я пришлю тебе расписание на этот день')

            elif text == 'начать' or text == 'старт':
                send_msg(id, f'Привет! Введи команду:\n- Расписание\n - Картинка')

            elif text == 'картинка':
                send_msg(id, 'Введи текст к картинке')
                not_command = True

            else:
                if text not in schedule.keys() and not_command is False:
                    send_msg(id, 'Моя твоя не понимать!!! Введи команду корректно')

            if last_text == 'расписание':
                if text == 'понедельник':
                    send_schedule(text)
                elif text == 'вторник':
                    send_schedule(text)
                elif text == 'среда':
                    send_schedule(text)
                elif text == 'четверг':
                    send_schedule(text)
                elif text == 'пятница':
                    send_schedule(text)
            if last_text == 'картинка':
                edit_photo(id, text)
                send_msg(id, '')
                not_command = False

            print(f'--Text: {text}, --LastText: {last_text}')
            last_text = text
