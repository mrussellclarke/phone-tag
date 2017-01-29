import os
import httplib, urllib, base64
import json
from twilio import twiml
from twilio.rest import TwilioRestClient
from flask import Flask, request, Response

app = Flask(__name__)

#TWILIO ACCOUNT VARIABLES
account_sid="AC67763bda7bd48a1ed040b75d3f2d5793"
auth_token="99fcaa71dddeaaf5be755283231b64d4"
client = TwilioRestClient(account_sid, auth_token)

headers = {
    # Request headers
    'api_key': '500b869f49fd463bbe2186f7b4fc4996',
}

params = urllib.urlencode({
})

station_dict = {"Metro Center": "A01",
    "Farragut North": "A02",
    "Dupont Circle": "A03",
    "Woodley Park-Zoo/Adams Morgan": "A04",
    "Cleveland Park": "A05",
    "Van Ness-UDC": "A06",
    "Tenleytown-AU": "A07",
    "Friendship Heights": "A08",
    "Bethesda": "A09",
    "Medical Center": "A10",
    "Grosvenor-Strathmore": "A11",
    "White Flint": "A12",
    "Twinbrook": "A13",
    "Rockville": "A14",
    "Shady Grove": "A15",
    "Shady Grove Yard": "A99",
    "Gallery Pl-Chinatown": "B01",
    "Judiciary Square": "B02",
    "Union Station": "B03",
    "New York Ave-Florida Ave-Gallaudet U": "B35",
    "Rhode Island Ave-Brentwood": "B04",
    "Brookland-CUA": "B05",
    "Fort Totten": "B06",
    "Takoma": "B07",
    "Silver Spring": "B08",
    "Forest Glen": "B09",
    "Wheaton": "B10",
    "Glenmont": "B11",
    "Glenmont Yard": "B98",
    "Brentwood Yard": "B99",
    "Metro Center": "C01",
    "McPherson Sq": "C02",
    "Farragut West": "C03",
    "Foggy Bottom-GWU": "C04",
    "Rosslyn": "C05",
    "Arlington Cemetery": "C06",
    "Pentagon": "C07",
    "Pentagon City": "C08",
    "Crystal City": "C09",
    "Ronald Reagan Washington National Airport": "C10",
    "Potomac Yard": "C11",
    "Braddock Road": "C12",
    "King Street": "C13",
    "Eisenhower Ave": "C14",
    "Huntington": "C15",
    "C & J Junction": "C97",
    "Alexandria Yard Leads": "C98",
    "Alexandria Yard": "C99",
    "Federal Triangle": "D01",
    "Smithsonian": "D02",
    "L'Enfant Plaza": "D03",
    "Federal Center SW": "D04",
    "Capitol South": "D05",
    "Eastern Market": "D06",
    "Potomac Ave": "D07",
    "Stadium-Armory": "D08",
    "Minnesota Ave": "D09",
    "Deanwood": "D10",
    "Cheverly": "D11",
    "Landover": "D12",
    "New Carrolton": "D13",
    "New Carrolton Yard": "D99",
    "Mt Vernon Sq/7th St-Convention Center": "E01",
    "Shaw-Howard U": "E02",
    "U St/African-Amer Civil War Memorial/Cardozo": "E03",
    "Columbia Heights": "E04",
    "Georgia Ave-Petworth": "E05",
    "Fort Totten": "E06",
    "West Hyattsville": "E07",
    "Prince George's Plaza": "E08",
    "College Park-U of MD": "E09",
    "Greenbelt": "E10",
    "Greenbelt Yard": "E99",
    "Gallery Pl-Chinatown": "F01",
    "Archives-Navy Mem'l-Penn Quarter": "F02",
    "L'Enfant Plaza": "F03",
    "Waterfront-SEU": "F04",
    "Navy Yard": "F05",
    "Anacostia": "F06",
    "Congress Heights": "F07",
    "Southern Ave": "F08",
    "Naylor Road": "F09",
    "Suitland": "F10",
    "Branch Avenue": "F11",
    "Branch Avenue Yard": "F99",
    "Benning Road": "G01",
    "Capitol Heights": "G02",
    "Addison Road-Seat Pleasant": "G03",
    "Morgan Boulevard": "G04",
    "Largo Town Center": "G05",
    "Quaker Lane": "J01",
    "Van Dorn Street": "J02",
    "Franconia-Springfield": "J03",
    "Court House": "K01",
    "Clarendon": "K02",
    "Virginia Sq-GMU": "K03",
    "Ballston-MU": "K04",
    "East Falls Church": "K05",
    "West Falls Church-VT/UVA": "K06",
    "Dunn Loring-Merrifield": "K07",
    "Vienna/Fairfax-GMU": "K08",
    "Falls Church Yard": "K99",
    "McLean": "N01",
    "Tysons Corner": "N02",
    "Greensboro": "N03",
    "Spring Hill": "N04",
    "Wiehle - Reston East": "N06"
}

#FUNCTION THAT GETS JSON STATION DATA FROM WMATA API
def raw_stn_data(staco):
    try:
        conn = httplib.HTTPSConnection('api.wmata.com')
        conn.request("GET", "/StationPrediction.svc/json/GetPrediction/%s?%s" %(staco, params), "{body}", headers)
        response = conn.getresponse()
        data = response.read()
        conn.close()
        return data
    except Exception as e:
        return ("[Errno {0}] {1}".format(e.errno, e.strerror))

#CHECKS IF DESIRED STATION IS IN THE STATION LIST
#FORMATS JSON DATA TO STRING WITH TIME AND LINE OF NEXT TRAINS
def next_train(station):
    for s in station_dict:
        if station in s:
            stn_time = []
            loc_dict = json.loads(raw_stn_data(station_dict[s]))

            for i in loc_dict["Trains"]:
                temp_str = "%s %s" %(i["DestinationName"], i["Min"])
                stn_time.append(temp_str)

            res_str = ', '.join(stn_time)
            return res_str


    return "\'%s\' is not a station" %station

#TWILIO SEND MESSAGE FUNCTION
#MSG MUST BE IN STRING FORMAT
#NUM MUST BE IN STRING FORMAT
def send_msg(msg, num):
    client.messages.create( from_='+18623079228',
                            to='+1%s' %num,
                            body=msg)

@app.route("/")
def check_app():
    # returns a simple string stating the app is working
    return "Phone-tag is live!"

@app.route("/twilio", methods=["POST"])
def inbound_sms():
    response = twiml.Response()
    # we get the SMS message from the request. we could also get the
    # "To" and the "From" phone number as well
    inbound_message = request.form.get("Body")
    # we can now use the incoming message text in our Python application
    response.message(next_train(inbound_message))
    #if inbound_message == "Hello":
    #    response.message("Hello back to you!")
    #else:
    #    response.message("Hi! Not quite sure what you meant, but okay.")
    # we return back the mimetype because Twilio needs an XML response
    return Response(str(response), mimetype="application/xml"), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
