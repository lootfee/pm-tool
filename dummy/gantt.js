

class Cell {
    width = 20;
    height = 40;
    constructor(element){

    }
    
}

var line = document.getElementById('line');
var div1 = document.getElementsByClassName('chart-li-one').item(0);
var div2 = document.getElementsByClassName('chart-li-two').item(0);
console.log(div1.offsetLeft);
var x1 = div1.offsetLeft + div1.offsetWidth;//div1.offset.left + (div1.width()/2);
var y1 = div1.offsetTop + (div1.offsetHeight/2);//div1.offset.top + (div1.height()/2);
var x2 = div2.offsetLeft ;//div2.offset.left + (div2.width()/2);
var y2 = div2.offsetTop + (div2.offsetHeight/2);//div2.offset.top + (div2.height()/2);

//line.attr('x1',x1).attr('y1',y1).attr('x2',x2).attr('y2',y2);
line.setAttribute('x1',x1)
line.setAttribute('y1',y1)
line.setAttribute('x2',x2)
line.setAttribute('y2',y2);
/*
projectStart
projectEnd
classDays
classHours
alphaDate
betaDate

groupMembers

tasks 
    id 
    name 
    assignedTo 
    prerequisite
    parentTask
    optimisticDuration
    expectedDuration
    pessimisticDuration
    weightedDuration
    reservedHours
    finalEstimatedDuration
    planStart
    planDuration
    actualStart
    actualDuration
    percentCompleted
    comments
    inAlpha


    totalEstimate
    timeBudget
    slackTime


    calculatedHrsPerDay - hrs per day per member


*/