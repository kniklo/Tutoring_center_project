from quart import Quart, render_template, request, session, redirect, url_for, jsonify
import mysql.connector
import aiomysql
import asyncio
import time

rolesstr = ('Гость', 'Репетитор', 'Клиент')
roles = ('', 'tutor', 'client')
selectedQueryId = -1

app = Quart(__name__)
app.secret_key = 'abcdef'

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
        elif usertype == 'tutor':
            data['head'] = {'authorized': authorized, 'usertypestr': usertypestr, 'usertype': usertype, 'name': name}
    else:
        authorized = False
        usertypestr = rolesstr[0]
        usertype = roles[0]
        name = ''
        data['head'] = {'authorized': authorized, 'usertypestr': usertypestr, 'usertype': usertype, 'name': name}

        connection = await connect_to_database()
        cursor = await connection.cursor()
        sql = "SELECT user.name FROM repetitor JOIN user ON repetitor.user_id = user.id"
        values = []
        await cursor.execute(sql, values)
        repetitors = await cursor.fetchall()
        await cursor.close()
        connection.close()
        data['repetitors'] = repetitors

    return await render_template('index.html', data=data)

@app.route('/add_query', methods=['GET', 'POST'])
async def add_query():
    a = await request.form

    user_id = session['login'][0]
    subject_id = int(a['subject_id'])
    theme = a['theme']
    qtext = a['qtext']

    connection = await connect_to_database()
    cursor = await connection.cursor()
    sql = "INSERT INTO query (user_id, subject_id, theme, text) VALUES (%s, %s, %s, %s)"
    values = (user_id, subject_id, theme, qtext)
    await cursor.execute(sql, values)

    query_id = cursor.lastrowid
    status_id = 0

    sql = "INSERT INTO request (query_id, status_id, time) VALUES (%s, %s, NOW())"
    values = [query_id, status_id]
    await cursor.execute(sql, values)
    await connection.commit()
    await cursor.close()
    connection.close()

    return redirect(url_for('index'))

@app.route('/accept_request', methods=['GET', 'POST'])
async def accept_request():
    a = await request.form

    user_id = session['login'][0]
    request_id = int(a['request_id'])

    connection = await connect_to_database()
    cursor = await connection.cursor()
    sql = "UPDATE request SET status_id = 1, time = NOW(), repetitor_id = %s WHERE id = %s"
    values = [user_id, request_id]
    await cursor.execute(sql, values)
    await connection.commit()
    await cursor.close()
    connection.close()

    return redirect(url_for('index'))

@app.route('/confirm_request', methods=['GET', 'POST'])
async def confirm_request():
    a = await request.form

    request_id = int(a['request_id'])

    connection = await connect_to_database()
    cursor = await connection.cursor()
    sql = "UPDATE request SET status_id = 2, time = NOW() WHERE id = %s"
    values = [request_id]
    await cursor.execute(sql, values)
    await connection.commit()
    await cursor.close()
    connection.close()

    return redirect(url_for('index'))

@app.route('/finish_request', methods=['GET', 'POST'])
async def finish_request():
    a = await request.form

    request_id = int(a['request_id'])

    connection = await connect_to_database()
    cursor = await connection.cursor()
    sql = "UPDATE request SET status_id = 3, time = NOW() WHERE id = %s"
    values = [request_id]
    await cursor.execute(sql, values)
    await connection.commit()
    await cursor.close()
    connection.close()

    return redirect(url_for('index'))

@app.route('/get_tutorrequestlist')
async def get_tutorrequestlist():
    connection = await connect_to_database()
    cursor = await connection.cursor()
    sql = "SELECT " \
          "request.id, " \
          "subject.name, " \
          "query.theme, " \
          "request.status_id, " \
          "request.time " \
          "FROM query JOIN request ON query.id = request.query_id " \
          "JOIN subject ON query.subject_id = subject.id " \
          "WHERE request.status_id = %s AND " \
          "subject_id IN (SELECT subject_id FROM repetitor_subject WHERE user_id = %s)"
    status_id = 0
    user_id = session['login'][0]
    values = [status_id, user_id]
    await cursor.execute(sql, values)
    querylist1 = list(await cursor.fetchall())

    sql = "SELECT " \
          "request.id, " \
          "subject.name, " \
          "query.theme, " \
          "request.status_id, " \
          "request.time " \
          "FROM query JOIN request ON query.id = request.query_id " \
          "JOIN subject ON query.subject_id = subject.id " \
          "WHERE request.repetitor_id = %s"
    user_id = session['login'][0]
    values = [user_id]
    await cursor.execute(sql, values)
    querylist2 = list(await cursor.fetchall())

    await cursor.close()
    connection.close()
    return jsonify({'requestlist': {'t1': querylist1, 't2': querylist2}})

@app.route('/get_clientrequestlist')
async def get_clientrequestlist():
    connection = await connect_to_database()
    cursor = await connection.cursor()
    sql = "SELECT " \
          "request.id, " \
          "subject.name, " \
          "query.theme, " \
          "request.status_id, " \
          "request.time " \
          "FROM query JOIN request ON query.id = request.query_id " \
          "JOIN subject ON query.subject_id = subject.id " \
          "WHERE query.user_id = %s"
    values = [session['login'][0]]
    await cursor.execute(sql, values)
    querylist = list(await cursor.fetchall())
    await cursor.close()
    connection.close()
    return jsonify({'requestlist': querylist})

@app.route('/get_request_details/<int:request_id>', methods=['GET'])
async def get_request_details(request_id):
    connection = await connect_to_database()
    cursor = await connection.cursor()
    sql = "SELECT subject.name, " \
          "query.theme, " \
          "query.text, " \
          "request.status_id " \
          "FROM query " \
          "JOIN request ON request.query_id = query.id " \
          "JOIN subject ON query.subject_id = subject.id " \
          "WHERE request.id = %s"
    values = [request_id]
    await cursor.execute(sql, values)
    query = await cursor.fetchone()
    await cursor.close()
    connection.close()
    return jsonify({'query': query})

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
            userid = cursor.lastrowid
            sql = "INSERT INTO client (user_id) VALUES (%s)"
            values = [userid]
            await cursor.execute(sql, values)
            await connection.commit()
            await cursor.close()
            connection.close()
            footer = 'Клиент зарегистрирован в базе данных. Можете авторизоваться.'
            return await render_template('register_client.html', footer=footer)
        except Exception as error:
            cod = error.args[0]
            if cod == 1062:
                footer = 'Логин уже существует!'
            else:
                footer = error.args[1]
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
            userid = cursor.lastrowid
            sql = "INSERT INTO repetitor (user_id, indeal, hourly_rate) VALUES (%s, %s, %s)"
            values = [userid, 1, 0]
            await cursor.execute(sql, values)
            await connection.commit()
            await cursor.close()
            connection.close()
            footer = 'Репетитор зарегистрирован в базе данных. Можете авторизоваться.'
            return await render_template('register_tutor.html', footer=footer)
        except Exception as error:
            cod = error.args[0]
            if cod == 1062:
                footer = 'Логин уже существует!'
            else:
                footer = error.args[1]
            return await render_template('register_client.html', footer=footer)

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
        subjects = set(sorted(list(await cursor.fetchall())))

        sql = "SELECT id, name FROM subject"
        await cursor.execute(sql)
        allsubjects = set(sorted(list(await cursor.fetchall()))).difference(subjects)

        await cursor.close()
        connection.close()

        data = {'userdata': userdata, 'subjects':subjects, 'allsubjects':allsubjects}
        return await render_template('personal_tutor.html', data=data)
    elif request.method == 'POST':
        form = await request.form
        connection = await connect_to_database()
        cursor = await connection.cursor()
        sql = "UPDATE user SET name=%s, email=%s WHERE id = %s"
        values = [form['name'], form['email'], session['login'][0]]
        await cursor.execute(sql, values)
        sql = "UPDATE repetitor SET hourly_rate=%s WHERE user_id = %s"
        values = [form['hourly_rate'], session['login'][0]]
        await cursor.execute(sql, values)
        await connection.commit()
        await cursor.close()
        connection.close()

        return redirect(url_for('personal_tutor'))

@app.route('/get_allsubjects', methods=['GET', 'POST'])
async def get_allsubjects():
    connection = await connect_to_database()
    cursor = await connection.cursor()
    sql = "SELECT id, name FROM subject"
    values = []
    await cursor.execute(sql, values)
    subjects = list(await cursor.fetchall())
    await cursor.close()
    connection.close()
    print("-----------", subjects)
    return jsonify({'subjects': subjects})


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

    return redirect(url_for('personal_tutor'))

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

    return redirect(url_for('personal_tutor'))

@app.route("/sql_request", methods=['GET', 'POST'])
async def sql_request():
    connection = await connect_to_database()
    cursor = await connection.cursor()
    sql = " SELECT subject.name, COUNT(subject.name) as count FROM subject JOIN query ON query.subject_id = subject.id " \
          "JOIN request ON query.id = request.query_id " \
          "WHERE request.status_id = 3 GROUP BY subject.name ORDER BY count DESC"
    values = []
    await cursor.execute(sql, values)
    result = await cursor.fetchall()
    await cursor.close()
    connection.close()
    data = {}
    data['result'] = result
    return await render_template('sql_request.html', data=data)

if __name__ == '__main__':
    app.run(host="0.0.0.0")


