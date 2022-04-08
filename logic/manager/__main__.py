from manager_interface import interface
from manager import ProcessManager
from threading import Thread


def main():
    # Create instance of ProcessManager
    process_manager = ProcessManager()

    # Start server for handling UI
    interface.start_ui(process_manager)


if __name__ == '__main__':
    main()
