from flask import Flask, request
from src.helper.callback_request import send_callback_request
from src.helper.json_helper import convert_jsonify
from src.helper.routific_format import routific_format_solution, routific_callback_solution
from src.routing.routing_problem import optimize_problem

app = Flask("ROUTE_ENGINE")


@app.route('/')
def index():
    return 'Server Works!'


@app.route('/vrp-long', methods=['POST'])
def vrp_long():
    json_obj = request.json

    problem = json_obj
    callback_url = problem.get('callback_url')

    # Optimize problem
    solution = optimize_problem(problem, True)
    out = routific_format_solution(solution)

    # Request the callback url
    job_id = json_obj.get('job_id')
    output = routific_callback_solution(job_id, out, solution)
    send_callback_request(output, callback_url)

    response = app.response_class(
        response=convert_jsonify(out),
        status=200,
        mimetype='application/json'
    )
    return response


if __name__ == "__main__":
    app.run('0.0.0.0', port=5000)
    # serve(app, host='0.0.0.0', port=5000)
