from flask_wtf import FlaskForm
from wtforms import StringField, HiddenField, SelectField, SubmitField
from wtforms.widgets import TextArea
from wtforms.validators import DataRequired, Optional


class AddForm(FlaskForm):
    location = StringField('Store/Location', validators=[DataRequired()])
    item = StringField('Item', validators=[DataRequired()])
    quantity = SelectField('Quantity', choices=[('out', 'Out of Stock'), ('limited', 'Limited'),
                                                ('stocked', 'Fully Stocked')], default='stocked',
                           validators=[DataRequired()])
    place_id = HiddenField('Place', validators=[DataRequired()])
    name = HiddenField('Name', validators=[DataRequired()])
    address = HiddenField('Address', validators=[DataRequired()])
    lat = HiddenField('Lat', validators=[DataRequired()])
    long = HiddenField('Long', validators=[DataRequired()])
    comment = StringField('Comments (optional)', widget=TextArea())
    submit = SubmitField('Save')


class SearchItemForm(FlaskForm):
    item = StringField('Item', validators=[DataRequired()])
    zip = StringField('Near', validators=[Optional()])
    radius = SelectField('Radius',
                         choices=[('25', '25 miles'), ('50', '50 miles'), ('75', '75 miles'), ('100', '100 miles')],
                         default='25', validators=[DataRequired()])
    lat = HiddenField('Lat', validators=[Optional()])
    long = HiddenField('Long', validators=[Optional()])
    submit = SubmitField('Search for Item')


class SearchBusinessForm(FlaskForm):
    business = StringField('Store', validators=[DataRequired()])
    place_id = HiddenField('Store', validators=[DataRequired()])
    name = HiddenField('Name', validators=[DataRequired()])
    address = HiddenField('Address', validators=[DataRequired()])
    submit = SubmitField('Search Store')


class BrowseItemsForm(FlaskForm):
    browse_loc = StringField('Near', validators=[Optional()])
    browse_radius = SelectField('Radius',
                                choices=[('25', '25 miles'), ('50', '50 miles'), ('75', '75 miles'),
                                         ('100', '100 miles')],
                                default='25', validators=[DataRequired()])
    browse_lat = HiddenField('Lat', validators=[Optional()])
    browse_long = HiddenField('Long', validators=[Optional()])
    submit = SubmitField('Browse Items')
