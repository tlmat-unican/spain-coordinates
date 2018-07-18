from flask import Flask, request, jsonify
import json
import pyproj

app = Flask(__name__)

# Define the projections using EPSG codes, check spatialreference.org for help
ED50_UTM30N = pyproj.Proj(init="EPSG:23030", nadgrids="./ntv2_grids/penr2009.gsb") # Add the shift grid with nadgrids option
WGS84 = pyproj.Proj(init="epsg:4326")

class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

@app.route("/", methods=['GET', 'POST'])
def transform():
    if request.method == 'GET':
        return do_get()
    else:
        return do_post()

def do_get():
    ED50_x = request.args.get('x')
    ED50_y = request.args.get('y')
    if ED50_x is None or ED50_x == '' or ED50_y is None or ED50_y == '':
        raise InvalidUsage('Must set both x and y query params', status_code=400)
    else:
        WGS84_long, WGS84_lat = pyproj.transform(ED50_UTM30N, WGS84, ED50_x, ED50_y)
        return jsonify(WGS84_long, WGS84_lat)

def do_post():
    if request.content_type != 'application/json':
        raise InvalidUsage('Only accepts application/json', status_code=415)
    json_data = request.get_json()
    isInstance(json_data, list)
    print(json_data);
    output = []
    for coordinates in json_data:
        ED50_x = coordinates[0]
        ED50_y = coordinates[1]
        WGS84_long, WGS84_lat = pyproj.transform(ED50_UTM30N, WGS84, ED50_x, ED50_y)
        output.append([WGS84_long, WGS84_lat])

    return json.dumps(output)
   

# # Do the transformation:
# ED50_x = 433829.9531810064
# ED50_y = 4811755.325688820
# ETRS89_x, ETRS89_y = pyproj.transform(ED50_UTM30N, WGS84, ED50_x, ED50_y)

# print ("ETRS89 UTM zone 30 coordinates = (%0.8f, %0.8f)" % (ETRS89_x, ETRS89_y))
#ETRS89 UTM zone 30 coordinates = (3,81917591, 43,45391861)



 
