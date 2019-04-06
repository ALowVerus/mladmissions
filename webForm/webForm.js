/*
	File: webForm.js
	Team: Will I Get In?
*/
$(document).ready(function(){
});
function validator() {
	var gpaVal = $( "#gpa" ).val();
	var actVal = $( "#act" ).val();
	var satVal = $( "#sat" ).val();
	if ( isNaN(gpaVal) || !between(gpaVal, 0.0, 4.0) ) {
		alert("Please provide a valid, unweighted GPA on a 4.0 scale.");
		return false;
	}
	if ( isNaN(actVal) || !between(actVal, 0, 36) ) {
		alert("Please provide a valid, composite ACT score out of 36.");
		return false;
	}
	if ( isNaN(satVal) || !between(satVal, 0, 1600) ) {
		alert("Please provide a valid, cumulative SAT score out of 1600.");
		return false;
	}
}
function between(x, min, max) {
	return x >= min && x <= max;
}