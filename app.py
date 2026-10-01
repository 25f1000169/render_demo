from flask import Flask, jsonify, render_template

app = Flask(__name__)

# A simple in-memory counter
counter_value = 0


@app.route("/")
def index():
    return render_template("index.html", counter=counter_value)


@app.route("/increment", methods=["POST"])
def increment():
    global counter_value
    counter_value += 1
    return jsonify({"success": True, "counter": counter_value})


if __name__ == "__main__":
    app.run(debug=True)
