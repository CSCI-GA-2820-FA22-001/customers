$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#id").val(res.id);
        $("#address_name").val(res.addresses[0].name);
        $("#address_street").val(res.addresses[0].street);
        $("#address_city").val(res.addresses[0].city);
        $("#address_state").val(res.addresses[0].state);
        $("#address_postalcode").val(res.addresses[0].postalcode);
        $("#first_name").val(res.first_name);
        $("#last_name").val(res.last_name);
        if (res.active == true) {
            $("#active").val("true");
        } else {
            $("#active").val("false");
        }
    }
  

    /// Clears all form fields
    function clear_form_data() {
        $("#id").val("");
        $("#address_name").val("");
        $("#address_street").val("");
        $("#address_city").val("");
        $("#address_state").val("");
        $("#address_postalcode").val("");
        $("#first_name").val("");
        $("#last_name").val("");
        $("#active").val("");
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

        let name = $("#address_name").val();
        let street = $("#address_street").val();
        let city = $("#address_city").val();
        let state = $("#address_state").val();
        let postalcode = $("#address_postalcode").val();
        let first_name = $("#first_name").val();
        let last_name = $("#last_name").val();
        let active = $("#active").val() == "true";
        json_address = {
            "name": name,
	        "street": street,
	        "city": city,
	        "state": state,
	        "postalcode" : postalcode
        };
        let data = {
            "first_name": first_name,
            "last_name": last_name,
            "active": active,
            "addresses": [json_address]
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
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Update a Customer
    // ****************************************

    $("#update-btn").click(function () {

        let name = $("#address_name").val();
        let id = $("#id").val();
        let street = $("#address_street").val();
        let city = $("#address_city").val();
        let state = $("#address_state").val();
        let postalcode = $("#address_postalcode").val();
        let first_name = $("#first_name").val();
        let last_name = $("#last_name").val();
        let active = $("#active").val() == "true";
        json_address = {
            "name": name,
	        "street": street,
	        "city": city,
	        "state": state,
	        "postalcode" : postalcode
        };
        let data = {
            "first_name": first_name,
            "last_name": last_name,
            "active": active,
            "addresses": [json_address]
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
                type: "PUT",
                url: `/customers/${id}`,
                contentType: "application/json",
                data: JSON.stringify(data)
            })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Retrieve a Customer
    // ****************************************

    $("#retrieve-btn").click(function () {

        let customer_id = $("#id").val();

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
            flash_message("Success")
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

        let id = $("#id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `/customers/${id}`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("Customer has been Deleted!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#id").val("");
        $("#flash_message").empty();
        clear_form_data()
    });

    // ****************************************
    // Search for a Customer
    // ****************************************

    $("#search-btn").click(function () {

        let active = $("#active").val() == "true";
        let inactive = $("#active").val() == "false";

        let queryString = ""

        if (active || inactive) {
            queryString += '?active=' + $("#active").val()
        }
        

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/customers${queryString}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            $("#search_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-2">ID</th>'
            table += '<th class="col-md-2">First Name</th>'
            table += '<th class="col-md-2">Last Name</th>'
            table += '<th class="col-md-2">Active</th>'
            table += '<th class="col-md-2">Address Name</th>'
            table += '<th class="col-md-2">Address Street</th>'
            table += '<th class="col-md-2">Address City</th>'
            table += '<th class="col-md-2">Address State</th>'
            table += '<th class="col-md-2">Address Postalcode</th>'
            table += '</tr></thead><tbody>'
            let firstCustomer = "";
            for(let i = 0; i < res.length; i++) {
                let customer = res[i];
                table +=  `<tr id="row_${i}"><td>${customer.id}</td><td>${customer.first_name}</td><td>${customer.last_name}</td><td>${customer.active}</td><td>${customer.addresses[0].name}</td><td>${customer.addresses[0].street}</td><td>${customer.addresses[0].city}</td><td>${customer.addresses[0].state}</td><td>${customer.addresses[0].postalcode}</td></tr>`;
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

            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

})
