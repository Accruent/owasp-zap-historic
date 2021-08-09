"""Main module for OWASP ZAP Historic application."""
import random
import string
import datetime
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL, MySQLdb
import bcrypt
import pytz
from .args import parse_options

app = Flask(__name__, template_folder='templates')
mysql = MySQL(app)
CENTRAL = pytz.timezone('US/Central')


@app.route('/', methods=['GET'])
def index():
    """render index.html page"""
    cursor = use_db("owaspzaphistoric")
    cursor.execute("select *, UPPER(LEFT(Environment, 35)) from TB_PROJECT ORDER BY Project_Name "
                   "ASC;")
    data = cursor.fetchall()
    data = convert_utc_to_cst(data)
    return render_template('index.html', data=data)


@app.route('/redirect')
def redirect_url():
    """redirect page"""
    return render_template('redirect.html')


@app.route('/<db>/deldbconf', methods=['GET'])
def delete_db_conf(db):
    """Confirm deletion of a project page"""
    return render_template('deldbconf.html', db_name=db)


@app.route('/<db>/delete', methods=['GET'])
def delete_db(db):
    """Actual deletion of project"""
    cursor = mysql.connection.cursor()
    cursor.execute("DROP DATABASE %s;" % db)
    cursor.execute("DELETE FROM owaspzaphistoric.TB_PROJECT WHERE Project_Name='%s';" % db)
    mysql.connection.commit()
    return redirect(url_for('index'))


@app.route('/login', methods=["GET", "POST"])
def login():
    """Login page"""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        curl = use_db("accounts", True)
        curl.execute("SELECT * FROM TB_USERS WHERE email=%s", (email,))
        user = curl.fetchone()
        curl.close()

        if len(user) > 0:
            if bcrypt.hashpw(password, user["password"].encode('utf-8')) == \
                    user["password"].encode('utf-8'):
                session['name'] = user['name']
                session['email'] = user['email']
                return redirect(url_for('index'))
            return redirect("/login")
        return redirect("/login")
    return render_template("login.html")


@app.route('/logout', methods=["GET", "POST"])
def logout():
    """Logout page"""
    session.clear()
    return redirect(url_for('index'))


@app.route('/register', methods=["GET", "POST"])
def register():
    """Register a new user page"""
    if request.method == 'GET':
        return render_template("register.html")
    else:
        name = request.form['name']
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        hash_password = bcrypt.hashpw(password, bcrypt.gensalt())
        cur = use_db("accounts", True)
        cur.execute("INSERT INTO TB_USERS (name, email, password) VALUES (%s,%s,%s)",
                    (name, email, hash_password,))
        mysql.connection.commit()
        session['name'] = request.form['name']
        session['email'] = request.form['email']
        return redirect(url_for('index'))


@app.route('/newdb', methods=['GET', 'POST'])
def add_db():
    """Add a new project page"""
    if request.method == "POST":
        db_name = request.form['dbname']
        db_desc = request.form['dbdesc']
        db_image = request.form['dbimage']
        cursor = mysql.connection.cursor()

        try:
            # create new database for project
            cursor.execute("Create DATABASE %s;" % db_name)
            # update created database info in robothistoric.TB_PROJECT table
            cursor.execute(
                "INSERT INTO owaspzaphistoric.TB_PROJECT ( Project_Id, Project_Name, Project_Desc, "
                "Project_Image, Environment, Scan_Type, Created_Date, Last_Updated, "
                "Total_Executions, Recent_High, Recent_Medium, Recent_Low, Recent_Informational, "
                "Recent_False, Version) VALUES (0, '%s', '%s', '%s', 0, 0, NOW(), NOW(), 0, 0, 0, "
                "0, 0, 0, 0);" % (db_name, db_desc, db_image))
            # create tables in created database
            cursor = use_db(db_name)
            cursor.execute(
                "Create table TB_EXECUTION ( Execution_Id INT NOT NULL auto_increment primary key, "
                "Environment TEXT, Scan_Type TEXT, Execution_Date DATETIME, High_Alerts INT, "
                "Medium_Alerts INT, Low_ALerts INT, Informational_Alerts INT, False_Alerts INT, "
                "URL_Link TEXT, Version TEXT);")
            cursor.execute(
                "Create table TB_ALERTS ( Alert_Id INT NOT NULL auto_increment primary key, "
                "Execution_Id INT, Alert_Level TEXT, Alert_Type TEXT, URLS_Affected INT);")
            mysql.connection.commit()
        except Exception as exc:
            print(str(exc))

        finally:
            return redirect(url_for('index'))
    return render_template('newdb.html')


@app.route('/<db>/dashboard', methods=['GET'])
def dashboard(db):
    """Project dashboard page"""
    cursor = use_db(db)

    cursor.execute("SELECT COUNT(Execution_Id) from TB_EXECUTION;")
    results_data = cursor.fetchall()
    cursor.execute("SELECT COUNT(Alert_Id) from TB_ALERTS;")
    alert_results_data = cursor.fetchall()

    if results_data[0][0] > 0 and alert_results_data[0][0] > 0:

        cursor.execute("select COUNT(*), ifnull(SUM(URLS_Affected), 0) from TB_ALERTS where "
                       "Alert_Level = 'High' and Execution_Id in (select MAX(Execution_Id) from "
                       "TB_EXECUTION);")
        high_last_exe_data = cursor.fetchall()

        cursor.execute(
            "select round(min(Alerts)), round(avg(Alerts),2), max(Alerts) from (select High_Alerts "
            "as Alerts from TB_EXECUTION group by execution_id) as custom;")
        high_overall_data = cursor.fetchall()

        cursor.execute(
            "select min(URLS), round(avg(URLS),2), max(URLS) from (select "
            "Execution_ID, sum(Total) as URLS from (select Execution_Id, sum(URLS_Affected) "
            "'Total' from TB_ALERTS where Alert_Level = 'High' group by Execution_Id "
            "UNION (SELECT Execution_Id,  0 'TOTAL' from TB_ALERTS)) as custom group by "
            "Execution_Id) as custom2;")
        high_urls_data = cursor.fetchall()

        cursor.execute("select COUNT(*), ifnull(SUM(URLS_Affected), 0) from TB_ALERTS where "
                       "Alert_Level = 'Medium' and Execution_Id in (select MAX(Execution_Id) from "
                       "TB_EXECUTION);")
        medium_last_exe_data = cursor.fetchall()

        cursor.execute(
            "select round(min(Alerts)), round(avg(Alerts),2), max(Alerts) from "
            "(select Medium_Alerts as Alerts from TB_EXECUTION group by execution_id)"
            " as custom;")
        medium_overall_data = cursor.fetchall()

        cursor.execute(
            "select min(URLS), round(avg(URLS),2), max(URLS) from (select "
            "Execution_ID, sum(Total) as URLS from (select Execution_Id, sum(URLS_Affected) "
            "'Total' from TB_ALERTS where Alert_Level = 'Medium' group by Execution_Id "
            "UNION (SELECT Execution_Id,  0 'TOTAL' from TB_ALERTS)) as custom group by "
            "Execution_Id) as custom2;")
        medium_urls_data = cursor.fetchall()

        cursor.execute("select COUNT(*), ifnull(SUM(URLS_Affected),0) from TB_ALERTS where "
                       "Alert_Level = 'Low' and Execution_Id in (select MAX(Execution_Id) from "
                       "TB_EXECUTION);")
        low_last_exe_data = cursor.fetchall()

        cursor.execute(
            "select round(min(Alerts)), round(avg(Alerts),2), max(Alerts) from "
            "(select Low_Alerts as Alerts from TB_EXECUTION group by execution_id)"
            " as custom;")
        low_overall_data = cursor.fetchall()

        cursor.execute(
            "select min(URLS), round(avg(URLS),2), max(URLS) from (select "
            "Execution_ID, sum(Total) as URLS from (select Execution_Id, sum(URLS_Affected) "
            "'Total' from TB_ALERTS where Alert_Level = 'Low' group by Execution_Id "
            "UNION (SELECT Execution_Id,  0 'TOTAL' from TB_ALERTS)) as custom group by "
            "Execution_Id) as custom2;")
        low_urls_data = cursor.fetchall()

        cursor.execute("select COUNT(*), ifnull(SUM(URLS_Affected),0) from TB_ALERTS where "
                       "Alert_Level = 'Informational' and Execution_Id in (select MAX(Execution_Id)"
                       " from TB_EXECUTION);")
        info_last_exe_data = cursor.fetchall()

        cursor.execute(
            "select round(min(Alerts)), round(avg(Alerts),2), max(Alerts) from "
            "(select Informational_Alerts as Alerts from TB_EXECUTION group by execution_id)"
            " as custom;")
        info_overall_data = cursor.fetchall()

        cursor.execute(
            "select min(URLS), round(avg(URLS),2), max(URLS) from (select "
            "Execution_ID, sum(Total) as URLS from (select Execution_Id, sum(URLS_Affected) "
            "'Total' from TB_ALERTS where Alert_Level = 'Informational' group by Execution_Id "
            "UNION (SELECT Execution_Id,  0 'TOTAL' from TB_ALERTS)) as custom group by "
            "Execution_Id) as custom2;")
        info_urls_data = cursor.fetchall()

        cursor.execute("select COUNT(*), ifnull(SUM(URLS_Affected),0) from TB_ALERTS where "
                       "Alert_Level = 'False Positive' and Execution_Id in (select MAX(Execution_Id)"
                       " from TB_EXECUTION);")
        false_last_exe_data = cursor.fetchall()

        cursor.execute(
            "select round(min(Alerts)), round(avg(Alerts),2), max(Alerts) from "
            "(select False_Alerts as Alerts from TB_EXECUTION group by execution_id)"
            " as custom;")
        false_overall_data = cursor.fetchall()

        cursor.execute(
            "select min(URLS), round(avg(URLS),2), max(URLS) from (select "
            "Execution_ID, sum(Total) as URLS from (select Execution_Id, sum(URLS_Affected) "
            "'Total' from TB_ALERTS where Alert_Level = 'False Positive' group by Execution_Id "
            "UNION (SELECT Execution_Id,  0 'TOTAL' from TB_ALERTS)) as custom group by "
            "Execution_Id) as custom2;")
        false_urls_data = cursor.fetchall()

        return render_template('dashboard.html', high_last_exe_data=high_last_exe_data,
                               high_overall_data=high_overall_data,
                               high_urls_data=high_urls_data,
                               medium_last_exe_data=medium_last_exe_data,
                               medium_overall_data=medium_overall_data,
                               medium_urls_data=medium_urls_data,
                               low_last_exe_data=low_last_exe_data,
                               low_overall_data=low_overall_data,
                               low_urls_data=low_urls_data,
                               info_last_exe_data=info_last_exe_data,
                               info_overall_data=info_overall_data,
                               info_urls_data=info_urls_data,
                               false_last_exe_data=false_last_exe_data,
                               false_overall_data=false_overall_data,
                               false_urls_data=false_urls_data,
                               results_data=results_data,
                               db_name=db)

    return redirect(url_for('redirect_url'))


@app.route('/<db>/ehistoric', methods=['GET'])
def ehistoric(db):
    """dashboard page"""
    cursor = use_db(db)
    cursor.execute("SELECT * from TB_EXECUTION order by Execution_Id desc LIMIT 500;")
    data = cursor.fetchall()
    data = convert_utc_to_cst(data)
    return render_template('ehistoric.html', data=data, db_name=db)


@app.route('/<db>/alerts/<eid>', methods=['GET'])
def metrics(db, eid):
    """alert breakdown page"""
    cursor = use_db(db)
    # Get testcase results of execution id
    cursor.execute("SELECT * from TB_ALERTS WHERE Execution_Id=%s;" % eid)
    alerts_data = cursor.fetchall()
    # get project image
    cursor.execute("SELECT Project_Image from owaspzaphistoric.TB_PROJECT WHERE "
                   "Project_Name='%s';" % db)
    project_image = cursor.fetchall()
    # get URL Link
    cursor.execute("SELECT URL_Link from TB_EXECUTION WHERE Execution_Id=%s;" % eid)
    url_link = cursor.fetchall()
    return render_template('alerts.html', alerts_data=alerts_data, eid=eid, url_link=url_link,
                           project_image=project_image[0][0])


@app.route('/<db>/allalerts', methods=['GET'])
def tmetrics(db):
    """display all alerts for a project"""
    cursor = use_db(db)
    # Get all from TB_Alerts for Project
    cursor.execute("SELECT e.Execution_Id, a.Alert_Id, e.Environment, e.Scan_Type, a.Alert_Level, "
                   "a.Alert_Type, a.URLS_Affected, e.Version from TB_EXECUTION e INNER JOIN "
                   "TB_ALERTS a on a.Execution_ID = e.Execution_Id order by e.Execution_ID DESC, "
                   "a.Alert_Id ASC;")
    data = cursor.fetchall()
    return render_template('allalerts.html', data=data, db_name=db)


@app.route('/<db>/deleconf/<eid>', methods=['GET'])
def delete_eid_conf(db, eid):
    """confirmation page to delete an execution"""
    return render_template('deleconf.html', db_name=db, eid=eid)


@app.route('/<db>/edelete/<eid>', methods=['GET'])
def delete_eid(db, eid):
    """delete page for execution deletion"""
    cursor = use_db(db)
    # remove execution from tables: execution, suite, test
    cursor.execute("DELETE FROM TB_EXECUTION WHERE Execution_Id='%s';" % eid)
    cursor.execute("DELETE FROM TB_ALERTS WHERE Execution_Id='%s';" % eid)
    # get latest execution info
    cursor.execute("SELECT Environment, Scan_Type, High_Alerts, Medium_Alerts, Low_Alerts, "
                   "Informational_ALerts from TB_EXECUTION ORDER BY Execution_Id DESC LIMIT 1;")
    data = cursor.fetchall()
    # get no. of executions
    cursor.execute("SELECT COUNT(*) from TB_EXECUTION;")
    exe_data = cursor.fetchall()
    # handle if only execution for project was just deleted
    if int(exe_data[0][0]) == 0:
        data = [[0, 0, 0, 0, 0, 0]]
    print(data[0])
    # update robothistoric project
    cursor.execute("UPDATE owaspzaphistoric.TB_PROJECT SET Total_Executions=%s, Environment='%s', "
                   "Scan_Type='%s', Last_Updated=now(), Recent_High=%s, Recent_Medium=%s, "
                   "Recent_Low=%s, Recent_Informational=%s WHERE Project_Name='%s';"
                   % (int(exe_data[0][0]), data[0][0], data[0][1], data[0][2], data[0][3],
                      data[0][4], data[0][5], db))
    # commit changes
    mysql.connection.commit()
    return redirect(url_for('ehistoric', db=db))


def use_db(db_name, use_dict=False):
    """method to switch db"""
    if use_dict:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    else:
        cursor = mysql.connection.cursor()
    cursor.execute("USE %s;" % db_name)
    return cursor


def convert_utc_to_cst(items):
    """This method takes a list of tuples and converts any datetime to CST."""
    new_list = []
    for item in items:
        item_list = list(item)
        this_list = []
        for itemb in item_list:
            if isinstance(itemb, datetime.datetime):
                itemb = itemb.replace(tzinfo=datetime.timezone.utc)
                conv_date = itemb.astimezone(CENTRAL)
                this_list.append(conv_date)
            else:
                this_list.append(itemb)
        new_list.append(tuple(this_list))
    return new_list


def main():
    """Main application method"""
    args = parse_options()

    app.config['MYSQL_HOST'] = args.sqlhost
    app.config['MYSQL_PORT'] = int(args.sqlport)
    app.config['MYSQL_USER'] = args.username
    app.config['MYSQL_PASSWORD'] = args.password
    # This cause issues
    # app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
    app.config['auth_plugin'] = 'mysql_native_password'

    letters = string.ascii_letters + string.digits
    salt = ''.join(random.choice(letters) for i in range(12))
    app.secret_key = salt

    app.run(host=args.apphost)
