import logging

from flask import Flask, render_template, request, redirect
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app, logger=True, engineio_logger=True)
thread = None


process_manager = None
LOGGER = logging.getLogger('UI')
LOGGER.addHandler(logging.StreamHandler())


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        new_machine_ip = request.form.get('ip')
        LOGGER.warning(f'Add new ip {new_machine_ip}')

        result = process_manager.add_new_client(new_machine_ip)
        if result:
            LOGGER.info(f'New machine was added')
        else:
            LOGGER.warning(f"Can't add machine")

        return redirect('/')

    response = process_manager.get_workers_info()

    return render_template(
        'index.html',
        async_mode=socketio.async_mode,
        info=response
    )


def background_thread():
    while True:
        socketio.sleep(5)
        time = process_manager.get_workers_info()
        socketio.emit('update time', time)


@socketio.on('connect')
def test_connect():
    global thread
    if thread is None:
        thread = socketio.start_background_task(target=background_thread)


def start_ui(manager):
    global process_manager
    process_manager = manager
    socketio.run(app)


if __name__ == '__main__':
    pass