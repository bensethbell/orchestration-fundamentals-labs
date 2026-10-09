from flask import Blueprint, abort, jsonify, render_template, request

from app import db

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    tasks = db.list_tasks()
    return render_template("index.html", tasks=tasks)


@bp.route("/api/tasks", methods=["GET"])
def list_tasks():
    return jsonify(db.list_tasks())


@bp.route("/api/tasks", methods=["POST"])
def create_task():
    data = request.get_json(force=True)
    task = db.create_task(
        title=data["title"],
        description=data.get("description", ""),
        status=data.get("status", "todo"),
    )
    return jsonify(task), 201


@bp.route("/api/tasks/<int:task_id>", methods=["PATCH"])
def update_task(task_id):
    if db.get_task(task_id) is None:
        abort(404)
    data = request.get_json(force=True)
    allowed = {k: v for k, v in data.items() if k in ("title", "description", "status")}
    task = db.update_task(task_id, **allowed)
    return jsonify(task)


@bp.route("/api/users", methods=["GET"])
def list_users():
    return jsonify(db.list_users())
