from flask import Flask, request, jsonify, render_template
import os
import subprocess
from flask_cors import CORS
import uuid
from werkzeug.exceptions import BadRequest
import threading
from transform import tranform_method

app = Flask(__name__)
WORKING_DIR = '/'
SCRIPT_DIR = 'script.sh'


from flask import Flask, jsonify
import subprocess

app = Flask(__name__)
CORS(app)
# Место для хранения статуса процесса
processes_status = {}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/stop-process-grall/<int:pid>')
def stop_process(pid):
    process = processes_status.get(pid)
    
    if not process:
        return jsonify({'result': False})
    
    try:
        process.kill()
    except KeyError as e:
        raise BadRequest(f"process id not defined")
    
    return jsonify({'result': True})

@app.route('/check-process-grall/<int:pid>')
def check_process(pid):
    process = processes_status.get(pid)
    if process and process.poll() is None:
        # Процесс все еще запущен
        return jsonify({'status': 'running'})
    else:
        # Процесс завершился
        return jsonify({'status': 'complete'})

def process_finished(pid, callback):
    process = processes_status[pid]
    process.wait()
    print(process)
    
    print('перешел в process_finished')
    # Удалите информацию о процессе из словаря после завершения процесса
    processes_status.pop(pid, None)
    # Вызовите функцию обратного вызова после завершения процесса
    callback(pid,'C:/Users/viatkinviatkin/Desktop/release GRAL/server/tesproj/Computation/00001-101.txt')
    
    process.kill()
    

@app.route('/process', methods=['GET'])
def process():

    process = subprocess.Popen(['gral', 'C:/Users/viatkinviatkin/Desktop/release GRAL/server/tesproj/Computation'])
    pid = process.pid
    processes_status[pid] = process
    
    # Запуск потока ожидания завершения процесса
    t = threading.Thread(target=process_finished, args=(process.pid, tranform_method))
    t.start()
    
    return jsonify({'pid': pid})

if __name__ == '__main__':
    app.run()
