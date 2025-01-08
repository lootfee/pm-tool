from app import app, PROJECTS, TASKS, USERS, USER_PROJECTS, PROJECT_INVITES, NOTIFICATIONS, PROJECT_LOGS, msal_app
from flask import flash, render_template, redirect, url_for, request, jsonify, session
from app.forms import ProjectForm, TaskForm, LoginForm, RegisterForm, AddMemberForm, UpdateUserForm, EditRoleForm, RemoveMemberForm
from app.models import User
from app.helpers import user_project_required, project_team_leader_required, create_profile_pic, sort_tasks, allowed_file, basedir, day_mapping, create_notification, create_project_log
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
def index(): # projects page
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
                                           'work_days': work_days, 'total_hours': total_hours, 'team_leaders': [current_user.id]})
        USER_PROJECTS.update_one({'user_id': current_user.id}, {'$push': {'projects': str(new_project.inserted_id)}}, upsert=True)
        create_project_log(str(new_project.inserted_id), str(current_user.id), "Project created")

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
                    # create_notification(current_user.id, f'Task {task_number} {title} has been updated')
                    create_project_log(project_id, current_user.id, 'Task', f'Task {task_number} {title} updated')
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
                
            # create_notification(current_user.id, f'Task {task_number} {title} has been created')
            create_project_log(project_id, current_user.id, 'Task', f'Task {task_number} {title} created')
        
        # to open the active tab where the user is after page refresh/form submit        
        return redirect(request.referrer)
    return render_template('project_page.html', title='PM Tool', project_id=project_id, project_title=project['title'], 
                           project_start_date=project["start_date"], project_end_date=project["end_date"], form=form, 
                           all_tasks=all_tasks, active_tab=active_tab, valid_form=valid_form, work_days=project['work_days'],
                           project_members=project_members, project_total_hours=project["total_hours"])



@app.route('/edit_project/<string:project_id>/', methods=['GET', 'POST'])
@login_required
@user_project_required
def edit_project(project_id):
    form = ProjectForm()
    add_member_form = AddMemberForm()
    edit_role_form = EditRoleForm()
    remove_member_form = RemoveMemberForm()
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
        
        # create_notification(current_user.id, f'Project {title} has been updated')
        create_project_log(project_id, current_user.id, 'Project', f'Project {title} updated')

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
                           project_members=project_members, project_id=project_id, add_member_form=add_member_form, edit_role_form=edit_role_form, 
                           remove_member_form=remove_member_form)


@app.route('/project/<string:project_id>/add_member/', methods=['POST'])
@login_required
@user_project_required
@project_team_leader_required
def invite_project_member(project_id):
    project = PROJECTS.find_one({'_id': ObjectId(project_id)})
    form = AddMemberForm()
    if form.validate_on_submit():
        email = form.amf_email.data
        member = USERS.find_one({'email': email})
        if member is not None:
            has_invites = PROJECT_INVITES.find_one({'project_id':  project_id, 'user_id': str(member['_id'])})
            if not has_invites:
                PROJECT_INVITES.insert_one({"project_id": str(project_id), "user_id": str(member['_id']), "invited_by_id": current_user.id})
                create_notification(str(member['_id']), f'You have been invited to join the project {project["title"]}.')
                create_project_log(str(project_id), current_user.id, 'Member', f'{member['name']} has been invited to join the project.')
                flash(f'An invitation to join the project {project['title']} has been sent to {member['name']}.', 'alert-info')
            else:
                flash(f'A previous invitation has been made and is waiting for acceptance from {member['name']}.', 'alert-warning')
        else:
            flash(f'No user is registered with {email} email address.', 'alert-warning')
    return redirect(url_for('edit_project', project_id=project_id))


@app.route('/projects/invite/<invite_id>/accept', methods=['POST'])
@login_required
def accept_project_invite(invite_id):
    invite = PROJECT_INVITES.find_one({'_id': ObjectId(invite_id)})
    if invite and invite['user_id'] == str(current_user.id):
        project = PROJECTS.find_one({'_id': ObjectId(invite['project_id'])})
        USER_PROJECTS.update_one({'user_id': str(current_user.id)}, {'$push': {'projects': str(project['_id'])}}, upsert=True) 
        PROJECTS.update_one({'_id': project['_id']}, {'$push': {'members': str(current_user.id)}}, upsert=True)
        PROJECT_INVITES.delete_one({'_id': ObjectId(invite_id)})
        # create_notification(str(current_user.id), f'You have accepted to join the project {project["title"]}.')
        create_project_log(str(project['_id']), current_user.id, 'Member', f'{current_user.name} has joined the project.')
        flash('Project invitation accepted!', 'alert-success')
    else:
        flash('Invalid invitation!', 'alert-danger')
    return redirect(url_for('user_profile'))


@app.route('/projects/invite/<invite_id>/reject', methods=['POST'])
@login_required
def reject_project_invite(invite_id):
    invite = PROJECT_INVITES.find_one({'_id': ObjectId(invite_id)})
    if invite and invite['user_id'] == str(current_user.id):
        project = PROJECTS.find_one({'_id': ObjectId(invite['project_id'])})
        PROJECT_INVITES.delete_one({'_id': ObjectId(invite_id)})
        create_project_log(str(project['_id']), current_user.id, 'Member', f'{current_user.name} has declined to join the project.')
        flash('Project invitation rejected.', 'alert-info')
    else:
        flash('Invalid invitation!', 'alert-danger')
    return redirect(url_for('user_profile'))


# @app.route('/project/<string:project_id>/accept_invite/<string:user_id>/', methods=['POST']) 
# @login_required 
# def accept_project_invite(project_id, user_id): 
#     invite = PROJECT_INVITES.find_one({'project_id': project_id, 'user_id': user_id}) 
#     if invite is not None: 
#         project = PROJECTS.find_one({'_id': ObjectId(project_id)}) 
#         member = USERS.find_one({'_id': ObjectId(user_id)}) 
#         if member is not None: 
#             USER_PROJECTS.update_one({'user_id': str(member['_id'])}, {'$push': {'projects': str(project['_id'])}}, upsert=True) 
#             PROJECTS.update_one({'_id': ObjectId(project_id)}, {'$push': {'members': str(member['_id'])}}, upsert=True) 
#             PROJECT_INVITES.delete_one({'_id': invite['_id']}) 
#             create_notification(str(member['_id']), f'You have accepted to join the project {project["title"]}.')
#             create_project_log(project_id, current_user.id, 'Member', f'{member['name']} has joined the project.')
#             flash(f'You have successfully joined the project {project['title']}.', 'alert-success') 
#         else: 
#             flash(f'Invalid invite.', 'alert-warning') 
#     else: 
#         flash(f'No invite found.', 'alert-warning') 
#     return redirect(url_for('user_profile', user_id=user_id))


@app.route('/project/<string:project_id>/remove_member/', methods=['POST'])
@login_required
@user_project_required
@project_team_leader_required
def remove_project_member(project_id):
    project = PROJECTS.find_one({'_id': ObjectId(project_id)})
    if not project:
            flash("Invalid project.", "alert-danger")
            return redirect(url_for('index'))
        
    form = RemoveMemberForm()
    if form.validate_on_submit():
        member_id = form.rmf_user_id.data
        member = USERS.find_one({'_id': ObjectId(member_id)})
        if not member:
            flash("User not found.", "alert-danger")
            
        # Check if the user is a team leader and cannot be removed if there is only one team leader left
        if member_id in project.get("team_leaders", []) and len(project.get("team_leaders", [])) <= 1:
            flash("Cannot remove the only team leader.", "alert-warning")
            
        # Check if the user has assigned tasks
        assigned_tasks = TASKS.count_documents({"project_id": project_id, "owners": {"$in": [member_id]}})
        if assigned_tasks > 0:
            flash(f"User {member['name']} has assigned tasks. Reassign tasks before removing.", "alert-warning")
            
        
        USER_PROJECTS.update_one({'user_id':str(member['_id'])}, {'$pull': {'projects': str(project['_id'])}})
        PROJECTS.update_one({'_id': ObjectId(project_id)}, {'$pull': {'members': str(member['_id'])}})
        
        # If the user was a team leader, remove them from the project
        if member_id in project.get("team_leaders"):
            PROJECTS.update_one({'_id': ObjectId(project_id)}, {'$pull': {'team_leaders': str(member['_id'])}})
            
        create_notification(str(member['_id']), f'You have been removed from project {project["title"]}.')
        create_project_log(str(project_id), current_user.id, 'Member', f'{member['name']} has been removed the project.')
        flash(f'User {member['name']} has been removed from the project', 'alert-info')
        
    return redirect(url_for('edit_project', project_id=project_id))
    
    
@app.route('/project/<string:project_id>/update_role/', methods=['POST'])
@login_required
@user_project_required
@project_team_leader_required
def update_project_member_role(project_id):
    project = PROJECTS.find_one({'_id': ObjectId(project_id)})
    if not project: 
        flash("Invalid project.", "alert-danger")
        return redirect(url_for('index'))
        
    form = EditRoleForm()
    if form.validate_on_submit():
        user_id = form.erf_user_id.data
        new_role = form.erf_role.data
        
        member = USERS.find_one({'_id': ObjectId(user_id)})
        if not member:
            flash("User not found.", "alert-danger")
        
        if new_role not in ['member', 'team_leader']:
            flash("Invalid role.", "alert-warning")
            
        if new_role == 'team_leader':
            if user_id not in project.get("team_leaders", []):
                PROJECTS.update_one({'_id': ObjectId(project_id)}, {'$addToSet': {'team_leaders': user_id}})
                create_notification(str(member['_id']), f'You have been added as team leader for project {project["title"]}.')
                create_project_log(str(project_id), current_user.id, 'Member', f'{member['name']} has been added as team leader.')
                flash(f'User {member['name']} has been added as project team leader', 'alert-info')
        elif new_role == 'member':
            if user_id in project.get("team_leaders", []):
                if len(project.get("team_leaders", [])) > 1:  # Ensure at least one team leader remains
                    PROJECTS.update_one({'_id': ObjectId(project_id)}, {'$pull': {'team_leaders': user_id}})
                    create_notification(str(member['_id']), f'Your role has been changed to "Member" for project {project["title"]}.')
                    create_project_log(str(project_id), current_user.id, 'Member', f'{member['name']} has been given the role "Member".')
                    flash(f'User {member['name']} role has been updated', 'alert-info')
                else:
                    flash("Cannot remove the only team leader.", "alert-warning")
            
    return redirect(url_for('edit_project', project_id=project_id))


@app.route('/projects/<project_id>/logs', methods=['GET'])
@login_required
@user_project_required
def get_project_logs(project_id):
    logs = PROJECT_LOGS.find({"project_id": project_id}).sort("timestamp", -1)
    logs_list = [
        {
            "_id": str(log["_id"]),
            "user_name": get_user(log["user_id"])['name'],
            "action": log["action"],
            "details": log["details"] if "details" in log else "N/A",
            "timestamp": log["timestamp"],
        }
        for log in logs
    ]
    return jsonify(logs_list)

    
@app.route('/register/', methods=['GET', 'POST'])
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
        form.name.data = form.name.data
        form.email.data = form.email.data
    return render_template('register.html', title='Register', form=form)


@app.route('/msal_login/')
def msal_login():
    # Generate the authorization URL
    auth_url = msal_app.get_authorization_request_url(
        app.config["MICROSOFT_SCOPES"],
        redirect_uri=url_for('auth_callback', _external=True)
    )
    return redirect(auth_url)


@app.route('/auth/callback/')
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


@app.route('/login/', methods=['GET', 'POST'])
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


@app.route('/logout/')
def logout():
    logout_user()
    session.clear()
    # return redirect(
    #     app.config["MICROSOFT_AUTHORITY"] + "/oauth2/v2.0/logout" +
    #     "?post_logout_redirect_uri=" + url_for("login", _external=True)
    # )
    return redirect(url_for('login'))


# GET - Retrieve user details by _id
@app.route('/api/user/<user_id>/', methods=['GET'])
@login_required
def get_user(user_id):
    try:
        user = USERS.find_one({"_id": ObjectId(user_id)})
        if user:
            # user['_id'] = str(user['_id'])  # Convert ObjectId to string for JSON serialization
            return user#jsonify(user), 200
        return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'error': 'Invalid user ID'}), 400
    
    
# GET - Retrieve user details by _id
@app.route('/api/project/<project_id>/', methods=['GET'])
@login_required
def get_project(project_id):
    try:
        project = PROJECTS.find_one({"_id": ObjectId(project_id)})
        if project:
            return project
        return jsonify({'error': 'Project not found'}), 404
    except Exception as e:
        return jsonify({'error': 'Invalid project ID'}), 400


# Combined route to display and update user profile
@app.route('/user/', methods=['GET', 'POST'])
@login_required
def user_profile():
    invites = list(PROJECT_INVITES.find({'user_id': str(current_user.id)}))
    project_invites = []
    if invites:
        project_invites = [
            {
                "id": str(invite["_id"]),
                "project_id": invite["project_id"],
                "project_name": get_project(invite["project_id"])['title'],
                "user_id": invite["user_id"],
                "invited_by": get_user(invite["invited_by_id"])['name'],
            }
            for invite in invites
        ]
                
    user = USERS.find_one({"_id": ObjectId(current_user.id)})
    form = UpdateUserForm()

    # Populate form with current user data if it's a GET request
    if request.method == 'GET':
        form.name.data = current_user.name
        form.email.data = current_user.email
        

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
                return redirect(url_for('user_profile'))

        # Update user in database
        USERS.update_one({"_id": ObjectId(current_user.id)}, {"$set": updated_data})
        flash('Profile updated successfully', 'alert-success')
        return redirect(url_for('user_profile'))
    
    # If form validation fails, re-render the page with errors
    return render_template('user.html', form=form, user=user, project_invites=project_invites)


@app.route('/notifications/read/<notification_id>/', methods=['POST'])
@login_required
def read_notification(notification_id):
    try:
        NOTIFICATIONS.update_one(
            {"_id": ObjectId(notification_id), "user_id": current_user.id},
            {"$set": {"read": True}}
        )
        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/notifications/', methods=['GET'])
@login_required
def get_notifications():
    notifications = NOTIFICATIONS.find({"user_id": current_user.id, "read": {"$ne": True}}).sort("timestamp", -1)
    notifications_list = [
        {
            "_id": str(notification["_id"]),
            "message": notification["message"],
            "timestamp": notification["timestamp"],
        }
        for notification in notifications
    ]
    return jsonify(notifications_list)
