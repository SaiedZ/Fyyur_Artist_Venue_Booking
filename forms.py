from datetime import datetime
import re
from flask_wtf import Form
from wtforms import (StringField, SelectField,
                     SelectMultipleField, DateTimeField,
                     BooleanField)
from wtforms.validators import DataRequired, AnyOf, URL, Regexp, Optional

import enum
from markupsafe import escape


class Genres(enum.Enum):
    Blues = 'Blues'
    Classical = 'Classical'
    Country = 'Country'
    Electronic = 'Electronic'
    Folk = 'Folk'
    Funk = 'Funk'
    HipHop = 'Hip-Hop'
    HeavyMetal = 'Heavy Metal'
    Instrumental = 'Instrumental'
    Jazz = 'Jazz'
    MusicalTheatre = 'Musical Theatre'
    Pop = 'Pop'
    Punk = 'Punk'
    RB = 'R&B'
    Reggae = 'Reggae'
    RockNRoll = 'Rock n Roll'
    Alternative = 'Alternative'
    Soul = 'Soul'
    Other = 'Other'

    def __str__(self):
        return self.name  # value string

    def __html__(self):
        return self.value  # label string


def enum_field_options(enum):
    """Produce WTForm Field instance configuration options for an Enum

    Returns a dictionary with 'choices' and 'coerce' keys, use this as
    **enum_fields_options(EnumClass) when constructing a field:

    enum_selection = SelectField("Enum Selection", **enum_field_options(EnumClass))

    Labels are produced from str(enum_instance.value) or
    str(eum_instance), value strings with str(enum_instance).

    """
    assert not {'__str__', '__html__'}.isdisjoint(vars(enum)), (
        "The {!r} enum class does not implement __str__ and __html__ methods")

    def coerce(name):
        if isinstance(name, enum):
            # already coerced to instance of this enum
            return name
        try:
            return enum[name]
        except KeyError:
            raise ValueError(name)

    return {'choices': [(v, escape(v)) for v in enum], 'coerce': coerce}


class ShowForm(Form):
    artist_id = StringField(
        'artist_id'
    )
    venue_id = StringField(
        'venue_id'
    )
    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired()],
        default=datetime.today()
    )


class VenueForm(Form):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices=[
            ('AL', 'AL'),
            ('AK', 'AK'),
            ('AZ', 'AZ'),
            ('AR', 'AR'),
            ('CA', 'CA'),
            ('CO', 'CO'),
            ('CT', 'CT'),
            ('DE', 'DE'),
            ('DC', 'DC'),
            ('FL', 'FL'),
            ('GA', 'GA'),
            ('HI', 'HI'),
            ('ID', 'ID'),
            ('IL', 'IL'),
            ('IN', 'IN'),
            ('IA', 'IA'),
            ('KS', 'KS'),
            ('KY', 'KY'),
            ('LA', 'LA'),
            ('ME', 'ME'),
            ('MT', 'MT'),
            ('NE', 'NE'),
            ('NV', 'NV'),
            ('NH', 'NH'),
            ('NJ', 'NJ'),
            ('NM', 'NM'),
            ('NY', 'NY'),
            ('NC', 'NC'),
            ('ND', 'ND'),
            ('OH', 'OH'),
            ('OK', 'OK'),
            ('OR', 'OR'),
            ('MD', 'MD'),
            ('MA', 'MA'),
            ('MI', 'MI'),
            ('MN', 'MN'),
            ('MS', 'MS'),
            ('MO', 'MO'),
            ('PA', 'PA'),
            ('RI', 'RI'),
            ('SC', 'SC'),
            ('SD', 'SD'),
            ('TN', 'TN'),
            ('TX', 'TX'),
            ('UT', 'UT'),
            ('VT', 'VT'),
            ('VA', 'VA'),
            ('WA', 'WA'),
            ('WV', 'WV'),
            ('WI', 'WI'),
            ('WY', 'WY'),
        ]
    )
    address = StringField(
        'address', validators=[DataRequired()]
    )
    phone = StringField(
        'phone'
    )
    image_link = StringField(
        'image_link'
    )
    genres = SelectMultipleField(
        'genres', validators=[DataRequired()],
        **enum_field_options(Genres)
    )
    facebook_link = StringField(
        'facebook_link', validators=[Optional(), URL()]
    )
    website_link = StringField(
        'website_link'
    )

    seeking_talent = BooleanField('seeking_talent')

    seeking_description = StringField(
        'seeking_description'
    )


class ArtistForm(Form):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices=[
            ('AL', 'AL'),
            ('AK', 'AK'),
            ('AZ', 'AZ'),
            ('AR', 'AR'),
            ('CA', 'CA'),
            ('CO', 'CO'),
            ('CT', 'CT'),
            ('DE', 'DE'),
            ('DC', 'DC'),
            ('FL', 'FL'),
            ('GA', 'GA'),
            ('HI', 'HI'),
            ('ID', 'ID'),
            ('IL', 'IL'),
            ('IN', 'IN'),
            ('IA', 'IA'),
            ('KS', 'KS'),
            ('KY', 'KY'),
            ('LA', 'LA'),
            ('ME', 'ME'),
            ('MT', 'MT'),
            ('NE', 'NE'),
            ('NV', 'NV'),
            ('NH', 'NH'),
            ('NJ', 'NJ'),
            ('NM', 'NM'),
            ('NY', 'NY'),
            ('NC', 'NC'),
            ('ND', 'ND'),
            ('OH', 'OH'),
            ('OK', 'OK'),
            ('OR', 'OR'),
            ('MD', 'MD'),
            ('MA', 'MA'),
            ('MI', 'MI'),
            ('MN', 'MN'),
            ('MS', 'MS'),
            ('MO', 'MO'),
            ('PA', 'PA'),
            ('RI', 'RI'),
            ('SC', 'SC'),
            ('SD', 'SD'),
            ('TN', 'TN'),
            ('TX', 'TX'),
            ('UT', 'UT'),
            ('VT', 'VT'),
            ('VA', 'VA'),
            ('WA', 'WA'),
            ('WV', 'WV'),
            ('WI', 'WI'),
            ('WY', 'WY'),
        ]
    )
    phone = StringField(
        'phone',
        validators=[
            Regexp(regex=r'^\s*\d{3}-\d{3}-\d{4}\s*$',
            message="Phone number muts be like xxx-xxx-xxxx")
        ]
    )
    image_link = StringField(
        'image_link'
    )
    genres = SelectMultipleField(
        'genres', validators=[DataRequired()],
        **enum_field_options(Genres)
    )
    facebook_link = StringField(
        'facebook_link', validators=[Optional(), URL()]
     )

    website_link = StringField(
        'website_link'
     )

    seeking_venue = BooleanField('seeking_venue')

    seeking_description = StringField(
            'seeking_description'
     )
