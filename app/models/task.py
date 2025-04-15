from datetime import datetime

from app.extension import db

class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now)
    form_data = db.Column(db.Text)


class TaskLog(db.Model):
    __tablename__ = 'task_logs'
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'))
    timestamp = db.Column(db.DateTime, default=datetime.now)
    level = db.Column(db.String)  # INFO, SUCCESS, ERROR
    step = db.Column(db.String)   # 如 rename, screenshot, torrent
    message = db.Column(db.String)

