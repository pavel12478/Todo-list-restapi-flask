from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@127.0.0.1/todolist'
db = SQLAlchemy(app)
ma = Marshmallow(app)

client = app.test_client()


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    # def __init__(self, title, description, created_at, updated_at):
    #     self.title = title
    #     self.description = description
    #     self.created_at = created_at
    #     self.updated_at = updated_at


class TaskSchema(ma.SQLAlchemySchema):
    class Meta:
        # model = Task
        fields = ('id', 'title', 'description', 'created_at', 'updated_at')


tasks_schema = TaskSchema(many=True)
task_schema = TaskSchema()


@app.route('/tasks', methods=["POST"])
def add_task():
    try:
        data = request.get_json()
        new_task = Task(description=data['description'], title=data['title'], created_at=datetime.now())
        # print(data)
        db.session.add(new_task)
        # db.session.flush()
        db.session.commit()
    except:
        db.session.rollback()
        print(f'Ошибка добавления в БД')

    task = Task.query.all()
    output = tasks_schema.dump(task)
    return jsonify(output)


@app.route('/tasks', methods=['GET'])
def check():
    task = Task.query.all()
    output = tasks_schema.dump(task)
    return jsonify(output)


@app.route('/tasks/<int:id>', methods=['GET'])
def check_id(id):
    task = Task.query.filter_by(id=id).first()
    output = task_schema.dump(task)
    return jsonify(output)


@app.route('/task/<int:id>', methods=["PUT"])
def update(id):
    data = request.get_json()

    task_up = Task.query.filter_by(id=id).first()

    title = data.get('title', task_up.title)
    description = data.get('description', task_up.description)
    updated_at = datetime.now()

    task_up.title = title
    task_up.description = description
    task_up.updated_at = updated_at
    db.session.commit()

    task = Task.query.all()
    output = tasks_schema.dump(task)
    return jsonify(output)


@app.route('/tasks/<int:id>', methods=['DELETE'])
def delete(id):
    task_del = Task.query.filter_by(id=id).first()
    db.session.delete(task_del)
    db.session.commit()
    return f'Строка с ID={id} успешно удалена'


if __name__ == '__main__':
    app.run(debug=True)
