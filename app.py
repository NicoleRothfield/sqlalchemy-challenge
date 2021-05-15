import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session, session
from sqlalchemy import create_engine, func
import numpy as np
import pandas as pd
import datetime as dt
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

conn = engine.connect()

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement

Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available API Routes:<br/>"
        f"-------------------------<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Starting from the most recent data point in the database. 
    date = dt.datetime(2017, 8, 23)
    # Calculate the date one year from the last date in data set.
    year_ago = date - dt.timedelta(days=365)
   
    # Perform a query to retrieve the data and precipitation scores
    data = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date>year_ago).order_by(Measurement.date).all()

    session.close()

    precipitation_data = []
    for date, prcp in data:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        precipitation_data.append(prcp_dict)

    return jsonify(precipitation_data)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of stations"""
    # Query all stations
    station_results = session.query(Station.station).all()
    
    session.close()

    all_station_results = list(np.ravel((station_results)))

    return jsonify(all_station_results)

@app.route("/api/v1.0/tobs")
def temperature():
    
    session = Session(engine)
    
    date = dt.datetime(2017, 8, 23)

    year_ago = date - dt.timedelta(days=365)
    
    MostActive = 'USC00519281'

    tobs_data = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date>year_ago).filter(Measurement.station == MostActive).all()

    session.close()

    temp_data = []
    for date, tobs in tobs_data:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        temp_data.append(tobs_dict)
    
    return jsonify(temp_data)


@app.route("/api/v1.0/onetemp/<string:date1>")
def onedate(date1):
    Measurement = Base.classes.measurement
    """Return temperature data"""
    TempData = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs),\
                                func.avg(Measurement.tobs)).all()

    stats = list(np.ravel(TempData))
    
    tmp_stats = []
    for Min, Max, Avg in TempData:
        result_dict = {}
        result_dict["min"] = Min
        result_dict["max"] = Max
        result_dict["avg"] = Avg
        tmp_stats.append(result_dict)

    return jsonify(tmp_stats)

@app.route("/api/v1.0/twotemp/<string:date1>/<string:date2>")
def StartEnd(Start, End):
    Measurement = Base.classes.measurement

    results = session.query(func.min(Measurement.tobs).label('min'),\
     func.avg(Measurement.tobs).label('avg')\
    , func.max(Measurement.tobs).label('max')).\
    filter(Measurement.date >= Start).filter(Measurement.date <= End).all()
    #Unravel the results

    temp_stats = []
    for Min, Max, Avg in results:
        result_dict = {}
        result_dict["min"] = Min
        result_dict["max"] = Max
        result_dict["avg"] = Avg
        temp_stats.append(result_dict)

    return jsonify(temp_stats)

if __name__ == '__main__':
    app.run(debug=True)
