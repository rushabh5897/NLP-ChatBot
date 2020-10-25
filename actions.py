from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from rasa_sdk import Action
from rasa_sdk.events import SlotSet
import zomatopy
import json


class ActionSearchRestaurants(Action):
    def name(self):
        return 'action_search_restaurants'

    def run(self, dispatcher, tracker, domain):
        config = {"user_key": "f4924dc9ad672ee8c4f8c84743301af5"}
        zomato = zomatopy.initialize_app(config)
        loc = tracker.get_slot('location')
        cuisine = tracker.get_slot('cuisine')
        location_detail = zomato.get_location(loc, 1)
        d1 = json.loads(location_detail)
        lat = d1["location_suggestions"][0]["latitude"]
        lon = d1["location_suggestions"][0]["longitude"]
        ct = d1["location_suggestions"][0]["city_name"]
        cuisines_dict = {'bakery': 5, 'chinese': 25, 'cafe': 30, 'italian': 55, 'biryani': 7, 'north indian': 50,
                         'Mexican': 73,'south indian': 85}

        ct=str(ct).lower()
        flag = 0
        with open('tier1_tier2_city_list.txt') as f:
            if ct in f.read():
                flag=1

        if flag == 0:
            response = "We do not operate in that area yet"
        else:
            results = zomato.restaurant_search("", lat, lon, str(cuisines_dict.get(cuisine)), 5)
            d = json.loads(results)
            response = ""
            if d['results_found'] == 0:
                response = "no results"
            else:
                for restaurant in d['restaurants']:
                    response = response + "Found " + restaurant['restaurant']['name'] + " in " + \
                               restaurant['restaurant']['location']['address'] + "\n"

        dispatcher.utter_message("------------------------**------------------------\n" + response+"\n------------------------**------------------------\n")
        return [SlotSet('location', loc)]


class ActionSendMail(Action):
    def name(self):
        return 'action_send_mail'

    def run(self, dispatcher, tracker, domain):
        config = {"user_key": "f4924dc9ad672ee8c4f8c84743301af5"}
        zomato = zomatopy.initialize_app(config)
        loc = tracker.get_slot('location')
        cuisine = tracker.get_slot('cuisine')
        location_detail = zomato.get_location(loc, 1)
        print(location_detail)
        d1 = json.loads(location_detail)
        lat = d1["location_suggestions"][0]["latitude"]
        lon = d1["location_suggestions"][0]["longitude"]
        cuisines_dict = {'bakery': 5, 'chinese': 25, 'cafe': 30, 'italian': 55, 'biryani': 7, 'north indian': 50,
                         'Mexican': 73, 'south indian': 85}
        results = zomato.restaurant_search("", lat, lon, str(cuisines_dict.get(cuisine)), 5)
        d = json.loads(results)
        response = ""
        if d['results_found'] == 0:
            response = "no results"
        else:
            for restaurant in d['restaurants']:
                response = response + "Found : " + restaurant['restaurant']['name'] + " in " + \
                           restaurant['restaurant']['location']['address'] + "\n"

        dispatcher.utter_message("------------------------**------------------------\n" + response+"------------------------**------------------------\n")
        return [SlotSet('location', loc)]