import vk_api
import vk
from vk_api.upload import VkUpload
from vk_api.longpoll import VkLongPoll, VkEventType
from PIL import Image, ImageDraw, ImageFont
import random
import os
from settings import token
import pymorphy2
import datetime
from threading import Timer

vk_sess = vk_api.VkApi(token=token())
longpoll = VkLongPoll(vk_sess)
api = vk.API(vk_sess)
uploader = VkUpload(vk_sess)
last_text = ''
attachments = []
not_command = False
morph = pymorphy2.MorphAnalyzer()
date_now = datetime.datetime.now()
date_need = date_now.replace(day=date_now.day + 1, hour=5, minute=0, second=0, microsecond=0)
delta_t = date_need - date_now

secs = delta_t.seconds + 1

schedule = {
    'воскресенье': 'На этот день нет расписания',
    'понедельник': [f'{c + 1} - {i}' for c, i in enumerate(
        ["География", "Русский язык", "Литература", "Практикум", "Алгебра", "Химия", "Английский язык"])],
    'вторник': [f'{c + 1} - {i}' for c, i in
                enumerate(["Геометрия", "Алгебра", "Родной язык (русский)", "История", "Английский язык", "Физика"])],
    'среда': [f'{c + 1} - {i}' for c, i in enumerate(
        ["Алгебра", "Обществознание", "История", "Английский язык", "География", "Физ-ра", "Биология"])],
    'четверг': [f'{c + 1} - {i}' for c, i in
                enumerate(["Геометрия", "Физ-ра", "Английский язык", "Физика", "Химия", "Алгебра", "Литература"])],
    'пятница': [f'{c + 1} - {i}' for c, i in enumerate(
        ["Информатика", "Английский язык", "Практикум по математике", "Биология", "Русский язык", "Литература"])],
    'суббота': 'На этот день нет расписания'
}

allow_command = ['сегодня', 'завтра']

teachers = ['Екатерина Викторовна', 'Любовь Федоровна', 'Олеся Михайловна', 'Наталья Юрьевна', 'Вера Геннадьевна',
            'Алексей Петрович', 'Елена Васильевна', 'Наталья Викторовна']


def send_msg(id, text):
    vk_sess.method('messages.send',
                   {'user_id': id, 'message': text, 'random_id': 0, 'attachment': ','.join(attachments)})


def check_date(text):
    global schedule
    dates = list(schedule.keys())
    return dates[int(text)]


def horoscope():
    global teachers
    type_of_ganger = random.choices(['1', '2', '3'], weights=[80, 15, 5])[0]
    teacher = random.choice(teachers).split()
    teacher_name = morph.parse(teacher[0])[0]
    teacher_secondName = morph.parse(teacher[1])[0]
    if type_of_ganger == '1':
        text = f'''Гороскоп на сегодня\n
    Стоит остерегаться {teacher_name.inflect({'accs'}).word.capitalize()} {teacher_secondName.inflect({'accs'}).word.capitalize()}'''
    elif type_of_ganger == '2':
        text = f'''!!!ВНИМАНИЕ!!!\n
    Сегодня у {teacher_name.inflect({'gent'}).word.capitalize()} {teacher_secondName.inflect({'gent'}).word.capitalize()}
    активируется шаринган. Лучше не приходить в школу...'''
    else:
        text = f'''Сегодня планеты встали в ряд!\n
    {teacher_name.word.capitalize()} {teacher_secondName.word.capitalize()} не даст работу! Ура!!!!'''
    with open('users.txt', 'r') as file:
        while True:
            user_id = file.readline()
            if not user_id:
                break
            send_msg(int(user_id), text)
    file.close()


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


print('timer')
timer = Timer(secs, horoscope)
timer.start()
print('timer_started')
for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        attachments = []
        id = event.user_id
        with open('users.txt', 'r+') as file:
            users_id = [i.strip('\n') for i in file.readlines()]
            if str(id) not in users_id:
                file.write(str(id) + '\n')

        file.close()

        if event.text:
            text = event.text.lower()

            if text == 'расписание':
                send_msg(id, 'Введи день и я пришлю тебе расписание на этот день')

            elif text == 'начать' or text == 'старт' or text == 'команды':
                send_msg(id, f'Привет! Введи команду:\nРасписание\nКартинка')

            elif text == 'картинка':
                send_msg(id, 'Введи текст к картинке')
                not_command = True

            else:
                if text not in schedule.keys() and text not in allow_command and not_command is False:
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
                elif text == 'сегодня':
                    date_today = check_date(datetime.datetime.now().strftime('%w'))
                    send_schedule(date_today)
                elif text == 'завтра':
                    date_today = datetime.datetime.now()
                    date_tom = check_date(date_today.replace(day=date_today.day + 1, month=date_today.month,
                                                     year=date_today.year).strftime('%w'))
                    send_schedule(date_tom)



            if last_text == 'картинка':
                edit_photo(id, text)
                send_msg(id, '')
                not_command = False

            print(f'--Text: {text}, --LastText: {last_text}')
            last_text = text
