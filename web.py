import socket
import threading
import os
from datetime import datetime

PORT = 8080
WORKING_DIRECTORY = "./web_content"


def handle_client(conn, addr):
    try:
        print(f"Подключение от: {addr}")
        # Чтение данных от клиента
        data = conn.recv(8192)
        if not data:
            return
        request = data.decode()
        print(f"Запрос от клиента:\n{request}")

        # Разбор запроса
        lines = request.split("\r\n")
        if len(lines) < 1:
            return
        method, path, _ = lines[0].split()

        # Только метод GET поддерживается
        if method != "GET":
            conn.send(b"HTTP/1.1 405 Method Not Allowed\r\n\r\n")
            return

        # Если путь == "/", перенаправляем на index.html
        if path == "/":
            path = "/index.html"

        # Полный путь к запрашиваемому файлу
        file_path = WORKING_DIRECTORY + path

        # Проверка существования файла
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            conn.send(b"HTTP/1.1 404 Not Found\r\n\r\n")
            conn.send(b"<h1>404 File Not Found</h1>")
            return

        # Чтение содержимого файла
        with open(file_path, "rb") as f:
            content = f.read()

        # Заголовки ответа
        headers = f"""HTTP/1.1 200 OK
Date: {datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')}
Content-Type: text/html; charset=utf-8
Content-Length: {len(content)}
Server: SimplePythonServer/1.0
Connection: close

"""
        conn.send(headers.encode() + content)

    except Exception as e:
        print(f"Ошибка обработки запроса от {addr}: {e}")
    finally:
        conn.close()


def start_server():
    if not os.path.exists(WORKING_DIRECTORY):
        os.makedirs(WORKING_DIRECTORY)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', PORT))
    server_socket.listen(5)
    print(f"Сервер запущен на порту {PORT}. Ожидаем подключения...")

    try:
        while True:
            conn, addr = server_socket.accept()
            client_thread = threading.Thread(
                target=handle_client, args=(conn, addr))
            client_thread.start()
    except KeyboardInterrupt:
        print("\nСервер завершает работу...")
    finally:
        server_socket.close()


if __name__ == "__main__":
    start_server()
