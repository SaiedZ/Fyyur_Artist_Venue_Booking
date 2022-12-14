from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


# ----------------------------------------------------------------------------#
# init DB
# ----------------------------------------------------------------------------#

db = SQLAlchemy()

def db_setup(app):
    app.config.from_object('config')
    db.init_app(app)
    Migrate(app, db)
    return db

# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))

    genres = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(500))

    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    shows = db.relationship('Show', backref='venue', lazy=True)

    def __repr__(self):
        return f"<Venue id: {self.id} - name: {self.name}>"


class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))

    # address = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(500))

    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    shows = db.relationship('Show', backref='artist', lazy=True)

    def __repr__(self):
        return f"<Artist id: {self.id} - name: {self.name}>"


class Show(db.Model):
    __tablename__ = 'show'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)

    artist_id = db.Column(
        db.Integer,
        db.ForeignKey('artist.id'),
        nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)

    def __repr__(self):
        return (f"<Show id: {self.id} -"
                f"artist_id: {self.artist_id} -"
                f"venue_id: {self.venue_id} >")
