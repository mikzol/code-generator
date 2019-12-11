from flask import Flask
from flask_restful import Resource, Api, reqparse
from sqlalchemy import create_engine
import sqlite3 
from sqlite3 import Error
import random
import MySQLdb


app = Flask(__name__)
api = Api(app)


def create_connection():
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = MySQLdb.connect(host="162.241.224.212", user="vishiuhc_api", passwd="-?n%oOp4JeMA", db="vishiuhc_WPRMG")
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
        db_con = create_connection()
        db_cursor = db_con.cursor()
        query = db_cursor.execute("select * from coupons_vouchers") # This line performs query and returns json result
        coupons = db_cursor.fetchall()
        db_con.commit()
        db_con.close()
        return {'coupons': [i[3] for i in coupons]} # Fetches first column that is Coupon ID
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('code_type')
        parser.add_argument('discount_val')
        parser.add_argument('code_len')
        parser.add_argument('attributed_to')
        args = parser.parse_args()

        code = generate_code()
        if args['code_len'] is not None:
            code = generate_code(args['code_len'])

        db_con = create_connection()
        db_cursor = db_con.cursor()
        query = db_cursor.execute("insert into coupons_vouchers values(null, '{0}', '{1}', '{2}', '{3}', NOW(), NOW() + INTERVAL 1 YEAR)".format(args['code_type'], args['discount_val'], code, args['attributed_to']))
        db_con.commit()
        db_con.close()
        return {'status': 'success'}


api.add_resource(Coupons_Vouchers, '/generate')


if __name__ == '__main__':
    code_table = """ CREATE TABLE IF NOT EXISTS coupons_vouchers (
                                        id integer PRIMARY KEY AUTO_INCREMENT,
                                        code_type text NOT NULL,
                                        discount_val text NOT NULL,
                                        code text NOT NULL,
                                        attributed_to text NOT NULL,
                                        start_date DATETIME NOT NULL,
                                        end_date DATETIME NOT NULL
                                    ); """

    conn = create_connection()
    create_table(conn, code_table)
    app.run()