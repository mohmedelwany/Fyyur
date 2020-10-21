#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import (
  Flask, 
  render_template,
  request, 
  Response, 
  flash, 
  redirect, 
  url_for, 
  abort)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import sys
from datetime import datetime
from models import db, Artist, Venue, Show

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)      


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():

  venues = Venue()
  data = venues.serialize_for_venues()
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term', None)
  venues = Venue.query.filter(
  Venue.name.ilike("%{}%".format(search_term))).all()
  count_venues = len(venues)
  data = []
  response = {
      "count": count_venues,
      "data": [v.serialize_for_venue_details() for v in venues]
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get(venue_id)
  if not venue :
    abort(404)
  data = venue.serialize_for_venue_details()
  
  return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------

'''
venue form
'''
@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

'''
create venue record
'''
@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(request.form)
  
  try :
    venue = Venue(
      name = form.name.data,
      genres = ','.join(form.genres.data),
      address = form.address.data,
      city = form.city.data,
      state = form.state.data,
      phone=form.phone.data,
      facebook_link=form.facebook_link.data,
      image_link=form.image_link.data,
    )
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' +
     request.form['name'] +
     ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred while adding Venue ' +
              request.form['name'])
    print(sys.exc_info())
  
  return render_template('pages/home.html')

'''
delete venue record
'''
@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  artists = Artist()
  data = artists.serialize_for_artists()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term', None)
  artists = Artist.query.filter(Artist.name.ilike("%{}%".format(search_term))).all()
  count_artists = len(artists)
  response = {
      "count": count_artists,
      "data": [a.serialize_for_artist_details() for a in artists]
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):

  artist = Artist().query.get(artist_id)
  if not artist :
    abort(404)
  data = artist.serialize_for_artist_details()
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist().query.get(artist_id)
  if not artist :
    abort(404)
  form = ArtistForm()
  data = artist.serialize_general()
  return render_template('forms/edit_artist.html', form=form, artist=data)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):

  form = ArtistForm(request.form)
  
  try :
    artist = Artist().query.get(artist_id)
    artist.name = form.name.data
    artist.genres = ','.join(form.genres.data)
    artist.city = form.city.data
    artist.state = form.state.data
    artist.phone=form.phone.data
    artist.facebook_link=form.facebook_link.data
    artist.image_link=form.image_link.data
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully updated!')
  except:
    db.session.rollback()
    flash('An error occurred while editting Artist ' +
              request.form['name'])
    print(sys.exc_info())

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue().query.get(venue_id)
  if not venue :
    venue(404)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):

  form = ArtistForm(request.form)
  try :
    venue = Venue().query.get(venue_id)
    venue.name = form.name.data
    venue.genres = ','.join(form.genres.data)
    venue.city = form.city.data
    venue.state = form.state.data
    venue.phone=form.phone.data
    venue.facebook_link=form.facebook_link.data
    venue.image_link=form.image_link.data
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully updated!')
  except:
    db.session.rollback()
    flash('An error occurred while editting Venue ' +
              request.form['name'])
    print(sys.exc_info())
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm(request.form)
  
  try :
    artist = Artist(
      name = form.name.data,
      genres = ','.join(form.genres.data),
      city = form.city.data,
      state = form.state.data,
      phone=form.phone.data,
      facebook_link=form.facebook_link.data,
      image_link=form.image_link.data,
    )
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred while adding Artist ' +
              request.form['name'])
    print(sys.exc_info())

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():

  data = []
  for show in db.session.query(Show).all():
    artist = Artist().query.get(show.artist_id)
    venue = Venue().query.get(show.venue_id)
    data.append({
      "venue_id": venue.id,
      "venue_name": venue.name,
      "artist_id": artist.id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": (show.start_time).strftime("%m/%d/%Y, %H:%M:%S")
    })
  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  form = ShowForm(request.form)
  try:
    show = Show.insert().values(venue_id=form.venue_id.data, artist_id=form.artist_id.data, start_time=form.start_time.data)
    db.session.execute(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred while adding Show ')
    print(sys.exc_info())
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run(debug=True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
