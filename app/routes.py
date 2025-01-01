from app import app, PROJECTS, TASKS, USERS, USER_PROJECTS, msal_app
from flask import flash, render_template, redirect, url_for, request, jsonify, session
from app.forms import ProjectForm, TaskForm, LoginForm, RegisterForm, AddMemberForm, UpdateUserForm
from app.models import User
from app.helpers import user_project_required, project_team_leader_required, create_profile_pic, sort_tasks, allowed_file, basedir, day_mapping, assign_team_leader, remove_team_leader, remove_team_member
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.utils import secure_filename
from urllib.parse import urlparse
from bson import ObjectId
from bson.errors import InvalidId
from pymongo.errors import WriteError

from uuid import uuid4
from datetime import datetime, timedelta
from pprint import pprint

import os


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
        
        monday_hrs = form.monday.data
        tuesday_hrs = form.tuesday.data
        wednesday_hrs = form.wednesday.data
        thursday_hrs = form.thursday.data
        friday_hrs = form.friday.data
        saturday_hrs = form.saturday.data
        sunday_hrs = form.sunday.data
        
        work_days = {'monday': monday_hrs, 'tuesday': tuesday_hrs, 'wednesday': wednesday_hrs,
                    'thursday': thursday_hrs, 'friday': friday_hrs, 'saturday': saturday_hrs, 'sunday': sunday_hrs}

        # Initialize total hours counter
        total_hours = 0

        # Iterate through each day from start_date to end_date
        current_date = start_date
        while current_date <= end_date:
            day_of_week = current_date.weekday()
            for day, hours in work_days.items():
                if day_mapping[day] == day_of_week:
                    if hours is not None:
                        total_hours += hours
                    break
            current_date += timedelta(days=1)
            
        new_project = PROJECTS.insert_one({"title": title, "description": description, "start_date": start_date, "end_date": end_date, 'members': [current_user.id], 
                                           'work_days': work_days, 'total_hours': total_hours})
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
    # print(request.args.get('active_tab', str))
    # print(request.referrer)
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
    pprint(_sorted_tasks)
    for task in sorted_tasks:
        def format_date(date):
            try:
                return date.strftime("%m/%d/%Y")
            except AttributeError:
                return ""

        expected_start_date = format_date(task.get('expected_start_date'))
        expected_end_date = format_date(task.get('expected_end_date'))
        actual_start_date = format_date(task.get('actual_start_date'))
        actual_end_date = format_date(task.get('actual_end_date'))
        
        owner_pics = []
        owner_names = []
        for owner_id in task['owners']:
            owner_names.append(get_user(owner_id)['name'])
            try:
                owner_pics.append(url_for('static', filename='profile_pics/' + get_user(owner_id)['profile_pic']))
            except KeyError:
                owner_pics.append(url_for('static', filename='default-avatar.png'))
        try:
            children = task['children']
        except KeyError:
            children = []
        all_tasks.append({'_id': str(task['_id']), 'project_id': task['project_id'], "task_number": task['task_number'], "title": task['title'], 
                                    "expected_start_date": expected_start_date, "expected_end_date": expected_end_date, "actual_start_date": actual_start_date, 
                                    "actual_end_date": actual_end_date, "optimistic_duration": task.get('optimistic_duration', 0), 
                                    "expected_duration": task.get('expected_duration', 0), "pessimistic_duration": task.get('pessimistic_duration', 0), 
                                    "reserve_analysis": task.get('reserve_analysis', 0), "total_expected_duration": task.get('total_expected_duration', 0), 
                                    "total_actual_duration": task.get('total_actual_duration', 0), "comments": task.get('comments', ''), 
                                    "parent_task_id": task['parent_task_id'], "completion": task['completion'], "hierarchy": task['hierarchy'],
                                    "dependency": task['dependency'], "level": task['level'], "children": children, 
                                    "owners": task['owners'], "owner_names": owner_names, "owner_pics": owner_pics})
        form.parent_task.choices.append((task['_id'], f'{task['task_number']} {task['title']}'))
        form.dependency.choices.append((task['_id'], f'{task['task_number']} {task['title']}'))

    # pprint(all_tasks)
    active_tab = request.args.get('active_tab', str)
    valid_tabs = ["nav-kanban-tab", "nav-gantt-tab", "nav-wbs-tab"]
    if not active_tab or active_tab not in valid_tabs:
        active_tab = "nav-kanban-tab"
    
    # for repopulating the modal if invalid
    valid_form = True
    if request.method == 'POST':
        valid_form = form.validate()
    # print(form.errors)
    # print(valid_form)
    if form.validate_on_submit():
        task_id = form.task_id.data
        task_number = form.task_number.data
        title = form.title.data
        optimistic_duration = float(form.optimistic_duration.data)  # parse to float since mongodb can only accept decimal128 type
        expected_duration = float(form.expected_duration.data)
        pessimistic_duration = float(form.pessimistic_duration.data)
        reserve_analysis = float(form.reserve_analysis.data)
        total_expected_duration = float(form.total_expected_duration.data)
        total_actual_duration = float(form.total_actual_duration.data)
        comments = form.comments.data
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
        # print(f'task id: {task_id}')
        # print({'project_id': project_id, "task_number": task_number, "title": title, 
        #                             "expected_start_date": expected_start_date, "expected_end_date": expected_end_date, 
        #                             "actual_start_date": actual_start_date, "actual_end_date": actual_end_date,
        #                             "parent_task_id": parent_task_id, "optimistic_duration": optimistic_duration,
        #                             "expected_duration": expected_duration, "pessimistic_duration": pessimistic_duration,
        #                             "reserve_analysis": reserve_analysis, "comments": comments,
        #                             "level": level,"hierarchy": hierarchy, "completion": completion, 
        #                             "dependency": dependency, "owners": owners})
        if task_id:
            try:
                upd_task = TASKS.update_one({'_id': ObjectId(task_id)}, {'$set': {'project_id': project_id, "task_number": task_number, "title": title, 
                                    "expected_start_date": expected_start_date, "expected_end_date": expected_end_date, 
                                    "actual_start_date": actual_start_date, "actual_end_date": actual_end_date,
                                    "parent_task_id": parent_task_id, "optimistic_duration": optimistic_duration,
                                    "expected_duration": expected_duration, "pessimistic_duration": pessimistic_duration,
                                    "reserve_analysis": reserve_analysis, "total_expected_duration": total_expected_duration, 
                                    "total_actual_duration": total_actual_duration, "comments": comments,
                                    "level": level,"hierarchy": hierarchy, "completion": completion, 
                                    "dependency": dependency, "owners": owners}}, upsert=True)
            
                if parent_task_id != "0": 
                    TASKS.update_one({'_id': ObjectId(parent_task_id)}, {'$addToSet': {'children': task_id}}, upsert=True)
            except InvalidId:
                flash('Invalid Task ID', 'alert-warning')
        else:
            new_task = TASKS.insert_one({'project_id': project_id, "task_number": task_number, "title": title, 
                                        "expected_start_date": expected_start_date, "expected_end_date": expected_end_date, 
                                        "actual_start_date": actual_start_date, "actual_end_date": actual_end_date,
                                        "parent_task_id": parent_task_id, "optimistic_duration": optimistic_duration,
                                        "expected_duration": expected_duration, "pessimistic_duration": pessimistic_duration,
                                        "reserve_analysis": reserve_analysis, "total_expected_duration": total_expected_duration, 
                                        "total_actual_duration": total_actual_duration, "comments": comments,
                                        "level": level,"hierarchy": hierarchy, "completion": completion, 
                                        "dependency": dependency, "owners": owners, "children": []})
        
            if parent_task_id != "0": 
                TASKS.update_one({'_id': ObjectId(parent_task_id)}, {'$addToSet': {'children': str(new_task.inserted_id)}}, upsert=True)
        
        # to open the active tab where the user is after page refresh/form submit
        # active_tab = request.args.get('active_tab', str)
        # next_page = url_for('project', project_id=project_id)
        # if active_tab:
        #     next_page += f'?active_tab={active_tab}'
        # print(next_page)
        
        return redirect(request.referrer)
    return render_template('project_page.html', title='PM Tool', project_id=project_id, project_title=project['title'], 
                           project_start_date=project["start_date"], project_end_date=project["end_date"], form=form, 
                           all_tasks=all_tasks, active_tab=active_tab, valid_form=valid_form, work_days=project['work_days'],
                           project_members=project_members, project_total_hours=project["total_hours"])



@app.route('/edit_project/<string:project_id>/', methods=['GET', 'POST'])
@login_required
@user_project_required
def edit_project(project_id):
    add_member_form = AddMemberForm()
    form = ProjectForm()
    edit_project = PROJECTS.find_one({'_id': ObjectId(project_id)})
    project_team_leaders = edit_project['team_leaders']
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
        sunday_hrs = form.sunday.data
        
        work_days = {'monday': monday_hrs, 'tuesday': tuesday_hrs, 'wednesday': wednesday_hrs,
                    'thursday': thursday_hrs, 'friday': friday_hrs, 'saturday': saturday_hrs, 'sunday': sunday_hrs}

        # Initialize total hours counter
        total_hours = 0

        # Iterate through each day from start_date to end_date
        current_date = start_date
        while current_date <= end_date:
            day_of_week = current_date.weekday()
            for day, hours in work_days.items():
                if day_mapping[day] == day_of_week:
                    total_hours += hours
                    break
            current_date += timedelta(days=1)
        
        PROJECTS.update_one({'_id': ObjectId(project_id)}, {'$set': {"title": title, "description": description, "start_date": start_date, "end_date": end_date, 'members': [current_user.id], 
                                           'work_days': work_days, 'total_hours': total_hours}}, upsert=False)

        return redirect(url_for('edit_project', project_id=project_id))

    elif request.method == 'GET':
        form.name.data = edit_project['title']
        form.description.data = edit_project['description']
        form.start_date.data = edit_project['start_date']
        form.end_date.data = edit_project['end_date']
        form.monday.data = edit_project['work_days']['monday']
        form.tuesday.data = edit_project['work_days']['tuesday']
        form.wednesday.data = edit_project['work_days']['wednesday']
        form.thursday.data = edit_project['work_days']['thursday']
        form.friday.data = edit_project['work_days']['friday']
        form.saturday.data = edit_project['work_days']['saturday']
        form.sunday.data = edit_project['work_days']['sunday']
    return render_template('edit_project.html', title='PM TOOL', form=form, project_title=edit_project['title'], project_team_leaders=project_team_leaders,
                           project_members=project_members, project_id=project_id, add_member_form=add_member_form)


@app.route('/add_member/<string:project_id>/', methods=['GET', 'POST'])
@login_required
@user_project_required
def add_member(project_id):
    project = PROJECTS.find_one({'_id': ObjectId(project_id)})
    form = AddMemberForm()
    if form.validate_on_submit():
        email = form.email.data
        member = USERS.find_one({'email': email})
        if member is not None:   
            USER_PROJECTS.update_one({'user_id':str(member['_id'])}, {'$push': {'projects': str(project['_id'])}}, upsert=True)
            PROJECTS.update_one({'_id': ObjectId(project_id)}, {'$push': {'members': str(member['_id'])}}, upsert=True)
        else:
            flash(f'No user is registered with {email} email address.', 'alert-warning')
    return redirect(url_for('edit_project', project_id=project_id))


@app.route('/remove_member/<string:project_id>/<string:member_id>', methods=['POST'])
@login_required
@user_project_required
def remove_member(project_id, member_id):
    if remove_team_member(member_id, project_id):
        return redirect(url_for('edit_project', project_id=project_id))
    return redirect(url_for('edit_project', project_id=project_id))
    # if request.referrer == url_for('index'):
    #     return redirect(url_for('index'))
    # return redirect(url_for('edit_project', project_id=project_id))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        user = USERS.find_one({"email": form.email.data})
        if not user:
            user_name = form.name.data.split(' ')
            filename = uuid4().hex + '.png'
            profile_pic = create_profile_pic(user_name[0], user_name[-1])
            file_path = os.path.join(app.config['PROFILE_PICS_PATH'], filename)
            profile_pic.save(file_path)
            USERS.insert_one({"name": form.name.data, "email": form.email.data, 
                              "password": User.set_password(form.password.data), "profile_pic": filename})
            flash('Congratulations, you are now a registered user!', 'alert-info')
        else:
            flash('Email has already been registered', 'alert-warning')
        return redirect(url_for('login'))
    elif form.errors:
        pprint(form.errors)
        form.name.data = form.name.data
        form.email.data = form.email.data
    return render_template('register.html', title='Register', form=form)


@app.route('/msal_login')
def msal_login():
    # Generate the authorization URL
    auth_url = msal_app.get_authorization_request_url(
        app.config["MICROSOFT_SCOPES"],
        redirect_uri=url_for('auth_callback', _external=True)
    )
    return redirect(auth_url)


@app.route('/auth/callback')
def auth_callback():
    # Get the authorization code from the URL
    code = request.args.get('code')
    if code:
        # Request tokens using the authorization code
        result = msal_app.acquire_token_by_authorization_code(
            code,
            scopes=app.config["MICROSOFT_SCOPES"],
            redirect_uri=url_for('auth_callback', _external=True)
        )
        
        if "access_token" in result:
            
            # Extract user information from the token
            user_id = result.get("id_token_claims").get("oid")
            user_name = result.get("id_token_claims").get("name")
            user_email = result.get("id_token_claims").get("preferred_username")

            user = USERS.find_one({"email": user_email})
            if not user:
                uname = user_name.split(',')
                if len(uname) == 1:
                    uname = user_name.split(' ')
                filename = uuid4().hex + '.png'
                profile_pic = create_profile_pic(uname[0].replace(' ',''), uname[-1].replace(' ',''))
                file_path = os.path.join(basedir, app.config['PROFILE_PICS_PATH'], filename)
                profile_pic.save(file_path)
                
                user = USERS.insert_one({"name": user_name, "email": user_email, 
                              "oid": user_id, "profile_pic": filename})
                
            
            try:
                user_obj = User(id=str(user['_id']))
            except TypeError:  # or the specific exception you expect
                user_obj = User(id=str(user.inserted_id))
            login_user(user_obj)
            next_page = request.args.get('next')
            if not next_page or urlparse(next_page).netloc != '':
                next_page = url_for('index')
            return redirect(next_page)
        else:
            flash(f"Login failed: {result.get('error')}", 'alert-warning')
            return redirect(url_for('login'))
    return "Authorization code not found."


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = USERS.find_one({"email": form.email.data})
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
    session.clear()
    # return redirect(
    #     app.config["MICROSOFT_AUTHORITY"] + "/oauth2/v2.0/logout" +
    #     "?post_logout_redirect_uri=" + url_for("login", _external=True)
    # )
    return redirect(url_for('login'))


# GET - Retrieve user details by _id
@app.route('/api/user/<user_id>', methods=['GET'])
def get_user(user_id):
    try:
        user = USERS.find_one({"_id": ObjectId(user_id)})
        if user:
            # user['_id'] = str(user['_id'])  # Convert ObjectId to string for JSON serialization
            return user#jsonify(user), 200
        return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'error': 'Invalid user ID'}), 400


# Combined route to display and update user profile
@app.route('/user/<user_id>', methods=['GET', 'POST'])
def user_profile(user_id):
    user = USERS.find_one({"_id": ObjectId(user_id)})
    if not user:
        flash('User not found', 'alert-danger')
        return redirect(url_for('index'))
    
    form = UpdateUserForm()

    # Populate form with current user data if it's a GET request
    if request.method == 'GET':
        form.name.data = user.get('name', '')
        form.email.data = user.get('email', '')
        return render_template('user.html', form=form, user=user)

    # Handle form submission on POST
    if form.validate_on_submit():
        # Update name and email (append domain for email)
        updated_data = {
            'name': form.name.data,
            'email': form.email.data
        }

        # Handle profile picture upload
        if 'profile_pic' in request.files:
            file = request.files['profile_pic']
            if file and allowed_file(file.filename):
                
                filename = secure_filename(file.filename)
                file_path = os.path.join(basedir, app.config['PROFILE_PICS_PATH'], filename)

                # Remove old profile picture if it exists
                if 'profile_pic' in user and os.path.exists(user['profile_pic']):
                    os.remove(user['profile_pic'])

                # Save new profile picture
                file.save(file_path)
                updated_data['profile_pic'] = filename
            else:
                flash('Invalid file type for profile picture', 'alert-danger')
                return redirect(url_for('user_profile', user_id=user_id))

        # Update user in database
        USERS.update_one({"_id": ObjectId(user_id)}, {"$set": updated_data})
        flash('Profile updated successfully', 'alert-success')
        return redirect(url_for('user_profile', user_id=user_id))
    
    # If form validation fails, re-render the page with errors
    return render_template('user.html', form=form, user=user)


# POST - Delete User Account
@app.route('/user/<user_id>/delete', methods=['POST'])
def delete_user(user_id):
    user = USERS.find_one({"_id": ObjectId(user_id)})

    if not user:
        flash('User not found', 'alert-danger')
        return redirect(url_for('index'))

    # Remove the profile picture if it exists
    if 'profile_pic' in user and os.path.exists(user['profile_pic']):
        os.remove(user['profile_pic'])

    # Remove user from the database
    USERS.delete_one({"_id": ObjectId(user_id)})

    flash('User deleted successfully', 'alert-success')
    return redirect(url_for('index'))

@app.route('/assign_project_team_leader/<user_id>/<project_id>', methods=['POST'])
@login_required
@project_team_leader_required
def assign_project_team_leader(user_id, project_id):
    if assign_team_leader(user_id, project_id):
        return redirect(url_for('edit_project', project_id=project_id))
    return redirect(url_for('edit_project', project_id=project_id))


@app.route('/remove_project_team_leader/<user_id>/<project_id>', methods=['POST'])
@login_required
@project_team_leader_required
def remove_project_team_leader(user_id, project_id):
    if remove_team_leader(user_id, project_id):
        return redirect(url_for("edit_project", project_id=project_id))
    return redirect(url_for("edit_project", project_id=project_id))