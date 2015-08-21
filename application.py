import json
from datetime import datetime
from random import sample

from flask import Flask
from factual import Factual
from flask import Response, request

from __init__ import __version__, __author__
from utils import find_closest_factual_id, find_smart_location, form_geo_query, get_restaurants
from middleware import validate_json
from factual_credentials import key, secret

application = Flask(__name__)

@application.route('/')
def version():
    return Response(json.dumps({'version': __version__,
            'status': 'live',
            'author': '{author}'.format(author=__author__),
            'datetime': datetime.now().isoformat()}), mimetype='application/json')


@application.route('/task1/<location>/<search_string>')
def task1(location, search_string):
    """
    :param location: location around which the restaurants are required
    :param search_string: keyword searched, e.g., coffee, thai, indian
    :return: 5 restaurants or cafes ordered by distance from the place

    If the location returns multiple results, the location closest to the ip of the search device is used.
    If a unique location can't be found in such a situation, a regions based results can be returned.
    """
    factual = Factual(key=key, secret=secret)

    # get the nearest location
    nearest_location = find_smart_location(factual, location)

    if 'Error' in nearest_location:
        return Response(json.dumps(
            {'Error': 'No location of that name or postcode found. '
                      'Please check the location or postcode name and try again.'}
            ),
            mimetype='application/json'
        ), 400

    # form the initial query based on geo location
    query = form_geo_query(factual, lat=nearest_location['latitude'], lon=nearest_location['longitude'])
    # add the filters
    query = query.search('{}'.format(search_string)).filters({"category_ids": {"$includes": 338}})
    data = query.data()

    if len(data):
        return Response(json.dumps(data),  mimetype='application/json')
    else:
        return Response(json.dumps(
            {'Error': 'The search returned no match. Please change the location or search string and try again.'}),
            mimetype='application/json'
        ), 400


@application.route('/task2/<location>/<meal_of_the_day>', methods=['POST'])
@validate_json
def task2(location, meal_of_the_day):
    """
    :param location: location around which the restaurants are looked up
    :param meal_of_the_day: the meal of the day, i.e., lunch, dinner, breakfast etc.
    :return: json body with 5 restaurants that meet the criteria
    # we can take many approaches to match the restaurants:
    # 1. We can take a attributes based approach, i.e., likes, dislikes, requirements of all individuals
    # 2. We can take an individual based approach, i.e., each person's likes, dislikes, and requirements at a time
    # 3. Possibly combine the weighted score of the first two approaches
    I am demonstrating a hybrid approach where the personal likes are checked for three people
    """
    factual = Factual(key=key, secret=secret)
    individuals = request.get_json()

    # get the nearest location
    nearest_location = find_smart_location(factual, location)

    if 'Error' in nearest_location:
        return Response(json.dumps(
            {'Error': 'No location of that name or postcode found. '
                      'Please check the location or postcode name and try again.'}
            ),
            mimetype='application/json'
        ), 400

    # initiate query with geo location search
    query = form_geo_query(factual, lat=nearest_location['latitude'], lon=nearest_location['longitude'])

    try:
        data = get_restaurants(individuals, meal_of_the_day, query)
    except:
        return Response(json.dumps(
            {'Error': 'An error occurred. Please try using one of breakfast, lunch, or dinner'}
            ), mimetype='application/json'
        )
    if len(data) > 4:  # if at least 5 results are found, return
        return Response(json.dumps(data), mimetype='application/json')

    return Response(json.dumps({'Error': 'No matching restaurant found. Please try again.'}),
                    mimetype='application/json'), 400


if __name__ == '__main__':
    application.run(debug=True)