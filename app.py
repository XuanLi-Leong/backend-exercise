from flask import Flask, jsonify, request
import mockdb.mockdb_interface as db

app = Flask(__name__)

def create_response(data={}, status=200, message=''):
    """
    Wraps response in a consistent format throughout the API
    Format inspired by https://medium.com/@shazow/how-i-design-json-api-responses-71900f00f2db
    Modifications included:
    - make success a boolean since there's only 2 values
    - make message a single string since we will only use one message per response

    IMPORTANT: data must be a dictionary where:
    - the key is the name of the type of data
    - the value is the data itself
    """
    response = {
        'success': 200 <= status < 300,
        'code': status,
        'message': message,
        'result': data
    }
    return jsonify(response), status

"""
~~~~~~~~~~~~ API ~~~~~~~~~~~~
"""

@app.route('/')
def hello_world():
    return create_response('hello world!')

@app.route('/mirror/<name>')
def mirror(name):
    data = {
        'name': name
    }
    return create_response(data)

# TODO: Implement the rest of the API here!

@app.route('/users', methods=['GET', 'POST'])
def users():
    if request.method == 'GET':
        data = db.get('users')
        team = request.args.get('team')
        if team is not None:
            data = [user for user in data if user['team'] == team]
        else:
            data = {'users': data}
        return create_response(data)
    elif request.method == 'POST':
        data = request.get_json()
        try:
            name, age, team = data['name'], data['age'], data['team']
        except KeyError:
            return create_response(status=422, message='User not created; name, age, and team are required.')
        newUser = db.create('users', data)
        return create_response(data=newUser, status=201)

@app.route('/users/<id>')
def users_id(id):
    data = db.getById('users',int(id))
    return create_response(status=404, message='User id not found') if data is None else create_response(data)
        
"""
~~~~~~~~~~~~ END API ~~~~~~~~~~~~
"""
if __name__ == '__main__':
    app.run(debug=True)
