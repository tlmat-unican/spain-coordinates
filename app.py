import os
from flask import Flask, request, jsonify
import json
import jsonschema
import pyproj
from functools import partial

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

with open('json-schema/GeoJSON.json', 'r') as f:
  schema_data = f.read()
GEOJSON_SCHEMA = json.loads(schema_data)

def is_geojson(data):
  try:
    jsonschema.validate(data, GEOJSON_SCHEMA)
  except jsonschema.exceptions.ValidationError as error:
    return False
  return True

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

  pyproj_transform = partial(pyproj.transform, ED50_ZONES[zone], DEST[dest])

  if request.method == 'GET':
    return do_get(pyproj_transform)
  else:
    return do_post(pyproj_transform)

def do_get(pyproj_transform):
  ED50_x = request.args.get('x')
  ED50_y = request.args.get('y')
  if ED50_x is None or ED50_x == '' or ED50_y is None or ED50_y == '':
    raise InvalidUsage('Must set both x and y query params.', status_code=400)
  else:
    lon, lat = pyproj_transform(ED50_x, ED50_y)
    return jsonify(lon, lat)

def coordinates_modification(item, pyproj_transform):
  if isinstance(item[0], list) == True:
    for row in item:
      coordinates_modification(row, pyproj_transform)
  else:
    new_coord = pyproj_transform(*item)
    item.clear()
    item.extend(new_coord)

def find_and_transform_coordinates(obj, pyproj_transform):
  if isinstance(obj, dict):
    for k, item in obj.items():
      if k == "coordinates":
        coordinates_modification(item, pyproj_transform)
      find_and_transform_coordinates(item, pyproj_transform)
  elif any(isinstance(obj, t) for t in (list, tuple)):
    for item in obj:
      find_and_transform_coordinates(item, pyproj_transform)

def do_post(pyproj_transform):
  if request.content_type != 'application/json':
      raise InvalidUsage('Only accepts application/json.', status_code=415)

  try:
    json_data = request.get_json()

    if is_geojson(json_data):
      find_and_transform_coordinates(json_data, pyproj_transform)
    else:
      coordinates_modification(json_data, pyproj_transform)
  except:
    raise InvalidUsage("Invalid JSON format. GeoJSON or an array of coordinates (i.e. [[x1,y1],...,[xn,yn]]) are supported.", status_code=400)

  return json.dumps(json_data)

if __name__ == '__main__':
  # Bind to PORT if defined, otherwise default to 5000.
  port = int(os.environ.get('PORT', 5000))
  app.run(debug=True,host='0.0.0.0', port=port)

# Example transformation:
# ED50 UTM zone 30 coordinates = (433829.9531810064, 4811755.325688820)
# ETRS89 UTM zone 30 coordinates = (3,81917591, 43,45391861)




