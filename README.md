# ED50 coordinates transformation for Spain
Webservice for transformation of coordinates in ED50 UTM to ETRS89/WGS84 within
the Spain boundaries, applying the official datum shift grid.

NTv2 grids are provided by [Instituto Geografico Nacional español]
(http://www.ign.es/web/gds-rejilla-cambio-datum). They also provide a
[SOAP webservice](https://www.ign.es/wcts-app/) to make the transformation but
it only works with GML files.

## Usage

The webservie currently supports transformation from ED50 UTM in zones 29N, 30N
and 31N, to latitude and longitude either ETRS89 or WSG84.

The different options are defined in the URL.

```
http://<host>:5000/<zone>/<dest-system>
```
where `<zone>` can be 29N, 30N or 31N, and `<dest-system>` can be ETRS89 or
WGS84.

### Using HTTP GET
This method is used for tranforming just one set of coordinates.

The values of `x` and `y` are included in the URL as query params.
```
http://<host>:5000/<zone>/<dest-system>?x=<utm_x>&y=<utm_y>
```
Example
```bash
curl -X GET \
  'http://<host>:5000/30N/etrs89?x=433829.9531810064&y=4811755.325688820' \
```

### Using HTTP POST
This method is used for tranforming multiple sets of coordinates.

The values of the coordinates are included in the body of the POST request as an
JSON array of set of coordinates:
```
[[utm_x1, utm_y1], [utm_x2, utm_y2], ..., [utm_xn, utm_yn]]
```
The response would be a similar array with the transformed coordinates. The
order of the items is kept.
```
[[lon1, lat1], [lon2, lat2], ..., [lonn, latn]]
```

Example
```bash
curl -X POST \
  'http://<host>:5000/30N/wgs89' \
  -H 'Content-Type: application/json' \
  -d '[[433829.9531810064, 4811755.325688820], [433828.9531810064, 4811755.325688820]]'
```

## Run

### Standalone
Install python and the required libraries

```
$ sudo apt install python3
$ pip install --no-cache-dir -r requirements.txt
$ python3 ./app.py
```

By default the webservice is run in port 5000, but this can be modified by
setting the environment variable `PORT`.

### Dockerize
Run the following command to build and run the docker image

```bash
$ sudo docker build -t ed50 .
$ sudo docker run -d -p 5000:5000 ed50
```

## Authors
This project has been developed by:

- [Jorge Lanza](https://github.com/jlanza)
- [Pablo Sotres](https://github.com/psotres)

## Acknowledgments

Thanks to [J. Victor Mora](https://jvmora.wordpress.com/2013/02/22/ed50-to-etrs89-using-a-spanish-shift-grid-with-pyproj/) as his example helped on the beginning ;)
