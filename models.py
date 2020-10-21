from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_moment import Moment
import datetime

db = SQLAlchemy()
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
Show = db.Table('Show',
    db.Column('venue_id', db.Integer, db.ForeignKey('Venue.id'), nullable=False),
    db.Column('artist_id', db.Integer, db.ForeignKey('Artist.id'), nullable=False),
    db.Column('start_time', db.DateTime, nullable=False)
)

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    genres = db.Column(db.String)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website =  db.Column(db.String(500))
    image_link = db.Column(db.String(500), nullable=False)
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable = False, default = True)
    seeking_description = db.Column(db.String(500))
    artists = db.relationship('Artist', secondary=Show, backref=db.backref('venues', lazy=True))
    
    def __repr__(self):
        return f'<Venue id: {self.id}, name: {self.name}, city: {self.city}, state: {self.state}>'
    def serialize_for_venues(self):
      city_states = []
      for d in Venue.query.all():
        city_states.append(d.city + ',' +d.state)
      unique_city_states = list(dict.fromkeys(city_states))
      
      data = []
      for cs in unique_city_states :
        csl = cs.split(',')
        city = csl[0]
        state = csl[1]
        
        venues = []
        venues_query = Venue.query.filter_by(city=city,state=state).all()
        
        for venue in venues_query:
          venues.append(
            {
              'id': venue.id,
              'name': venue.name,
              'num_upcoming_shows': 0
            }
          )

        data.append({
          'city': city,
          'state': state,
          'venues': venues
        })
      return data

    def serialize_general(self):
      return {
        "id": self.id,
        "name": self.name,
        "genres": self.genres.split(','),
        "address": self.address,
        "city": self.city,
        "state": self.state,
        "phone": self.phone,
        "website": self.website,
        "facebook_link": self.facebook_link,
        "seeking_talent": self.seeking_talent,
        "seeking_description": self.seeking_description,
        "image_link": self.image_link,
      }

    def serialize_for_venue_details(self):
      general = self.serialize_general()
      upcoming = self.serialize_upcoming_show()
      past = self.serialize_past_show()

      data = general
      data['upcoming_shows'] = upcoming
      data['upcoming_shows_count'] = len(upcoming)
      data['past_shows'] = past
      data['past_shows_count'] = len(past)
      return general

    def serialize_upcoming_show(self):
      upcoming = []
      for show in db.session.query(Show).filter(Show.c.start_time > datetime.now(), Show.c.venue_id == self.id).all():
        artist = Artist().query.get(show.artist_id)
        upcoming.append({
          "artist_id": artist.id,
          "artist_name": artist.name,
          "artist_image_link": artist.image_link,
          "start_time": (show.start_time).strftime("%m/%d/%Y, %H:%M:%S")
        })
      return upcoming

    def serialize_past_show(self):
      past = []
      for show in db.session.query(Show).filter(Show.c.start_time < datetime.now(), Show.c.venue_id == self.id).all():
        artist = Artist().query.get(show.artist_id)
        past.append({
          "artist_id": artist.id,
          "artist_name": artist.name,
          "artist_image_link": artist.image_link,
          "start_time": (show.start_time).strftime("%m/%d/%Y, %H:%M:%S")
        })
      return past


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable = False)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, nullable = False, default = True)

    def serialize_for_artists (self):
      data = []
      for d in Artist.query.all():
        data.append({
          'id': d.id,
          'name': d.name
        })
      
      return data

    def serialize_general(self):
      return {
        "id": self.id,
        "name": self.name,
        "genres": self.genres.split(','),
        "city": self.city,
        "state": self.state,
        "phone": self.phone,
        "website": self.website,
        "facebook_link": self.facebook_link,
        "seeking_venue": self.seeking_venue,
        "image_link": self.image_link,
      }
    
    def serialize_for_artist_details(self):
      general = self.serialize_general()
      upcoming = self.serialize_upcoming_show()
      past = self.serialize_past_show()
      data = general
      data['upcoming_shows'] = upcoming
      data['upcoming_shows_count'] = len(upcoming)
      data['past_shows'] = past
      data['past_shows_count'] = len(past)
      return general

    def serialize_upcoming_show(self):
      upcoming = []
      for show in db.session.query(Show).filter(Show.c.start_time > datetime.now(), Show.c.artist_id == self.id).all():
        venue = Venue().query.get(show.artist_id)
        upcoming.append({
          "venue_id": venue.id,
          "venue_name": venue.name,
          "venue_image_link": venue.image_link,
          "start_time": (show.start_time).strftime("%m/%d/%Y, %H:%M:%S")
        })
      return upcoming

    def serialize_past_show(self):
      past = []
      for show in db.session.query(Show).filter(Show.c.start_time < datetime.now(), Show.c.artist_id == self.id).all():
        venue = Venue().query.get(show.artist_id)
        past.append({
          "venue_id": venue.id,
          "venue_name": venue.name,
          "venue_image_link": venue.image_link,
          "start_time": (show.start_time).strftime("%m/%d/%Y, %H:%M:%S")
        })
        return past
