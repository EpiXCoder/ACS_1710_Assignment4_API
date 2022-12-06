import os
import requests

from pprint import PrettyPrinter
from datetime import datetime, timedelta
from dotenv import load_dotenv
from flask import Flask, render_template, request, send_file
from geopy.geocoders import Nominatim


################################################################################
## SETUP
################################################################################

app = Flask(__name__)

# Get the API key from the '.env' file
load_dotenv()

pp = PrettyPrinter(indent=4)

API_KEY = os.getenv('API_KEY')
API_URL = 'http://api.openweathermap.org/data/2.5/weather'
WEATHER_ICON_URL = 'http://openweathermap.org/img/wn/'

################################################################################
## ROUTES
################################################################################

@app.route('/')
def home():
    """Displays the homepage with forms for current or historical data."""
    context = {
        'min_date': (datetime.now() - timedelta(days=5)),
        'max_date': datetime.now()
    }
    return render_template('home.html', **context)

def get_letter_for_units(units):
    """Returns a shorthand letter for the given units."""
    return 'F' if units == 'imperial' else 'C' if units == 'metric' else 'K'

def get_weather_info(city, units):
    params = {
    'appid': API_KEY,
    'q': city,
    'units': units,
    }
    result_json = requests.get(API_URL, params=params).json()
    return result_json

def difference(city1, city2, weather_component):
    difference = city1 - city2
    if difference > 0:
        if weather_component == 'temp':
            comparison = 'warmer'
        elif weather_component == 'wind' or weather_component == 'humidity':
            comparison = 'greater'
        else:
            difference = (difference / 3600)
            comparison = 'later'
    else:
        difference = difference * -1
        if weather_component == 'temp':
            comparison = 'colder'
        elif weather_component == 'wind' or weather_component == 'humidity':
            comparison = 'less'
        else:
            difference = (difference / 3600)
            comparison = 'earlier'
    difference = round(difference, 2)
    return [difference, comparison]

@app.route('/results')
def results():
    """Displays results for current weather conditions."""
    # TODO: Use 'request.args' to retrieve the city & units from the query
    # parameters.
    city = request.args.get('city')
    units = request.args.get('units')

    result_json = get_weather_info(city, units)

    # Uncomment the line below to see the results of the API call!
    pp.pprint(result_json)

    # TODO: Replace the empty variables below with their appropriate values.
    # You'll need to retrieve these from the result_json object above.

    # For the sunrise & sunset variables, I would recommend to turn them into
    # datetime objects. You can do so using the `datetime.fromtimestamp()` 
    # function.
    context = {
        'date': datetime.now().strftime('%A, %B %d, %Y'),
        'city': result_json['name'],
        'description':result_json['weather'][0]["description"],
        'temp': result_json['main']['temp'],
        'humidity': result_json['main']['humidity'],
        'wind_speed': result_json['wind']['speed'],
        'sunrise': datetime.fromtimestamp(result_json['sys']['sunrise']),
        'sunset': datetime.fromtimestamp(result_json['sys']['sunset']),
        'units_letter': get_letter_for_units(units),
        'icon': WEATHER_ICON_URL+result_json['weather'][0]['icon']+'@2x.png'
    }

    return render_template('results.html', **context)


@app.route('/comparison_results')
def comparison_results():
    """Displays the relative weather for 2 different cities."""
    # TODO: Use 'request.args' to retrieve the cities & units from the query
    # parameters.
    city1 = request.args.get('city1')
    city2 = request.args.get('city2')
    units = request.args.get('units')


    # TODO: Make 2 API calls, one for each city. HINT: You may want to write a 
    # helper function for this!
    city1_result_json = get_weather_info(city1, units)
    city2_result_json = get_weather_info(city2, units)
    pp.pprint(city1_result_json)
    pp.pprint(city2_result_json)

    temp_diff = None
    humidity_diff = None
    wind_diff = None
    sunset_diff = None

    if city1 and city2:
        temp_diff = difference(city1_result_json['main']['temp'], city2_result_json['main']['temp'],'temp')
        humidity_diff = difference(city1_result_json['main']['humidity'], city2_result_json['main']['humidity'],'humidity')
        wind_diff = difference(city1_result_json['wind']['speed'], city2_result_json['wind']['speed'],'wind')
        sunset_diff = difference(city1_result_json['sys']['sunset'], city2_result_json['sys']['sunset'],'sunset')

    # TODO: Pass the information for both cities in the context. Make sure to
    # pass info for the temperature, humidity, wind speed, and sunset time!
    # HINT: It may be useful to create 2 new dictionaries, `city1_info` and 
    # `city2_info`, to organize the data.
    context = {
        'units_letter': get_letter_for_units(units),
        'date': datetime.now().strftime('%A, %B %d, %Y'),
        'temp_diff': temp_diff,
        'humidity_diff': humidity_diff,
        'wind_diff': wind_diff,
        'sunset_diff': sunset_diff,
        'city1_data': {
                'city': city1_result_json['name'],
                'description': city1_result_json['weather'][0]['description'],
                'temp': city1_result_json['main']['temp'],
                'humidity': city1_result_json['main']['humidity'],
                'wind_speed': city1_result_json['wind']['speed'],
                'sunrise': datetime.fromtimestamp(city1_result_json['sys']['sunrise']),
                'sunset': datetime.fromtimestamp(city1_result_json['sys']['sunset']),
                'icon': WEATHER_ICON_URL+city1_result_json['weather'][0]['icon']+'@2x.png',
            },
            'city2_data': {
                'city': city2_result_json['name'],
                'description': city2_result_json['weather'][0]['description'],
                'temp': city2_result_json['main']['temp'],
                'humidity': city2_result_json['main']['humidity'],
                'wind_speed': city2_result_json['wind']['speed'],
                'sunrise': datetime.fromtimestamp(city2_result_json['sys']['sunrise']),
                'sunset': datetime.fromtimestamp(city2_result_json['sys']['sunset']),
                'icon': WEATHER_ICON_URL+city2_result_json['weather'][0]['icon']+'@2x.png',
            }
    }

    return render_template('comparison_results.html', **context)


if __name__ == '__main__':
    app.config['ENV'] = 'development'
    app.run(debug=True, port=3000)
