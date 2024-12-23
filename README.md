# PM Tool

**PM Tool** is a project management web application designed to help teams collaborate on projects, manage tasks, and visualize progress using features like Kanban boards, Gantt charts, and Work Breakdown Structures (WBS).



## Features

* User authentication and profile management.
* Microsoft OAuth login.
* Easy management of projects and tasks.
* Visualize tasks on Kanban boards, Gantt charts, and WBS diagrams.
* VIsualize task dependencies and completion % on Gantt chart.
* Gantt chart navigation with treegrid axis.
* Assigning team members to projects.
* Track member expected and actual work hours.
* Track project expected and actual hours.
* Program Evaluation and Review Technique (PERT) calculation based on work hours.
* Auto calculation of estimated end date based on PERT and selected work days.


## Installation

**Prerequisites**

1. Python 3.12+

2. MongoDB

**Setup Instructions**

1. Clone the repository:
```bash
git clone https://github.com/lootfee/pm-tool.git
cd pm-tool
```

2. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: cd venv\Scripts then run activate.bat
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a .env file in the root directory:
```bash
SECRET_KEY=your_secret_key
DB_USERNAME=db_username
DB_PASSWORD=db_password
MICROSOFT_CLIENT_ID=your_msal_client_id
MICROSOFT_CLIENT_SECRET=your_msal_client_secret
TENANT_ID=
```

5. Setup the database
* Create user and connection in MongoDB Compass
    - https://www.geeksforgeeks.org/how-to-set-username-and-password-in-mongodb-compass/
    - database name is "pm-tool"

* Create the following database collections
     - projects
     - tasks
     - user_projects
     - users


6. Run the application:
```bash
flask run
```

## Technologies Used

**Frontend**
* HTML, CSS: For structure and styling.
* Bootstrap 5: Responsive design and prebuilt UI components.
* Highcharts.js: For visualizations including Gantt charts and WBS.

**Backend**

* Flask: Web framework for backend logic.
* Flask-WTF: Form handling.
* Flask-Login: User authentication.

**Database**

* MongoDB: NoSQL database for storing projects, tasks, and user information.

## Usage Guide

**Creating a Project**

1. Log in to your account.

2. Navigate to the "Projects" page.

3. Click the "New Project" button.

4. Fill out the project form:

**Managing Project Members**

1. Navigate to the "Edit Project" page for a specific project.

2. Use the "Add Member" form to invite team members by email.

3. To remove a member, click the "Remove" button next to their name in the Members table.

**Creating a Task**

1. Open the project page.

2. Select a project.

3. Click the "New Task" button.

4. Fill out the task details:

**Managing Tasks**

* Tasks are displayed on the Kanban board, WBS and Gantt charts and can be moved between columns based on status.

* Tasks can be edited or deleted by clicking the corresponding buttons in the Kanban or Gantt views.

## Visualizing Progress

**Kanban Board**

* View and organize tasks by status (To Do, In Progress, Delayed, On Hold, Completed).

**Gantt Chart**

* Visualize task timelines, dependencies, and progress.

**Work Breakdown Structure (WBS)**

* View the hierarchical structure of tasks and subtasks.

## Todo's
* Add team leader role and create decorator
* Move deleting project button to edit project page
* Update user_project decorator
* Download projects data as JSON
* Email and in app notifications
* User accept/reject a project
* Removing members with already assigned tasks
* Add overtime hrs (days/hrs not included in working days/hrs)

## License

This project is licensed under the MIT License.