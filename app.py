from waitress import serve
from flask import Flask, request
from problem import main
from src.helper.callback_request import send_callback_request
from src.helper.json_helper import convert_jsonify
from src.helper.routific_format import routific_format_solution

app = Flask(__name__)


@app.route('/')
def index():
    return 'Server Works!'


@app.route('/vrp-long', methods=['POST'])
def vrp_long():
    json_obj = request.json

    problem = json_obj
    job_id = json_obj.get('job_id')
    if job_id is not None:
        problem = json_obj.get('problem')

    callback_url = problem.get('callback_url')

    # Optimize problem
    solution = main(problem)
    out = routific_format_solution(solution)
    output = {
        'id': job_id,
        'output': out
    }

    # Request the callback url
    send_callback_request(output, callback_url)

    response = app.response_class(
        response=convert_jsonify(out),
        status=200,
        mimetype='application/json'
    )
    return response


if __name__ == "__main__":
    # app.run('0.0.0.0',port=server_port)
    serve(app, host='0.0.0.0', port=5000)
