from configparser import ConfigParser

import mysql.connector

import csv


def read_DB_config(filename, section):

    db = {}

    parser = ConfigParser()

    parser.read(filename)

    if parser.has_section(section):
        cons = parser.items(section)
        for con in cons:
            db[con[0]] = con[1]
    else:
        print('No such a section')

    return db


user = read_DB_config('config.ini', 'mysql')

connection = mysql.connector.MySQLConnection(**user)

cursor = connection.cursor()

cursor.execute("select * from employees")

emp_data = cursor.fetchall()


# CSV writing for each row

with open('employees_db.csv', 'w', newline='') as csv_file:
    csvwriter = csv.writer(csv_file)

    header = ['ID', 'First Name', 'Last Name', 'Email', 'Password',
              'Annual Gross Income', 'Federal tax', 'Ontario tax', 'CPP', 'EI', 'Net Income']

    csvwriter.writerow(header)

    for emp in emp_data:
        csvwriter.writerow(emp)
