import pymysql
import datetime


class Connection:

    def __init__(self):

        self.conn = pymysql.connect(user='tasktracker_user', password='password',
                               host='127.0.0.1',
                               database='tasktracker_db',
                               charset='utf8'
                               )
        self.cur = self.conn.cursor()

    def close_connection(self):
        self.cur.close()
        self.conn.close()

    def find_sub_task(self, base_task, user_token):
        sql_query = "select b.taskid, b.name, b.status from task as a INNER JOIN task AS b ON a.taskid = b.base_task_id WHERE a.name = '{}' and b.user_token = '{}';".format(base_task,user_token)
        self.cur.execute(sql_query)
        return [str(sub_task[0]) for sub_task in self.cur]

    def add_task(self, category, name, base_task_id='null',user_token='null'):

        date = datetime.datetime.now()
        # 1 - created 2 - in progress 3 - done
        status = 1

        category_id_sql_query = "SELECT idtype FROM type WHERE type_name = '{}'".format(category)
        self.cur.execute(category_id_sql_query)
        category_id = self.cur.fetchone()[0]

        if user_token == 'null':
            sql_query = "INSERT INTO task(date, status, name, type, user_token, base_task_id) VALUES('{}',{},'{}',{},{},{})".format(
                date, status, name, category_id, user_token, base_task_id)

        else:
            sql_query = "INSERT INTO task(date, status, name, type, user_token, base_task_id) VALUES('{}',{},'{}',{},'{}',{})".format(
                date, status, name, category_id, user_token, base_task_id)

        try:
            self.cur.execute(sql_query)
        except pymysql.err.IntegrityError:
            print('У вас уже поставлена такая задача')

        self.conn.commit()

    def set_task_status(self, task_name, user_token, status):
        tasks_in = self.find_sub_task(task_name,user_token)

        id_users_task_sql_query = "SELECT taskid FROM task WHERE name = '{}' AND user_token = '{}';".format(task_name,user_token)
        self.cur.execute(id_users_task_sql_query)
        base_task_id = str(self.cur.fetchone()[0])
        tasks_in.append(base_task_id)

        if status == 'in process':
            status_id = 2
        elif status == 'done':
            status_id = 3

        sql = "UPDATE task SET status = {} WHERE taskid IN({});".format(status_id,','.join(tasks_in), user_token)
        self.cur.execute(sql)
        self.conn.commit()

    def get_task_status(self, task_name, user_token):
        sql_query = "SELECT status FROM task WHERE name = '{}' AND user_token = '{}';".format(task_name, user_token)
        self.cur.execute(sql_query)

        try:
            status_id = self.cur.fetchone()[0]
            print(status_id)

            if status_id == 1:
                status = 'created'
            elif status_id == 2:
                status = 'in progress'
            elif status_id == 3:
                status = 'done'
            return status
        except TypeError:
            print('Задача не найдена')