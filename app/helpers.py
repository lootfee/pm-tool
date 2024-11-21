from app import TASKS, USER_PROJECTS
from flask import flash, redirect, url_for
from flask_login import current_user
from bson import ObjectId
from functools import wraps
import os
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