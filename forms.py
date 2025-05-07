from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, FloatField, BooleanField, SelectField, IntegerField, HiddenField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Optional
from models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose a different one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different one.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class ListingForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(max=100)])
    assistance_type = SelectField('Type of Assistance', validators=[DataRequired()], 
                                  choices=[
                                      ('nurse', 'Registered Nurse'),
                                      ('caregiver', 'Caregiver'),
                                      ('physiotherapist', 'Physiotherapist'),
                                      ('babysitter', 'Babysitter'),
                                      ('elderly_care', 'Elderly Care'),
                                      ('disability_support', 'Disability Support'),
                                      ('other', 'Other')
                                  ])
    description = TextAreaField('Description', validators=[DataRequired()])
    hourly_rate = FloatField('Hourly Rate (€)', validators=[DataRequired()])
    location = StringField('Location/City', validators=[DataRequired(), Length(max=100)])
    is_premium = BooleanField('Premium Listing (Get more visibility!)')
    premium_duration = SelectField(
        'Premium Duration', 
        choices=[
            ('', 'Select duration...'),
            ('1', '1 day (€2.99)'),
            ('3', '3 days (€7.99)'),
            ('7', '7 days (€14.99)'),
            ('30', '30 days (€39.99)')
        ],
        validators=[Optional()],
        default=''
    )
    submit = SubmitField('Create Listing')
    
    def validate_premium_duration(self, premium_duration):
        if self.is_premium.data and (not premium_duration.data or premium_duration.data == ''):
            raise ValidationError('Please select a duration for your premium listing.')
            
class PaymentForm(FlaskForm):
    """Form for handling payments (to be used with Stripe in the future)"""
    listing_id = HiddenField('Listing ID', validators=[DataRequired()])
    premium_duration = HiddenField('Premium Duration', validators=[DataRequired()])
    amount = HiddenField('Amount', validators=[DataRequired()])
    submit = SubmitField('Proceed to Payment')
