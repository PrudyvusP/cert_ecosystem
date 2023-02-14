    var is_inbox = document.getElementById('is_inbox');
    var date_approved = document.getElementById('date_approved');
    var our_outbox_number = document.getElementById('our_outbox_number');

    var date_registered = document.getElementById("date_registered");
    var our_inbox_number = document.getElementById("our_inbox_number");
    var number_inbox_approved = document.getElementById("number_inbox_approved");
    var date_inbox_approved = document.getElementById("date_inbox_approved");

    is_inbox.disabled = true;

    if (is_inbox.checked == true) {
        date_approved.disabled = true;
        our_outbox_number.disabled = true;
    }
    else {
      date_registered.disabled = true;
      our_inbox_number.disabled = true;
      number_inbox_approved.disabled = true;
      date_inbox_approved.disabled = true;
    };