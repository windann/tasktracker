import pymysql
import datetime


class Connection:

    def __init__(self, token):
        conn = pymysql.connect(user='tasktracker_user', password='password',
                               host='127.0.0.1',
                               database='tasktracker_db',
                               charset='utf8'
                               )
        self.cur = self.conn.cursor()
        self.user_token = token

    def close_connection(self):
        self.cur.close()
        self.conn.close()

    def find_sub_task(self,base_task):
        sql_query = "select b.name,  b.status from task as a INNER JOIN task AS b ON a.taskid = b.base_task_id WHERE a.name = '{}';".format(base_task)
        self.cur.execute(sql_query)
        return [sub_task[0] for sub_task in self.cur]

    def add_task(self, category, name, base_task_id = None):

        user_task_list_sql_query = "SELECT name FROM task WHERE user_token = '{}'".format(self.user_token)
        self.cur.execute(user_task_list_sql_query)
        user_task_list = [sub_task[0] for sub_task in self.cur]

        if name in user_task_list:
            print('Такая задача уже есть в списке!')
            return

        date = datetime.datetime.now()
        status = 'created'

        category_id_sql_query = "SELECT idtype FROM type WHERE type_name = '{}'".format(category)
        self.cur.execute(category_id_sql_query)
        category_id = self.cur.fetchone()[0]

        taskid_sql_query = "SELECT COUNT(1) FROM task"
        self.cur.execute(taskid_sql_query)
        task_id = self.cur.fetchone()[0] + 1

        if base_task_id is None:
            base_task_id = 'null'

        sql_query = "INSERT INTO task(taskid, date, status, name, type, user_token, base_task_id) VALUES({},'{}','{}','{}',{},'{}',{})".format(
                task_id,
                date, status, name, category_id, self.user_token, base_task_id)


        self.cur.execute(sql_query)
        self.conn.commit()

    def set_task_in_progress(self, task_name):
        tasks_in = self.find_sub_task(task_name)

        if tasks_in:
            for task in tasks_in:
                sql = "UPDATE task SET status = 'in progress' WHERE name = '{}' AND user_token = '{}';".format(task,self.user_token)
                self.cur.execute(sql)

        sql_query = "UPDATE task SET status = 'in progress' WHERE name = '{}' AND user_token = '{}';".format(task_name, self.user_token)

        self.cur.execute(sql_query)
        self.conn.commit()

    def set_task_done(self, task_name):
        tasks_in = self.find_sub_task(task_name)

        if tasks_in:
            for task in tasks_in:
                sql_query = "UPDATE task SET status = 'done' WHERE name = '{}' AND user_token = '{}';".format(task,self.user_token)
                self.cur.execute(sql_query)

        sql_query = "UPDATE task SET status = 'done' WHERE name = '{}' AND user_token = '{}';".format(task_name, self.user_token)

        self.cur.execute(sql_query)
        self.conn.commit()

    def get_task_status(self, task_name):
        sql_query = "SELECT status FROM task WHERE name = '{}' AND user_token = '{}';".format(task_name, self.user_token)
        self.cur.execute(sql_query)
        try:
            status = self.cur.fetchone()[0]
            return status
        except TypeError:
            print('Задача не найдена')