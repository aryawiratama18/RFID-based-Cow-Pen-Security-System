from flask import Flask, render_template, request, jsonify, url_for, redirect
# from flask_wtf import Form 
# from wtforms import TextField
# import requests
import pymysql 
from datetime import datetime
# from firebase import firebase 
from flask_mqtt import Mqtt


app = Flask(__name__)
app.secret_key = '6512tbkbdfb'
app.config['MQTT_BROKER_URL'] = 'maqiatto.com'           # use the free broker from HIVEMQ
app.config['MQTT_BROKER_PORT'] = 1883                    # default port for non-tls connection
app.config['MQTT_USERNAME'] = 'mansyla.ub@gmail.com'      # set the username here if you need authentication for the broker
app.config['MQTT_PASSWORD'] = 'mansyla67'          # set the password here if the broker demands authentication
# app.config['MQTT_KEEPALIVE'] = 5                         # set the time interval for sending a ping to the broker to 5 seconds
# app.config['MQTT_TLS_ENABLED'] = False                   # set TLS to disabled for testing purposes

mqtt = Mqtt(app)


def connection():
    conn = pymysql.connect(host='localhost',
                            user = 'rfid',
                            passwd = 'rfid12345678',
                            db = 'rfid_sapi')
    c = conn.cursor()

    return c, conn

c, conn = connection()

class regristationForm(Form):
    id = TextField("id")


@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    mqtt.subscribe('mansyla.ub@gmail.com/id')

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    now = datetime.now()
    time = now.strftime("%H:%M:%S")

    id = message.payload.decode()

    print(id)

    c.execute("INSERT INTO last_id(ID) VALUES(%s)", (id))
    conn.commit()

    c.execute("DELETE FROM last_id ORDER BY NO ASC LIMIT 1")
    conn.commit()

    c.execute("SELECT * FROM data_sapi WHERE ID=%s", (id))
    result = c.fetchall()

    tempat = result[0][4]


    if tempat == 0:
        c.execute("UPDATE data_sapi SET WAKTU_MASUK = %s, DI_DALAM = 1 WHERE ID = %s", (time, id))
        conn.commit()

    elif tempat == 1:
        c.execute("UPDATE data_sapi SET WAKTU_KELUAR = %s, DI_DALAM = 0 WHERE ID = %s", (time, id))
        conn.commit()

@app.route('/')
def homePage():
    c.execute("SELECT * FROM data_sapi")
    data = c.fetchall()
    diDalam = 0
    diLuar = 0

    for i in data:
        if i[4] == 1:
            diDalam += 1
        elif i[4] == 0:
            diLuar += 1
    
    return render_template('index.html', data=data, diDalam=diDalam, diLuar=diLuar)

@app.route('/form', methods=['GET', 'POST'])
def form():
    # newId = ""

    # if request.method == 'GET':
    #     now = datetime.now()
    #     time = now.strftime("%H:%M:%S")

    #     newId = request.args.get('ID')
    #     try:
    #         c.execute("INSERT INTO data_sapi(ID, WAKTU_MASUK, WAKTU_KELUAR) VALUES('12345678', '12:34:59', '12:34:59')")
    #         conn.commit()

    #         return redirect(url_for('success', id=newId))
        
    #     except:
    #         return "gagal menambahkan ID"

        

    c.execute("SELECT * FROM last_id ORDER BY NO DESC LIMIT 1")
    result = c.fetchall()
    id = result[0][1]

    return render_template('form.html', id=id)

@app.route('/input', methods = ['GET', 'POST'])
def input():
    if request.method == 'GET':
        now = datetime.now()
        time = now.strftime("%H:%M:%S")

        newId = request.args.get('ID')
        try:
            c.execute("INSERT INTO data_sapi(ID, WAKTU_MASUK, WAKTU_KELUAR) VALUES(%s, %s,  %s)", (newId, time, time))
            conn.commit()

            return redirect(url_for('success', id=newId))
        
        except:
            return "gagal menambahkan ID"

@app.route('/success')
def success():
    return "Sukses menambahkan ID"

@app.route('/get-id')
def getId():
    # url = 'http://172.20.10.8/get-data'
    # req = requests.get(url)
    # id = req.text

    # firebaseUrl = 'https://coba-e3dd3.firebaseio.com/'
    # getId = firebase.FirebaseApplication(firebaseUrl, None)

    # id = getId.get('/ID', None)

    c.execute("SELECT * FROM last_id ORDER BY NO DESC LIMIT 1")
    result = c.fetchall()

    lastId = result[0][1]

    c.execute("SELECT * FROM data_sapi")
    results = c.fetchall()

    for result in results:
        print(result)
    # id = data[0][1]
    # masuk = data[0][2]
    # keluar = data[0][3]

    return "Hello World!"
    # return jsonify(id=id, masuk=masuk, keluar=keluar)


if __name__ == '__main__':
    app.run(debug=True) 