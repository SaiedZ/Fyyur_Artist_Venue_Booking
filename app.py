# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import sys
from datetime import datetime
import dateutil.parser
import babel
from flask import (Flask, render_template, request, abort,
                   flash, redirect, url_for, jsonify)
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from forms import *

from models import db, db_setup, Venue, Artist, Show

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = db_setup(app)

# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():

    venues = Venue.query.all()
    data = {}
    buffer_locations = set()

    for venue in venues:
        location_dict = {}
        upcoming_shows_number = Show.query.filter(Show.venue_id == venue.id,
                                           Show.start_time > datetime.now()).count()
        if venue.city not in buffer_locations:
            location_dict = {
                "city": venue.city,
                "state":  venue.state,
                "venues": [{
                    "id": venue.id,
                    "name": venue.name,
                    "num_upcoming_shows": upcoming_shows_number,
                }]
            }
            buffer_locations.add(venue.city)
            data[venue.city] = location_dict
        else:
            data[venue.city]["venues"].append(
                {
                    "id": venue.id,
                    "name": venue.name,
                    "num_upcoming_shows": upcoming_shows_number,
                }
            )
    return render_template('pages/venues.html', areas=data.values())


@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form['search_term']
    venues = Venue.query.filter(Venue.name.ilike(f"%{search_term}%")).all()
    current_time = datetime.now()
    data = []

    for venue in venues:
        num_upcoming_shows = Show.query.filter(
          Show.artist_id == venue.id, Show.start_time > current_time
          ).count()
        data.append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": num_upcoming_shows,
        })
    response = {
        "count": len(venues),
        "data": data
    }
    return render_template(
        'pages/search_venues.html',
        results=response,
        search_term=request.form.get(
            'search_term',
            ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue = Venue.query.get(venue_id)
    if not venue:
        abort(404)
    data = {}
    data.update(vars(venue))
    data["genres"] = data['genres'].split("-")
    data["past_shows" ] = []
    data["upcoming_shows"] = []
    data["past_shows_count"] = 0
    data["upcoming_shows_count"] = 0

    for show in venue.shows:
        artist = Artist.query.get(show.artist_id)
        serialized_show = {
            "artist_id": show.artist_id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": str(show.start_time)
        }
        if show.start_time < datetime.now():
            data["past_shows" ].append(serialized_show)
            data["past_shows_count"] += 1
        else:
            data["upcoming_shows" ].append(serialized_show)
            data["upcoming_shows_count"] += 1

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    form = VenueForm(request.form)
    error = False
    if form.validate():
        if form.genres.data:
            genres = "-".join([genre.value for genre in form.genres.data])
        try:
            venue = Venue(
              address=form.address.data, phone=form.phone.data, state=form.state.data,
              website_link=form.website_link.data, facebook_link=form.facebook_link.data,
              seeking_talent=form.seeking_talent.data, image_link=form.image_link.data,
              seeking_description=form.seeking_description.data, city=form.city.data,
              genres=genres, name=form.name.data,
            )
            db.session.add(venue)
            db.session.commit()
        except Exception as e:
            error = True
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()
        if not error:
            flash('Venue ' + request.form['name'] + ' was successfully listed!')
            return render_template('pages/home.html')
        else:
            flash(f'An error occurred. Venue {form.name.data} could not be listed.')
    else:
        message = [f'{field} ' + '|'.join(err) for field, err in form.errors.items()]
        flash(f'Errors {message}')
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/<int:venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    error = False
    try:
        venue_to_be_deleted =  Venue.query.get(venue_id)
        db.session.delete(venue_to_be_deleted)
        db.session.commit()
    except Exception:
        error = True
        db.session.rollback()
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        return jsonify({'success': True})


#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    data = Artist.query.all()
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():

    search_term = request.form['search_term']
    artists = Artist.query.filter(Artist.name.ilike(f"%{search_term}%")).all()
    current_time = datetime.now()
    data = []

    for artist in artists:
        num_upcoming_shows = Show.query.filter(
          Show.artist_id == artist.id, Show.start_time > current_time
          ).count()
        data.append({
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": num_upcoming_shows,
        })
    response = {
        "count": len(artists),
        "data": data
    }
    return render_template(
        'pages/search_artists.html',
        results=response,
        search_term=request.form.get(
            'search_term',
            ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist = Artist.query.get(artist_id)
    if not artist:
        abort(404)
    data = {}
    data.update(vars(artist))
    data["genres"] = data['genres'].split("-")
    data["past_shows" ] = []
    data["upcoming_shows"] = []
    data["past_shows_count"] = 0
    data["upcoming_shows_count"] = 0

    for show in artist.shows:
        venue = Venue.query.get(show.venue_id)
        serialized_show = {
            "venue_id": show.venue_id,
            "venue_name": venue.name,
            "venue_image_link": venue.image_link,
            "start_time": str(show.start_time)
        }
        if show.start_time < datetime.now():
            data["past_shows" ].append(serialized_show)
            data["past_shows_count"] += 1
        else:
            data["upcoming_shows" ].append(serialized_show)
            data["upcoming_shows_count"] += 1

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist = Artist.query.get(artist_id)
    form = ArtistForm(obj=artist)
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    artist = Artist.query.get(artist_id)
    if not artist:
        abort(404)
    form = ArtistForm(request.form)
    if form.genres.data:
        genres = "-".join([genre.value for genre in form.genres.data])
    error = False
    if form.validate():
        try:
            form.populate_obj(artist)
            artist.genres = genres
            db.session.commit()
        except Exception as e:
            error = True
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()
        if not error:
            flash('Artist ' + request.form['name'] + ' was successfully updated!')
            return redirect(url_for('show_artist', artist_id=artist_id))
        else:
            flash(f'An error occurred. Artist {form.name.data} could not be updated.')
    else:
        flash('An error occurred. Form is not  valid', 'error')
    return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue = Venue.query.get(venue_id)
    form = VenueForm(obj=venue)
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    venue = Venue.query.get(venue_id)
    if not venue:
        abort(404)
    form = ArtistForm(request.form)
    if form.genres.data:
        genres = "-".join([genre.value for genre in form.genres.data])
    error = False
    if form.validate():
        try:
            form.populate_obj(venue)
            venue.genres = genres
            db.session.commit()
        except Exception as e:
            error = True
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()
        if not error:
            flash('venue ' + request.form['name'] + ' was successfully updated!')
            return redirect(url_for('show_venue', venue_id=venue_id))
        else:
            flash(f'An error occurred. Venue {form.name.data} could not be updated.')
    else:
        flash('An error occurred. Form is not  valid', 'error')
    return render_template('forms/edit_venue.html', form=form, venue=venue)

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    form = ArtistForm(request.form)
    error = False
    if form.validate():
        if form.genres.data:
            genres = "-".join([genre.value for genre in form.genres.data])
        try:
            artist = Artist(
                name=form.name.data, phone=form.phone.data, state=form.state.data,
                website_link=form.website_link.data, facebook_link=form.facebook_link.data,
                seeking_venue=form.seeking_venue.data, image_link=form.image_link.data,
                seeking_description=form.seeking_description.data, city=form.city.data,
                genres=genres,
            )
            db.session.add(artist)
            db.session.commit()
        except Exception as e:
            error = True
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()
        if not error:
            flash('Artist ' + request.form['name'] + ' was successfully listed!')
            return render_template('pages/home.html')
        else:
            flash(f'An error occurred. Venue {form.name.data} could not be listed.')
    else:
        flash('An error occurred. Form is not  valid', 'error')
    return render_template('forms/new_artist.html', form=form)

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():

    shows = Show.query.all()
    data = []

    for show in shows:
        venue = Venue.query.get(show.venue_id)
        artist = Artist.query.get(show.artist_id)
        data.append(
            {
                "venue_id": venue.id,
                "venue_name": venue.name,
                "artist_id": artist.id,
                "artist_name": artist.name,
                "artist_image_link": artist.image_link,
                "start_time": str(show.start_time),
            }
        )

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():

    form = ShowForm(request.form)
    error = False

    if form.validate():
        try:
            show = Show(
              start_time=form.start_time.data,
              artist_id=form.artist_id.data,
              venue_id=form.venue_id.data,
            )
            db.session.add(show)
            db.session.commit()
        except Exception as e:
            error = True
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()
        if not error:
            flash('Show was successfully listed!')

            return render_template('pages/home.html')

        else:
            flash('An error occurred. Show could not be listed.')
    else:
        flash('An error occurred. Form is not  valid', 'error')

    return render_template('forms/new_show.html', form=form)


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
