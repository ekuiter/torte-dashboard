from flask import Flask, send_from_directory, request
import random
import os

app = Flask(__name__)
FIGURE_FOLDER = "frontend/public/figures"
TMP_MAPPING = {
    "Linux-Sloc": "sloc.html",
    "Jaccard-Features": "features-jaccard.html",
    "Configuration-Similarity": "configuration-similarity.html",
    "Total-Features": "total-features.html",
}

# Path for our main Svelte page
@app.route("/")
def base():
    return send_from_directory('frontend/public', 'index.html')

@app.route("/<path:path>")
def home(path):
    return send_from_directory('frontend/public', path)


@app.route("/rand")
def hello():
    return str(random.randint(0, 100))

@app.route('/graph', methods=["POST"])
def graph():
    req = request.json
    print(req)
    file_name = f"{req['plot']}-{req['project'].replace('/', '-')}.html"
    print(file_name)
    return send_from_directory(os.path.join(FIGURE_FOLDER, req["plot"]), file_name)

@app.route('/init')
def init():
    return send_from_directory('frontend/public', 'init.json')

if __name__ == "__main__":
    app.run(debug=True)
