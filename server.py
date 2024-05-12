from flask import Flask, request, jsonify, render_template
import os
import subprocess
from flask_cors import CORS
from werkzeug.exceptions import BadRequest
import threading
from transform import tranform_method
from setup_gral_params import setup_params
WORKING_DIR = '/'
DIR = os.path.dirname(__file__) #<-- absolute dir the script is in
COMPUTATION_DIR = os.path.join(DIR, 'tesproj/Computation/')
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
 
    # Удалите информацию о процессе из словаря после завершения процесса
    processes_status.pop(pid, None)
 
    rel_path = '00001-101.txt'
 
    # Вызовите функцию обратного вызова после завершения процесса
    callback(pid, os.path.join(COMPUTATION_DIR, rel_path))
 
    process.kill()    
    
@app.route('/process', methods=['GET'])
def process():
    
    arguments  = request.args.to_dict()
    try: 
        setup_params(arguments)
    except:
        raise BadRequest(f"Неверные параметры", jsonify({'error':'неверные параметры'}))
    
    process = subprocess.Popen(['gral', COMPUTATION_DIR], stdin=subprocess.PIPE)
    pid = process.pid
    processes_status[pid] = process
    
    # Посылаем 'enter', чтобы имитировать нажатие клавиши по завершении gral process
    process.stdin.write(b"a")

    # Запуск потока ожидания завершения процесса
    t = threading.Thread(target=process_finished, args=(process.pid, tranform_method))
    t.start()
    
    return jsonify({'pid': pid})

if __name__ == '__main__':
    app.run()
