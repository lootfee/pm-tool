from app import TASKS, PROJECTS, USERS, USER_PROJECTS
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


def remove_team_member(user_id, project_id):
    try:
        project = PROJECTS.find_one({'_id': ObjectId(project_id)})
        member = USERS.find_one({'_id': ObjectId(user_id)})
            
        if not member or not project:
            flash("Invalid user or project.", "alert-danger")
            return False

        if user_id in project.get("team_leaders", []) and len(project.get("team_leaders", [])) <= 1:
            flash("Cannot remove the only team leader.", "alert-warning")
            return False

        # Check if the user has assigned tasks
        assigned_tasks = TASKS.count_documents({"project_id": project_id, "owners": {"$in": [user_id]}})
        if assigned_tasks > 0:
            flash(f"User {member['name']} has assigned tasks. Reassign tasks before removing.", "alert-warning")
            return False
        
        USER_PROJECTS.update_one({'user_id':str(member['_id'])}, {'$pull': {'projects': str(project['_id'])}})
        PROJECTS.update_one({'_id': ObjectId(project_id)}, {'$pull': {'members': str(member['_id'])}})
        flash(f'User {member['name']} has been removed from the project', 'alert-info')
        return True
    
    except Exception as e:
        # Log the error and flash a message
        flash(f"Invalid ID format: {e}", "alert-danger")
        return False


def assign_team_leader(user_id, project_id):
    try:
        # Ensure user_id and project_id are valid ObjectIds
        obj_user_id = ObjectId(user_id)
        obj_project_id = ObjectId(project_id)
            
        # Check if the user exists in the database
        user = USERS.find_one({"_id": obj_user_id})
        if not user:
            flash("User not found", "alert-danger")
            return False
        
        # Check if the project exists
        project = PROJECTS.find_one({"_id": obj_project_id})
        if not project:
            flash("Project not found", "alert-danger")
            return False
        
        # Check if the user is already assigned as a team leader
        if "team_leaders" in project and user_id in project["team_leaders"]:
            flash(f"{user['name']} is already a team leader for this project", "alert-warning")
            return False
        
        # Add the user to the project's team leaders list
        PROJECTS.update_one(
            {"_id": obj_project_id},
            {"$addToSet": {"team_leaders": user_id}}
        )
        flash("User successfully assigned as team leader", "alert-info")
        return True
    
    except Exception as e:
        # Log the error and flash a message
        flash(f"Invalid ID format: {e}", "alert-danger")
        return False
    
    
def remove_team_leader(user_id, project_id):
    try:
        # Ensure IDs are valid ObjectId instances
        user_id = str(user_id)  # Keep as string to match stored format
        obj_project_id = ObjectId(project_id)
        
        # Fetch the project
        project = PROJECTS.find_one({"_id": obj_project_id})
        if not project:
            flash("Project not found", "alert-danger")
            return False
        
        # Check if the user is already a team leader
        team_leaders = project.get("team_leaders", [])
        if user_id not in team_leaders:
            flash("User is not a team leader for this project", "alert-danger")
            return False
        
        if len(team_leaders) <= 1:
            flash("Cannot remove the only team leader.", "alert-warning")
            return False

        # Remove the user from the team_leaders array
        PROJECTS.update_one(
            {"_id": obj_project_id},
            {"$pull": {"team_leaders": user_id}}
        )
        
        flash("Team leader role removed successfully", "alert-info")
        return True

    except Exception as e:
        # Log the error and flash a message
        flash(f"An error occurred: {str(e)}", "alert-danger")
        return False