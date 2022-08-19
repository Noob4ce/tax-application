from pprint import pprint

from configparser import ConfigParser

import mysql.connector


# get config data

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


# calculators

def calc_fed_tax(gross_income):
    range_1 = 50197
    range_2 = 50195
    range_3 = 55233
    range_4 = 66083

    rate_list = [0.15, 0.205, 0.26, 0.29, 0.33]

    tax_list = [0, 0, 0, 0, 0]

    tax_total = 0

    # append taxable amount of each rate to the list

    if gross_income <= range_1:
        tax_list[0] = gross_income
    elif gross_income <= range_1 + range_2:
        tax_list[0] = range_1
        tax_list[1] = gross_income - range_1
    elif gross_income <= range_1 + range_2 + range_3:
        tax_list[0] = range_1
        tax_list[1] = range_2
        tax_list[2] = gross_income - (range_1 + range_2)
    elif gross_income <= range_1 + range_2 + range_3 + range_4:
        tax_list[0] = range_1
        tax_list[1] = range_2
        tax_list[2] = range_3
        tax_list[3] = gross_income - (range_1 + range_2 + range_3)
    else:
        tax_list[0] = range_1
        tax_list[1] = range_2
        tax_list[2] = range_3
        tax_list[3] = range_4
        tax_list[4] = gross_income - (range_1 + range_2 + range_3 + range_4)

    # multiply each taxable amount by its rate

    i = 0

    for income in tax_list:
        tax_total += income * rate_list[i]
        i += 1

    return round(tax_total, 2)

# same idea here
def calc_on_tax(gross_income):
    range_1 = 46226
    range_2 = 92454
    range_3 = 150000
    range_4 = 220000

    rate_list = [0.0505, 0.0915, 0.1116, 0.1216, 0.1316]

    tax_list = [0, 0, 0, 0, 0]

    tax_total = 0

    if gross_income <= range_1:
        tax_list[0] = gross_income
    elif gross_income <= range_1 + range_2:
        tax_list[0] = range_1
        tax_list[1] = gross_income - range_1
    elif gross_income <= range_1 + range_2 + range_3:
        tax_list[0] = range_1
        tax_list[1] = range_2
        tax_list[2] = gross_income - (range_1 + range_2)
    elif gross_income <= range_1 + range_2 + range_3 + range_4:
        tax_list[0] = range_1
        tax_list[1] = range_2
        tax_list[2] = range_3
        tax_list[3] = gross_income - (range_1 + range_2 + range_3)
    else:
        tax_list[0] = range_1
        tax_list[1] = range_2
        tax_list[2] = range_3
        tax_list[3] = range_4
        tax_list[4] = gross_income - (range_1 + range_2 + range_3 + range_4)

    i = 0

    for income in tax_list:
        tax_total += income * rate_list[i]
        i += 1

    return round(tax_total, 2)


def calc_cpp(gross_income):
    earnings = 0

    rate = 0.057

    max_income = 61400

    if gross_income < max_income:
        earnings += gross_income * rate
    else:
        earnings += max_income * rate

    return round(earnings, 2)


def calc_ei(gross_income):
    earnings = 0

    rate = 0.0158

    max_income = 60300

    if gross_income < max_income:
        earnings += gross_income * rate
    else:
        earnings += max_income * rate

    return round(earnings, 2)


# Retrieve employee data

with open('employee_data.txt', 'r') as retrieved:
    emp_data = retrieved.readlines()

emp_list = []

emp_dict = []

for emp in emp_data:
    e_list_with_slash = emp.splitlines()

    e_list = e_list_with_slash[0].split('\t')

    emp_list.append(e_list)

emp_list.pop(0)


# add an extra ' to the names like O'Conor in order to insert correct value to the database
def validate_name(n):
    name = n

    check = list(name)

    for letter in check:
        if letter == "'":
            i = check.index(letter)
            check.insert(i, "'")
            name = ''.join(check)
            return name
    return name


# create a dict by using arguments
def create_emp_dict(emp_id, fname, lname, e_mail, password, income):
    first_name = validate_name(fname)

    last_name = validate_name(lname)

    gross_income = float(income)

    fedtax = calc_fed_tax(gross_income)

    ontax = calc_on_tax(gross_income)

    cpp = calc_cpp(gross_income)

    ei = calc_ei(gross_income)

    net_income = round((gross_income - fedtax - ontax - cpp - ei), 2)

    new_emp = {
        'id': int(emp_id),
        'Fname': first_name,
        'Lname': last_name,
        'email': e_mail,
        'password': password,
        'gross_income': gross_income,
        'fed_tax': fedtax,
        'on_tax': ontax,
        'cpp': cpp,
        'ei': ei,
        'net_income': net_income}

    return new_emp


for emp in emp_list:
    emp_dict.append(create_emp_dict(emp[0], emp[1], emp[2], emp[3], emp[4], emp[5]))

# insert records to database
user = read_DB_config('config.ini', 'mysql')

connection = mysql.connector.MySQLConnection(**user)

cursor = connection.cursor()


def insert_emp(emp_id, fname, lname, e_mail, password,
               gross_income, fed_tax, on_tax, cpp, ei, net_income):
    cursor.execute(f"insert into employees (id, "
                   f"FName, LName, email, password, "
                   f"gross_income, fed_tax, on_tax, cpp, ei, net_income)"
                   f" values ('{emp_id}','{fname}', '{lname}', '{e_mail}', '{password}',"
                   f" '{gross_income}', '{fed_tax}', '{on_tax}', '{cpp}', '{ei}', '{net_income}')")

    connection.commit()


for e in emp_dict:
    insert_emp(e['id'], e['Fname'], e['Lname'], e['email'], e['password'],
               e['gross_income'], e['fed_tax'], e['on_tax'], e['cpp'], e['ei'], e['net_income'])

# This is that little buggy name that caused many troubles lol

# for e in emp_dict:
#     if e['email'] == 'eofallon1o@wikispaces.com':
#         print(e)
