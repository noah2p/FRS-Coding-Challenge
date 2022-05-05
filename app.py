import http.client
import json
import traceback
import os

from flask import Flask, render_template, request, redirect, url_for, abort, jsonify
from werkzeug.exceptions import InternalServerError
from flask_mail import Mail, Message

app = Flask(__name__)

# configure mail so that if there's an Internal Server Error I will be notified
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'petra095@umn.edu'
# not putting my password here
app.config['MAIL_PASSWORD'] = '****************'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

# handle default route
@app.route('/')
def index():
    app.logger.info('Serving home page')
    try:
        return render_template('index.html')
    except:
        app.logger.error('Error serving index.html page')
        abort(500)

# GET request to /jokes API (dad jokes)
@app.route("/jokes")
def dad_jokes():
    try: 
        app.logger.info('Making GET request to dad jokes API')
        conn = http.client.HTTPSConnection("icanhazdadjoke.com")
        payload = ''
        headers = {'Accept': 'application/json'}
        conn.request("GET", "/", payload, headers)
        app.logger.debug('GET request successful')
        # after request get response from server and format response to send necessary information
        app.logger.info('attempting to format JSON response data')
        try:
            res = conn.getresponse()
            data = res.read()
            data = data.decode("utf-8")
            jsonfile = json.loads(data)
            app.logger.debug('Attempting to extract data from JSON response')
            joke = jsonfile['joke']
            app.logger.debug('Successful GET request and successfully formatted response to send to render_template')
            return render_template('jokes.html', title="Dad Jokes", joke = joke)
        except KeyError:
            app.logger.error('KeyError parsing JSON file for data')
            abort(500)
    except:
        app.logger.error('Bad request to dad jokes API')
        abort(400)

# GET request to /films API (studio ghibli)
@app.route("/films")
def ghibli_films():
    app.logger.info('Making GET request to studio ghibli API')
    try:
        conn = http.client.HTTPSConnection("ghibliapi.herokuapp.com")
        payload = ''
        headers = {}
        conn.request("GET", "/films", payload, headers)
        res = conn.getresponse()
        app.logger.debug('GET request successful')
        # since there's a lot of data here, I am only displaying a table of all the studio ghibli movies with some (lots of) data from the json omitted
        app.logger.info('attempting to format JSON response data')
        try:
            data = res.read()
            data = data.decode("utf-8")
            jsondata = json.loads(data)
            # idea here is to format the data such that it is a list of lists with some elements grouped together in the order they appear
            # to make it easier to display the data using nested for each calls
            formatted_data = []
            for item in jsondata:
                temp = []
                temp.append(item['title'])
                temp.append(item['description'])
                temp.append(item['release_date'])
                formatted_data.append(temp)
            headings = ("Title", "Description", "Release Date")
            app.logger.debug('Successfully formatted JSON data')
            return render_template('films.html', title="Studio Ghibli Films", data = formatted_data, headings=headings)
        except:
            app.logger.error('KeyError when formatting json data')
            abort(500)
    except:
        app.logger.error('Bad request to studio ghibli API')
        abort(400)

#error handlers 
@app.errorhandler(400)
def bad_request(error):
    app.logger.error('Bad Request')
    error_tb = traceback.format_exc()
    app.finalize_request(error, from_error_handler=True)
    return render_template('400.html'), 400

@app.errorhandler(403)
def forbidden(error):
    app.logger.error('Forbidden')
    error_tb = traceback.format_exc()
    app.finalize_request(error, from_error_handler=True)
    return render_template('403.html'), 403

@app.errorhandler(404)
def page_not_found(error):
    app.logger.error('Page Not Found')
    error_tb = traceback.format_exc()
    app.finalize_request(error, from_error_handler=True)
    return render_template('404.html'), 404

@app.errorhandler(405)
def method_not_allowed(error):
    app.logger.error('Method Not Allowed')
    error_tb = traceback.format_exc()
    app.finalize_request(error, from_error_handler=True)
    return render_template('405.html'), 405

@app.errorhandler(429)
def too_many_requests(error):
    app.logger.error('Too Many Requests')
    error_tb = traceback.format_exc()
    app.finalize_request(error, from_error_handler=True)
    return render_template('429.html'), 429

@app.errorhandler(431)
def header_too_large(error):
    app.logger.error('Request Header Fields Too Large')
    error_tb = traceback.format_exc()
    app.finalize_request(error, from_error_handler=True)
    return render_template('431.html'), 431

# in the case of an Internal Server Error, notify someone
@app.errorhandler(500)
def inter(error):
    app.logger.error('Internal Server Error')
    error_tb = traceback.format_exc()
    app.finalize_request(error, from_error_handler=True)
    msg = Message('Internal Server Error in Flask App!', sender = 'petra095@umn.edu', recipients = ['petra095@umn.edu'])
    msg.body = "The following error logs were recovered:"
    msg.body += error_tb
    mail.send(msg)
    return render_template('500.html'), 500

@app.errorhandler(502)
def bad_gateway(error):
    app.logger.error('Bad Gateway')
    error_tb = traceback.format_exc()
    app.finalize_request(error, from_error_handler=True)
    return render_template('502.html'), 502

@app.errorhandler(503)
def service_unavailable(error):
    app.logger.error('Service Unavailable')
    error_tb = traceback.format_exc()
    app.finalize_request(error, from_error_handler=True)
    return render_template('503.html'), 503

@app.errorhandler(504)
def gateway_timeout(error):
    app.logger.error('Gateway Timeout')
    error_tb = traceback.format_exc()
    app.finalize_request(error, from_error_handler=True)
    return render_template('504.html'), 504

if __name__ == '__main__':
    app.run(debug=True)
