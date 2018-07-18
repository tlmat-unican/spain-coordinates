import os

from flask import Flask, request, jsonify
import json
import pyproj

app = Flask(__name__)

# Define the projections using EPSG codes, check spatialreference.org for help
# Add the shift grid with nadgrids option
ZONES = {
    "29N": pyproj.Proj(init="EPSG:23029", nadgrids="./ntv2_grids/PENR2009.gsb"),
    "30N": pyproj.Proj(init="EPSG:23030", nadgrids="./ntv2_grids/PENR2009.gsb"),
    "31N": pyproj.Proj(init="EPSG:23031", nadgrids="./ntv2_grids/PENR2009.gsb,./ntv2_grids/BALR2009.gsb ")
}

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

@app.route("/<zone>", methods=['GET', 'POST'])
def transform(zone):
    if zone not in ZONES:
        raise InvalidUsage('Not valid zone for Spain.', status_code=404)

    if request.method == 'GET':
        return do_get(ZONES[zone])
    else:
        return do_post(ZONES[zone])

def do_get(ED50_zone):
    ED50_x = request.args.get('x')
    ED50_y = request.args.get('y')
    if ED50_x is None or ED50_x == '' or ED50_y is None or ED50_y == '':
        raise InvalidUsage('Must set both x and y query params.', status_code=400)
    else:
        WGS84_long, WGS84_lat = pyproj.transform(ED50_zone, WGS84, ED50_x, ED50_y)
        return jsonify(WGS84_long, WGS84_lat)

def do_post(ED50_zone):
    if request.content_type != 'application/json':
        raise InvalidUsage('Only accepts application/json.', status_code=415)
    try:
        json_data = request.get_json()
        output = []
        for coordinates in json_data:
            ED50_x = coordinates[0]
            ED50_y = coordinates[1]
            WGS84_long, WGS84_lat = pyproj.transform(ED50_zone, WGS84, ED50_x, ED50_y)
            output.append([WGS84_long, WGS84_lat])
    except:
        raise InvalidUsage("Invalid JSON format. Include array of coordinates (i.e. [[x1,y1],...,[xn,yn]].", status_code=400)

    return json.dumps(output)

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True,host='0.0.0.0', port=port)

# Example transformation:
# ED50 UTM zone 30 coordinates = (433829.9531810064, 4811755.325688820)
# ETRS89 UTM zone 30 coordinates = (3,81917591, 43,45391861)




