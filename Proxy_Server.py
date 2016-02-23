from flask import Flask, jsonify, make_response, request
from flask_restful import Resource, Api
from redis import Redis
import requests
from itertools import cycle

app = Flask(__name__)
api = Api(app)
redis = Redis('localhost')

apps = []
app_instances = cycle(apps)


class Employees(Resource):
    def post(self, id):
        name = request.form['name']
        surname = request.form['surname']
        age = request.form['age']
        url = next(app_instances) + '/employee/' + str(id)
        payload = {"name": name, "surname": surname, "age": age}
        r = requests.post(url, data=payload)
        return r.json()

    def get(self, id):
        try:
            uri = next(app_instances) + '/employee/' + str(id)
            print uri
        except StopIteration:
            pass
        except UnboundLocalError:
            print 'please set instance first'
        cache = redis.get(id)
        print cache

        if cache is None:
            r = requests.get(uri)
            r = r.json()
            name = r['name']
            surname = r['surname']
            age = r['age']
            redis.setex(id, name, 10)
        else:
            r = {"id": id, "name": cache}
            return r


class OpenInstance(Resource):
    def post(self):
        host = request.form['host']
        port = request.form['port']
        incoming = 'http://' + host + ":" + port
        apps.append(incoming.encode('utf-8'))
        print incoming + " opening" + "\n " + str(apps)
        return {"status": "OK"}

    def get(self):
        return 1


class CloseInstance(Resource):
    def post(self):
        host = request.form['host']
        port = request.form['port']
        incoming = "http://" + host + ":" + port
        print incoming + " closing"
        try:
            apps.remove(incoming.encode('utf-8'))
        except ValueError:
            print 'instance is not in the list'
        if apps is None:
            print 'no instances'
        else:
            print "currents instances:" + str(apps)
        return {"status": "ok"}


class CacheClear(Resource):
    def get(self):
        redis.flushdb()
        return 1


@app.errorhandler(404)
def err_404(error):
    return make_response(jsonify({'Error': '404'}), 404)

api.add_resource(Employees, '/employee/<int:id>')
api.add_resource(OpenInstance, '/openinstance')
api.add_resource(CloseInstance, '/closeinstance')
api.add_resource(CacheClear, '/cacheclear')

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5002)
