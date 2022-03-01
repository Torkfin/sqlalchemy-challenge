## Imports Needed

import numpy as np
import datetime as dt

from flask import Flask, jsonify

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func


# Set up Database

engine = create_engine("sqlite:///hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

# Use Flask to set up API Server

app = Flask(__name__)

# Define Flask Routes

@app.route("/")
def homet():   
   
    """ List of the API Routes Available on this Server"""
    return (
        f"Welcome:  The API Routes Available on this Server are:<br/>"
        f"Precipitation: /api/v1.0/precipitation<br/>"
        f"List of Stations: /api/v1.0/stations<br/>"
        f"Temperature for Most Active Station over the Last Year: /api/v1.0/tobs<br/>"
        f"Temperature Stats (Minimum, Average, Max) from Start Date (yyyy-mm-dd): /api/v1.0/yyyy-mm-dd<br/>"
        f"Temperature Stats (Minimum, Average, Max) between Start to End Dates (Inclusive) (yyyy-mm-dd): /api/v1.0/yyyy-mm-dd/yyyy-mm-dd"
    )
# Set up Precipitation API

@app.route('/api/v1.0/precipitation')
def precipitation():
    session = Session(engine)
    sel = [Measurement.date,Measurement.prcp]
    queryresult = session.query(*sel).all()
    session.close()

    precipitation = []
    for date, prcp in queryresult:
        prcp_dict = {}
        prcp_dict["Date"] = date
        prcp_dict["Precipitation"] = prcp
        precipitation.append(prcp_dict)

    return jsonify(precipitation)

# Set up Stations API

@app.route('/api/v1.0/stations')
def stations():
    session = Session(engine)
    sel = [Station.station,Station.name,Station.latitude,Station.longitude,Station.elevation]
    queryresult = session.query(*sel).all()
    session.close()

    stations = []
    for station,name,lat,lon,elev in queryresult:
        station_dict = {}
        station_dict["Station"] = station
        station_dict["Name"] = name
        station_dict["Lat"] = lat
        station_dict["Lon"] = lon
        station_dict["Elevation"] = elev
        stations.append(station_dict)
 
    return jsonify(stations)

# Set up Temperature API

@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)
    lateststr = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    latestdate = dt.datetime.strptime(lateststr, '%Y-%m-%d')
    querydate = dt.date(latestdate.year -1, latestdate.month, latestdate.day)
    sel = [Measurement.date,Measurement.tobs]
    queryresult = session.query(*sel).filter(Measurement.date >= querydate).all()
    session.close()

    tobs_results = []
    for date, tobs in queryresult:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Temperature"] = tobs
        tobs_results.append(tobs_dict)

    return jsonify(tobs_results) 

# Set up Start Date API

@app.route('/api/v1.0/<start>')
def date_start(start):
    session = Session(engine)
    queryresult = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    session.close()

    tobs_results = []
    for min,avg,max in queryresult:
        tobs_dict = {}
        tobs_dict["Minimum"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Maximum"] = max
        tobs_results.append(tobs_dict)

    return jsonify(tobs_results)


#Set up Start / Stop Date API

@app.route('/api/v1.0/<start>/<stop>')
def date_start_stop(start,stop):
    session = Session(engine)
    queryresult = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= stop).all()
    session.close()

    tobs_results = []
    for min,avg,max in queryresult:
        tobs_dict = {}
        tobs_dict["Minimum"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Maximum"] = max
        tobs_results.append(tobs_dict)

    return jsonify(tobs_results)


if __name__ == "__main__":
    app.run(debug=True)