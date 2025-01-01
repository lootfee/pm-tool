document.addEventListener('DOMContentLoaded', function() {
    console.log(allTasks)
    // Cache DOM Elements
    const form = document.getElementById('addTaskForm');
    const modalTitle = document.getElementById('addTaskModalLabel');
    const editTaskModal = new bootstrap.Modal('#addTaskModal');
    const tabEls = document.querySelectorAll('button[data-bs-toggle="tab"]');
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

    form.action = window.location.href; // update form action to include current active_tab

    // Add active_tab arg when submitting forms and for refreshing pages
    tabEls.forEach(el => {
        el.addEventListener('click', function(event) {
            console.log(event.target.id)
            const redirectUrl = `${form.action.split('?')[0]}?active_tab=${event.target.id}`;
            form.action = redirectUrl;
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
        console.log(parentTask)
        return parentTask;
    }

    // Function to update hierarchy based on child tasks
    function updateHierarchy() {
        const parentTaskId = formElements.parent_task_id.value;

        if (parentTaskId) {
            const childCount = getParentTask(parentTaskId).children.length;
            console.log(childCount)
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
            modalTitle.textContent = `Edit Task: ${task.title}`;
            console.log(taskId)
            populateFormWithTaskData(task);
            editTaskModal.show();
        });
    });

    // Populate form fields with task data
    function populateFormWithTaskData(task) {
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

    // closing modals
    document.querySelectorAll('[data-bs-dismiss="modal"]').forEach(button => {
        button.addEventListener('click', function() {
        editTaskModal.hide();
        });
    });

    // Clear form data on modal close
    document.getElementById('addTaskModal').addEventListener('hidden.bs.modal', () => {
        modalTitle.textContent = 'Add Task';
        Object.values(formElements).forEach(el => el.value = '');
    });
});

// document.addEventListener('DOMContentLoaded', function() {
//     // to add active_tab args when submitting forms
//     // so i will reopen the same tab upon reload
//     var tabEl = document.querySelectorAll('button[data-bs-toggle="tab"]')
//     var form = document.getElementById('addTaskForm')
//     tabEl.forEach(el => {
//         el.addEventListener('click', function (event) {
//         var formUrl = form.action.split('?')[0]
//         var redirectUrl = formUrl + '?active_tab=' + event.target.id;
//         // form.action = redirectUrl;
//         history.pushState(null, '', redirectUrl);
//         // console.log(form.action)
//     })
//     });

//     // to reopen the modal automatically when there's error in form
//     var modal = new bootstrap.Modal(document.getElementById('addTaskModal'));
//     if (!validForm) {
//         modal.show();
//     }

//     // for calculatiing estimated end date
//     const optimisticDuration = document.getElementById('optimistic_duration');
//     const expectedDuration = document.getElementById('expected_duration');
//     const pessimisticDuration = document.getElementById('pessimistic_duration');
//     const reserveAnalysis = document.getElementById('reserve_analysis');
//     const expectedStartDate = document.getElementById('expected_start_date');
//     const expectedEndDate = document.getElementById('expected_end_date');
//     const actualStartDate = document.getElementById('actual_start_date');

//     function calculateEndDate() {
//         const expectedStartDate = new Date(expectedStartDate.value);
//         const actualStartDate = new Date(actualStartDate.value);
//         const optimistic = parseInt(optimisticDuration.value) || 0;
//         const expected = parseInt(expectedDuration.value) || 0;
//         const pessimistic = parseInt(pessimisticDuration.value) || 0;
//         const reserve = parseInt(reserveAnalysis.value) || 0;

//         // Calculate the average duration
//         const averageDuration = (optimistic + 4*expected + pessimistic) / 6;

//         // Calculate the total duration including reserve analysis
//         const totalDuration = averageDuration + reserve;

//         // Calculate the end date
//         let endDate = new Date(expectedStartDate);
//         endDate.setDate(expectedStartDate.getDate() + totalDuration);
//         if (actualStartDate){
//             endDate = new Date(actualStartDate);
//             endDate.setDate(startDate.getDate() + totalDuration);
//         }       

//         endDate.setDate(startDate.getDate() + totalDuration);

//         // Update the end date input field
//         expectedEndDate.value = endDate.toISOString().split('T')[0];
//     }

//     // Add event listeners to recalculate the end date when inputs change
//     optimisticDuration.addEventListener('input', calculateEndDate);
//     expectedDuration.addEventListener('input', calculateEndDate);
//     pessimisticDuration.addEventListener('input', calculateEndDate);
//     reserveAnalysis.addEventListener('input', calculateEndDate);

//     // for expected startdate - add validation for a valid project working day
//     expectedStartDate.addEventListener('input', function() {
//         const selectedDate = new Date(expectedStartDate.value);
//         const dayOfWeek = selectedDate.getUTCDay();
//         var errorDiv = document.getElementById('invalid-expected-start-date-picked');
//         // Set valid days of the week (0 = Sunday, 1 = Monday, ..., 6 = Saturday)
//         const validDays = getValidDays();

//         if (!validDays.includes(dayOfWeek)) {
//           errorDiv.classList.remove('d-none');
//           expectedStartDate.value = '';
//           expectedEndDate.value = '';
//       } else {
//           errorDiv.classList.add('d-none');
//           calculateEndDate();
//       }
//     });

//     // for actual startdate - add validation for a valid project working day
//     actualStartDate.addEventListener('input', function() {
//         const selectedDate = new Date(actualStartDate.value);
//         const dayOfWeek = selectedDate.getUTCDay();
//         var errorDiv = document.getElementById('invalid-actual-start-date-picked');
//         // Set valid days of the week (0 = Sunday, 1 = Monday, ..., 6 = Saturday)
//         const validDays = getValidDays();

//         if (!validDays.includes(dayOfWeek)) {
//           errorDiv.classList.remove('d-none');
//           actualStartDate.value = '';
//           expectedEndDate.value = '';
//       } else {
//           errorDiv.classList.add('d-none');
//           calculateEndDate();
//       }
//     });

//     function getValidDays() {
//       const dayMapping = {
//           'sunday': 0,
//           'monday': 1,
//           'tuesday': 2,
//           'wednesday': 3,
//           'thursday': 4,
//           'friday': 5,
//           'saturday': 6
//       };

//       return Object.keys(workDays)
//           .filter(day => workDays[day] > 0)
//           .map(day => dayMapping[day]);
//   }

//     console.log('all tasks')
//     console.log(allTasks)
//     // Elements and Modal Initialization
//     const modalTitle = document.getElementById('addTaskModalLabel');
//     const formElements = {
//         _id: document.getElementById('task_id'),
//         title: document.getElementById('title'),
//         task_number: document.getElementById('task_number'),
//         hierarchy: document.getElementById('hierarchy'),
//         optimistic_duration: document.getElementById('optimistic_duration'),
//         expected_duration: document.getElementById('expected_duration'),
//         pessimistic_duration: document.getElementById('pessimistic_duration'),
//         reserve_analysis: document.getElementById('reserve_analysis'),
//         comments: document.getElementById('comments'),
//         expected_start_date: document.getElementById('expected_start_date'),
//         expected_end_date: document.getElementById('expected_end_date'),
//         actual_start_date: document.getElementById('actual_start_date'),
//         actual_end_date: document.getElementById('actual_end_date'),
//         completion: document.getElementById('completion'),
//         dependency: document.getElementById('dependency'),
//         parent_task_id: document.getElementById('parent_task'),
//         owners: document.querySelectorAll('[name="owners"]')
//     };
//     const editTaskModal = new bootstrap.Modal(document.getElementById('addTaskModal'));

//     // Event Listener for Edit Task Buttons
//     document.querySelectorAll('.editTaskBtn').forEach(button => {
//         button.addEventListener('click', function() {
//             const taskData = this.id.split('-');
//             const task = allTasks[parseInt(taskData[1])]; // Get task data

//             modalTitle.textContent = `Edit Task: ${task.title}`; // Set modal title
            
//             // Populate form fields
//             for (const key in formElements) {
//                 if (task[key] !== undefined || task[key] !== '') {
//                     if (key.endsWith('date')){
//                         formElements[key].value = task[key] ? new Date(task[key]).toISOString().split('T')[0] : '';
//                     } else if (key === 'owners') {
//                         // Handle owners checkboxes
//                         Array.from(formElements.owners).forEach(checkbox => {
//                             checkbox.checked = task.owners.includes(checkbox.value); // Check if the task's owners include this checkbox's value
//                         });
//                     } else {
//                         formElements[key].value = task[key];
//                     }
                    
//                 }
//             }

//             editTaskModal.show(); // Show the modal
//         });
//     });

//     document.querySelectorAll('[data-bs-dismiss="modal"]').forEach(button => {
//         button.addEventListener('click', function() {
//         editTaskModal.hide();
//         });
//     });


//     // Clear Form Data on Modal Close
//     document.getElementById('addTaskModal').addEventListener('hidden.bs.modal', function () {
//         modalTitle.textContent = 'Add Task'; // Reset modal title
//         for (const key in formElements) {
//             formElements[key].value = ''; // Clear all input fields
//         }
//     });

//     // Function to validate and update completion based on actual start and end dates
//     function updateCompletion() {
//         let actualStartDate = formElements.actual_start_date.value;
//         const actualEndDate = formElements.actual_end_date.value;
//         const completionField = formElements.completion;

//         // If there is an actual end date, set completion to 100%
//         if (actualEndDate) {
//             completionField.value = 100;
//         } else if (actualStartDate) {
//             // If there is an actual start date, ensure completion is not 0
//             if (completionField.value == 0) {
//                 completionField.value = 1; // Set a minimum completion of 1
//             }
//         }
//     }

//     // Event listeners to trigger update on change
//     formElements.actual_start_date.addEventListener('change', updateCompletion);
//     formElements.actual_end_date.addEventListener('change', updateCompletion);


//     // render kanban board
//     function addTaskToColumn(index, task, columnId) {
//         const taskDiv = document.createElement('div');
//         taskDiv.className = 'kanban-task';

//         // Create a container for the task title and buttons
//         const taskContainer = document.createElement('div');
//         taskContainer.className = 'task-container';

//         // Create the task title element
//         const taskTitle = document.createElement('strong');
//         taskTitle.textContent = task.title;

//         // Create the edit button
//         const editButton = document.createElement('button');
//         editButton.className = 'btn btn-info btn-sm editTaskBtn';
//         editButton.title = 'Edit Task';
//         editButton.id = `kbEditBtn-${index}-${task._id}`;
//         editButton.type = 'button';
//         editButton.innerHTML = `<i class='bi bi-pencil-square'></i>`;

//         // Create the delete button
//         const deleteButton = document.createElement('button');
//         deleteButton.className = 'btn btn-danger btn-sm deleteTaskBtn';
//         deleteButton.title = 'Delete Task';
//         deleteButton.id = `kbDeleteBtn-${index}-${task._id}`;
//         deleteButton.type = 'button';
//         deleteButton.innerHTML = `<i class='bi bi-trash'></i>`;

//         // Create a container for the buttons
//         const buttonContainer = document.createElement('div');
//         buttonContainer.className = 'button-container';
//         buttonContainer.appendChild(editButton);
//         buttonContainer.appendChild(deleteButton);

//         // Append the task title and button container to the task container
//         taskContainer.appendChild(taskTitle);
//         taskContainer.appendChild(buttonContainer);

//         // Append the task container to the task div
//         taskDiv.appendChild(taskContainer);

//         // Append the task div to the column
//         document.getElementById(columnId).appendChild(taskDiv);
//     }

//     function renderKanbanBoard() {
//         allTasks.forEach((task, index) => {
//             if (task.children.length === 0) {
//                 if (task.completion === 100) {
//                     addTaskToColumn(index, task, 'kb-completed');
//                 } else if (task.actual_end_date === '' && new Date() > new Date(task.expected_start_date)) {
//                     addTaskToColumn(index, task, 'kb-delayed');
//                 } else if (task.completion > 0 && task.completion < 100) {
//                     addTaskToColumn(index, task, 'kb-in-progress');
//                 } else if (task.completion === 0 && task.actual_start_date === '') {
//                     addTaskToColumn(index, task, 'kb-to-do');
//                 } else {
//                     addTaskToColumn(index, task, 'kb-on-hold');
//                 }
//             }
//         });
//     }

//     renderKanbanBoard();
// }); 