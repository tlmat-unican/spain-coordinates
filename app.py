import os

from flask import Flask, request, jsonify
import json
import pyproj

app = Flask(__name__)

# Define the projections using EPSG codes, check spatialreference.org for help
# Add the shift grid with nadgrids option
ED50_ZONES = {
    "29N": pyproj.Proj(init="EPSG:23029", nadgrids="./ntv2_grids/PENR2009.gsb"),
    "30N": pyproj.Proj(init="EPSG:23030", nadgrids="./ntv2_grids/PENR2009.gsb"),
    "31N": pyproj.Proj(init="EPSG:23031", nadgrids="./ntv2_grids/PENR2009.gsb,./ntv2_grids/BALR2009.gsb ")
}

DEST = {
    "WGS84": pyproj.Proj(init="epsg:4326"),
    "ETRS89": pyproj.Proj(init="epsg:4258")
}

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

@app.route("/<zone>/<dest>", methods=['GET', 'POST'])
def transform(zone, dest):
    zone = zone.upper()
    if zone not in ED50_ZONES:
        raise InvalidUsage('Not valid zone for Spain.', status_code=404)

    dest = dest.upper()
    if dest not in DEST:
        raise InvalidUsage('Not valid destination system.', status_code=404)

    if request.method == 'GET':
        return do_get(ED50_ZONES[zone], DEST[dest])
    else:
        return do_post(ED50_ZONES[zone], DEST[dest])

def do_get(ED50_zone, dest):
    ED50_x = request.args.get('x')
    ED50_y = request.args.get('y')
    if ED50_x is None or ED50_x == '' or ED50_y is None or ED50_y == '':
        raise InvalidUsage('Must set both x and y query params.', status_code=400)
    else:
        lon, lat = pyproj.transform(ED50_zone, dest, ED50_x, ED50_y)
        return jsonify(lon, lat)

def do_post(ED50_zone, dest):
    if request.content_type != 'application/json':
        raise InvalidUsage('Only accepts application/json.', status_code=415)

    try:
        json_data = request.get_json()
        output = []
        for coordinates in json_data:
            ED50_x = coordinates[0]
            ED50_y = coordinates[1]
            lon, lat = pyproj.transform(ED50_zone, dest, ED50_x, ED50_y)
            output.append([lon, lat])
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




