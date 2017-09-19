from flask import Flask, request, jsonify
from datetime import datetime
import mongoengine as me

me.connect('todo_list')

class User(me.Document):
	name = me.StringField()
	email = me.StringField()
	def to_dict(self):
		return{
			'id': str(self.id),
			'name': self.name,
			'email': self.email,
		}

class Task(me.Document):
	title = me.StringField()
	description = me.StringField()
	deadline = me.DateTimeField()
	complete = me.BooleanField()
	tags = me.ListField(me.StringField)
	added = me.DateTimeField()
	user = me.ReferenceField(User)
	color = me.StringField()

	def to_dict(self):
		return {
			'id':str(self.id),
			'title':self.title,
			'description':self.description,
			'deadline':int(self.deadline.timestamp()),
			'complete':self.complete,
			'tags':self.tags,
			'added':int(self.added.timestamp()),
			'user': str(self.user.id) if self.user else '',
			'color':self.color,
		}

app = Flask(__name__)


@app.route("/users", methods=['GET'])
def get_users():
	users = User.objects.all()
	array = []
	for user in users:
		array.append(user.to_dict())

	return jsonify(array)

@app.route("/users", methods=['POST'])
def create_user():
	if not request.is_json:
		return jsonify({'error': 'not_json'}), 400
	data = request.get_json()
	name = data.get('name')
	email = data.get('email')
	user = User(name=name, email=email)
	user.save()

@app.route("/tasks", methods=['GET'])
def get_tasks():
	tasks = Task.objects.all()
	array = []
	for task in tasks:
		array.append(task.to_dict())

	return jsonify(array)

@app.route("/tasks", methods=['POST'])
def create_tasks():
	if not request.is_json:
		return jsonify({'error': 'not_json'}), 400
	data = request.get_json()
	task = Task(complete=False, added=datetime.now())
	task.title = data.get('title')
	task.description = data.get('description')
	task.deadline = datetime.fromtimestamp(data.get('deadline',0))
	task.tags = data.get('tags', [])
	if(data.get('user')):
		task.user = User.objects.filter(id=data.get('user')).first()
	task.color = data.get('color')
	task.save()
	return jsonify(task.to_dict())

@app.route('/tasks/<string:task_id>', methods=['PATCH'])
def update_tasks(task_id):
	if not request.is_json:
		return jsonify({'error': 'not_json'}), 400
	task = Task.objects.filter(id=task_id).first()
	if not task:
		return jsonify({'error': 'not_found'}), 404
	data = request.get_json()
	task.complete = data.get('complete', task.complete)
	task.save()
	return jsonify(task.to_dict())

if __name__ == "__main__":
	app.run(debug=True)