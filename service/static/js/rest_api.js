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
        // Add suspended status update
        $("#customer_suspended").val(res.suspended ? 'true' : 'false');
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#customer_id").val(""); // Clear ID field as well
        $("#customer_first_name").val("");
        $("#customer_last_name").val("");
        $("#customer_email_address").val("");
        $("#customer_phone_number").val("");
        $("#customer_address").val("");
        // Reset suspended status to default (False)
        $("#customer_suspended").val("false");
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
        let suspended = $("#customer_suspended").val() === 'true'; // Get suspended status

        let data = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone_number": phone_number,
            "address": address,
            "suspended": suspended // Include suspended status
        };

        $("#flash_message").empty();
        
        let ajax = $.ajax({
            type: "POST",
            url: "/api/customers",
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
        let suspended = $("#customer_suspended").val() === 'true'; // Get suspended status

        let data = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone_number": phone_number,
            "address": address,
            "suspended": suspended // Include suspended status
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
                type: "PUT",
                url: `/api/customers/${customer_id}`,
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
            url: `/api/customers/${customer_id}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            update_form_data(res) // This now handles the suspended status
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
            url: `/api/customers/${customer_id}`,
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
        clear_form_data() // Use the updated clear_form_data
        $("#flash_message").empty();
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
        // Get suspended status from the main form for search
        let suspended = $("#customer_suspended").val(); // This will be 'true' or 'false' string

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
        // Add suspended status to query string if not "All" (empty string)
        if (suspended !== "") {
            if (queryString.length > 0) {
                queryString += '&suspended=' + encodeURIComponent(suspended)
            } else {
                queryString += 'suspended=' + encodeURIComponent(suspended)
            }
        }


        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/api/customers?${queryString}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            $("#search_results table tbody").empty(); // Clear only tbody
            // Ensure the table header is consistent with index.html
            let table = '<table class="table table-striped table-bordered">'
            table += '<thead class="table-dark"><tr>'
            table += '<th class="col-md-1">ID</th>'
            table += '<th class="col-md-2">First Name</th>'
            table += '<th class="col-md-2">Last Name</th>'
            table += '<th class="col-md-3">Email</th>'
            table += '<th class="col-md-2">Phone</th>'
            table += '<th class="col-md-2">Address</th>'
            table += '<th class="col-md-1">Suspended</th>' // Added Suspended column header
            table += '</tr></thead><tbody>'

            let firstCustomer = "";
            for(let i = 0; i < res.length; i++) {
                let customer = res[i];
                table +=  `<tr id="row_${i}">
                    <td>${customer.id}</td>
                    <td>${customer.first_name}</td>
                    <td>${customer.last_name}</td>
                    <td>${customer.email}</td>
                    <td>${customer.phone_number || ''}</td>
                    <td>${customer.address || ''}</td>
                    <td><span class="badge ${customer.suspended ? 'bg-warning' : 'bg-success'}">${customer.suspended ? 'Suspended' : 'Active'}</span></td>
                </tr>`;
                if (i == 0) {
                    firstCustomer = customer;
                }
            }
            table += '</tbody></table>';
            $("#search_results").html(table); // Use .html() to replace content including table structure

            // copy the first result to the form
            if (firstCustomer != "") {
                update_form_data(firstCustomer) // This will now set the suspended status in the form
            }

            flash_message("Customer found.")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    }

    // ****************************************
    // Suspend customer functionality (triggered by #suspend-btn or dynamically from table)
    // ****************************************
    function performSuspend(id) {
        $.ajax({
            type: "PUT",
            url: `/api/customers/${id}/suspend`,
            contentType: "application/json"
        }).done(function(res) {
            $("#flash_message").text("Customer suspended successfully");
            // Update the form's suspended dropdown and reload all customers
            $("#customer_suspended").val(res.suspended ? 'true' : 'false');
            loadAllCustomers();
        }).fail(function() {
            $("#flash_message").text("Failed to suspend customer");
        });
    }

    // ****************************************
    // Activate customer functionality (triggered by #activate-btn or dynamically from table)
    // ****************************************
    function performActivate(id) {
        $.ajax({
            type: "PUT",
            url: `/api/customers/${id}/activate`,
            contentType: "application/json"
        }).done(function(res) {
            $("#flash_message").text("Customer activated successfully");
            // Update the form's suspended dropdown and reload all customers
            $("#customer_suspended").val(res.suspended ? 'true' : 'false');
            loadAllCustomers();
        }).fail(function() {
            $("#flash_message").text("Failed to activate customer");
        });
    }

    // ****************************************
    // Event Handlers for Buttons
    // ****************************************

    // Wire up the main form's Suspend button
    $("#suspend-btn").click(function() {
        const id = $("#customer_id").val(); // Get ID from the main form's ID field
        if (!id) {
            flash_message("Please retrieve a Customer first to suspend.");
            return;
        }
        performSuspend(id);
    });

    // Wire up the main form's Activate button
    $("#activate-btn").click(function() {
        const id = $("#customer_id").val(); // Get ID from the main form's ID field
        if (!id) {
            flash_message("Please retrieve a Customer first to activate.");
            return;
        }
        performActivate(id);
    });

    // Manual Suspend/Activate buttons (if you still want them)
    // These are for the "Customer Management Actions" section
    $("#suspend-customer-btn-manual").click(function() {
        const id = $("#suspend_customer_id").val();
        if (!id) {
            flash_message("Please enter Customer ID to suspend");
            return;
        }
        performSuspend(id);
    });

    $("#activate-customer-btn-manual").click(function() {
        const id = $("#activate_customer_id").val();
        if (!id) {
            flash_message("Please enter Customer ID to activate");
            return;
        }
        performActivate(id);
    });

    // Refresh functionality
    $("#refresh-btn, #reload-table-btn").click(function() {
      loadAllCustomers();
      flash_message("Customer list refreshed");
    });

    // Count customers
    $("#count-customers-btn").click(function() {
      $.ajax({
        type: "GET",
        url: "/api/customers",
        contentType: "application/json"
      }).done(function(res) {
        flash_message("Total customers: " + res.length);
      });
    });

    // Export customers (simple version)
    $("#export-customers-btn").click(function() {
      flash_message("Export functionality would be implemented here");
    });

    // Helper function to load all customers into the live table
    function loadAllCustomers() {
      $.ajax({
        type: "GET",
        url: "/api/customers",
        contentType: "application/json"
      }).done(function(customers) {
        const tbody = $("#customer-table tbody");
        tbody.empty();
        
        customers.forEach(function(c) {
          const row = `<tr>
            <td>${c.id}</td>
            <td>${c.first_name}</td>
            <td>${c.last_name}</td>
            <td>${c.email}</td>
            <td>${c.phone_number || ''}</td>
            <td>${c.address || ''}</td>
            <td><span class="badge ${c.suspended ? 'bg-warning' : 'bg-success'}">${c.suspended ? 'Suspended' : 'Active'}</span></td>
            <td>
              <button class="btn btn-sm btn-warning suspend-btn" data-id="${c.id}">Suspend</button>
              <button class="btn btn-sm btn-success activate-btn" data-id="${c.id}">Activate</button>
              <button class="btn btn-sm btn-danger delete-btn" data-id="${c.id}">Delete</button>
            </td>
          </tr>`;
          tbody.append(row);
        });
      });
    }

    // Event delegation for dynamic buttons within the live table
    $(document).on('click', '.suspend-btn', function() {
      const id = $(this).data('id');
      // Populate the main form's ID field and trigger its suspend button
      $("#customer_id").val(id);
      $("#retrieve-btn").click(); // Retrieve to load data into form first
      setTimeout(() => { // Add a small delay to allow retrieve to complete
        $("#suspend-btn").click();
      }, 500);
    });

    $(document).on('click', '.activate-btn', function() {
      const id = $(this).data('id');
      // Populate the main form's ID field and trigger its activate button
      $("#customer_id").val(id);
      $("#retrieve-btn").click(); // Retrieve to load data into form first
      setTimeout(() => { // Add a small delay to allow retrieve to complete
        $("#activate-btn").click();
      }, 500);
    });

    $(document).on('click', '.delete-btn', function() {
      const id = $(this).data('id');
      if (confirm('Are you sure you want to delete this customer?')) {
        $.ajax({
          type: "DELETE",
          url: `/api/customers/${id}`,
          contentType: "application/json"
        }).done(function() {
          flash_message("Customer deleted successfully");
          loadAllCustomers();
        }).fail(function() {
          flash_message("Failed to delete customer");
        });
      }
    });

    // Load customers on page load
    loadAllCustomers();
});
