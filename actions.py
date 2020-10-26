from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import json
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from rasa_sdk import Action
from rasa_sdk.events import SlotSet

import zomatopy


class ActionSearchRestaurants(Action):
    def name(self):
        return 'action_search_restaurants'

    def run(self, dispatcher, tracker, domain):
        config = {"user_key": "e1def62de91816d1dce4cda2c2b39ca5"}
        zomato = zomatopy.initialize_app(config)
        loc = tracker.get_slot('location')
        cuisine = tracker.get_slot('cuisine')
        location_detail = zomato.get_location(loc, 1)
        d1 = json.loads(location_detail)
        try:
            lat = d1["location_suggestions"][0]["latitude"]
            lon = d1["location_suggestions"][0]["longitude"]
            ct = d1["location_suggestions"][0]["city_name"]
        except IndexError:
            dispatcher.utter_message(
                "--------------------**--------------------\n" + "I am not able understand your location, Please try again" + "--------------------**--------------------\n")
            return [SlotSet('flag_response', False)]

        cuisines_dict = {'bakery': 5, 'chinese': 25, 'cafe': 30, 'italian': 55, 'biryani': 7, 'north indian': 50,
                         'south indian': 85, 'thai': 95, 'mexican': 73}
        dispatcher.utter_message("--ct--" + ct)

        if not ct:
            dispatcher.utter_message(
                "--------------------**--------------------\n" + "I am not able understand your location, Please try again" + "--------------------**--------------------\n")
            return [SlotSet('flag_response', False)]
        else:
            ct = ct.lower()
        if not self.checkCityAvailable(ct):
            response = "We do not opearate in this city yet"
            dispatcher.utter_message(
                "--------------------**--------------------\n" + response + "--------------------**--------------------\n")
            return [SlotSet('flag_response', False)]
        else:
            results = zomato.restaurant_search("", lat, lon, str(cuisines_dict.get(cuisine)), 5)
            d = json.loads(results)
            response = ""
            if d['results_found'] == 0:
                response = "Extremely Sorry !!! I'm not able to find any related results to your query \n"
                dispatcher.utter_message(
                    "--------------------**--------------------\n" + response + "--------------------**--------------------\n")
                return [SlotSet('flag_response', False)]
            else:
                for restaurant in d['restaurants']:
                    response = response + "Found " + restaurant['restaurant']['name'] + " in " + \
                               restaurant['restaurant']['location']['address'] + " has been rated " + \
                               restaurant['restaurant']['user_rating']['aggregate_rating'] + "\n"

                dispatcher.utter_message(
                    "--------------------**--------------------\n" + response + "--------------------**--------------------\n")
                return [SlotSet('flag_response', True)]

    def checkCityAvailable(self, ct):
        tier1_tier2_city_list = ["ahmedabad", "bengaluru", "chennai", "delhi ncr", "hyderabad", "kolkata", "mumbai",
                                 "pune", "agra", "ajmer", "aligarh", "amravati", "amritsar", "asansol", "aurangabad",
                                 "bareilly", "belgaum", "bhavnagar", "bhiwandi", "bhopal", "bhubaneswar", "bikaner",
                                 "bilaspur", "bokaro steel city", "chandigarh", "coimbatore", "cuttack", "dehradun",
                                 "dhanbad", "bhilai", "durgapur", "dindigul", "erode", "faridabad", "firozabad",
                                 "ghaziabad", "gorakhpur", "gulbarga", "guntur", "gwalior", "gurgaon", "guwahati",
                                 "hamirpur", "hubli–dharwad", "indore", "jabalpur", "jaipur", "jalandhar", "jammu",
                                 "jamnagar", "jamshedpur", "jhansi", "jodhpur", "kakinada", "kannur", "kanpur",
                                 "karnal", "kochi", "kolhapur", "kollam", "kozhikode", "kurnool", "ludhiana", "lucknow",
                                 "madurai", "malappuram", "mathura", "mangalore", "meerut", "moradabad", "mysore",
                                 "nagpur", "nanded", "nashik", "nellore", "noida", "patna", "pondicherry", "purulia",
                                 "prayagraj", "raipur", "rajkot", "rajahmundry", "ranchi", "rourkela", "salem",
                                 "sangli", "shimla", "siliguri", "solapur", "srinagar", "surat", "thanjavur",
                                 "thiruvananthapuram", "thrissur", "tiruchirappalli", "tirunelveli", "ujjain",
                                 "bijapur", "vadodara", "varanasi", "vasai-virar city", "vijayawada", "visakhapatnam",
                                 "vellore", "warangal"]

        if ct in tier1_tier2_city_list:
            return True
        else:
            return False


class ActionSendMail(Action):
    def name(self):
        return 'action_send_mail'

    def run(self, dispatcher, tracker, domain):
        config = {"user_key": "e1def62de91816d1dce4cda2c2b39ca5"}
        zomato = zomatopy.initialize_app(config)
        loc = tracker.get_slot('location')
        cuisine = tracker.get_slot('cuisine')
        location_detail = zomato.get_location(loc, 1)
        d1 = json.loads(location_detail)
        if d1["location_suggestions"] is None :
            dispatcher.utter_message(
                "--------------------**--------------------\n" + "I am not able understand your location, Please try again" + "--------------------**--------------------\n")
            return [SlotSet('flag_response', False)]
        lat = d1["location_suggestions"][0]["latitude"]
        lon = d1["location_suggestions"][0]["longitude"]
        cuisines_dict = {'bakery': 5, 'chinese': 25, 'cafe': 30, 'italian': 55, 'biryani': 7, 'north indian': 50,
                         'south indian': 85, 'thai': 95, 'mexican': 73}
        results = zomato.restaurant_search("", lat, lon, str(cuisines_dict.get(cuisine)), 10)
        d = json.loads(results)
        response = ""
        if not lat:
            dispatcher.utter_message(
                "--------------------**--------------------\n" + "I am not able understand your location, Please try again" + "--------------------**--------------------\n")
            return [SlotSet('flag_response', False)]
        if d['results_found'] == 0:
            response = "Extremely Sorry !!! I'm not able to find any related results to your query \n"
            dispatcher.utter_message(
                "--------------------**--------------------\n" + response + "--------------------**--------------------\n")

        else:
            for restaurant in d['restaurants']:
                response = response + "<h2>" + restaurant['restaurant']['name'] + "</h2><ul><li><b>" + \
                "Restaurant locality address : </b>" + restaurant['restaurant']['location']['address'] + "</li><li><b>" +\
                "Average budget for two people: " + restaurant['restaurant']['average_cost_for_two'] +\
                "</b></li><li><b>Zomato user rating :</b>" +restaurant['restaurant']['user_rating']['aggregate_rating'] + "</li></ul> </br>"

            sender_email = "chatbotatyourhelp@gmail.com"
            receiver_email = tracker.get_slot('user_email_id')
            # receiver_email = "rushabhpsancheti@gmail.com"
            password = "chatbot123"
            dispatcher.utter_message("--receiver_email---" + receiver_email)
            message = MIMEMultipart("alternative")
            message["Subject"] = "multipart test"
            message["From"] = sender_email
            message["To"] = receiver_email
            # response = "<h1>Hello</h1>"
            # Create the plain-text and HTML version of your message
            text = """\
                        Hi,
                        Hope you are doing well"""
            html = """\
                        <html>
                          <body>
                            <>You can choose one of the option for your restuarant<>
                               """ + response + """
                            </p>
                          </body>
                        </html>
                        """

            # Turn these into plain/html MIMEText objects
            part1 = MIMEText(text, "plain")
            part2 = MIMEText(html, "html")

            # Add HTML/plain-text parts to MIMEMultipart message
            # The email client will try to render the last part first
            message.attach(part1)
            message.attach(part2)

            # Create secure connection with server and send email
            context = ssl.create_default_context()
            try:
                with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                    server.login(sender_email, password)
                    server.sendmail(
                        sender_email, receiver_email, message.as_string()
                    )
                dispatcher.utter_message("Mail Sent Successfully")
            except smtplib.SMTPException as e:
                dispatcher.utter_message("You have provided incorrect email ID")

        # dispatcher.utter_message("-----" + response)
        # return [SlotSet('location', loc)]
