#   Dependencies
from flask import Flask, jsonify

import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import datetime as dt

########################################
#   Database Setup
########################################

#   Create engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

#   Reflect hawaii db and tables
Base = automap_base()
Base.prepare(autoload_with = engine)

#   Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

########################################
#   Flask Setup
########################################

app = Flask(__name__)

########################################
#   Flask Routes
########################################

@app.route("/")
def home():
    #   Log request
    print("Server requested home page")
    #   welcome message and available routes
    return(f"Welcome to my API!<br/>"
            f"{'-'*30}<br/>"
            f"<br/>"
            f"Available Routes: <br/>"
            f"/api/v1.0/precipitation<br/>"
            f"/api/v1.0/stations<br/>"
            f"/api/v1.0/tobs<br/>"
            f"/api/v1.0/<b>&lt;start&gt;</b> <br/>"
            f"<li>insert <b>start</b> date in YYYY-MM-DD format</li>"
            f"/api/v1.0/<b>&lt;start&gt;</b>/<b>&lt;end&gt;</b> <br/>"
            f"<li>insert <b>start</b> and <b>end</b> date in YYYY-MM-DD format</li>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    #   Log request
    print("Server requested precipitation page")

    #   Create session from Python to db
    session = Session(bind = engine)

    #   Query Precipitation data
    query = session.query(Measurement.date, Measurement.prcp).all()

    #   Close session
    session.close()

    #   Store query response to a dictionary so it can be jsonified
    response = [{"date":x[0], "precipitation":x[1]} for x in query]

    #   Return json response on api
    return(jsonify(response))

@app.route("/api/v1.0/stations")
def stations():
    #   Log request
    print("Server requested stations page")

    #   Create session from Python to db
    session = Session(engine)

    #   Query Station data
    query = session.query(Station.station, Station.name).all()

    #   Close session
    session.close()

    #   Store query response in to a dictionary for jsonification
    response = [{"station_id":x[0], "station_name":x[1]} for x in query]

    #   Return json response on api
    return(jsonify(response))

@app.route("/api/v1.0/tobs")
def tobs():
    #   Log request
    print("Server requested tobs page")

    #   Create session from Python to db
    session = Session(engine)

    #   Query Most active station

    # Columns to return
    sel = [Station.name,
            Station.station,
            func.count(Measurement.station)]

    # Store query into object for iteration
    query =         session.query(*sel)                                 \
                    .filter(Station.station == Measurement.station)     \
                    .group_by(Station.station)                          \
                    .order_by(sel[2].desc()).all()

    # Store most active station
    station = query[0][1]

    #   Query latest date for station
    date, =         session.query(Measurement.date)                 \
                    .filter(Measurement.station == station)         \
                    .order_by(Measurement.station.desc())           \
                    .first()

    # Store date for previous year
    date = dt.date(int(date[0:4]), int(date[5:7]), int(date[8:11])) - dt.timedelta(365)

    #   Query tobs for the most active station for the last year

    # Columns to return
    sel = [Measurement.date, Measurement.tobs]

    # Store query
    query = session.query(*sel)         \
            .filter(Measurement.station == station) \
            .filter(Measurement.date >= date)       \
            .all()

    #   Close session
    session.close()

    #   Store query response in to a dictionary for jsonification
    response = [{"date":x[0], "temperature":x[1]} for x in query]

    #   Return json response on api
    return(jsonify(response))

@app.route("/api/v1.0/<start>")
def min(start):

    #   Log result
    print(f"Server requested min page with starting date of {start}")

    #   Create Session
    session = Session(engine)

    #   Query

    # Columns to search
    sel = [Measurement.date, Measurement.station, Measurement.tobs]

    # Store query for jsonification
    query = session.query(*sel)   \
            .filter(Measurement.date >= start)                  \
            .all()

    #   Close session
    session.close()

    #   Store query response in to a dictionary for jsonification
    response = [{"date":x[0], "station":x[1],"temperature":x[2]} for x in query]

    #   Return json response on api
    return(jsonify(response))

@app.route("/api/v1.0/<start>/<end>")
def minmax(start, end):
    #   Log result
    print(f"Server requested minmax page with starting date of {start} and end date of {end}")

    #   Create Session
    session = Session(engine)

    #   Query

    # Columns to search
    sel = [Measurement.date, Measurement.station, Measurement.tobs]

    # Store query for jsonification
    query = session.query(*sel)   \
            .filter(Measurement.date >= start)                  \
            .filter(Measurement.date <= end)                    \
            .all()

    #   Close session
    session.close()

    #   Store query response in to a dictionary for jsonification
    response = [{"date":x[0], "station":x[1],"temperature":x[2]} for x in query]

    #   Return json response on api
    return(jsonify(response))


########################################
#   Main Behavior
########################################

if __name__ == "__main__":
    app.run(debug = True)