from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import Adafruit_DHT
import time
from flask_cors import CORS
import sys
import RPi.GPIO as GPIO
import threading

app = Flask(__name__)
socketio = SocketIO(app)
CORS(app)

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)


def turn(steps, clockwise):
    arr = [0, 1, 2, 3];
    if clockwise != 1:
        arr = [3, 2, 1, 0];
    ports = [40, 38, 36, 35]
    for p in ports:
        GPIO.setup(p, GPIO.OUT)

    for step in range(0, steps):
        for i in arr:
            time.sleep(0.01)
            for j in range(0, 4):
                if j == i:
                    GPIO.output(ports[j], GPIO.HIGH)
                else:
                    GPIO.output(ports[j], GPIO.LOW)


def check_gpio():
    GPIO.setup(12, GPIO.IN)
    while True:
        time.sleep(1)
        if GPIO.input(12) == True:
            current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            warning_message = current_time + "   warn"
            print(warning_message)
            socketio.emit('warning_message', '1')
        else:
            socketio.emit('warning_message', '0')


@app.route('/weather')
def weather():
    humidity, temperature = Adafruit_DHT.read_retry(11, 17)
    # return '{0:0.1f} {0:0.1f}'.format(temperature,humidity)
    # return render_template('weather.html', Temp=temperature, Humidity=humidity)
    return {"Temp": temperature, "Humidity": humidity}

@app.route('/left', methods=["GET", "POST"])
def left():
    turn(120, 0)
    return '0'


@app.route('/right', methods=["GET", "POST"])
def right():
    turn(120, 1)
    return '1'

@app.route('/monitor', methods=['GET', 'POST'])
def monitor():
    return render_template('index.html')


@app.route('/')
def main():
    return render_template('main.html')


if __name__ == '__main__':
    threading.Thread(target=check_gpio).start()
    socketio.run(app, port=5000)
# app.run(port=5000)
