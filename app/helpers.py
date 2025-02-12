import os
from app import TASKS, PROJECTS, USERS, USER_PROJECTS, NOTIFICATIONS, PROJECT_LOGS
from flask import flash, redirect, url_for
from flask_login import current_user
from bson import ObjectId
from functools import wraps
import datetime
from PIL import Image, ImageDraw, ImageFont

# decorator to only allow users to access projects they have been given access
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


# decorator to only allow access to team leaders of a project
def project_team_leader_required(f):
    @wraps(f)
    def decorated_function(project_id, *args, **kwargs):
        try:
            # Ensure project_id is a valid ObjectId
            project_id = ObjectId(project_id)
        except Exception:
            flash("Invalid project ID", "alert-danger")
            return redirect(url_for("index"))
        
        # Fetch the project from the database
        project = PROJECTS.find_one({"_id": project_id})
        if not project:
            flash("Project not found", "alert-danger")
            return redirect(url_for("index"))
        
        # Check if the current user is a team leader for the project
        if str(current_user.id) not in project.get("team_leaders", []):
            flash("You are not registered as a team leader for this project", "alert-danger")
            return redirect(url_for("index"))
        
        # Proceed to the wrapped function if the check passes
        return f(project_id, *args, **kwargs)
    return decorated_function


# sort tasks by hierarchy and by parent
# def sort_tasks(project_id: str, parent_task_id: str, task_list: list):
#     _tasks = sorted(list(TASKS.find({"project_id": project_id, "parent_task_id": parent_task_id})), key=lambda d: d['hierarchy'])
#     for t in _tasks:
#         task_list.append(t)
#         sort_tasks(project_id, str(t["_id"]), task_list)
#     return task_list

def sort_tasks(project_id: str) -> list:
    """
    Loads all tasks for a given project exactly once from the DB,
    then returns a list of tasks sorted by hierarchy in a parent->child order.
    """

    # 1) Load all tasks at once
    all_tasks = list(TASKS.find({"project_id": project_id}))

    # 2) Build a map of parent_task_id -> list of child tasks
    tasks_by_parent = {}
    for t in all_tasks:
        parent_id = t.get("parent_task_id", "0")
        tasks_by_parent.setdefault(parent_id, []).append(t)

    # 3) Recursive function to collect tasks in sorted order
    def _collect_sorted(parent_id: str, result: list):
        # Get tasks under this parent_id
        children = tasks_by_parent.get(parent_id, [])
        # Sort them by 'hierarchy' or any other criteria
        children.sort(key=lambda d: d["hierarchy"])

        for child in children:
            result.append(child)
            # Recurse for this child's children
            _collect_sorted(str(child["_id"]), result)

    # 4) Start with parent_task_id="0" or whatever your root is
    sorted_list = []
    _collect_sorted("0", sorted_list)
    return sorted_list


# updating child tasks of each tasks
# not in any route, only used for updating db
def update_child_tasks(project_id:str, parent_task_id:str):
    _tasks = TASKS.find({"project_id": project_id, "parent_task_id": parent_task_id})
    _t = None
    for t in _tasks:
        if parent_task_id != "0":
            TASKS.update_one({'_id': ObjectId(parent_task_id)}, {'$addToSet': {'children': str(t["_id"])}}, upsert=True)
        
        update_child_tasks(project_id, str(t["_id"]))
        # try:
        #     TASKS.update_one({'_id': ObjectId(parent_task_id)}, {'$addToSet': {'children': str(t["_id"])}}, upsert=True)
        #     print(f'{TASKS.find_one(ObjectId(t["_id"]))}')
        # except WriteError:
        #     print('error')
        #     TASKS.update_one({'_id': ObjectId(parent_task_id)}, {'$push': {'children': str(t["_id"])}}, upsert=True)
        
    return "done"

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Mapping weekdays to corresponding indices
day_mapping = {
    'sunday': 6,
    'monday': 0,
    'tuesday': 1,
    'wednesday': 2,
    'thursday': 3,
    'friday': 4,
    'saturday': 5
}

basedir = os.path.abspath(os.path.dirname(__file__))

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
           

def create_profile_pic(first_name, last_name, size=128, bg_color=(47, 47, 47), text_color=(255, 255, 255)):
    # Create initials from first and last name
    initials = f"{first_name[0].upper()}{last_name[0].upper()}"
    
    # Create a square image with the specified background color
    image = Image.new('RGB', (size, size), color=bg_color)
    draw = ImageDraw.Draw(image)

    # Set font size to be relative to the image size
    font_size = int(size * 0.5)
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        # Use a default font if Arial is not available
        font = ImageFont.load_default()

    # Calculate text position to center it
    text_length = draw.textlength(initials, font=font)
    text_x = (size - text_length) // 2
    text_y = (size - text_length) // 2

    # Add the initials text to the image
    draw.text((text_x, text_y), initials, fill=text_color, font=font)

    # Save or return the image
    return image
   
    
def create_notification(user_id, message, type="info"):
    NOTIFICATIONS.insert_one({
        "user_id": user_id,
        "message": message,
        "type": type,
        "is_read": False,
        "timestamp": datetime.datetime.now(datetime.UTC)
    })
    
    
def create_project_log(project_id, user_id, action, details=None):
    PROJECT_LOGS.insert_one({
        "project_id": project_id,
        "user_id": user_id,
        "action": action,
        "details": details,
        "timestamp": datetime.datetime.now(datetime.UTC)
    })