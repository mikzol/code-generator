from flask import Flask, request, jsonify
from flask_restful import Resource, Api, reqparse
from sqlalchemy import create_engine
from json import dumps
import sqlite3
from sqlite3 import Error
import random


db_connect = create_engine('sqlite:///database.db') # 'mysql://username:pass@localhost/'
app = Flask(__name__)
api = Api(app)


def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return conn


def create_table(conn, code_table_sql):
    """ create a table from the code_table_sql statement
    :param conn: Connection object
    :param code_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(code_table_sql)
    except Error as e:
        print(e)


def generate_code(len=5):
    SYMBOLS = list('0123456789ABCDEFGHJKLMNPQRTUVWXY')
    code = ''
    for j in range(len):
        code += random.choice(SYMBOLS)
    return code


class Coupons_Vouchers(Resource):
    def get(self):
        conn = db_connect.connect() # connect to database
        query = conn.execute("select * from coupons_vouchers") # This line performs query and returns json result
        return {'coupons': [i[0] for i in query.cursor.fetchall()]} # Fetches first column that is Coupon ID
    def post(self):
        conn = db_connect.connect() # connect to database
        parser = reqparse.RequestParser()
        parser.add_argument('code_type')
        parser.add_argument('discount_val')
        parser.add_argument('code_len')
        parser.add_argument('attributed_to')
        args = parser.parse_args()

        code = generate_code()
        if args['code_len'] is not None:
            code = generate_code(args['code_len'])

        query = conn.execute("insert into coupons_vouchers values(null, '{0}', '{1}', '{2}')".format(args['code_type'], args['discount_val'], code))
        return {'status': 'success'}


api.add_resource(Coupons_Vouchers, '/generate') # 


if __name__ == '__main__':
    database = r"/home/markmanu/task/jean/database.db"
    code_table = """ CREATE TABLE IF NOT EXISTS coupons_vouchers (
                                        id integer PRIMARY KEY,
                                        code_type text NOT NULL,
                                        discount_val text NOT NULL,
                                        code text NOT NULL,
                                        attributed_to text NOT NULL
                                    ); """

    conn = create_connection(database)
    create_table(conn, code_table)
    app.run()