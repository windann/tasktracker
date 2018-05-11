import pymysql
from random import choice as ch, randint as r
from transliterate import translit, get_available_language_codes
import datetime

from faker import Faker
fake = Faker('ru_RU')


def connection_close(cur,conn):
    cur.close()
    conn.close()

def insert_into_type(cur,conn):
    task_type = ['работа', 'учёба', 'дом', 'покупки']

    for i in range(len(task_type)):
        sql_query = "INSERT INTO type(idtype,type_name) VALUES({}, '{}')".format(i,task_type[i])
        cur.execute(sql_query)
    conn.commit()

def insert_into_task(cur,conn):

    task_type_sql_query = "SELECT type_name FROM type"
    cur.execute(task_type_sql_query)
    task_types = [elem[0] for elem in cur]

    count_user_sql_query = "SELECT COUNT(1) FROM user"
    cur.execute(count_user_sql_query)
    count_user = cur.fetchone()[0]

    user_token_sql_query = "SELECT token FROM user"
    cur.execute(user_token_sql_query)
    user_token = [elem[0] for elem in cur]

    status = 'created'

    for i in range(count_user):

        date = datetime.datetime.now()

        category_id = r(1, len(task_types))
        category = task_types[category_id-1]

        user = ch(user_token)

        base_task_id_sql_query = "SELECT taskid FROM task"
        cur.execute(base_task_id_sql_query)
        base_tasks = [elem[0] for elem in cur]

        if base_tasks:
            base_task_id = ch(base_tasks)
        else:
            base_task_id = 0

        if category == 'покупки':
            products = ['молоко', 'хлеб', 'кефир', 'яблоки', 'шоколад', 'капуста', 'сок']
            product = ch(products)

            name = 'купить {}'.format(product)

        elif category == 'дом':
            rooms = ['кухню', 'ванную', 'комнату', 'гостинную']
            actions = ['помыть', 'пропылесосить', 'разобрать']

            room = ch(rooms)
            action = ch(actions)

            name = '{} {}'.format(action, room)

        elif category == 'учёба':
            courses = ['матан', 'супер ЭВМ', 'базы данных', 'АСОИУ', 'философия']
            actions = ['выучить', 'переписать', 'сделать ДЗ']

            action = ch(actions)
            course = ch(courses)

            name = '{} {}'.format(action, course)

        elif category == 'работа':
            work = ['составить отчёт', 'сделать задание', 'провести планёрку', 'написать заявление']

            name = ch(work)

        sql_query = "INSERT INTO task(taskid, date, status, name, type, user_token, base_task_id) VALUES({},'{}','{}','{}',{},{},{})".format(i,
                                                                                                                               date, status, name, category_id, user, base_task_id)
        cur.execute(sql_query)
        conn.commit()


def insert_into_user(cur,conn):
    sex_list = ['M', 'F']

    for i in range(40):

        age = r(14, 99)
        sex = ch(sex_list)

        if sex == 'F':
            first_name = fake.first_name_female()
            last_name = fake.last_name_female()
        else:
            first_name = fake.first_name_male()
            last_name = fake.last_name_male()

        login = translit(first_name[:2], reversed=True) + translit(last_name[:2], reversed=True) + str(age)

        sql_query = "INSERT INTO user(token, first_name, last_name, age, sex) VALUES ('{}','{}','{}',{},'{}')".format(login,
                                                                                                              first_name,
                                                                                                              last_name,
                                                                                                     age, sex)
        cur.execute(sql_query)
    conn.commit()


conn = pymysql.connect(user='tasktracker_user', password='password',
                               host='127.0.0.1',
                               database='tasktracker_db',
                               charset='utf8'
                               )
cur = conn.cursor()

insert_into_type(cur,conn)
insert_into_user(cur,conn)
insert_into_task(cur,conn)
connection_close(cur,conn)

