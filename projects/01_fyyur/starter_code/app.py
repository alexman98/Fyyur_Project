#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from models import Venue, Artist, Show, db,migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')

moment = Moment(app)

db.init_app(app)


migrate.init_app(app, db)


# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

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
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  data=[]

  places={}
  venues=Venue.query.all()

  for venue in venues:
    Location = (venue.city, venue.state)
    if Location not in places:
            places[Location] = {
                "city": venue.city,
                "state": venue.state,
                "venues": []
            }

    Num_Shows = len([show for show in venue.shows if show.start_time > datetime.now()])

    places[Location]["venues"].append({
            "id": venue.id,
            "name": venue.name,
            "Num_Shows": Num_Shows
        })

  data = places.values()
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  word = request.form.get('search_term', '')
  search_venues=Venue.query.filter(Venue.name.ilike('%' + word + '%')).all()  
  info=[] 

  for venue in search_venues: 
    info.append({
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": sum(1 for show in venue.shows if show.start_time > datetime.now())
    })

  response={
    "count": len(info),
    "data": info}

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  venue=Venue.query.get(venue_id)
  #past_shows = Show.query.filter(Show.venue_id == venue_id).filter(Show.start_time < datetime.now()).all()
  #future_shows = Show.query.filter(Show.venue_id == venue_id).filter(Show.start_time > datetime.now()).all()

  #past_shows=Show.query.join(Artist).filter(Show.venue_id == venue_id).filter(Show.start_time < datetime.now()).all()
  #grfuture_shows=Show.query.join(Artist).filter(Show.venue_id == venue_id).filter(Show.start_time > datetime.now()).all()
  past_shows=db.session.query(Show).join(Artist).filter(Show.venue_id == venue_id).filter(Show.start_time < datetime.now()).all()
  future_shows=db.session.query(Show).join(Artist).filter(Show.venue_id == venue_id).filter(Show.start_time > datetime.now()).all()

  past_shows=[{
    "artist_id": show.artist.id,
    "artist_name": show.artist.name,
    "artist_image_link": show.artist.image_link,
    "start_time": str(show.start_time)
  } for show in past_shows]

  future_shows=[{
    "artist_id": show.artist.id,
    "artist_name": show.artist.name,
    "artist_image_link": show.artist.image_link,
    "start_time": str(show.start_time)
  } for show in future_shows]
  data={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website_link,  
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,  
    "past_shows": past_shows,
    "upcoming_shows": future_shows, 
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(future_shows)
  } 
 
  data = list(filter(lambda d: d['id'] == venue_id, [data]))[0] 
  return render_template('pages/show_venue.html', venue=data)  

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission(): 
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  form=VenueForm(request.form, meta={'csrf': False})

  if form.validate():
    try:
          new_venue = Venue(
          name=form.name.data,
          city=form.city.data,
          state=form.state.data,
          address=form.address.data,
          phone=form.phone.data,
          image_link=form.image_link.data,
          genres=form.genres.data,
          facebook_link=form.facebook_link.data,
          website_link=form.website_link.data,
          seeking_talent=form.seeking_talent.data,
          seeking_description=form.seeking_description.data
        )
          db.session.add(new_venue)
          db.session.commit()
          flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except Exception as e:
          print(e)
          db.session.rollback()
          flash('An error occurred. Venue could not be listed.')
    finally:
          db.session.close()
  else:
    error_messages = []
    for field, errors in form.errors.items():
        for error in errors:
            error_message = f"Error in the {field} field - {error}"
            error_messages.append(error_message)
            flash(error_message)
    print("Form validation errors:", error_messages)


  
  # on successful db insert, flash success
  #flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  venue=Venue.query.get(venue_id)
  try:
  

    db.session.delete(venue)
    db.session.commit()
    flash('Venue was successfully deleted!')
  except Exception as e:

    print(e)
    db.session.rollback()
    flash('An error occurred. Venue could not be deleted.')
  finally:

    db.session.close()

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

  artists=Artist.query.all()
  data = []
  for artist in artists:
    data.append({
      "id": artist.id,
      "name": artist.name,
    })
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  word = request.form.get('search_term', '')
  search_artists=Artist.query.filter(Artist.name.ilike('%' + word + '%')).all()
  info=[]
  for artist in search_artists:
    info.append({
        "id": artist.id,
        "name": artist.name,
        "num_upcoming_shows": sum(1 for show in artist.shows if show.start_time > datetime.now())
    })
    
  response={
    "count": len(info),
    "data": info}  
  
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id

  artists=Artist.query.get(artist_id)
  #past_shows = Show.query.filter(Show.artist_id == artist_id).filter(Show.start_time < datetime.now()).all()
  #future_shows = Show.query.filter(Show.artist_id == artist_id).filter(Show.start_time > datetime.now()).all()

  #past_shows=Show.query.join(Venue).filter(Show.artist_id == artist_id).filter(Show.start_time < datetime.now()).all()
  #future_shows=Show.query.join(Venue).filter(Show.artist_id == artist_id).filter(Show.start_time > datetime.now()).all()

  past_shows=db.session.query(Show).join(Venue).filter(Show.artist_id == artist_id).filter(Show.start_time < datetime.now()).all()
  future_shows=db.session.query(Show).join(Venue).filter(Show.artist_id == artist_id).filter(Show.start_time > datetime.now()).all()

  past_shows=[{
    "venue_id": show.venue.id,
    "venue_name": show.venue.name,
    "venue_image_link": show.venue.image_link,
    "start_time": str(show.start_time) 
  } for show in past_shows]
  future_shows=[{
    "venue_id": show.venue.id,
    "venue_name": show.venue.name,
    "venue_image_link": show.venue.image_link,
    "start_time": str(show.start_time)
  } for show in future_shows]

  data={
    "id": artists.id,
    "name": artists.name,
    "genres": artists.genres,
    "city": artists.city,
    "state": artists.state,
    "phone": artists.phone,
    "website": artists.website_link,
    "facebook_link": artists.facebook_link,
    "seeking_venue": artists.seeking_venue,
    "seeking_description": artists.seeking_description,
    "image_link": artists.image_link,
    "past_shows": past_shows,
    "upcoming_shows": future_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(future_shows)
  }

  data = list(filter(lambda d: d['id'] == artist_id, [data]))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    
    form = ArtistForm()
    artist = db.session.get(Artist, artist_id)
    if artist:
        form.name.data = artist.name
        form.genres.data=artist.genres
        form.city.data = artist.city
        form.state.data = artist.state
        form.phone.data = artist.phone
        form.image_link.data = artist.image_link
        form.website_link.data = artist.website_link
        form.facebook_link.data = artist.facebook_link
        form.seeking_venue.data = artist.seeking_venue
        form.seeking_description.data = artist.seeking_description

    return render_template('forms/edit_artist.html', form=form, artist=artist)
  
  # TODO: populate form with fields from artist with ID <artist_id>


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

    artist = db.session.get(Artist, artist_id)

    try:
        artist.name = request.form['name']
        artist.city = request.form['city']
        artist.state = request.form['state']
        artist.phone = request.form['phone']
        artist.genres = request.form.getlist('genres')
        artist.website_link = request.form['website_link']
        artist.facebook_link = request.form['facebook_link']
        artist.image_link = request.form['image_link']
        artist.seeking_venue = 'seeking_venue' in request.form
        artist.seeking_description = request.form['seeking_description']
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully updated!')
    except Exception as e:
        print(e)
        db.session.rollback()
        flash('An error occurred. Artist could not be updated.')
    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)

    # Appropriately updating venue data from form
    if venue:
        form.name.data = venue.name
        form.genres.data = venue.genres
        form.address.data = venue.address
        form.city.data = venue.city
        form.state.data = venue.state
        form.phone.data = venue.phone
        form.website_link.data = venue.website_link
        form.facebook_link.data = venue.facebook_link
        form.seeking_talent.data = venue.seeking_talent
        form.seeking_description.data = venue.seeking_description

    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes

    # Querying venue information based on venue_id
    venue = Venue.query.get(venue_id)

    try:
        venue.name = request.form['name']
        venue.genres = request.form.getlist('genres')
        venue.city = request.form['city']
        venue.state = request.form['state']
        venue.address = request.form['address']
        venue.phone = request.form['phone']
        venue.website_link = request.form['website_link']
        venue.facebook_link = request.form['facebook_link']
        venue.image_link = request.form['image_link']
        venue.seeking_talent = True if 'seeking_talent' in request.form else False
        venue.seeking_description = request.form['seeking_description']
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully updated!')


    except Exception as e:
        print(e)
        db.session.rollback()
        flash('An error occurred. Venue could not be updated.')

    finally:
        db.session.close()
       
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = ArtistForm(request.form, meta={'csrf': False})
  if form.validate():
    try:
      new_artist = Artist(
          name=form.name.data,
          city=form.city.data,
          state=form.state.data,
          phone=form.phone.data,
          genres=form.genres.data,
          image_link=form.image_link.data,
          facebook_link=form.facebook_link.data,
          website_link=form.website_link.data,
          seeking_venue=form.seeking_venue.data,
          seeking_description=form.seeking_description.data
      )
      db.session.add(new_artist)
      db.session.commit()
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except Exception as e:
      print(e)
      db.session.rollback()
      flash('An error occurred. Artist could not be listed.')
    finally:
      db.session.close()
  else:
    error_messages = []
    for field, errors in form.errors.items():
        for error in errors:
            error_message = f"Error in the {field} field - {error}"
            error_messages.append(error_message)
            flash(error_message)
            print("Form validation errors:", error_messages)

  # on successful db insert, flash success
  #flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():

  # displays list of shows at /shows
  # TODO: replace with real venues data.
  shows=Show.query.all()
  data = []
  for show in shows:
    data.append({
      "venue_id": show.venue.id,
      "venue_name": show.venue.name, 
      "artist_id": show.artist.id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": str(show.start_time)
    })

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  form=ShowForm(request.form, meta={'csrf': False})
  if form.validate():
    try:
      new_show = Show(
          artist_id=form.artist_id.data,
          venue_id=form.venue_id.data,
          start_time=form.start_time.data
          
      ) 
      db.session.add(new_show)
      db.session.commit()
      flash('Show was successfully listed!')
    except Exception as e:
      print(e)
      db.session.rollback()
      flash('An error occurred. Show could not be listed.')
    finally:
      db.session.close()
    
  else:
    error_messages = []
    for field, errors in form.errors.items():
        for error in errors:
            error_message = f"Error in the {field} field - {error}"
            error_messages.append(error_message)
            flash(error_message)
            print("Form validation errors:", error_messages)



  #flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
