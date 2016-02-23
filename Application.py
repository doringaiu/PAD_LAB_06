from flask import Flask, jsonify, make_response, request
from flask_restful import Resource, Api
from cassandra.cluster import Cluster
import requests, atexit

app = Flask(__name__)
api = Api(app)
cluster = Cluster()
dbsession = cluster.connect('intro')
input_port = input('enter the port # \n')

def open_instance(host, port): # notify proxy of the new instance
    try:
        response = 1
        url = 'http://' + 'localhost' + ':' + str(5002) + '/openinstance'
        payload = {'host': host,'port': port}
        r = requests.post(url, data=payload)
        response = r.status_code
    except requests.exceptions.MissingSchema:
        print 'The proxy was not notified of the new instance. Please re-check the URL in settings.py.'
    except requests.exceptions.ConnectionError as error:
        print 'Could not connect to proxy: ' + str(error)
    else:
        print 'Instance open - proxy notification sent, response: %d' % response
    return response


def close_instance(host, port): # notify proxy of instance closing
    try:
        response = 1
        url = 'http://' + 'localhost' + ':' + str(5002) + '/closeinstance'
        payload = {'host': host, 'port': port}
        r=requests.post(url, data=payload)
        response = r.status_code
    except requests.exceptions.MissingSchema:
        print 'The proxy was not notified of instance closing. Please re-check the URL in settings.py.'
    except requests.exceptions.ConnectionError as error:
        print 'Could not connect to proxy: ' + str(error)
    else:
        print 'Instance closing, proxy notification sent, response: %d' % response
    return response


class Employees(Resource):
    def post(self, id):
        dbsession.execute("USE intro;")
        name = request.form['name']
        surname = request.form['surname']
        age = request.form['age']
        id += 1
        dbsession.execute("INSERT INTO employees (id, name, surname, age) values (%s,%s,%s,%s)", [id, name, surname, age])
        return {'status': 'OK'}

    def get(self, id):
        single = dbsession.execute("SELECT * FROM employees WHERE id = %s", [id])
        return {'id': single[0][0], 'name': single[0][1], 'surname': single[0][2], 'age': single[0][3]}


@app.errorhandler(404)
def error_404(error):
    return make_response(jsonify({'Error', '404'}), 404)


api.add_resource(Employees, '/employee/<int:id>')
print open_instance('localhost', input_port)
app.run(host='localhost', port=input_port)
atexit.register(close_instance, 'localhost', input_port)
