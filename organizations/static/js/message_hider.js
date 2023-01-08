var our_outbox_number = document.getElementById("our_outbox_number");
var date_approved = document.getElementById("date_approved");

var date_registered = document.getElementById("date_registered");
var our_inbox_number = document.getElementById("our_inbox_number");
var number_inbox_approved = document.getElementById("number_inbox_approved");
var date_inbox_approved = document.getElementById("date_inbox_approved");

function HideMsgType() {
  var outboxChoice = document.getElementById("outboxChoice");
  var inboxChoice = document.getElementById("inboxChoice");

  if (inboxChoice.checked) {
    our_outbox_number.disabled = true;
    date_approved.disabled = true;
    }
  else {
    our_outbox_number.disabled = false;
    date_approved.disabled = false;
    }

  if (outboxChoice.checked) {
    date_registered.disabled = true;
    our_inbox_number.disabled = true;
    date_inbox_approved.disabled = true;
    number_inbox_approved.disabled = true;
    }
  else {
    date_registered.disabled = false;
    our_inbox_number.disabled = false;
    date_inbox_approved.disabled = false;
    number_inbox_approved.disabled = false;
    }
  }
