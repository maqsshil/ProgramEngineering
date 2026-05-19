from flask import Flask, request, jsonify
from database import Database

app = Flask(__name__)
db = Database()
db.create_tables()

# тестовые пользователи
try:
    db.create_user("admin", "admin", "admin")
    db.create_user("player", "player", "player")
except:
    pass


@app.route("/login", methods=["POST"])
def login():
    data = request.json
    user = db.get_user(data["login"], data["password"])

    if user:
        return jsonify({
            "status": "success",
            "role": user[2],
            "login": user[1]
        })
    else:
        return jsonify({
            "status": "error",
            "message": "Invalid credentials"
        }), 401


@app.route("/register", methods=["POST"])
def register():
    data = request.json
    try:
        db.create_user(data["login"], data["password"], "player")
        return jsonify({"status": "success"})
    except:
        return jsonify({
            "status": "error",
            "message": "User already exists"
        }), 400


@app.route("/mazes", methods=["GET"])
def get_mazes():
    return jsonify(db.get_all_mazes())


@app.route("/mazes/<int:maze_id>", methods=["DELETE"])
def delete_maze(maze_id):
    db.delete_maze(maze_id)
    return jsonify({"status": "deleted"})

@app.route("/mazes", methods=["POST"])
def save_maze():
    data = request.json
    success = db.save_maze(
        data["name"],
        data["height"],
        data["width"],
        data["maze_map"],
        data["theme"],
        data["entry"],
        data["exit"]
    )

    if success:
        return jsonify({"status": "success"})
    else:
        return jsonify({
            "status": "error",
            "message": "Лабиринт с таким названием уже существует"
        }), 400

if __name__ == "__main__":
    app.run(debug=True)