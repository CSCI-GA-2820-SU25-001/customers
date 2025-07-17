$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#customer_id").val(res.id);
        $("#customer_first_name").val(res.first_name);
        $("#customer_last_name").val(res.last_name);
        $("#customer_email_address").val(res.email);
        $("#customer_phone_number").val(res.phone_number || "");
        $("#customer_address").val(res.address || "");
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#customer_first_name").val("");
        $("#customer_last_name").val("");
        $("#customer_email_address").val("");
        $("#customer_phone_number").val("");
        $("#customer_address").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Create a Customer
    // ****************************************

    $("#create-btn").click(function () {

        let first_name = $("#customer_first_name").val();
        let last_name = $("#customer_last_name").val();
        let email = $("#customer_email_address").val();
        let phone_number = $("#customer_phone_number").val();
        let address = $("#customer_address").val();

        let data = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone_number": phone_number,
            "address": address
        };

        $("#flash_message").empty();
        
        let ajax = $.ajax({
            type: "POST",
            url: "/customers",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Customer created successfully!")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Update a Customer
    // ****************************************

    $("#update-btn").click(function () {

        let customer_id = $("#customer_id").val();
        let first_name = $("#customer_first_name").val();
        let last_name = $("#customer_last_name").val();
        let email = $("#customer_email_address").val();
        let phone_number = $("#customer_phone_number").val();
        let address = $("#customer_address").val();

        let data = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone_number": phone_number,
            "address": address
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
                type: "PUT",
                url: `/customers/${customer_id}`,
                contentType: "application/json",
                data: JSON.stringify(data)
            })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Customer updated successfully!")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Retrieve a Customer
    // ****************************************

    $("#retrieve-btn").click(function () {

        let customer_id = $("#customer_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/customers/${customer_id}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            update_form_data(res)
            flash_message("Customer found.")
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Delete a Customer
    // ****************************************

    $("#delete-btn").click(function () {

        let customer_id = $("#customer_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `/customers/${customer_id}`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("Customer deleted.")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#customer_id").val("");
        $("#flash_message").empty();
        clear_form_data()
    });

    // ****************************************
    // Search for a Customer
    // ****************************************

    // Modified search button click handler with increased delay
    $("#search-btn").click(function () {
        // Increased delay to give the UI more time to render after updates
        setTimeout(function() {
            performSearch();
        }, 2000); // Increased to 2000ms (2 seconds) delay
    });

    // Extract search logic into separate function
    function performSearch() {
        let first_name = $("#customer_first_name").val();
        let last_name = $("#customer_last_name").val();
        let email = $("#customer_email_address").val();
        let phone_number = $("#customer_phone_number").val();

        let queryString = ""

        if (first_name) {
            queryString += 'first_name=' + encodeURIComponent(first_name)
        }
        if (last_name) {
            if (queryString.length > 0) {
                queryString += '&last_name=' + encodeURIComponent(last_name)
            } else {
                queryString += 'last_name=' + encodeURIComponent(last_name)
            }
        }
        if (email) {
            if (queryString.length > 0) {
                queryString += '&email=' + encodeURIComponent(email)
            } else {
                queryString += 'email=' + encodeURIComponent(email)
            }
        }
        if (phone_number) {
            if (queryString.length > 0) {
                queryString += '&phone_number=' + encodeURIComponent(phone_number)
            } else {
                queryString += 'phone_number=' + encodeURIComponent(phone_number)
            }
        }

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/customers?${queryString}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            $("#search_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-1">ID</th>'
            table += '<th class="col-md-2">First Name</th>'
            table += '<th class="col-md-2">Last Name</th>'
            table += '<th class="col-md-3">Email</th>'
            table += '<th class="col-md-2">Phone</th>'
            table += '<th class="col-md-2">Address</th>'
            table += '</tr></thead><tbody>'
            let firstCustomer = "";
            for(let i = 0; i < res.length; i++) {
                let customer = res[i];
                table +=  `<tr id="row_${i}"><td>${customer.id}</td><td>${customer.first_name}</td><td>${customer.last_name}</td><td>${customer.email}</td><td>${customer.phone_number || ''}</td><td>${customer.address || ''}</td></tr>`;
                if (i == 0) {
                    firstCustomer = customer;
                }
            }
            table += '</tbody></table>';
            $("#search_results").append(table);

            // copy the first result to the form
            if (firstCustomer != "") {
                update_form_data(firstCustomer)
            }

            flash_message("Customer found.")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    }

})