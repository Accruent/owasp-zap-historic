"""Main module for OWASP ZAP Historic application."""
import random
import string
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL, MySQLdb
import bcrypt
from .args import parse_options

app = Flask(__name__, template_folder='templates')
mysql = MySQL(app)


@app.route('/', methods=['GET'])
def index():
    """render index.html page"""
    cursor = mysql.connection.cursor()
    use_db(cursor, "owaspzaphistoric")
    cursor.execute("select * from TB_PROJECT ORDER BY Project_Name ASC;")
    data = cursor.fetchall()
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
    # use_db(cursor, "robothistoric")
    cursor.execute("DELETE FROM owaspzaphistoric.TB_PROJECT WHERE Project_Name='%s';" % db)
    mysql.connection.commit()
    return redirect(url_for('index'))


@app.route('/login', methods=["GET", "POST"])
def login():
    """Login page"""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password'].encode('utf-8')

        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        use_db(curl, "accounts")
        curl.execute("SELECT * FROM TB_USERS WHERE email=%s", (email,))
        user = curl.fetchone()
        curl.close()

        if len(user) > 0:
            if bcrypt.hashpw(password, user["password"].encode('utf-8')) == \
                    user["password"].encode('utf-8'):
                session['name'] = user['name']
                session['email'] = user['email']
                return redirect(url_for('index'))
            else:
                return redirect("/login")
        else:
            return redirect("/login")
    else:
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

        cur = mysql.connection.cursor()
        use_db(cur, "accounts")
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
                "Total_Executions, Recent_High, Recent_Medium, Recent_Low, Recent_Informational) "
                "VALUES (0, '%s', '%s', '%s', 0, 0, NOW(), NOW(), 0, 0, 0, 0, 0);" %
                (db_name, db_desc, db_image))
            # create tables in created database
            use_db(cursor, db_name)
            cursor.execute(
                "Create table TB_EXECUTION ( Execution_Id INT NOT NULL auto_increment primary key, "
                "Environment TEXT, Scan_Type TEXT, Execution_Date DATETIME, High_Alerts INT, "
                "Medium_Alerts INT, Low_ALerts INT, Informational_Alerts INT, URL_Link TEXT);")
            cursor.execute(
                "Create table TB_ALERTS ( Alert_Id INT NOT NULL auto_increment primary key, "
                "Execution_Id INT, Alert_Level TEXT, Alert_Type TEXT, URLS_Affected INT);")
            mysql.connection.commit()
        except Exception as exc:
            print(str(exc))

        finally:
            return redirect(url_for('index'))
    else:
        return render_template('newdb.html')


@app.route('/<db>/dashboard', methods=['GET'])
def dashboard(db):
    """Project dashboard page"""
    cursor = mysql.connection.cursor()
    use_db(cursor, db)

    cursor.execute("SELECT COUNT(Execution_Id) from TB_EXECUTION;")
    results_data = cursor.fetchall()
    cursor.execute("SELECT COUNT(Alert_Id) from TB_ALERTS;")
    alert_results_data = cursor.fetchall()

    if results_data[0][0] > 0 and alert_results_data[0][0] > 0:

        cursor.execute("select COUNT(*), ifnull(SUM(URLS_Affected), 0) from tb_alerts where "
                       "Alert_Level = 'High' and Execution_Id in (select MAX(Execution_Id) from "
                       "tb_execution);")
        high_last_exe_data = cursor.fetchall()

        cursor.execute(
            "select round(min(Alerts)), round(avg(Alerts),2), max(Alerts) from (select High_Alerts "
            "as Alerts from TB_EXECUTION group by execution_id) as custom;")
        high_overall_data = cursor.fetchall()
        print(high_overall_data)

        cursor.execute(
            "select min(URLS), round(avg(URLS),2), max(URLS) from (select "
            "Execution_ID, sum(Total) as URLS from (select Execution_Id, sum(URLS_Affected) "
            "'Total' from tb_alerts where Alert_Level = 'High' group by Execution_Id "
            "UNION (SELECT Execution_Id,  0 'TOTAL' from tb_alerts)) as custom group by "
            "Execution_Id) as custom2;")
        high_urls_data = cursor.fetchall()

        cursor.execute("select COUNT(*), ifnull(SUM(URLS_Affected), 0) from tb_alerts where "
                       "Alert_Level = 'Medium' and Execution_Id in (select MAX(Execution_Id) from "
                       "tb_execution);")
        medium_last_exe_data = cursor.fetchall()

        cursor.execute(
            "select round(min(Alerts)), round(avg(Alerts),2), max(Alerts) from "
            "(select Medium_Alerts as Alerts from TB_EXECUTION group by execution_id)"
            " as custom;")
        medium_overall_data = cursor.fetchall()

        cursor.execute(
            "select min(URLS), round(avg(URLS),2), max(URLS) from (select "
            "Execution_ID, sum(Total) as URLS from (select Execution_Id, sum(URLS_Affected) "
            "'Total' from tb_alerts where Alert_Level = 'Medium' group by Execution_Id "
            "UNION (SELECT Execution_Id,  0 'TOTAL' from tb_alerts)) as custom group by "
            "Execution_Id) as custom2;")
        medium_urls_data = cursor.fetchall()

        cursor.execute("select COUNT(*), ifnull(SUM(URLS_Affected),0) from tb_alerts where "
                       "Alert_Level = 'Low' and Execution_Id in (select MAX(Execution_Id) from "
                       "tb_execution);")
        low_last_exe_data = cursor.fetchall()

        cursor.execute(
            "select round(min(Alerts)), round(avg(Alerts),2), max(Alerts) from "
            "(select Low_Alerts as Alerts from TB_EXECUTION group by execution_id)"
            " as custom;")
        low_overall_data = cursor.fetchall()

        cursor.execute(
            "select min(URLS), round(avg(URLS),2), max(URLS) from (select "
            "Execution_ID, sum(Total) as URLS from (select Execution_Id, sum(URLS_Affected) "
            "'Total' from tb_alerts where Alert_Level = 'Low' group by Execution_Id "
            "UNION (SELECT Execution_Id,  0 'TOTAL' from tb_alerts)) as custom group by "
            "Execution_Id) as custom2;")
        low_urls_data = cursor.fetchall()

        cursor.execute("select COUNT(*), ifnull(SUM(URLS_Affected),0) from tb_alerts where "
                       "Alert_Level = 'Informational' and Execution_Id in (select MAX(Execution_Id)"
                       " from tb_execution);")
        info_last_exe_data = cursor.fetchall()

        cursor.execute(
            "select round(min(Alerts)), round(avg(Alerts),2), max(Alerts) from "
            "(select Informational_Alerts as Alerts from TB_EXECUTION group by execution_id)"
            " as custom;")
        info_overall_data = cursor.fetchall()

        cursor.execute(
            "select min(URLS), round(avg(URLS),2), max(URLS) from (select "
            "Execution_ID, sum(Total) as URLS from (select Execution_Id, sum(URLS_Affected) "
            "'Total' from tb_alerts where Alert_Level = 'Informational' group by Execution_Id "
            "UNION (SELECT Execution_Id,  0 'TOTAL' from tb_alerts)) as custom group by "
            "Execution_Id) as custom2;")
        info_urls_data = cursor.fetchall()

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
                               results_data=results_data,
                               db_name=db)

    else:
        return redirect(url_for('redirect_url'))


def use_db(cursor, db_name):
    """method to switch db"""
    cursor.execute("USE %s;" % db_name)


def sort_tests(data_list):
    """Test sorting method."""
    out = {}
    for elem in data_list:
        try:
            out[elem[1]].extend(elem[2:])
        except KeyError:
            out[elem[1]] = list(elem)
    return [tuple(values) for values in out.values()]


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
