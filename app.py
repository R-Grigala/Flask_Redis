from flask import Flask
from flask_restx import Api, Resource, fields, reqparse
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import redis
import json

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tasks.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
api = Api(app, version="1.0", title="To-Do API", description="A simple Flask-RESTX To-Do API with SQLite")
task_ns = api.namespace("tasks", description="Task operations")

# Redis client connecting to localhost:6380 (your docker Redis port)
redis_client = redis.Redis(host='localhost', port=6380, db=0)

def str_to_bool(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ('true', '1', 'yes', 'y', 't')
    return False

# Parser for POST data
task_parser = reqparse.RequestParser()
task_parser.add_argument("title", type=str, required=True, help="Task title is required")
task_parser.add_argument("description", type=str, required=False, help="Optional task description")
task_parser.add_argument("done", type=str_to_bool, required=False, default=False, help="Task completion status")

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)  # optional longer text
    done = db.Column(db.Boolean, default=False)  # task completion status
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# RESTX model for Swagger
task_model = task_ns.model("Task", {
    "id": fields.Integer(readOnly=True, description="The task identifier"),
    "title": fields.String(required=True, description="The task title"),
    "description": fields.String(description="Optional task description"),
    "done": fields.Boolean(description="Task completion status"),
    "created_at": fields.DateTime(description="Task creation timestamp")
})

@task_ns.route("/")
@task_ns.doc(responses={200: 'OK', 400: 'Invalid Argument', 401: 'JWT Token Expires', 403: 'Forbidden', 404: 'Not Found'})
class TaskList(Resource):
    @task_ns.marshal_list_with(task_model)
    def get(self):
        """List all tasks with Redis read cache"""

        cached_tasks = redis_client.get("tasks:all")
        if cached_tasks:
            tasks = json.loads(cached_tasks.decode('utf-8'))
            return tasks

        tasks = Task.query.all()
        tasks_serialized = [
            {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "done": task.done,
                "created_at": task.created_at.isoformat()
            }
            for task in tasks
        ]

        redis_client.setex("tasks:all", 60, json.dumps(tasks_serialized))
        return tasks_serialized
    
    @task_ns.doc(parser=task_parser)
    def post(self):
        """Add new task"""
        args = task_parser.parse_args()
        new_task = Task(
            title=args["title"],
            description=args.get("description"),
            done=args.get("done", False)
        )
        db.session.add(new_task)
        db.session.commit()

        # Invalidate Redis cache on data change
        redis_client.delete("tasks:all")

        return {"id": new_task.id, "title": new_task.title}, 201
    
@task_ns.route("/<int:id>")
@task_ns.response(404, "Task not found")
class TaskResource(Resource):
    @task_ns.marshal_with(task_model)
    def get(self, id):
        """Get a task by ID"""
        task = Task.query.get_or_404(id)
        return task
    
    @task_ns.doc(parser=task_parser)
    def put(self, id):
        """Update a task"""
        task = Task.query.get_or_404(id)
        args = task_parser.parse_args()  # reqparse-ით წაკითხვა
        task.title = args["title"]
        task.description = args.get("description")
        task.done = args.get("done", task.done)
        db.session.commit()

        # Invalidate Redis cache on data change
        redis_client.delete("tasks:all")

        return {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "done": task.done,
            "created_at": task.created_at.isoformat()
        }

    def delete(self, id):
        """Delete a task by ID"""
        task = Task.query.get_or_404(id)
        db.session.delete(task)
        db.session.commit()

        # Invalidate Redis cache on data change
        redis_client.delete("tasks:all")

        return "", 204

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    try:
        redis_client.ping()
        print("Connected to Redis successfully")
    except redis.ConnectionError:
        print("Failed to connect to Redis")
    app.run(debug=True)