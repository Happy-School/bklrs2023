import json
import time

def generate_log():
    log_file_path = 'main.log'

    try:
        with open(log_file_path, 'r') as log_file:
            while True:
                line = log_file.readline()
                if line:
                    # Encode the line to bytes and yield it
                    yield json.dumps({'log_line': line.strip()}).encode('utf-8') + b'\n'
                else:
                    break # Adjust the sleep time as needed
    except FileNotFoundError:
        # Encode the error message to bytes and yield it with a 404 status
        yield json.dumps({'error': 'Log file not found'}).encode('utf-8') + b'\n', 404


if __name__ == "__main__":
    for log_line in generate_log():
        print(log_line)
