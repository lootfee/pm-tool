document.addEventListener('DOMContentLoaded', function() {
    // Cache DOM Elements
    const addTaskForm = document.getElementById('addTaskForm');
    const deleteTaskForm = document.getElementById('deleteTaskForm');
    const editTaskModalTitle = document.getElementById('addTaskModalLabel');
    const editTaskModal = new bootstrap.Modal('#addTaskModal');
    const deleteTaskModal = new bootstrap.Modal('#deleteTaskModal');
    const tabEls = document.querySelectorAll('button[data-bs-toggle="tab"]');
    // add/edit task form
    const formElements = {
        _id: document.getElementById('task_id'),
        title: document.getElementById('title'),
        task_number: document.getElementById('task_number'),
        hierarchy: document.getElementById('hierarchy'),
        optimistic_duration: document.getElementById('optimistic_duration'),
        expected_duration: document.getElementById('expected_duration'),
        pessimistic_duration: document.getElementById('pessimistic_duration'),
        reserve_analysis: document.getElementById('reserve_analysis'),
        comments: document.getElementById('comments'),
        expected_start_date: document.getElementById('expected_start_date'),
        expected_end_date: document.getElementById('expected_end_date'),
        total_expected_duration: document.getElementById('total_expected_duration'),
        actual_start_date: document.getElementById('actual_start_date'),
        actual_end_date: document.getElementById('actual_end_date'),
        total_actual_duration: document.getElementById('total_actual_duration'),
        completion: document.getElementById('completion'),
        dependency: document.getElementById('dependency'),
        parent_task_id: document.getElementById('parent_task'),
        owners: document.querySelectorAll('[name="owners"]')
    };

    const defaultFormValues = {
        hierarchy: 1,
        optimistic_duration: 0,
        expected_duration: 0,
        pessimistic_duration: 0,
        reserve_analysis: 0,
        total_expected_duration: 0,
        total_actual_duration: 0,
        completion: 0,
        dependency: 0,
        parent_task_id: 0,

    };

    addTaskForm.action = window.location.href; // update form action to include current active_tab

    // Add active_tab arg when submitting forms and for refreshing pages
    tabEls.forEach(el => {
        el.addEventListener('click', function(event) {
            const redirectUrl = `${addTaskForm.action.split('?')[0]}?active_tab=${event.target.id}`;
            addTaskForm.action = redirectUrl;
            history.pushState(null, '', redirectUrl);
        });
    });

    // Reopen the modal automatically if form validation fails
    if (!validForm) {
        editTaskModal.show();
    }

    // Debounce utility function to limit input events
    function debounce(fn, delay = 300) {
        let timeout;
        return function(...args) {
            clearTimeout(timeout);
            timeout = setTimeout(() => fn.apply(this, args), delay);
        };
    }

    // Get valid project working days (Monday to Friday)
    function getValidDays() {
        const dayMapping = {
            'sunday': 0,
            'monday': 1,
            'tuesday': 2,
            'wednesday': 3,
            'thursday': 4,
            'friday': 5,
            'saturday': 6
        };
  
        return Object.keys(workDays)
            .filter(day => workDays[day] > 0)
            .map(day => dayMapping[day]);
    }

    // // Helper function to check if a given day is a working day
    // function isWorkingDay(dayOfWeek) {
    //     const validDays = getValidDays();
    //     return validDays.includes(dayOfWeek);
    // }

    // Helper function to get work hours for a specific day of the week
    function getWorkHoursForDay(dayOfWeek) {
        const dayMapping = {
            0: 'sunday',
            1: 'monday',
            2: 'tuesday',
            3: 'wednesday',
            4: 'thursday',
            5: 'friday',
            6: 'saturday'
        };

        return workDays[dayMapping[dayOfWeek]] || 0;
    }


    // Calculate estimated end date
    function calculateEndDate() {
        const optimistic = parseInt(formElements.optimistic_duration.value) || 0;
        const expected = parseInt(formElements.expected_duration.value) || 0;
        const pessimistic = parseInt(formElements.pessimistic_duration.value) || 0;
        const reserve = parseInt(formElements.reserve_analysis.value) || 0;

        const averageDuration = (optimistic + 4 * expected + pessimistic) / 6;
        const totalExpectedDuration = averageDuration + reserve;

        let startDate = formElements.actual_start_date.value || formElements.expected_start_date.value;
        if (startDate) {
            startDate = new Date(startDate);
            let hrsToAdd = totalExpectedDuration
            let endDate = new Date(startDate);

            // Loop to add only working days
            while (hrsToAdd > 0) {
                const dayOfWeek = endDate.getUTCDay();
                hrsToAdd -= getWorkHoursForDay(dayOfWeek)
                if (hrsToAdd > 0){
                    endDate.setDate(endDate.getDate() + 1);
                }
                                
                // if (isWorkingDay(dayOfWeek)) {
                //     daysToAdd--;
                // }
            }

            formElements.expected_end_date.value = endDate.toISOString().split('T')[0];
            formElements.total_expected_duration.value = parseFloat(totalExpectedDuration).toFixed(2);
        }
    }

    // Add event listeners with debounce for recalculating end date
    ['input', 'change'].forEach(event => {
        formElements.optimistic_duration.addEventListener(event, debounce(calculateEndDate));
        formElements.expected_duration.addEventListener(event, debounce(calculateEndDate));
        formElements.pessimistic_duration.addEventListener(event, debounce(calculateEndDate));
        formElements.reserve_analysis.addEventListener(event, debounce(calculateEndDate));
        formElements.actual_start_date.addEventListener(event, debounce(calculateEndDate));
        formElements.expected_start_date.addEventListener(event, debounce(calculateEndDate));
    });

    // Validation function for working days
    function validateWorkingDay(dateInput, errorDivId) {
        const errorDiv = document.getElementById(errorDivId);
        
        // If the date input is empty, clear the error message and return
        if (!dateInput.value) {
            errorDiv.classList.add('d-none');
            return;
        }

        const selectedDate = new Date(dateInput.value);
        const dayOfWeek = selectedDate.getUTCDay();
        const validDays = getValidDays();

        if (!validDays.includes(dayOfWeek)) {
            errorDiv.classList.remove('d-none');
            dateInput.value = '';
            formElements.expected_end_date.value = '';
        } else {
            errorDiv.classList.add('d-none');
            calculateEndDate();
        }
    }

    // Add validation listeners for start dates
    formElements.expected_start_date.addEventListener('input', () => {
        validateWorkingDay(formElements.expected_start_date, 'invalid-expected-start-date-picked');
    });

    formElements.actual_start_date.addEventListener('input', () => {
        validateWorkingDay(formElements.actual_start_date, 'invalid-actual-start-date-picked');
    });

    // Function to validate and update task completion
    function updateCompletion() {
        const actualStartDate = formElements.actual_start_date.value;
        const actualEndDate = formElements.actual_end_date.value;
        const completionField = formElements.completion;

        if (actualEndDate) {
            completionField.value = 100; // Task is completed
        } else if (actualStartDate) {
            if (completionField.value == 0) {
                completionField.value = 1; // Ensure minimum completion of 1% if started
            }
        } else if (!actualStartDate) {
            completionField.value = 0; // Return value to 0 if no actualStartDate
        }
    }

    // Add event listeners to update completion based on start/end dates
    formElements.actual_start_date.addEventListener('change', updateCompletion);
    formElements.actual_end_date.addEventListener('change', updateCompletion);

    // Function to get child tasks count for the selected parent task
    function getParentTask(parentTaskId) {
        const parentTask = allTasks.find(task => task._id === parentTaskId);
        return parentTask;
    }

    // Function to update hierarchy based on child tasks
    function updateHierarchy() {
        const parentTaskId = formElements.parent_task_id.value;

        if (parentTaskId) {
            const childCount = getParentTask(parentTaskId).children.length;
            formElements.hierarchy.value = childCount + 1;
        } else {
            formElements.hierarchy.value = 1; // Default hierarchy if no parent task
        }
    }

    // Function to update task number based on parent task and hierarchy
    function updateTaskNumber() {
        const parentTaskId = formElements.parent_task_id.value;
        const parentTaskNumber = getParentTask(parentTaskId).task_number
        const hierarchy = formElements.hierarchy.value;

        if (parentTaskNumber && hierarchy) {
            formElements.task_number.value = `${parentTaskNumber}.${hierarchy}`;
        } else if (hierarchy) {
            formElements.task_number.value = hierarchy;
        }
    }

    // Event listener to update hierarchy and task number when parent task or hierarchy changes
    formElements.parent_task_id.addEventListener('change', () => {
        updateHierarchy();
        updateTaskNumber();
    });

    formElements.hierarchy.addEventListener('change', updateTaskNumber);
       

    // Render Kanban board
    function renderKanbanBoard() {
        allTasks.forEach((task, index) => {
            if (task.children.length === 0) {
                const columnId = getTaskColumnId(task);
                if (columnId) {
                    addTaskToColumn(index, task, columnId);
                }
            }
        });
    }

    // Get the appropriate column ID based on task status
    function getTaskColumnId(task) {
        if (task.completion === 100) {
            return 'kb-completed';
        }
        if (task.completion > 0 && task.completion < 100) {
            return 'kb-in-progress';
        }
        if (!task.actual_end_date && new Date() > new Date(task.expected_start_date)) {
            return 'kb-delayed';
        }
        if (task.completion === 0 && !task.actual_start_date) {
            return 'kb-to-do';
        }
        return 'kb-on-hold';
    }

    // Add a task to a Kanban column
    function addTaskToColumn(index, task, columnId) {
        const taskDiv = document.createElement('div');
        taskDiv.className = 'kanban-task';

        const taskContainer = document.createElement('div');
        taskContainer.className = 'task-container';

        const taskTitle = document.createElement('strong');
        taskTitle.textContent = task.title;

        const editButton = createButton(`kbEditBtn-${index}-${task._id}`, 'Edit Task', 'btn-info editTaskBtn', 'bi-pencil-square');
        const deleteButton = createButton(`kbDeleteBtn-${index}-${task._id}`, 'Delete Task', 'btn-danger deleteTaskBtn', 'bi-trash');

        const buttonContainer = document.createElement('div');
        buttonContainer.className = 'button-container';
        buttonContainer.append(editButton, deleteButton);

        taskContainer.append(taskTitle, buttonContainer);
        taskDiv.append(taskContainer);
        document.getElementById(columnId).append(taskDiv);
    }

    // Create a button for task actions
    function createButton(id, title, btnClass, iconClass) {
        const button = document.createElement('button');
        button.id = id;
        button.className = `btn btn-sm ${btnClass}`;
        button.title = title;
        button.type = 'button';
        button.innerHTML = `<i class='bi ${iconClass}'></i>`;
        return button;
    }

    // Initialize the Kanban board
    renderKanbanBoard();

    // Handle task edit button click
    document.querySelectorAll('.editTaskBtn').forEach(button => {
        button.addEventListener('click', function() {
            const taskId = this.id.split('-')[2];
            const task = allTasks.find(t => t._id === taskId);
            editTaskModalTitle.textContent = `Edit Task: ${task.title}`;
            populateEditFormWithTaskData(task);
            editTaskModal.show();
        });
    });

    // Populate edit form fields with task data
    function populateEditFormWithTaskData(task) {
        for (const key in formElements) {
            if (task[key] !== undefined) {
                if (key.endsWith('date')) {
                    formElements[key].value = task[key] ? new Date(task[key]).toISOString().split('T')[0] : '';
                } else if (key === 'owners') {
                    Array.from(formElements.owners).forEach(checkbox => {
                        checkbox.checked = task.owners.includes(checkbox.value);
                    });
                } else {
                    formElements[key].value = task[key];
                }
            }
        }
    }


    // Handle task delete button click
    document.querySelectorAll('.deleteTaskBtn').forEach(button => {
        button.addEventListener('click', function() {
            const taskId = this.id.split('-')[2];
            const task = allTasks.find(t => t._id === taskId);
            populateDeleteFormWithTaskData(task);
            deleteTaskModal.show();
        });
    });


    function populateDeleteFormWithTaskData(task) {
        const deleteTaskModalElement = document.getElementById('deleteTaskModal');
        const projectId = deleteTaskModalElement.getAttribute('data-project-id');
        const taskId = task._id;
        const taskTitle = task.title;
        const deleteTaskTitleSpan = document.getElementById('deleteTaskTitle');
        const deleteTaskModalTitle = document.getElementById('deleteTaskModalLabel');
        deleteTaskModalTitle.textContent = `Delete Task: ${taskTitle}`;
        // Set form action URL dynamically
        deleteTaskForm.action = `${location.protocol}//${location.host}/project/${projectId}/tasks/${taskId}/delete`;

        // Update modal content
        deleteTaskTitleSpan.textContent = taskTitle;
    }


    // closing modals
    // document.querySelectorAll('[data-bs-dismiss="modal"]').forEach(button => {
    //     button.addEventListener('click', function() {
    //     editTaskModal.hide();
    //     });
    // });

    // return to default values
    document.getElementById('newTaskBtn').addEventListener('click', () => {
        editTaskModalTitle.textContent = 'Add Task';
        Object.keys(formElements).forEach(el => {
            defaultFormValues.hasOwnProperty(el) ?  formElements[el].value = defaultFormValues[el] : formElements[el].value = "";
        });
    });


    async function loadProjectLogs(projectId) {
        const logsList = document.getElementById('logsList');
        try {
            const response = await fetch(`/projects/${projectId}/logs`);
            const logs = await response.json();

            logsList.innerHTML = ''; // Clear existing logs

            logs.forEach(log => {
                const listItem = document.createElement('li');
                listItem.className = 'list-group-item';

                // Determine the badge color based on log type
                let badgeClass = '';
                switch (log.action) {
                    case 'Project':
                        badgeClass = 'badge bg-primary';
                        break;
                    case 'Task':
                        badgeClass = 'badge bg-warning text-dark';
                        break;
                    case 'Member':
                        badgeClass = 'badge bg-success';
                        break;
                    default:
                        badgeClass = 'badge bg-secondary';
                }

                // Format log message
                listItem.innerHTML = `
                    <div class="d-flex justify-content-between align-items-start">
                        <strong>${log.details}</strong>
                        <span class="${badgeClass}">${log.action}</span>
                    </div>
                    <small class="d-block text-muted">
                        <span class="text-start">${log.user_name}</span>
                        <span class="float-end">${new Date(log.timestamp).toLocaleString()}</span>
                    </small>
                `;

                logsList.appendChild(listItem);
            });
        } catch (error) {
            logsList.innerHTML = `<li class="list-group-item text-danger">Failed to load logs.</li>`;
        }
    }
    
    // Trigger log loading when modal is shown
    let logsModal = document.getElementById('logsModal');
    logsModal.addEventListener('show.bs.modal', function () {
        const projectId = this.getAttribute('data-project-id');
        loadProjectLogs(projectId);
    });
});