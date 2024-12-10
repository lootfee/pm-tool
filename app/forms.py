from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, DecimalField, SubmitField, SelectField, IntegerField, SelectMultipleField, DateField, HiddenField, FileField, FloatField
# from wtforms.fields import DateField
from wtforms.widgets import CheckboxInput, ListWidget, TableWidget, RangeInput
from wtforms.validators import DataRequired, Optional, NumberRange


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Validate Password', validators=[DataRequired()])
    submit = SubmitField('Register')
    

class UpdateUserForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    profile_pic = FileField('Profile Picture', validators=[Optional()])
    submit = SubmitField('Register')


class AddMemberForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    submit = SubmitField('Add')

class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()
    # option_widget = RangeInput()


class ProjectForm(FlaskForm):
    name = StringField('Project Name', validators=[DataRequired()])
    description = TextAreaField('Description')
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[DataRequired()])
    monday = FloatField('Monday', validators=[Optional(), NumberRange(min=0, max=100)], default=0)
    tuesday = FloatField('Tuesday', validators=[Optional(), NumberRange(min=0, max=100)], default=0)
    wednesday = FloatField('Wednesday', validators=[Optional(), NumberRange(min=0, max=100)], default=0)
    thursday = FloatField('Thursday', validators=[Optional(), NumberRange(min=0, max=100)], default=0)
    friday = FloatField('Friday', validators=[Optional(), NumberRange(min=0, max=100)], default=0)
    saturday = FloatField('Saturday', validators=[Optional(), NumberRange(min=0, max=100)], default=0)
    sunday = FloatField('Sunday', validators=[Optional(), NumberRange(min=0, max=100)], default=0)
    submit = SubmitField('Save')


class TaskForm(FlaskForm):
    task_id = HiddenField('Task ID', validators=[Optional()])
    title = StringField('Task', validators=[DataRequired()])
    task_number = StringField('Task Number', validators=[DataRequired()])
    parent_task = SelectField('Parent Task', validators=[DataRequired()], coerce=str)
    optimistic_duration = IntegerField('Optimistic Duration', validators=[NumberRange(min=0, max=100)], default=0, render_kw={'placeholder': 'Number of work hours'})
    expected_duration = IntegerField('Expected Duration', validators=[NumberRange(min=0, max=100)], default=0, render_kw={'placeholder': 'Number of work hours'})
    pessimistic_duration = IntegerField('Pessimistic Duration', validators=[NumberRange(min=0, max=100)], default=0, render_kw={'placeholder': 'Number of work hours'})
    reserve_analysis = IntegerField('Reserve Analysis', validators=[NumberRange(min=0, max=100)], default=0, render_kw={'placeholder': 'Number of work hours'})
    comments = TextAreaField('Comments', validators=[Optional()])
    expected_start_date = DateField('Expected Start Date', validators=[DataRequired()])
    expected_end_date = DateField('Estimated End Date', validators=[DataRequired()], render_kw={'readonly': True})
    total_expected_duration = FloatField('Total expected Duration', validators=[Optional(), NumberRange(min=0, max=100)], default=0, render_kw={'readonly': True})
    actual_start_date = DateField('Actual Start Date', validators=[Optional()])
    actual_end_date = DateField('Actual End Date', validators=[Optional()])
    total_actual_duration = FloatField('Total Actual Duration', validators=[Optional(), NumberRange(min=0, max=100)], default=0, render_kw={'readonly': True})
    hierarchy = IntegerField('Hierarchy', validators=[NumberRange(min=1, max=100)], default=1)
    completion = IntegerField('Completion', validators=[NumberRange(min=0, max=100)], default=0)
    dependency = SelectField('Dependency', coerce=str)
    owners = MultiCheckboxField('Owners', coerce=str)
    submit = SubmitField('Save')
    