import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

vk_sess = vk_api.VkApi(token='32e1c4d8d1360ced570756d0a743f65bb494a8f489dd3a8300c414e2698cacf472ba5b7c48ca2c2622371')
longpoll = VkLongPoll(vk_sess)
last_text = ''

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
    vk_sess.method('messages.send', {'user_id': id, 'message': text, 'random_id': 0})


def send_schedule(text):
    send_msg(id, '\n'.join(schedule[text]))


for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
        text = event.text.lower()
        id = event.user_id

        if text == 'расписание':
            send_msg(id, 'Введи день и я пришлю тебе расписание на этот день')

        elif text == 'начать' or text == 'старт':
            send_msg(id, f'Привет! Введи команду:\n- Расписание')

        else:
            if text not in schedule.keys():
                send_msg(id, 'Я твоя не понимать!!! Введи команду корректно')

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

        print(f'--Text: {text}, --LastText: {last_text}')
        last_text = text
