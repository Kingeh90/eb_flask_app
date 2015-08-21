#!/usr/bin/env python
__author__ = 'sudipta'
from urllib2 import urlopen
import json
from collections import namedtuple
import numpy as np
from random import sample
from difflib import get_close_matches

url = 'http://ip-api.com/json'
Location = namedtuple('Location', 'region, city, latitude, longitude')


def get_current_device_location_by_ip():
    """
    Automatically geolocate the connecting IP
    :return: Location, a namedtuple, or error dict
    """
    try:
        response = urlopen(url).read()
        response = json.loads(response)
        return Location(**{'region': response['region'], 'city': response['city'],
                           'latitude': response['lat'], 'longitude': response['lon']})
    except:
        return {'Error': 'the device locations lookup was not successful'}


def find_closest_factual_id(locations):
    """
    :param locations: the list of locations using find_named_locations()
    :return: the nearest location closest to the connecting device id,
    If the ip can not be located, returns the original list of locations.
    """
    nearest_location = locations[0]  # use the first location returned by Factual
    nearest_location_by_ip = get_current_device_location_by_ip()

    if 'Error' in nearest_location_by_ip:  # if the ip based location lookup failed
        #  should log this error
        return nearest_location

    a = np.array((nearest_location_by_ip.latitude, nearest_location_by_ip.longitude))
    dis = 1.0e6
    try:
        for ii in range(len(locations)):
            b = np.array((locations[ii]['latitude'], locations[ii]['longitude']))
            new_dis = np.linalg.norm(a - b)
            if new_dis < dis:
                dis = new_dis
                nearest_location = locations[ii]
    except Exception as e:
        print e   # this should be logged
    return nearest_location


def find_smart_location(factual, location):
    """
    :param factual: Factual class instance
    :param location: location to be found on factual database
    :return: the best matched location
    The best location is decided based on two different strategies depending on the situation.

    If a factual database filter returns multiple matches, then the location is chosen based on closet to device ip.
    Otherwise, if no direct match is found in the database, a likelihood search on the factual database decides the
     location. The top of the list returned by factual database search is chosen in this case.
    """

    locations = factual.table('world-geographies').filters(
            {'$and': [{'name': {'$eq': '{}'.format(location)}},
                      {'country': {'$eq': 'AU'}}
                      ]}
            ).select('name, factual_id, latitude, longitude, parent').data()

    ''' if multiple places are returned, choose based on device id, else let factual's smarts decide the place'''
    if len(locations):  # if multiple places are returned, choose based on device id
        return find_closest_factual_id(locations)
    else:  # let factual's smarts decide the place
        locations = factual.table('world-geographies').filters(
            {'$and': [{'country': {'$eq': 'AU'}}
                      ]}
            ).search('{}'.format(location)).select('name, factual_id, latitude, longitude, parent').data()
        if len(locations):
            return locations[0]  # let the location returned by Factual be the best location
        else:
            return {'Error': 'No location was found'}


def form_geo_query(factual, lat, lon, radius=20000):
    """
    :param factual: the factual class instance
    :param lat: latitude of the location
    :param lon: longitude of the location
    :param radius: radius in which the restaurants are required
    :return: query for Australian restaurants that meet geo criteria
    """
    c = {'$circle': {'$center': [lat, lon], '$meters': radius}}
    return factual.table('restaurants-au').geo(c).sort('$distance').limit(5).threshold('confident')


def check_data_len(data):
    if len(data) > 4:
        return True
    else:
        return False


def check_likes_or_dislikes(individuals, query, filter_string, likes, likes_or):
    number_of_individuals = len(individuals)
    for n in range(number_of_individuals, 0, -1):
        data = []
        # try and few different combinations of the individuals, the number of combinations tried increases with
        # a lower number of individuals selected
        for j in range(n*(number_of_individuals - n) + 1):
            likes_temp = sample(likes, n)  # take n random individuals
            filter_string_temp = [fs for fs in filter_string]
            for l in likes_temp:
                l = filter(None, l)  # check if only None in the list, i.e., when a like is not provided in the json
                if l:
                    if likes_or == 'likes':
                        filter_string_temp.append({'category_labels': {'$includes_any': l}})
                    elif likes_or == 'dislikes':
                        filter_string_temp.append({'category_labels': {'$excludes_any': l}})
                    else:
                        for li in l:
                            filter_string_temp.append({"options_{}".format(li): {"$eq": "true"}})

            data_temp = query.filters({'$and': filter_string_temp}).data()
            if check_data_len(data_temp):
                data = data_temp
                break
        if check_data_len(data):
            filter_string = filter_string_temp
            break
    return filter_string


def get_restaurants(individuals, meal_of_the_day, query):
    """
    :param individuals: list of individuals
    :param meal_of_the_day: meal of the day, must be either breakfast, lunch, or dinner.
    :param query: query to be appended to
    :return: list of restaurants based on individuals' like/dislikes/requirements
    """

    # list of factual supported options
    supported_requirements = ['vegetarian', 'vegan', 'glutenfree', 'lowfat', 'organic', 'healthy']

    # start with restaurants that are open for the particular meal_of_the_day
    filter_string = [{"meal_{}".format(meal_of_the_day): {"$eq": "true"}}]

    data = []
    likes = map(lambda x: x['likes'] if 'likes' in x else [None], individuals)
    dislikes = map(lambda x: x['dislikes'] if 'dislikes' in x else [None], individuals)
    requirements = map(lambda x:
                       get_close_matches(x['requirements'], supported_requirements, n=1, cutoff=0.5)
                       if 'requirements' in x else [None], individuals)

    # check likes
    filter_string = check_likes_or_dislikes(individuals, query, filter_string, likes, likes_or='likes')

    # and dislikes
    # TODO(): improve the dislikes discards
    filter_string = check_likes_or_dislikes(individuals, query, filter_string, dislikes, likes_or='dislikes')

    # Then check requirements
    filter_string = check_likes_or_dislikes(individuals, query, filter_string, requirements, likes_or='requirements')

    data = query.filters({'$and': filter_string}).data()
    return data
