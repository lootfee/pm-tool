from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, DecimalField, SubmitField, SelectField, IntegerField, SelectMultipleField, DateField, HiddenField, FileField, FloatField
# from wtforms.fields import DateField
from wtforms.widgets import CheckboxInput, ListWidget, TableWidget, RangeInput
from wtforms.validators import DataRequired, Optional, NumberRange, Length, EqualTo, Regexp, Email
from flask_wtf.file import FileAllowed


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email(message="Must be a valid email address.")])
    password = PasswordField('Password', validators=[
                                            DataRequired(), 
                                            Length(min=8, message="Password must be at least 8 characters long."), 
                                            Regexp(
                                                regex="^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%^&*])",
                                                message="Password must include an uppercase letter, a number, and a special character."
                                            )
                                        ]
                            )
    password2 = PasswordField('Validate Password', validators=[DataRequired(), EqualTo('password', message="Passwords must match.")])
    submit = SubmitField('Register')
    

class UpdateUserForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    profile_pic = FileField('Profile Picture', validators=[Optional(), FileAllowed(['jpg', 'png'], "Only .jpg and .png files are allowed.")])
    submit = SubmitField('Register')


class AddMemberForm(FlaskForm):
    amf_email = StringField('Email', validators=[DataRequired(), Email()], render_kw={'placeholder': 'User Email Address'})
    amf_submit = SubmitField('Add')
    

class EditRoleForm(FlaskForm):
    erf_user_id = HiddenField('User ID', validators=[DataRequired()])
    erf_role = SelectField('Role', choices=[("member", "Member"), ("team_leader", "Team Leader")])
    erf_submit = SubmitField('Save')
    
    
class RemoveMemberForm(FlaskForm):
    rmf_user_id = HiddenField('User ID', validators=[DataRequired()])
    rmf_submit = SubmitField('Remove')


class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()
    # option_widget = RangeInput()


class ProjectForm(FlaskForm):
    name = StringField('Project Name', validators=[DataRequired()])
    description = TextAreaField('Description', render_kw={'maxlength': 100, 'placeholder': 'Max 100 characters'})
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
    comments = TextAreaField('Comments', validators=[Optional()], render_kw={'maxlength': 100, 'placeholder': 'Max 100 characters'})
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
    