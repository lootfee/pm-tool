from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, BooleanField, SubmitField, SelectField, IntegerField, SelectMultipleField, DateField, TimeField
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
    monday = IntegerField('Monday', validators=[Optional()])
    tuesday = IntegerField('Tuesday', validators=[Optional()])
    wednesday = IntegerField('Wednesday', validators=[Optional()])
    thursday = IntegerField('Thursday', validators=[Optional()])
    friday = IntegerField('Friday', validators=[Optional()])
    saturday = IntegerField('Saturday', validators=[Optional()])
    # sunday = IntegerField('Sunday', validators=[Optional()])
    # class_days = MultiCheckboxField('Class Days', coerce=str, choices=[('monday', 'Monday'), 
    #                                                            ('tuesday', 'Tuesday'), 
    #                                                            ('wednesday', 'Wednesday'),
    #                                                            ('thursday', 'Thursday'), 
    #                                                            ('friday', 'Friday'), 
    #                                                            ('saturday', 'Saturday'),
    #                                                            ('sunday', 'Sunday')])
    submit = SubmitField('Save')


class TaskForm(FlaskForm):
    title = StringField('Task', validators=[DataRequired()])
    task_number = StringField('Task Number', validators=[DataRequired()])
    parent_task = SelectField('Parent Task', validators=[DataRequired()], coerce=str)
    expected_start_date = DateField('Expected Start Date', validators=[Optional()])
    expected_end_date = DateField('Expected End Date', validators=[Optional()])
    actual_start_date = DateField('Actual Start Date', validators=[Optional()])
    actual_end_date = DateField('Actual End Date', validators=[Optional()])
    hierarchy = IntegerField('Hierarchy', validators=[NumberRange(min=1, max=100)], default=1)
    completion = IntegerField('Completion', validators=[NumberRange(min=0, max=100)], default=0)
    dependency = SelectField('Dependency', coerce=str)
    # owners = SelectMultipleField('Owners', validators=[DataRequired()], 
    #                              option_widget=CheckboxInput(), widget=ListWidget(prefix_label=True))
    owners = MultiCheckboxField('Owners', coerce=str)
    submit = SubmitField('Save')

    # def validate(self, extra_validators=None):                                                         

    #     rv = FlaskForm.validate(self)                                           

    #     if not rv:                                                              
    #         return False                                                        

    #     print(self.owners.data)                                                

    #     if len(self.owners.data) < 1:                                          
    #         self.owners.errors.append('Please select atleast 1 user')    
    #         return False                                                        

    #     return True 
    