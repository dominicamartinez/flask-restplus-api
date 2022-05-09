import json
import re
import time
from datetime import datetime, timedelta
import zoneinfo
import werkzeug, flask.scaffold
werkzeug.cached_property = werkzeug.utils.cached_property
flask.helpers._endpoint_from_view_func = flask.scaffold._endpoint_from_view_func
from flask_restplus import Api, Resource, reqparse, inputs
from flask import Flask, request

WEEKDAY_XREF = {"mon":0,"tues":1,"wed":2,"thurs":3,"fri":4,"sat":5,"sun":6}

app = Flask(__name__)
api = Api(app, version='1.0', title='BE Take Home API',
    description='An API that allows a user to enter a date time range and get back the price at which they would be charged to park for that time span.',
)
app.config['last_price_query'] = 0
app.config['avg_price_query'] = []

########### METHODS ##############################################

def appendPriceQueryRuntime(query_runtime):
    if len(app.config['avg_price_query']) < 100:
        app.config['avg_price_query'].append(query_runtime)
    if len(app.config['avg_price_query']) == 100:
        trash = app.config['avg_price_query'].pop(0)
        app.config['avg_price_query'].append(query_runtime)

def verifyData(rates_input):
    for rates_detail in rates_input:

        # Validate day values
        days = rates_detail['days'].split(',')
        for d in days:
            if d not in WEEKDAY_XREF.keys():
                return False

        # Validate times (in order - string, valid time, valid chronologically start/end)
        if (bool(re.match("[0-2][0-9][0-5][0-9]-[0-2][0-9][0-5][0-9]", rates_detail['times']))):
            try:
                test_dt1 = datetime.strptime(rates_detail['times'].split('-')[0],'%H%M')
                test_dt2 = datetime.strptime(rates_detail['times'].split('-')[1],'%H%M')
                if (test_dt1 >= test_dt2):
                    return False
            except:
                return False
        else:
            return False

        # Validate price
        if (not str(rates_detail['price']).isnumeric()):
            return False
        
        # Validate timezones
        if (rates_detail['tz'] not in zoneinfo.available_timezones()):
            return False
    return True

def parseData(rates_input):
    rates = {}
    for rates_detail in rates_input:
        if rates_detail['tz'] not in rates.keys():
            rates[rates_detail['tz']] = {}

    for rates_detail in rates_input:
        days = rates_detail["days"].split(',')
        for day in days:
            if WEEKDAY_XREF[day] not in rates[rates_detail['tz']].keys():
                rates[rates_detail['tz']][WEEKDAY_XREF[day]] = []

    for rates_detail in rates_input:
        days = rates_detail["days"].split(',')
        times = rates_detail["times"].split('-')
        for day in days:
            rates[rates_detail['tz']][WEEKDAY_XREF[day]].append({
                "start_hour":int(times[0][0:2]), "start_min":int(times[0][2:]),
                "end_hour":int(times[1][0:2]), "end_min":int(times[1][2:]), 
                "price":rates_detail['price']})
    return rates

# Initial loading of data
with open('initialRates.json') as f:   
    app.config['rates_input'] = json.load(f)
if (verifyData(app.config['rates_input']['rates'])):
    app.config['rates'] = parseData(app.config['rates_input']['rates'])

########### RATES ENDPOINT ##############################################

rates_parser = reqparse.RequestParser()
rates_parser.add_argument('json', location='json', required=True)

@api.route('/rates')
class MyRates(Resource):
    def get(self):
        return app.config['rates_input']

    @api.doc(responses={
        200: 'Success',
        400: 'Validation Error'
    })
    @api.expect(rates_parser, validate=True)
    def put(self):
        try:
            if (verifyData(request.json['rates'])):
                app.config['rates_input'] = request.json
                app.config['rates'] = parseData(app.config['rates_input']['rates'])
                return "success"
        except:
            return "Data Validation Error", 400
        return "Data Validation Error", 400


##########################################################################
########### PRICE ENDPOINT #############################################

price_parser = reqparse.RequestParser()
price_parser.add_argument('start', location='args', type=inputs.datetime_from_iso8601, required=True)
price_parser.add_argument('end', location='args', type=inputs.datetime_from_iso8601, required=True)

@api.route('/price')
class MyPrice(Resource):
    @api.doc(parser=price_parser,
    params={
        "start": "start date/times as ISO-8601 with timezones",
        "end":"end date/times as ISO-8601 with timezones"
    }, 
    responses={
        200: 'Success',
        400: 'Validation Error'
    })
    def get(self):
        start_time = time.time()
        args = price_parser.parse_args(strict=True)
        for key in app.config['rates'].keys():
            new_dt_start = args['start'].astimezone(zoneinfo.ZoneInfo(key))
            new_dt_end = args['end'].astimezone(zoneinfo.ZoneInfo(key))

            # Assumption: Input values are within the same day
            if (new_dt_start.weekday() == new_dt_end.weekday()):
                if new_dt_start.weekday() in app.config['rates'][key].keys():
                    for t in app.config['rates'][key][new_dt_start.weekday()]:
                        if (t['start_hour'] <= new_dt_start.hour and t['start_min'] <= new_dt_start.minute):
                            if (new_dt_end.hour < t['end_hour']):
                                app.config['last_price_query'] = time.time() - start_time
                                appendPriceQueryRuntime(app.config['last_price_query'])
                                return {"price":t['price']}
                            if (new_dt_end.hour == t['end_hour']): # verify minutes are less than
                                if (new_dt_end.minute <= t['end_min']):
                                    app.config['last_price_query'] = time.time() - start_time
                                    appendPriceQueryRuntime(app.config['last_price_query'])
                                    return {"price":t['price']}

        app.config['last_price_query'] = time.time() - start_time
        appendPriceQueryRuntime(app.config['last_price_query'])
        return "unavailable"


##########################################################################
########### INFO ENDPOINT #############################################

@api.route('/info')
class MyInfo(Resource):
    def get(self):
        if len(app.config['avg_price_query']) > 0:
            avg = sum(app.config['avg_price_query'])/len(app.config['avg_price_query'])
        else:
            avg = 0

        return {"status":"up","ver":"1.0",
            "last_price_query_runtime_sec":app.config['last_price_query'],
            "last_100_price_query_runtime_avg_sec":avg
            }


##########################################################################

if __name__ == '__main__':
    app.run(host='0.0.0.0')