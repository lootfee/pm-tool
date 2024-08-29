    let nodesArr = [
            {
                id: '0',
                name: projectTitle,
                title: '',
                layout: 'hanging'
            }
        ];
    let dataArr = [];
    let ganttDataArr = [];

    
    for(var i=0; i<allTasks.length; i++){
        //   nodesArr - for WBS nodes
        nodesArr.push(
            {
                id: allTasks[i]['_id'],
                name: allTasks[i]['task_number'],
                title: allTasks[i]['title'],
                layout: 'hanging'
            }
        );

        dataArr.push([allTasks[i]['parent_task_id'], allTasks[i]['_id']]);

        // ganttArr - for gantt data
        if (allTasks[i]['children'].length === 0){

            if (allTasks[i]['parent_task_id'] !== "0"){
                ganttDataArr.push(
                    {
                        id: allTasks[i]['_id'],
                        name: allTasks[i]['title'],
                        parent: allTasks[i]['parent_task_id'],
                        start: Date.parse(allTasks[i]['expected_start_date']),
                        end: Date.parse(allTasks[i]['expected_end_date']),
                        owner: allTasks[i]['owners'],
                        pointWidth: 3,
                        y: i
                    }
                );
    
                ganttDataArr.push(
                    {
                        id: allTasks[i]['_id'],
                        name: allTasks[i]['title'],
                        parent: allTasks[i]['parent_task_id'],
                        start: Date.parse(allTasks[i]['actual_start_date']) || 0,
                        end: Date.parse(allTasks[i]['actual_end_date']) || 0,
                        completed: {
                            amount: allTasks[i]['completion'],
                        },
                        owner: allTasks[i]['owners'],
                        y: i
                    }
                );
            } else {
                ganttDataArr.push(
                    {
                        id: allTasks[i]['_id'],
                        name: allTasks[i]['title'],
                        // parent: allTasks[i]['parent_task_id'],
                        start: Date.parse(allTasks[i]['expected_start_date']),
                        end: Date.parse(allTasks[i]['expected_end_date']),
                        owner: allTasks[i]['owners'],
                        y: i
                    }
                );
    
                ganttDataArr.push(
                    {
                        id: allTasks[i]['_id'],
                        name: allTasks[i]['title'],
                        // parent: allTasks[i]['parent_task_id'],
                        start: Date.parse(allTasks[i]['actual_start_date']) || 0,
                        end: Date.parse(allTasks[i]['actual_end_date']) || 0,
                        completed: {
                            amount: allTasks[i]['completion'],
                        },
                        owner: allTasks[i]['owners'],
                        y: i
                    }
                );
            }
            
        } else {
            ganttDataArr.push(
                {
                    id: allTasks[i]['_id'],
                    name: allTasks[i]['title'],
                    // parent: allTasks[i]['parent_task_id'],
                    // start: Date.parse(allTasks[i]['expected_start_date']),
                    // end: Date.parse(allTasks[i]['expected_end_date']),
                    owner: allTasks[i]['owners'],
                    // pointWidth: 3,
                    y: i
                    
                }
            );
        }
    }

console.log(nodesArr);
console.log(dataArr);
console.log(ganttDataArr);
  
// WBS chart --------------------------------------------------------
  Highcharts.chart('wbs-container', {
    chart: {
        height: 600,
        inverted: true
    },

    title: {
        text: projectTitle,
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
        name: 'Work Breakdown Structure',
        // height: 600,
        // width: 500,
        keys: ['from', 'to'],
        data: dataArr,
        levels: [{
            level: 0,
            color: '#093A3E',
            dataLabels: {
                color: 'white'
            },
            height: 25
        }, {
            level: 1,
            color: '#3AAFB9',
            height: 25
        }, {
            level: 2,
            color: '#64E9EE'
        }, {
            level: 3,
            color: '#97C8EB'
        }, {
            level: 4,
            color: '#001011'
        }],
        nodes: nodesArr,
        colorByPoint: false,
        color: '#007ad0',
        dataLabels: {
            color: 'white'
        },
        borderColor: 'white',
    }],
    tooltip: {
        outside: true
    },
    exporting: {
        allowHTML: true,
        sourceWidth: 800,
        sourceHeight: 600
    }

});

// GANTT chart -----------------------------------------------------------------------
const day = 24 * 36e5,
    today = Math.floor(Date.now() / day) * day;

const option1 = {

    title: {
        text: projectTitle,
    },

    yAxis: {
        uniqueNames: true
    },

    navigator: {
        enabled: true,
        liveRedraw: true,
        series: {
            type: 'gantt',
            pointPlacement: 0.5,
            pointPadding: 0.25,
            accessibility: {
                enabled: false
            }
        },
        yAxis: {
            min: 0,
            max: 3,
            reversed: true,
            categories: []
        }
    },

    scrollbar: {
        enabled: true
    },

    rangeSelector: {
        enabled: true,
        selected: 0
    },

    accessibility: {
        point: {
            descriptionFormat: '{yCategory}. ' +
                '{#if completed}Task {(multiply completed.amount 100):.1f}% ' +
                'completed. {/if}' +
                'Start {x:%Y-%m-%d}, end {x2:%Y-%m-%d}.'
        },
        series: {
            descriptionFormat: '{name}'
        }
    },

    lang: {
        accessibility: {
            axis: {
                xAxisDescriptionPlural: 'The chart has a two-part X axis ' +
                    'showing time in both week numbers and days.',
                yAxisDescriptionPlural: 'The chart has one Y axis showing ' +
                    'task categories.'
            }
        }
    },

    series: [{
        name: projectTitle,
        data: ganttDataArr,
    }],
    tooltip: {
        pointFormat: '<span style="font-weight: bold">{point.name}</span><br>' +
            '{point.start:%e %b}' +
            '{#unless point.milestone} → {point.end:%e %b}{/unless}' +
            '<br>' +
            '{#if point.completed} {#if point.completed.amount > 0 }' +
            'Completed: {point.completed.amount}%<br>' +
            '{/if}{/if}' +
            'Owner: {#if point.owner}{point.owner}{else} - {/if}'
    },
    xAxis: [{
        currentDateIndicator: {
            color: '#2caffe',
            dashStyle: 'ShortDot',
            width: 5,
            label: {
                format: ''
            }
        }
    }],
}

const option2 = { chart: {
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
                format: '{point.name}',
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
            '{point.start:%e %b}' +
            '{#unless point.milestone} → {point.end:%e %b}{/unless}' +
            '<br>' +
            '{#if point.completed}' +
            'Completed: {multiply point.completed.amount 100}%<br>' +
            '{/if}' +
            'Owner: {#if point.owner}{point.owner}{else}unassigned{/if}'
    },
    title: {
        text: projectTitle
    },
    xAxis: [{
        currentDateIndicator: {
            color: '#2caffe',
            dashStyle: 'ShortDot',
            width: 5,
            label: {
                format: ''
            }
        },
        dateTimeLabelFormats: {
            day: '%e<br><span style="opacity: 0.5; font-size: 0.7em">%a</span>'
        },
        grid: {
            borderWidth: 0
        },
        gridLineWidth: 1,
        min: today - 3 * day,
        max: today + 18 * day,
        custom: {
            today,
            weekendPlotBands: true
        }
    }],
    yAxis: {
        grid: {
            borderWidth: 0
        },
        gridLineWidth: 0,
        labels: {
            symbol: {
                width: 8,
                height: 6,
                x: -4,
                y: -2
            }
        },
        staticScale: 30
    },
    accessibility: {
        keyboardNavigation: {
            seriesNavigation: {
                mode: 'serialize'
            }
        },
        point: {
            descriptionFormatter: function (point) {
                const completedValue = point.completed ?
                        point.completed.amount || point.completed : null,
                    completed = completedValue ?
                        ' Task ' + Math.round(completedValue * 1000) / 10 +
                            '% completed.' :
                        '',
                    dependency = point.dependency &&
                        point.series.chart.get(point.dependency).name,
                    dependsOn = dependency ?
                        ' Depends on ' + dependency + '.' : '';

                return Highcharts.format(
                    point.milestone ?
                        '{point.yCategory}. Milestone at {point.x:%Y-%m-%d}. ' +
                        'Owner: {point.owner}.{dependsOn}' :
                        '{point.yCategory}.{completed} Start ' +
                        '{point.x:%Y-%m-%d}, end {point.x2:%Y-%m-%d}. Owner: ' +
                        '{point.owner}.{dependsOn}',
                    { point, completed, dependsOn }
                );
            }
        }
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
Highcharts.ganttChart('gantt-container', option1);
