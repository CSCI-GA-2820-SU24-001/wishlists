$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************


    // Updates the form with data from the response
    function update_form_data(res) {

        $("#wishlist_id").val(res.id);
        $("#wishlist_name").val(res.name);
        $("#wishlist_customer_id").val(res.customer_id);
        let createdDate = new Date(res.created_date);
        let formattedCreatedDate = createdDate.toISOString().split('T')[0];
        $("#wishlist_created_date").val(formattedCreatedDate);
    
        // Convert modified_date to YYYY-MM-DD format
        let modifiedDate = new Date(res.modified_date);
        let formattedModifiedDate = modifiedDate.toISOString().split('T')[0];
        $("#wishlist_modified_date").val(formattedModifiedDate);
   
    // Updates the wishlist item form with data from the response
    function update_wishlist_item_form_data(res) {
        $("#item_id").val(res.id);
        $("#item_product_id").val(res.product_id);
        $("#item_price").val(res.price);
        $("#item_description").val(res.description);
        $("#item_wishlist_id").val(res.wishlist_id);
    }

    /// Clears all wishlist form fields
    function clear_wishlist_form_data() {
        $("#wishlist_id").val("");
        $("#wishlist_name").val("");
        $("#wishlist_item_product_id").val("");
        $("#wishlist_item_name").val("");
    }

    /// Clears all wishlist item form fields
    function clear_wishlist_item_form_data() {
        $("#item_id").val("");
        $("#item_price").val("");
        $("#item_product_id").val("");
        $("#item_description").val("");
        $("#item_wishlist_id").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    //  W I S H L I S T   F U N C T I O N S
    // ****************************************


    // ****************************************
    // Create a Wishlist
    // ****************************************

    $("#wishlist-create-btn").click(function () {

        let name = $("#wishlist_name").val();
        let customer_id = $("#wishlist_customer_id").val();

        let data = {
            "name": name,
            "customer_id": customer_id
        };

        $("#wishlist_search_results").empty();
        $("#flash_message").empty();
        
        let ajax = $.ajax({
            type: "POST",
            url: "/wishlists",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_wishlist_form_data(res)
            flash_message("Wishlist has been created!")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // List Wishlists
    // ****************************************



    // ****************************************
    // Update a Wishlist
    // ****************************************

    $("#update-btn").click(function () {

        let pet_id = $("#pet_id").val();
        let name = $("#pet_name").val();
        let category = $("#pet_category").val();
        let available = $("#pet_available").val() == "true";
        let gender = $("#pet_gender").val();
        let birthday = $("#pet_birthday").val();

        let data = {
            "name": name,
            "category": category,
            "available": available,
            "gender": gender,
            "birthday": birthday
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
                type: "PUT",
                url: `/pets/${pet_id}`,
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
    // Retrieve a Wishlist
    // ****************************************

    $("#retrieve-btn").click(function () {

        let pet_id = $("#pet_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/pets/${pet_id}`,
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
    // Delete a Wishlist
    // ****************************************

    $("#delete-btn").click(function () {

        let pet_id = $("#pet_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `/pets/${pet_id}`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("Pet has been Deleted!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Search Wishlists
    // ****************************************

    $("#search-btn").click(function () {

        let name = $("#pet_name").val();
        let category = $("#pet_category").val();
        let available = $("#pet_available").val() == "true";

        let queryString = ""

        if (name) {
            queryString += 'name=' + name
        }
        if (category) {
            if (queryString.length > 0) {
                queryString += '&category=' + category
            } else {
                queryString += 'category=' + category
            }
        }
        if (available) {
            if (queryString.length > 0) {
                queryString += '&available=' + available
            } else {
                queryString += 'available=' + available
            }
        }

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/pets?${queryString}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            $("#search_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-2">ID</th>'
            table += '<th class="col-md-2">Name</th>'
            table += '<th class="col-md-2">Category</th>'
            table += '<th class="col-md-2">Available</th>'
            table += '<th class="col-md-2">Gender</th>'
            table += '<th class="col-md-2">Birthday</th>'
            table += '</tr></thead><tbody>'
            let firstPet = "";
            for(let i = 0; i < res.length; i++) {
                let pet = res[i];
                table +=  `<tr id="row_${i}"><td>${pet.id}</td><td>${pet.name}</td><td>${pet.category}</td><td>${pet.available}</td><td>${pet.gender}</td><td>${pet.birthday}</td></tr>`;
                if (i == 0) {
                    firstPet = pet;
                }
            }
            table += '</tbody></table>';
            $("#search_results").append(table);

            // copy the first result to the form
            if (firstPet != "") {
                update_form_data(firstPet)
            }

            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Clear the Wishlist form
    // ****************************************

    $("#wishlist-form-clear-btn").click(function () {
        $("#flash_message").empty();
        clear_wishlist_form_data()
    });


    // *************************************************
    //  W I S H L I S T  I T E M   F U N C T I O N S
    // *************************************************


    // ****************************************
    // Create a Wishlist Item
    // ****************************************

    $("#item-create-btn").click(function () {

        let product_id = $("#item_product_id").val();
        let price = parseFloat($("#item_price").val());
        let description = $("#item_description").val();
        let wishlist_id = $("#item_wishlist_id").val();

        let data = {
            "product_id": product_id,
            "price": price,
            "description": description,
            "wishlist_id": wishlist_id
        };

        $("#flash_message").empty();
        
        let ajax = $.ajax({
            type: "POST",
            url: `/wishlists/${wishlist_id}/items`,
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_wishlist_item_form_data(res)
            flash_message("An item has been created!")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });

    $("#wishlist-update-btn").click(function () {

        let wishlist_id = $("#wishlist_id").val();
        let wishlist_name = $("#wishlist_name").val();
        let wishlist_customer_id = $("#wishlist_customer_id").val();
        let wishlist_created_date = $("#wishlist_created_date").val() == "true";
        let wishlist_modified_date = $("#wishlist_modified_date").val();

        let data = {
            "name": wishlist_name,
            "id":wishlist_id,
            "customer_id": wishlist_customer_id,
            "created_date": wishlist_created_date,
            "modified_date": wishlist_modified_date,
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
                type: "PUT",
                url: `/wishlists/${wishlist_id}`,
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
    // Retrieve a Wishlist Item
    // ****************************************

    $("#retrieve-btn").click(function () {

        let pet_id = $("#pet_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/pets/${pet_id}`,
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
    // Delete a Wishlist Item
    // ****************************************

    $("#delete-btn").click(function () {

        let pet_id = $("#pet_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `/pets/${pet_id}`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("Pet has been Deleted!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Search Wishlist Items
    // ****************************************

    $("#search-btn").click(function () {

        let name = $("#pet_name").val();
        let category = $("#pet_category").val();
        let available = $("#pet_available").val() == "true";

        let queryString = ""

        if (name) {
            queryString += 'name=' + name
        }
        if (category) {
            if (queryString.length > 0) {
                queryString += '&category=' + category
            } else {
                queryString += 'category=' + category
            }
        }
        if (available) {
            if (queryString.length > 0) {
                queryString += '&available=' + available
            } else {
                queryString += 'available=' + available
            }
        }

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/pets?${queryString}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            $("#search_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-2">ID</th>'
            table += '<th class="col-md-2">Name</th>'
            table += '<th class="col-md-2">Category</th>'
            table += '<th class="col-md-2">Available</th>'
            table += '<th class="col-md-2">Gender</th>'
            table += '<th class="col-md-2">Birthday</th>'
            table += '</tr></thead><tbody>'
            let firstPet = "";
            for(let i = 0; i < res.length; i++) {
                let pet = res[i];
                table +=  `<tr id="row_${i}"><td>${pet.id}</td><td>${pet.name}</td><td>${pet.category}</td><td>${pet.available}</td><td>${pet.gender}</td><td>${pet.birthday}</td></tr>`;
                if (i == 0) {
                    firstPet = pet;
                }
            }
            table += '</tbody></table>';
            $("#search_results").append(table);

            // copy the first result to the form
            if (firstPet != "") {
                update_form_data(firstPet)
            }

            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Clear the Wishlist Item form
    // ****************************************

    $("#item-form-clear-btn").click(function () {
        $("#flash_message").empty();
        clear_wishlist_item_form_data()
    });
}})





