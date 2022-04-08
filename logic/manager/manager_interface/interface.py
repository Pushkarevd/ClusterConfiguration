from flask import Flask, render_template, request, redirect
import logging
app = Flask(__name__)


process_manager = None
LOGGER = logging.getLogger('UI')
LOGGER.addHandler(logging.StreamHandler())


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        new_machine_ip = request.form.get('ip')
        LOGGER.info(f'Add new ip {new_machine_ip}')

        result = process_manager.add_new_client(new_machine_ip)
        if result:
            LOGGER.info(f'New machine was added')
        else:
            LOGGER.warning(f"Can't add machine")

        return redirect('/')

    status = process_manager.get_workers_info()
    LOGGER.info(status)
    if not status:
        status = []
    return render_template('index.html', status=status)


def start_ui(manager):
    global process_manager
    process_manager = manager
    app.run()


if __name__ == '__main__':
    app.run()