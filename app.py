import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, and_

from flask import Flask, jsonify

import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the tables
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
        f"Welcome to the Hawaiian Surfer Weather API with data from 2010-01-01 through 2017-08-23.<br/>"
        f"Use your dates of interest for the date queries!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/2010-01-01<br/>"
        f"/api/v1.0/2010-01-01/2017-08-23<br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all measurement data"""

    # Query all passengers
    results = session.query(Measurement.date,Measurement.prcp).all()

    session.close()

    # Create a dictionary from the results(in rows) data and append to a list of measurement data.
    measurement_data = []

    for date, prcp in results:
        measurement_dict = {}
        measurement_dict['date'] = date
        measurement_dict['prcp'] = prcp
        measurement_data.append(measurement_dict)

    return jsonify(measurement_data)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of Stations from the Stations Table """

    # Query all stations in the stations table.
    results = session.query(Station.station).order_by(Station.station).all()

    session.close()

    station_data = list(np.ravel(results))

    return jsonify(station_data)


@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Query and list the temperature observations for the most active stations for the last year of data."""
    # Query the latest date in the measurement table.
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    # Calculate the start range for the data query.
    fmt = "('%Y-%m-%d',)"
    latest_date_sql = dt.datetime.strptime(str(latest_date),fmt)
    query_date = latest_date_sql - dt.timedelta(days=365)
    
    results = session.query(Measurement.date,Measurement.tobs).\
    filter(func.strftime("%Y-%m-%d", Measurement.date) >= query_date).\
    filter(Measurement.station == 'USC00519281').\
    order_by(Measurement.date).all()

    session.close()
    
    temp_data = []
    for date, tobs in results:
        temp_dict = {}
        temp_dict['date'] = date
        temp_dict['tobs'] = tobs
        temp_data.append(temp_dict)
    
    return jsonify(temp_data)
    
@app.route("/api/v1.0/<start>")
def end_date(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Query and list the min, max and mean temperatures for all data from the start date to the end of the data."""
    # Query the data in the measurement table.
    
    max_temp = session.query(func.max(Measurement.tobs)).\
    filter(func.strftime("%Y-%m-%d", Measurement.date) >= start).all()

    min_temp = session.query(func.min(Measurement.tobs)).\
    filter(func.strftime("%Y-%m-%d", Measurement.date) >= start).all()

    avg_temp = session.query(func.avg(Measurement.tobs)).\
    filter(func.strftime("%Y-%m-%d", Measurement.date) >= start).all()
  
    session.close()
        
    return f"Maximum Temperature --> {max_temp}. \n   Minimum Temperature --> {min_temp}. \n   Average Temperature --> {avg_temp}."


@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start,end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Query and list the min, max and mean temperatures for all data from the start date through the end date."""
    # Query the data in the measurement table.
    
    max_temp = session.query(func.max(Measurement.tobs)).\
    filter(and_(func.strftime("%Y-%m-%d", Measurement.date) >= start, func.strftime("%Y-%m-%d", Measurement.date) <= end)).all()
    

    min_temp = session.query(func.min(Measurement.tobs)).\
    filter(and_(func.strftime("%Y-%m-%d", Measurement.date) >= start, func.strftime("%Y-%m-%d", Measurement.date) <= end)).all()

    avg_temp = session.query(func.avg(Measurement.tobs)).\
    filter(and_(func.strftime("%Y-%m-%d", Measurement.date) >= start, func.strftime("%Y-%m-%d", Measurement.date) <= end)).all()

    session.close()
        
    return f"Maximum Temperature --> {max_temp}. \n   Minimum Temperature --> {min_temp}. \n   Average Temperature --> {avg_temp}."
  


if __name__ == '__main__':
    app.run(debug=True)
