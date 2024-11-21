document.addEventListener('DOMContentLoaded', function() {
    let nodesArr = [
            {
                id: '0',
                name: projectTitle,
                title: '',
            }
        ];
    let dataArr = [];
    let ganttDataArr = [];

    
    for(var i=0; i<allTasks.length; i++){
        //   nodesArr - for WBS nodes
        nodesArr.push(
            {
                id: allTasks[i]['_id'],
                name: allTasks[i]['task_number'] + ' ' + allTasks[i]['title'],
                // title: allTasks[i]['task_number'] + ': ' + allTasks[i]['title'],
                layout: 'hanging'
            }
        );

        dataArr.push([allTasks[i]['parent_task_id'], allTasks[i]['_id']]);

        // ganttArr - for gantt data
        if (allTasks[i]['children'].length === 0){
            if (allTasks[i]['parent_task_id'] !== "0"){
                if (allTasks[i]['actual_start_date'] !== ''){
                    console.log(1 + ' ' + allTasks[i]['title'])
                    ganttDataArr.push(
                        {
                            id: allTasks[i]['_id'],
                            name: allTasks[i]['title'],
                            label: allTasks[i]['title'],
                            parent: allTasks[i]['parent_task_id'],
                            dependency: allTasks[i]['dependency'],
                            start: Date.parse(allTasks[i]['actual_start_date']),
                            end: Date.parse(allTasks[i]['actual_end_date']) || Date.parse(allTasks[i]['expected_end_date']),
                            completed: {
                                amount: allTasks[i]['completion'] / 100,
                            },
                            owner: allTasks[i]['owners'],
                            owner_pics: allTasks[i]['owner_pics'].map(pic => 
                                `<div style="width: 20px; height: 20px; overflow: hidden; border-radius: 50%; display: inline-block; margin-left: -10px;">
                                    <img src="${pic}" style="width: 30px; margin-left: -5px; margin-top: -2px;">
                                </div>`
                            ).join(''),
                            optimistic_duration: allTasks[i]['optimistic_duration'],
                            expected_duration: allTasks[i]['expected_duration'],
                            pessimistic_duration: allTasks[i]['pessimistic_duration'],
                            y: i,
                        }
                    );
                }
                else {
                    console.log(2 + ' ' + allTasks[i]['title'])
                    ganttDataArr.push(
                        {
                            id: allTasks[i]['_id'],
                            name: allTasks[i]['title'],
                            label: allTasks[i]['title'],
                            parent: allTasks[i]['parent_task_id'],
                            dependency: allTasks[i]['dependency'],
                            start: Date.parse(allTasks[i]['expected_start_date']),
                            end: Date.parse(allTasks[i]['expected_end_date']),
                            owner: allTasks[i]['owners'],
                            owner_pics: allTasks[i]['owner_pics'].map(pic => 
                                `<div style="width: 20px; height: 20px; overflow: hidden; border-radius: 50%; display: inline-block; margin-left: -10px;">
                                    <img src="${pic}" style="width: 30px; margin-left: -5px; margin-top: -2px;">
                                </div>`
                            ).join(''),
                            optimistic_duration: allTasks[i]['optimistic_duration'],
                            expected_duration: allTasks[i]['expected_duration'],
                            pessimistic_duration: allTasks[i]['pessimistic_duration'],
                            y: i,
                        }
                    );
                }
            } else {
                if (allTasks[i]['actual_start_date'] !== ''){
                    console.log(3 + ' ' + allTasks[i]['title'])
                    ganttDataArr.push(
                        {
                            id: allTasks[i]['_id'],
                            name: allTasks[i]['title'],
                            label: allTasks[i]['title'],
                            // parent: allTasks[i]['parent_task_id'],
                            start: Date.parse(allTasks[i]['actual_start_date']),
                            end: Date.parse(allTasks[i]['actual_end_date']) || Date.parse(allTasks[i]['expected_end_date']),
                            completed: {
                                amount: allTasks[i]['completion'] / 100,
                            },
                            owner: allTasks[i]['owners'],
                            owner_pics: allTasks[i]['owner_pics'].map(pic => 
                                `<div style="width: 20px; height: 20px; overflow: hidden; border-radius: 50%; display: inline-block; margin-left: -10px;">
                                    <img src="${pic}" style="width: 30px; margin-left: -5px; margin-top: -2px;">
                                </div>`
                            ).join(''),
                            optimistic_duration: allTasks[i]['optimistic_duration'],
                            expected_duration: allTasks[i]['expected_duration'],
                            pessimistic_duration: allTasks[i]['pessimistic_duration'],
                            y: i
                        }
                    );
                }
                else {
                    console.log(4 + ' ' + allTasks[i]['title'])
                    ganttDataArr.push(
                        {
                            id: allTasks[i]['_id'],
                            name: allTasks[i]['title'],
                            label: allTasks[i]['title'],
                            // parent: allTasks[i]['parent_task_id'],
                            start: Date.parse(allTasks[i]['expected_start_date']),
                            end: Date.parse(allTasks[i]['expected_end_date']),
                            owner: allTasks[i]['owners'],
                            owner_pics: allTasks[i]['owner_pics'].map(pic => 
                                `<div style="width: 20px; height: 20px; overflow: hidden; border-radius: 50%; display: inline-block; margin-left: -10px;">
                                    <img src="${pic}" style="width: 30px; margin-left: -5px; margin-top: -2px;">
                                </div>`
                            ).join(''),
                            optimistic_duration: allTasks[i]['optimistic_duration'],
                            expected_duration: allTasks[i]['expected_duration'],
                            pessimistic_duration: allTasks[i]['pessimistic_duration'],
                            y: i
                        }
                    );
                }   
            }
            
        } else {
            ganttDataArr.push(
                {
                    id: allTasks[i]['_id'],
                    name: allTasks[i]['title'],
                    label: '',
                    // parent: allTasks[i]['parent_task_id'],
                    // start: null,
                    // end: null,
                    // owner: allTasks[i]['owners'],
                    pointWidth: 3,
                    optimistic_duration: allTasks[i]['optimistic_duration'],
                    expected_duration: allTasks[i]['expected_duration'],
                    pessimistic_duration: allTasks[i]['pessimistic_duration'],
                    y: i
                }
            );
        }
    }

    const colors = Highcharts.getOptions().colors;
    console.log('gant arr')
    console.log(ganttDataArr)
    // WBS chart --------------------------------------------------------
    Highcharts.chart('wbs-container', {
        chart: {
            // height: 800,
            inverted: true
        },

        title: {
            text: projectTitle + ' Work Breakdown Structure',
        },

        accessibility: {
            point: {
                descriptionFormat: '{add index 1}. {toNode.name}' +
                    '{#if (ne toNode.name toNode.id)}, {toNode.id}{/if}, ' +
                    'reports to {fromNode.id}'
            }
        },

        series: [{
            type: 'organization',
            name: projectTitle,
            // height: 40,
            // width: 400,
            keys: ['from', 'to'],
            nodeWidth: 40,
            nodePadding: 20,
            hangingIndentTranslation: 'cumulative',
            hangingIndent: 20,
            data: dataArr,
            levels: [
                {
                    level: 0,
                    color: colors[0],
                    // dataLabels: {
                    //     color: 'white'
                    // },
                    // height: 25
                }, {
                    level: 1,
                    color: colors[1],
                    // height: 25
                }, {
                    level: 2,
                    color: colors[2]
                }, {
                    level: 3,
                    color: colors[3]
                }, {
                    level: 4,
                    color: colors[4]
                }
            ],
            nodes: nodesArr,
            colorByPoint: false,
            // color: '#007ad0',
            dataLabels: {
                color: 'white'
            },
            borderColor: 'white',
        }],
        tooltip: {
            outside: true
        },
        // exporting: {
        //     allowHTML: true,
        //     sourceWidth: 800,
        //     sourceHeight: 600
        // }

    });

    // GANTT chart -----------------------------------------------------------------------
    const day = 24 * 36e5,
        today = Math.floor(Date.now() / day) * day;

    const option1 = {
        chart: {
            // styledMode: true
            plotBackgroundColor: 'rgba(128,128,128,0.02)',
            plotBorderColor: 'rgba(128,128,128,0.1)',
            plotBorderWidth: 1
        },
        title: {
            text: projectTitle,
        },
        xAxis: [{
            currentDateIndicator: {
                color: '#2caffe',
                dashStyle: 'ShortDot',
                width: 5,
                label: {
                    format: 'Today'
                }
            },
            min: Date.parse(projectStartDate) - 7 * day || today - 60 * day,
            max: Date.parse(projectEndDate) + 7 * day || today + 60 * day,
            custom: {
                today,
                // weekendPlotBands: true
            }
        }],
        yAxis: {
            uniqueNames: true,
            type: 'category',
            grid: {
                enabled: true,
                borderColor: 'rgba(0,0,0,0.3)',
                borderWidth: 1,
                columns: [{
                    title: {
                        text: 'Task'
                    },
                    labels: {
                        format: '{point.name}'
                    }
                }, {
                    title: {
                        text: 'Action'
                    },
                    labels: {
                        format: "<div class='button-container'>" + 
                                "<button class='btn btn-info btn-sm editTaskBtn' title='Edit Task' id='ganttEditBtn-{point.y}-{point.id}' type='button'>" + 
                                "<i class='bi bi-pencil-square'></i>" +
                                "</button>" + 
                                "<button class='btn btn-danger btn-sm deleteTaskBtn' title='Delete Task' id='ganttDeleteBtn-{point.y}-{point.id}' type='button'>" + 
                                "<i class='bi bi-trash'></i>" + 
                                "</button>" + 
                                "</div>",
                        useHTML: true,
                    }
                }]
            },
        },
        navigator: {
            enabled: true,
            liveRedraw: true,
            stickToMax: false,
            handles: {
                // backgroundColor: '',
                borderColor: 'blue'
            },
            series: {
                type: 'gantt',
                pointPlacement: 0.5,
                pointPadding: 0.25,
                accessibility: {
                    enabled: false
                }
            },
            // yAxis: {
            //     min: 0,
            //     max: 3,
            //     reversed: true,
            //     categories: []
            // }
        },

        scrollbar: {
            enabled: true
        },
        rangeSelector: {
            enabled: true,
            selected: 5
        },
        accessibility: {
            keyboardNavigation: {
                seriesNavigation: {
                    mode: 'serialize'
                }
            },
            // point: {
            //     descriptionFormat: '{yCategory}. ' +
            //         '{#if point.completed}Task {completed.amount} % ' +
            //         'completed. {/if}' +
            //         'Start {x:%Y-%m-%d}, end {x2:%Y-%m-%d}.'
            // },
            // series: {
            //     descriptionFormat: '{name}'
            // },
        },
        series: [{
            name: projectTitle,
            data: ganttDataArr,
            dataLabels: [{
                enabled: true,
                format: '<div style="width: 20px; height: 20px; overflow: ' +
                    'hidden; border-radius: 50%; margin-left: -5px">' +
                    '<img src="https://www.gravatar.com/avatar/{point.id}" ' +
                    'style="width: 30px; margin-left: -5px; margin-top: -2px">' +
                    '</div>',
                useHTML: true,
                // align: 'left'
            }]
        }],
        tooltip: {
            pointFormat: '<div style="z-index:100"></div><span style="font-weight: bold">{point.name}</span><br>' +
                '{point.start:%e %b} → {point.end:%e %b} <br>' +
                'Completed: {#if point.completed.amount > 0}{(multiply point.completed.amount 100):.0f}{/if} %<br>' +
                'Owner: {#if point.owner}{point.owner}{else} - {/if}</div>'
        },
        
    }

    const ganttOptions = { 
        chart: {
            plotBackgroundColor: 'rgba(128,128,128,0.02)',
            plotBorderColor: 'rgba(128,128,128,0.1)',
            plotBorderWidth: 1
        },
        plotOptions: {
            series: {
                borderRadius: '50%',
                connectors: {
                    dashStyle: 'ShortDot',
                    lineWidth: 2,
                    radius: 5,
                    startMarker: {
                        enabled: false
                    }
                },
                groupPadding: 0,
                dataLabels: [{
                    enabled: true,
                    align: 'left',
                    format: '{point.owner_pics}',
                    useHTML: true,
                    padding: 10,
                    style: {
                        fontWeight: 'normal',
                        textOutline: 'none'
                    }
                }, {
                    enabled: true,
                    align: 'right',
                    format: '{#if point.completed}{(multiply ' +
                        'point.completed.amount 100):.0f}%{/if}',
                    padding: 10,
                    style: {
                        fontWeight: 'normal',
                        textOutline: 'none',
                        opacity: 0.6
                    }
                }]
            }
        },

        series: 
        [{
            name: projectTitle,
            data: ganttDataArr,
        }],
        tooltip: {
            pointFormat: '<span style="font-weight: bold">{point.name}</span><br>' +
                '{point.start:%e %b} → {point.end:%e %b}' +
                '<br>' +
                '{#if point.completed}' +
                'Completed: {multiply point.completed.amount 100}%<br>' +
                '{/if}' +
                'Owner: {#if point.owner}{point.owner}{/if}'
        },
        title: {
            text: projectTitle + ' Gantt Chart'
        },
        xAxis: [{
            currentDateIndicator: {
                color: '#2caffe',
                dashStyle: 'ShortDot',
                width: 2,
                label: {
                    format: 'Today'
                }
            },
            dateTimeLabelFormats: {
                day: '%e<br><span style="opacity: 0.5; font-size: 0.7em">%a</span>'
            },
            grid: {
                borderWidth: 0
            },
            gridLineWidth: 1,
            min: Date.parse(projectStartDate) - 7 * day || today - 3 * day,
            max: Date.parse(projectEndDate) + 7 * day || today + 18 * day,
            custom: {
                today,
                weekendPlotBands: true
            },
        }],
        yAxis: {
            uniqueNames: true,
            // type: 'category',
            grid: {
                // enabled: true,
                borderColor: 'rgba(0,0,0,0.3)',
                // borderWidth: 1,
                columns: [{
                    title: {
                        text: 'Task'
                    },
                    // labels: {
                    //     format: '{point.name}'
                    // }
                }, {
                    title: {
                        text: 'Action'
                    },
                    labels: {
                        format: "<div class='button-container'>" + 
                                "<button class='btn btn-info btn-sm editTaskBtn' title='Edit Task' id='ganttEditBtn-{point.y}-{point.id}' type='button'>" + 
                                "<i class='bi bi-pencil-square'></i>" +
                                "</button>" + 
                                "<button class='btn btn-danger btn-sm deleteTaskBtn' title='Delete Task' id='ganttDeleteBtn-{point.y}-{point.id}' type='button'>" + 
                                "<i class='bi bi-trash'></i>" + 
                                "</button>" + 
                                "</div>",
                        useHTML: true,
                    }
                }, {title: {
                    text: 'Optimistic Duration'
                    },
                    labels: {
                        format: '{point.optimistic_duration}'
                    }
                }, {
                    title: {
                        text: 'Expected Duration'
                    },
                    labels: {
                        format: '{point.expected_duration}'
                    }
                }, {
                    title: {
                        text: 'Pessimistic Duration'
                    },
                    labels: {
                        format: '{point.pessimistic_duration}'
                    }
                }, {
                    title: {
                        text: 'Reserve Analysis'
                    },
                    labels: {
                        format: '{point.reserve_analysis}'
                    }
                }]
            },
            gridLineWidth: 1,
            labels: {
                symbol: {
                    width: 8,
                    height: 6,
                    x: -4,
                    y: -2
                }
            },
            staticScale: 40
        },
        accessibility: {
            keyboardNavigation: {
                seriesNavigation: {
                    mode: 'serialize'
                }
            },
            // point: {
            //     descriptionFormatter: function (point) {
            //         const completedValue = point.completed ?
            //                 point.completed.amount || point.completed : null,
            //             completed = completedValue ?
            //                 ' Task ' + Math.round(completedValue * 1000) / 10 +
            //                     '% completed.' :
            //                 '',
            //             dependency = point.dependency &&
            //                 point.series.chart.get(point.dependency).name,
            //             dependsOn = dependency ?
            //                 ' Depends on ' + dependency + '.' : '';

            //         return Highcharts.format(
            //             point.milestone ?
            //                 '{point.yCategory}. Milestone at {point.x:%Y-%m-%d}. ' +
            //                 'Owner: {point.owner}.{dependsOn}' :
            //                 '{point.yCategory}.{completed} Start ' +
            //                 '{point.x:%Y-%m-%d}, end {point.x2:%Y-%m-%d}. Owner: ' +
            //                 '{point.owner}.{dependsOn}',
            //             { point, completed, dependsOn }
            //         );
            //     }
            // }
        },
        navigator: {
            enabled: true,
            liveRedraw: true,
            stickToMax: false,
            handles: {
                // backgroundColor: '',
                borderColor: 'blue'
            },
            series: {
                type: 'gantt',
                pointPlacement: 0.5,
                pointPadding: 0.25,
                accessibility: {
                    enabled: false
                }
            },
        },
        scrollbar: {
            enabled: true
        },
        rangeSelector: {
            enabled: true,
            selected: 0
        },
        lang: {
            accessibility: {
                axis: {
                    xAxisDescriptionPlural: 'The chart has a two-part X axis ' +
                        'showing time in both week numbers and days.'
                }
            }
        }
    };

    const ganttChart = Highcharts.ganttChart('gantt-container', ganttOptions);
    ganttChart.xAxis[0].setExtremes(
        today - 15 * day,
        today + 15 * day,
    );


    // Estimating worksheet datagrid (table) chart
    // Prepare the data once by looping through all_tasks just once
    // const ewOptions = {
    //     title: {
    //         text: `${projectTitle} Estimating Worksheet`
    //     },
    //     series: [{
    //         data: ganttDataArr,
    //     }],
    //     chart: {
    //         width: null,
    //         // plotBackgroundColor: '#ffccaa',
    //         // height: null
    //     },
    //     plotOptions: {
    //         series: [{
    //             data: ganttDataArr,
    //         }],
    //         borderColor: '#ffccaa'
    //         // area: {
    //         //     visible: true
    //         // }
    //     },
    //     // xAxis: {
    //     //     visible: false,
    //     //     width: 1,
    //     //     height: '20%',
    //     //     tickAmount: 1
    //     // },
    //     yAxis: {
    //         grid: {
    //             borderColor: 'rgba(128,128,128,0.2)',
    //             columns: [
    //                 {
    //                     title: {
    //                         text: 'Task'
    //                     },
    //                 }, {
    //                     title: {
    //                         text: 'Action'
    //                     },
    //                     labels: {
    //                         format: "<div class='button-container'>" + 
    //                                 "<button class='btn btn-info btn-sm editTaskBtn' title='Edit Task' id='ganttEditBtn-{point.y}-{point.id}' type='button'>" + 
    //                                 "<i class='bi bi-pencil-square'></i>" +
    //                                 "</button>" + 
    //                                 "<button class='btn btn-danger btn-sm deleteTaskBtn' title='Delete Task' id='ganttDeleteBtn-{point.y}-{point.id}' type='button'>" + 
    //                                 "<i class='bi bi-trash'></i>" + 
    //                                 "</button>" + 
    //                                 "</div>",
    //                         useHTML: true,
    //                     }
    //                 }, {
    //                     title: {
    //                         text: 'Optimistic Duration'
    //                     },
    //                     labels: {
    //                         format: '{point.optimistic_duration}'
    //                     }
    //                 }, {
    //                     title: {
    //                         text: 'Expected Duration'
    //                     },
    //                     labels: {
    //                         format: '{point.expected_duration}'
    //                     }
    //                 }, {
    //                     title: {
    //                         text: 'Pessimistic Duration'
    //                     },
    //                     labels: {
    //                         format: '{point.pessimistic_duration}'
    //                     }
    //                 }
    //             ]
    //         }
    //     }
    
    // };
    // Highcharts.ganttChart('ew-container', ewOptions);
});