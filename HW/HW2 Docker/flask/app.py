import os
from flask import Flask, request, make_response

app = Flask(__name__)

@app.route('/')
def hello():
    response = make_response(
        {
            'response': 'Hello, World!',
            'status': 200
        }
    )
    return response

@app.route('/repeat', methods=['GET'])
def repeat():
    to_return = request.args.get('input')
    return make_response({
        'body': to_return,
        'status': 200
    })

if __name__ == '__main__':
    port = os.getenv('PORT')
    # By default flask is only accessible from localhost.
    # Set this to '0.0.0.0' to make it accessible from any IP address
    # on your network (not recommended for production use)
    app.run(host='0.0.0.0', port=port, debug=True)
