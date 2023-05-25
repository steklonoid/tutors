from quart import Quart, render_template, request, session, redirect, url_for, make_response
import mysql.connector
import aiomysql
import asyncio

rolesstr = ('Гость', 'Репетитор', 'Клиент')
roles = ('', 'tutor', 'client')

app = Quart(__name__)
app.secret_key = 'abcdef'
# db = mysql.connector.connect(
#     host="localhost",
#     user="root",
#     password="12345678",
#     database="tutor"
# )

async def connect_to_database():
    connection = await aiomysql.connect(
        host="localhost",
        user="root",
        password="12345678",
        db="tutor")
    return connection

@app.route('/')
async def index():
    data = {}
    if 'login' in session:
        authorized = True
        usertypestr = rolesstr[session['login'][2]]
        usertype = roles[session['login'][2]]
        name = session['login'][3]
        if usertype == 'client':
            data['head'] = {'authorized': authorized, 'usertypestr': usertypestr, 'usertype': usertype, 'name': name}
            data['reqlist'] = {'id': 0}
        else:
            data['head'] = {'authorized': authorized, 'usertypestr': usertypestr, 'usertype': usertype, 'name': name}
            data['reqlist'] = {'id': 0}
    else:
        authorized = False
        usertypestr = rolesstr[0]
        usertype = roles[0]
        name = ''
        data['head'] = {'authorized': authorized, 'usertypestr': usertypestr, 'usertype': usertype, 'name': name}
        data['reqlist'] = {'id': 0}
    return await render_template('index.html', data=data)

@app.route('/register')
async def register():
    return await render_template('register.html')

@app.route('/register_client', methods=['GET', 'POST'])
async def register_client():
    if request.method == 'POST':
        form = await request.form
        login = form['login']
        password = form['password']
        name = form['name']
        email = form['email']
        try:
            connection = await connect_to_database()
            cursor = await connection.cursor()
            sql = "INSERT INTO user (login, password, usertype, name, email) VALUES (%s, %s, %s, %s, %s)"
            values = (login, password, 2, name, email)
            await cursor.execute(sql, values)
            userid = await cursor.lastrowid
            sql = "INSERT INTO client (user_id) VALUES (%s)"
            values = [userid]
            await cursor.execute(sql, values)
            await connection.commit()
            await cursor.close()
            connection.close()
            footer = 'Клиент зарегистрирован в базе данных. Можете авторизоваться.'
            return await render_template('register_client.html', footer=footer)
        except mysql.connector.Error as error:
            footer = error.msg
            return await render_template('register_client.html', footer=footer)

    footer = ''
    return await render_template('register_client.html', footer=footer)

@app.route('/register_tutor', methods=['GET', 'POST'])
async def register_tutor():
    if request.method == 'POST':
        form = await request.form
        login = form['login']
        password = form['password']
        name = form['name']
        email = form['email']
        try:
            connection = await connect_to_database()
            cursor = await connection.cursor()
            sql = "INSERT INTO user (login, password, usertype, name, email) VALUES (%s, %s, %s, %s, %s)"
            values = (login, password, 1, name, email)
            await cursor.execute(sql, values)
            userid = await cursor.lastrowid
            sql = "INSERT INTO repetitor (user_id, indeal, hourly_rate) VALUES (%s, %s, %s)"
            values = [userid, 1, 0]
            await cursor.execute(sql, values)
            await connection.commit()
            await cursor.close()
            connection.close()
            footer = 'Репетитор зарегистрирован в базе данных. Можете авторизоваться.'
            return await render_template('register_tutor.html', footer=footer)
        except mysql.connector.Error as error:
            footer = error.msg
            return await render_template('register_tutor.html', footer=footer)

    footer = ''
    return await render_template('register_tutor.html', footer=footer)

@app.route('/login', methods=['GET', 'POST'])
async def login():
    if request.method == 'POST':
        form = await request.form
        login = form['login']
        password = form['password']
        connection = await connect_to_database()
        cursor = await connection.cursor()
        sql = "SELECT id, login, usertype, name FROM user WHERE login = %s AND password = %s"
        values = (login, password)
        await cursor.execute(sql, values)
        user = await cursor.fetchone()
        await cursor.close()
        connection.close()
        if user:
            session['login'] = user
            return redirect(url_for('index'))
        else:
            footer = 'Не верное имя пользователя или пароль'
            return await render_template('login.html', footer=footer)

    footer = ''
    return await render_template('login.html', footer=footer)

@app.route('/logout')
async def logout():
    session.pop('login', None)
    return redirect(url_for('index'))

@app.route('/personal_client')
async def personal_client():
    return await render_template('personal_client.html')

@app.route('/personal_tutor', methods=['GET', 'POST'])
async def personal_tutor():
    if request.method == 'GET':
        connection = await connect_to_database()
        cursor = await connection.cursor()
        sql = "SELECT user.login, user.name, user.email, repetitor.hourly_rate FROM user JOIN repetitor ON user.id = repetitor.user_id WHERE user.id = %s"
        values = [session['login'][0]]
        await cursor.execute(sql, values)
        userdata = await cursor.fetchone()

        sql = "SELECT subject.id, subject.name FROM repetitor_subject JOIN subject ON repetitor_subject.subject_id = subject.id WHERE repetitor_subject.user_id = %s"
        values = [session['login'][0]]
        await cursor.execute(sql, values)
        subjects = set(await cursor.fetchall())

        sql = "SELECT id, name FROM subject"
        await cursor.execute(sql)
        allsubjects = set(await cursor.fetchall()).difference(subjects)

        await cursor.close()
        connection.close()

        data = {'userdata': userdata, 'subjects':subjects, 'allsubjects':allsubjects}
        return await render_template('personal_tutor.html', data=data)
    elif request.method == 'POST':
        connection = await connect_to_database()
        cursor = await connection.cursor()
        sql = "UPDATE user SET name=%s, email=%s WHERE id = %s"
        values = [request.form['name'], request.form['email'], session['login'][0]]
        await cursor.execute(sql, values)
        sql = "UPDATE repetitor SET hourly_rate=%s WHERE user_id = %s"
        values = [request.form['hourly_rate'], session['login'][0]]
        await cursor.execute(sql, values)
        await connection.commit()
        await cursor.close()
        connection.close()

        return await redirect(url_for('personal_tutor'))

@app.route('/add_subject', methods=['GET', 'POST'])
async def add_subject():
    a = await request.form
    subject_id = int(a['subject'])
    connection = await connect_to_database()
    cursor = await connection.cursor()
    sql = "INSERT INTO repetitor_subject (subject_id, user_id) VALUES (%s, %s)"
    values = [subject_id, session['login'][0]]
    await cursor.execute(sql, values)
    await connection.commit()
    await cursor.close()
    connection.close()

    response = make_response()
    response.status_code = 200
    return await response
    # return redirect(url_for('personal_tutor'))

@app.route('/remove_subject', methods=['GET', 'POST'])
async def remove_subject():
    a = await request.form
    subject_id = int(a['subject'])
    connection = await connect_to_database()
    cursor = await connection.cursor()
    sql = "DELETE FROM repetitor_subject WHERE subject_id = %s AND user_id = %s;"
    values = [subject_id, session['login'][0]]
    await cursor.execute(sql, values)
    await connection.commit()
    await cursor.close()
    connection.close()

    response = make_response()
    response.status_code = 200
    return await response
    # return redirect(url_for('personal_tutor'))

if __name__ == '__main__':
    app.run()
