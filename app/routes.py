from app import app, PROJECTS, TASKS, USERS, USER_PROJECTS
from flask import flash, render_template, redirect, url_for, request
from app.forms import ProjectForm, TaskForm, LoginForm, RegisterForm, AddMemberForm
from app.models import User
from flask_login import current_user, login_user, logout_user, login_required
from urllib.parse import urlparse
from bson import ObjectId
from bson.errors import InvalidId
from pymongo.errors import WriteError
import requests
from uuid import uuid4
from datetime import datetime, date

from functools import wraps
from pprint import pprint

# decorator
def user_project_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        ret = f(*args, **kwargs)
        project_id = kwargs["project_id"]
        user_id = current_user.id
        try:
            user_projects = USER_PROJECTS.find_one({"user_id": user_id})
            for project in user_projects['projects']:
                if project == project_id:
                    return ret
        except:
            flash("You don't have permission to access this project", "alert-warning")
            return redirect(url_for('index'))
        flash("You don't have permission to access this project", "alert-warning")
        return redirect(url_for('index'))
    return wrapped


# sort tasks by hierarchy and by parent
def sort_tasks(project_id: str, parent_task_id: str, task_list: list):
    _tasks = sorted(list(TASKS.find({"project_id": project_id, "parent_task_id": parent_task_id})), key=lambda d: d['hierarchy'])
    for t in _tasks:
        # print(t)
        task_list.append(t)
        sort_tasks(project_id, str(t["_id"]), task_list)
    return task_list


# updating child tasks of each tasks
# not in any route, only used for updating db
def update_child_tasks(project_id:str, parent_task_id:str):
    _tasks = TASKS.find({"project_id": project_id, "parent_task_id": parent_task_id})
    _t = None
    for t in _tasks:
        if parent_task_id != "0":
            print(parent_task_id)
            TASKS.update_one({'_id': ObjectId(parent_task_id)}, {'$addToSet': {'children': str(t["_id"])}}, upsert=True)
            print(f'{TASKS.find_one(ObjectId(t["_id"]))}')
        update_child_tasks(project_id, str(t["_id"]))
        # try:
        #     TASKS.update_one({'_id': ObjectId(parent_task_id)}, {'$addToSet': {'children': str(t["_id"])}}, upsert=True)
        #     print(f'{TASKS.find_one(ObjectId(t["_id"]))}')
        # except WriteError:
        #     print('error')
        #     TASKS.update_one({'_id': ObjectId(parent_task_id)}, {'$push': {'children': str(t["_id"])}}, upsert=True)
        
    return "done"


@app.route('/', methods=['GET', 'POST'])
@app.route('/index/', methods=['GET', 'POST'])
@login_required
def index():
    form = ProjectForm()
    if form.validate_on_submit():
        title = form.name.data
        description = form.description.data
        start_date = datetime.combine(form.start_date.data, datetime.min.time())
        end_date = datetime.combine(form.end_date.data, datetime.min.time())
        # time0 = datetime.strptime('000000',"%H%M%S").time()
        # monday_hrs = (datetime.combine(date.today(), time0) - datetime.combine(date.today(), form.monday.data)).total_seconds()/3600 if form.monday.data is not None else 0
        # tuesday_hrs = (datetime.combine(date.today(), time0) - datetime.combine(date.today(), form.tuesday.data)).total_seconds()/3600 if form.tuesday.data is not None else 0
        # wednesday_hrs = (datetime.combine(date.today(), time0) - datetime.combine(date.today(), form.wednesday.data)).total_seconds()/3600 if form.wednesday.data is not None else 0
        # thursday_hrs = (datetime.combine(date.today(), time0) - datetime.combine(date.today(), form.thursday.data)).total_seconds()/3600 if form.thursday.data is not None else 0
        # friday_hrs = (datetime.combine(date.today(), time0) - datetime.combine(date.today(), form.friday.data)).total_seconds()/3600 if form.friday.data is not None else 0
        # saturday_hrs = (datetime.combine(date.today(), time0) - datetime.combine(date.today(), form.saturday.data)).total_seconds()/3600 if form.saturday.data is not None else 0
        # # sunday_hrs = form.sunday.data
        monday_hrs = form.monday.data
        tuesday_hrs = form.tuesday.data
        wednesday_hrs = form.wednesday.data
        thursday_hrs = form.thursday.data
        friday_hrs = form.friday.data
        saturday_hrs = form.saturday.data
        new_project = PROJECTS.insert_one({"title": title, "description": description, "start_date": start_date, "end_date": end_date, 'members': [current_user.id], 
                                           'class_days': {'monday': monday_hrs, 'tuesday': tuesday_hrs, 'wednesday': wednesday_hrs,
                                                          'thursday': thursday_hrs, 'friday': friday_hrs, 'saturday': saturday_hrs}})
        USER_PROJECTS.update_one({'user_id': current_user.id}, {'$push': {'projects': str(new_project.inserted_id)}}, upsert=True)

        return redirect(url_for('index'))

    all_projects = []
    _all_user_projects = USER_PROJECTS.find_one({'user_id': current_user.id})
    # print(_all_user_projects)
    if _all_user_projects is not None:
        all_user_projects = _all_user_projects['projects']
        for project in all_user_projects:
            p = PROJECTS.find_one(ObjectId(project))
            all_projects.append(p)
    return render_template('index.html', title='PM TOOL', projects=all_projects, form=form)


# used single route for all because it just uses the same TaskForm and charting is done client side 
@app.route('/project/<string:project_id>/', methods=['GET', 'POST'])
@login_required
@user_project_required
def project(project_id):
    project = PROJECTS.find_one(ObjectId(project_id))
    _sorted_tasks = []
    sorted_tasks = sort_tasks(project_id, "0", _sorted_tasks)
    project_members = []
    for member in project['members']:
        m = USERS.find_one(ObjectId(member))
        project_members.append((str(m['_id']), m['name']))

    form = TaskForm()
    form.parent_task.choices = [("0", "None")]
    form.owners.choices = project_members
    form.dependency.choices = [("0", "None")]
    
    all_tasks = []
    for task in sorted_tasks:
        _owners = []
        for owner in task['owners']:
            try:
                m = USERS.find_one(ObjectId(owner))
                _owners.append(m['name'])
            except InvalidId:
                pass
        owners = ', '.join(_owners)
        
        try:
            expected_start_date = task['expected_start_date'].strftime("%m/%d/%Y")
            expected_end_date = task['expected_end_date'].strftime("%m/%d/%Y")
        except AttributeError:
            expected_start_date = ""
            expected_end_date = ""
            
        try:
            actual_start_date = task['actual_start_date'].strftime("%m/%d/%Y")
            actual_end_date = task['actual_end_date'].strftime("%m/%d/%Y")
        except AttributeError:
            actual_start_date = ""
            actual_end_date = ""
            
        try:
            children = task['children']
        except KeyError:
            children = []
        all_tasks.append({'_id': str(task['_id']), 'project_id': task['project_id'], "task_number": task['task_number'], "title": task['title'], 
                                    "expected_start_date": expected_start_date, "expected_end_date": expected_end_date, 
                                    "actual_start_date": actual_start_date, "actual_end_date": actual_end_date, 
                                    "parent_task_id": task['parent_task_id'], "completion": task['completion'], 
                                    "dependency": task['dependency'], "level": task['level'], "owners": owners, "children": children})
        form.parent_task.choices.append((task['_id'], task['title']))
        form.dependency.choices.append((task['_id'], task['title']))

    
    active_tab = request.args.get('active_tab', str)
    valid_tabs = ["nav-kanban-tab", "nav-ew-tab", "nav-gantt-tab", "nav-wbs-tab"]
    if not active_tab or active_tab not in valid_tabs:
        active_tab = "nav-kanban-tab"
    
    valid_form = True
    if request.method == 'POST':
        valid_form = form.validate()
    
    if form.validate_on_submit():
        task_number = form.task_number.data
        title = form.title.data
        expected_start_date = ""
        expected_end_date = ""
        actual_start_date = ""
        actual_end_date = ""
        if form.expected_start_date.data:
            expected_start_date = datetime.combine(form.expected_start_date.data, datetime.min.time())
        if form.expected_end_date.data:
            expected_end_date = datetime.combine(form.expected_end_date.data, datetime.min.time())
        if form.actual_start_date.data:
            actual_start_date = datetime.combine(form.actual_start_date.data, datetime.min.time())
        if form.actual_end_date.data:
            actual_end_date = datetime.combine(form.actual_end_date.data, datetime.min.time())
        
        # hierarchy will be used for sorting tasks
        hierarchy = form.hierarchy.data
        completion = form.completion.data
        dependency = form.dependency.data
        owners = form.owners.data
    
        # levels are used in WBS
        try:
            parent_task = TASKS.find_one({"_id": ObjectId(request.form.get('parent_task'))})
            level = parent_task["level"] + 1
            parent_task_id = str(parent_task["_id"])
            
        except InvalidId:
            parent_task_id = "0"
            level = 0
        
        new_task = TASKS.insert_one({'project_id': project_id, "task_number": task_number, "title": title, 
                                    "expected_start_date": expected_start_date, "expected_end_date": expected_end_date, 
                                    "actual_start_date": actual_start_date, "actual_end_date": actual_end_date,
                                    "parent_task_id": parent_task_id, 
                                    "level": level,"hierarchy": hierarchy, "completion": completion, 
                                    "dependency": dependency, "owners": owners, "children": []})
        
        if parent_task_id != "0": 
            TASKS.update_one({'_id': ObjectId(parent_task_id)}, {'$push': {'children': str(new_task.inserted_id)}}, upsert=True)
        
        # to open the active tab where the user is after page refresh/form submit
        print(request.args)
        active_tab = request.args.get('active_tab', str)
        next_page = url_for('project', project_id=project_id)
        if not active_tab or urlparse(next_page).netloc != '':
            next_page += f'?active_tab={active_tab}'
        return redirect(next_page)
    return render_template('project_page.html', title=project['title'], project_id=project_id, project_title=project['title'], 
                           form=form, all_tasks=all_tasks, active_tab=active_tab, valid_form=valid_form)



@app.route('/edit_project/<string:project_id>/', methods=['GET', 'POST'])
@login_required
@user_project_required
def edit_project(project_id):
    add_member_form = AddMemberForm()
    form = ProjectForm()
    edit_project = PROJECTS.find_one({'_id': ObjectId(project_id)})
    project_members = []
    for member in edit_project['members']:
        m = USERS.find_one(ObjectId(member))
        project_members.append((str(m['_id']), m['name']))
    if form.validate_on_submit():
        title = form.name.data
        description = form.description.data
        start_date = datetime.combine(form.start_date.data, datetime.min.time())
        end_date = datetime.combine(form.end_date.data, datetime.min.time())
        monday_hrs = form.monday.data
        tuesday_hrs = form.tuesday.data
        wednesday_hrs = form.wednesday.data
        thursday_hrs = form.thursday.data
        friday_hrs = form.friday.data
        saturday_hrs = form.saturday.data
 
        PROJECTS.update_one({'_id': ObjectId(project_id)}, {'$set': {"title": title, "description": description, "start_date": start_date, "end_date": end_date, 'members': [current_user.id], 
                                           'class_days': {'monday': monday_hrs, 'tuesday': tuesday_hrs, 'wednesday': wednesday_hrs,
                                                          'thursday': thursday_hrs, 'friday': friday_hrs, 'saturday': saturday_hrs}}}, upsert=False)

        return redirect(url_for('edit_project', project_id=project_id))

    elif request.method == 'GET':
        form.name.data = edit_project['title']
        form.description.data = edit_project['description']
        form.start_date.data = edit_project['start_date']
        form.end_date.data = edit_project['end_date']
        form.monday.data = edit_project['class_days']['monday']
        form.tuesday.data = edit_project['class_days']['tuesday']
        form.wednesday.data = edit_project['class_days']['wednesday']
        form.thursday.data = edit_project['class_days']['thursday']
        form.friday.data = edit_project['class_days']['friday']
        form.saturday.data = edit_project['class_days']['saturday']
    return render_template('edit_project.html', title='PM TOOL', form=form, project_title=edit_project['title'], 
                           project_members=project_members, project_id=project_id, add_member_form=add_member_form)


@app.route('/add_member/<string:project_id>/', methods=['GET', 'POST'])
@login_required
@user_project_required
def add_member(project_id):
    project = PROJECTS.find_one({'_id': ObjectId(project_id)})
    form = AddMemberForm()
    if form.validate_on_submit():
        email = f'{form.email.data}@saskpolytech.ca'
        member = USERS.find_one({'email': email})
        if member is not None:   
            USER_PROJECTS.update_one({'user_id':str(member['_id'])}, {'$push': {'projects': str(project['_id'])}}, upsert=True)
            PROJECTS.update_one({'_id': ObjectId(project_id)}, {'$push': {'members': str(member['_id'])}}, upsert=True)
        else:
            flash(f'No user is registered with {email} email address.', 'alert-warning')
    return redirect(url_for('edit_project', project_id=project_id))


@app.route('/remove_member/<string:project_id>/<string:member_id>', methods=['GET', 'POST'])
@login_required
@user_project_required
def remove_member(project_id, member_id):
    project = PROJECTS.find_one({'_id': ObjectId(project_id)})
    member = USERS.find_one({'_id': ObjectId(member_id)})
    
    USER_PROJECTS.update_one({'user_id':str(member['_id'])}, {'$pull': {'projects': str(project['_id'])}})
    PROJECTS.update_one({'_id': ObjectId(project_id)}, {'$pull': {'members': str(member['_id'])}})
    flash(f'User {member['name']} has been removed from the project', 'alert-info')
    return redirect(url_for('edit_project', project_id=project_id))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        user = USERS.find_one({"email": form.email.data})
        if not user:
            USERS.insert_one({"name": form.name.data, "email": f'{form.email.data}@saskpolytech.ca', 
                              "password": User.set_password(form.password.data)})
            flash('Congratulations, you are now a registered user!', 'alert-info')
        else:
            flash('Email has already been registered', 'alert-warning')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = USERS.find_one({"email": f'{form.email.data}@saskpolytech.ca'})
        if user and User.check_password(user['password'], form.password.data):
            user_obj = User(id=str(user['_id']))
            login_user(user_obj)
            next_page = request.args.get('next')
            if not next_page or urlparse(next_page).netloc != '':
                next_page = url_for('index')
            return redirect(next_page)
        else:
            flash("Invalid username or password", 'alert-warning')
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))