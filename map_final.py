import twurl
import json
import ssl
import urllib.error
import urllib.parse
import urllib.request
import folium
from flask import Flask, render_template, request
from geopy.geocoders import ArcGIS

TWITTER_URL = 'https://api.twitter.com/1.1/friends/list.json'

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


def lst_loc(p):
    lst = ['id', 'name', 'location']
    url = twurl.augment(TWITTER_URL,
                        {'screen_name': p, 'count': '5'})

    connection = urllib.request.urlopen(url, context=ctx)
    data = connection.read().decode()

    js = json.loads(data)
    headers = dict(connection.getheaders())
    lst1 = []
    for u in js['users']:
        lst2 = []
        for k, v in u.items():
            if k in lst:
                lst2.append(u[k])
        lst1.append(lst2)
    return lst1


def coordinates(lst_loc):
    """(list)->(list)
    The function takes the list of locations and return the list of their
    coordinates"""
    lst = []
    geo = ArcGIS()
    for i in lst_loc:
        try:
            loc = geo.geocode(i[1])
            loc1 = [loc.latitude, loc.longitude]
            lst.append([i[0], loc1])
        except:
            pass
    return lst


def map():
    """Create an HTML map"""
    return folium.Map()


def point(p):
    """The function put points into the map and make the map coloured
     according to countries' population"""
    map1 = map()
    lst = coordinates(lst_loc(p))

    names = folium.FeatureGroup("names")
    for i in lst:
        names.add_child(folium.Marker(location=i[1],
                                      popup=i[0],
                                      icon=folium.Icon()))
    map1.add_child(names)
    return map1.save("/template/result.html")


app = Flask(__name__, template_folder='template')


@app.route('/')
def my_form():
    return render_template('form.html')


@app.route('/', methods=['POST'])
def my_form_post():
    text = request.form['text']
    main(text)
    return render_template('result.html')


def main(n):
    a = point(n)


if __name__ == "__main__":
    app.run()
