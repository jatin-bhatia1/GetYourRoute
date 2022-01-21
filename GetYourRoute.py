import time #To generate the OAuth timestamp
import urllib.parse #To URLencode the parameter string
import hmac #To implement HMAC algorithm
import hashlib #To generate SHA256 digest
from base64 import b64encode #To encode binary data into Base64
import binascii #To convert data into ASCII
import requests #To make HTTP requests

# Some essentiel parameters 
grant_type = 'client_credentials'
oauth_consumer_key = 'Wll4MQjhC_DJqysDyt_Ovw'
oauth_nonce = str(int(time.time()*1000))
oauth_signature_method = 'HMAC-SHA256'
oauth_timestamp = str(int(time.time()))
oauth_version = '1.0'

# Combining the parameters into a single string
def create_parameter_string(grant_type, oauth_consumer_key,oauth_nonce,oauth_signature_method,oauth_timestamp,oauth_version):
    parameter_string = ''
    parameter_string = parameter_string + 'grant_type=' + grant_type
    parameter_string = parameter_string + '&oauth_consumer_key=' + oauth_consumer_key
    parameter_string = parameter_string + '&oauth_nonce=' + oauth_nonce
    parameter_string = parameter_string + '&oauth_signature_method=' + oauth_signature_method
    parameter_string = parameter_string + '&oauth_timestamp=' + oauth_timestamp
    parameter_string = parameter_string + '&oauth_version=' + oauth_version
    return parameter_string

# Encoding the parameter string 
parameter_string = create_parameter_string(grant_type, oauth_consumer_key,oauth_nonce,oauth_signature_method,oauth_timestamp,oauth_version)
encoded_parameter_string = urllib.parse.quote(parameter_string, safe='')


url = 'https://account.api.here.com/oauth2/token'
encoded_base_string = 'POST' + '&' + urllib.parse.quote(url, safe='')
encoded_base_string = encoded_base_string + '&' + encoded_parameter_string

access_key_secret = '0uZvdAqLRG2mHO164U8suB3rYuIPidWc0pnNOog2Vuz0qH_JVHQMjA9PzAmtu-4qwQzrHRuXRf65BZRla4gEvg'
signing_key = access_key_secret + '&'

# Creating signature and other parameters more secure by hashing and then converting into a base64 string
def create_signature(secret_key, signature_base_string):
    encoded_string = signature_base_string.encode()
    encoded_key = secret_key.encode()
    temp = hmac.new(encoded_key, encoded_string, hashlib.sha256).hexdigest()
    byte_array = b64encode(binascii.unhexlify(temp))
    return byte_array.decode()

oauth_signature = create_signature(signing_key, encoded_base_string)
encoded_oauth_signature = urllib.parse.quote(oauth_signature, safe='')

# Recover the access token 
def GetToken():
    body = {'grant_type' : '{}'.format(grant_type)}

    headers = {
                'Content-Type' : 'application/x-www-form-urlencoded',
                'Authorization' : 'OAuth oauth_consumer_key="{0}",oauth_nonce="{1}",oauth_signature="{2}",oauth_signature_method="HMAC-SHA256",oauth_timestamp="{3}",oauth_version="1.0"'.format(oauth_consumer_key,oauth_nonce,encoded_oauth_signature,oauth_timestamp)
            }
        
    response = requests.post(url, data=body, headers=headers, verify=False)

    # Converting the request response into json
    response_json = response.json()

    # Returning the access token 
    return response_json['access_token']

# Retriving the access token for once
access_token = GetToken()

# Recover the GPS coordinates of a city
def GetLocationCoordinates(cityName):
    Url = 'https://geocode.search.hereapi.com/v1/geocode?q={0}'.format(cityName)

    headers = {
                'Content-Type' : 'application/x-www-form-urlencoded',
                'Authorization' : 'Bearer {0}'.format(access_token)
            }

    response = requests.get(Url, headers=headers, verify=False)

    # Converting the request response into json
    response_json = response.json()

    # Recovering gps coordinates from the json response
    lattitude = response_json['items'][0]['position']['lat']
    longitude = response_json['items'][0]['position']['lng']

    # Puting gps coordinates into it's correct form
    Coordinates = '{0},{1}'.format(lattitude, longitude)

    return Coordinates


# Allow to recover the route between two cities
def GetRoute(departure, arrival):
    baseUrl = 'https://router.hereapi.com/v8/routes?'
    transportMode = 'car'
    origin = GetLocationCoordinates(departure)
    destination = GetLocationCoordinates(arrival)
    returns = 'summary'
    lang = 'fr'

    url = baseUrl + 'transportMode=' + transportMode + '&origin=' + origin + '&destination=' + destination + '&return=' + returns + '&lang=' + lang
    
    headers = {
                'Content-Type' : 'application/x-www-form-urlencoded',
                'Authorization' : 'Bearer {0}'.format(access_token)
            }

    response = requests.get(url, headers=headers, verify=False)

    # Returing the request's json response
    return response.json()


# Allow to recover the route between two cities via a third city
def GetRouteWithStopover(departure, arrival, stopover):
    baseUrl = 'https://router.hereapi.com/v8/routes?'
    transportMode = 'car'
    origin = GetLocationCoordinates(departure)
    destination = GetLocationCoordinates(arrival)
    via = GetLocationCoordinates(stopover)
    returns = 'summary'
    lang = 'fr'

    url = baseUrl + 'transportMode=' + transportMode + '&origin=' + origin + '&destination=' + destination + '&return=' + returns + '&lang=' + lang + '&via=' + via
    
    headers = {
                'Content-Type' : 'application/x-www-form-urlencoded',
                'Authorization' : 'Bearer {0}'.format(access_token)
            }

    response = requests.get(url, headers=headers, verify=False)

    # Returing the request's json response
    return response.json()
