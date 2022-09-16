import os
import socket
from pathlib import Path

import qrcode
from flask import Flask, redirect, request, send_file

app = Flask(__name__)
root = Path.cwd() / "__files__"
root.mkdir(exist_ok=True)

css = """
form {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    width: max-content;
}
"""


@app.route("/upload/<path:name>", methods=["POST"])
def upload_file(name):
    if "main.py" in name:
        return "Failure"
    with open(root / name, "wb+") as fout:
        for line in request.files["file"].stream:
            fout.write(line)

    return "Success"


@app.route("/file", methods=["POST"])
def file():
    if "filename" in request.files:
        file = request.files["filename"]
        with open(root / file.filename, "wb+") as fout:
            fout.write(file.stream.read())
    return redirect("/")


@app.route("/files/<path:name>", methods=["GET"])
def files(name):
    return send_file(root / name)


@app.route("/", methods=["GET"])
def index():
    return f"""
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
    {css}
    </style>
    </head>
    <body>
    <h1>Hello world</h1>
    <h2>Submit a file</h2>
    <form action="/file" method="post" enctype="multipart/form-data">
        <input type="file" id="filename" name="filename" />
        <input type="submit" value="Upload" name="submitted" />
    </form>

    <h2>Files</h2>
    <ol>
        {get_available_files_html()}
    </ol>
    </body>
    """


def get_available_files_html():
    return "".join(
        f"<li><a href='/files/{file}'>{file}</a></li>" for file in os.listdir(str(root))
    )


if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(("8.8.8.8", 80))
        hostaddr = s.getsockname()[0]

    qr = qrcode.QRCode()
    qr.add_data(f"http://{hostaddr}:8080")
    qr.print_ascii()

    app.run(host="0.0.0.0", debug=True, port=8080)
