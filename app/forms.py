from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, BooleanField, SubmitField, SelectField, IntegerField, SelectMultipleField, DateField, TimeField
# from wtforms.fields import DateField
from wtforms.widgets import CheckboxInput, ListWidget, TableWidget
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


class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()


class ProjectForm(FlaskForm):
    name = StringField('Project Name', validators=[DataRequired()])
    description = TextAreaField('Description')
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[DataRequired()])
    monday = TimeField('Monday', validators=[Optional()])
    tuesday = TimeField('Tuesday', validators=[Optional()])
    wednesday = TimeField('Wednesday', validators=[Optional()])
    thursday = TimeField('Thursday', validators=[Optional()])
    friday = TimeField('Friday', validators=[Optional()])
    saturday = TimeField('Saturday', validators=[Optional()])
    sunday = TimeField('Sunday', validators=[Optional()])
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
    start_date = DateField('Start Date', validators=[Optional()])
    end_date = DateField('End Date', validators=[Optional()])
    heirarchy = IntegerField('Heirarchy', validators=[NumberRange(min=1, max=100)], default=1)
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