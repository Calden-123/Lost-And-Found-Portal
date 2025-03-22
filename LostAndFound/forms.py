from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField,SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo, InputRequired, ValidationError




class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email(), ])
    phone = StringField('Phone', validators=[Length(max=15)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Register')

    # Custom validator for DUT email
    def validate_email(self, field):
        print("Validating email:", field.data)  # Debugging
        if not field.data.endswith('@dut4life.ac.za'):
            print("Validation failed!")  # Debugging
            raise ValidationError('Email must be from the @dut4life.ac.za domain.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class AdminLoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class ReportItemForm(FlaskForm):
    name = StringField('Item Name', validators=[DataRequired(), Length(min=2, max=100)])
    description = StringField('Description', validators=[DataRequired(), Length(min=10, max=500)])
    category = SelectField('Category', validators=[DataRequired()],
                           choices=[('Electronics', 'Electronics'),
                                    ('Clothing', 'Clothing'),
                                    ('Accessories', 'Accessories'),
                                    ('Books', 'Books'),
                                    ('Other', 'Other')])
    status = SelectField('Status', validators=[DataRequired()],
                         choices=[('Lost', 'Lost'),
                                  ('Found', 'Found')],
                         default='Lost')  # Default to 'Lost'
    location = StringField('Location', validators=[DataRequired(), Length(min=2, max=100)])
    submit = SubmitField('Report Item')


