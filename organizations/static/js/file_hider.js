function ShowHideDiv() {
var chkYes = document.getElementById("chkYes");
var file = document.getElementById("file");
file.disabled = chkNo.checked ? "disabled" : true;
file.required = chkNo.checked ? "disabled": true;
file.disabled = chkYes.checked ? "disabled" : false;
}