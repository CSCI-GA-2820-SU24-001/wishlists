
$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the wishlist form with data from the response
    function update_wishlist_form_data(res) {
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
    }

    // Updates the wishlist item form with data from the response
    function update_wishlist_item_form_data(res) {
        $("#item_id").val(res.id);
        $("#item_product_id").val(res.product_id);
        $("#item_price").val(res.price);
        $("#item_description").val(res.description);
        $("#item_wishlist_id").val(res.wishlist_id);
    }

    // Clears all wishlist form fields
    function clear_wishlist_form_data() {
        $("#wishlist_id").val("");
        $("#wishlist_name").val("");
        $("#wishlist_customer_id").val("");
        $("#wishlist_created_date").val("");
        $("#wishlist_modified_date").val("");
    }

    // Clears all wishlistitem form fields
    function clear_wishlist_item_data() {
        $("#item_id").val("");
        $("#item_product_id").val("");
        $("#item_price").val("");
        $("#item_description").val("");
        $("#item_wishlist_id").val("");
        $("#item_added_date").val("");
        $("#item_modified_date").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
        console.log("Flash message updated:", message); 
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
            url: "/api/wishlists",
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
    // Retrieve a Wishlist
    // ****************************************

    $("#wishlist-retrieve-btn").click(function () {

        let wishlist_id = $("#wishlist_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/api/wishlists/${wishlist_id}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            update_wishlist_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            clear_wishlist_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Update a Wishlist
    // ****************************************

    $("#wishlist-update-btn").click(function () {

        let wishlist_id = $("#wishlist_id").val();
        let wishlist_name = $("#wishlist_name").val();
        let wishlist_customer_id = $("#wishlist_customer_id").val();
        let wishlist_created_date = $("#wishlist_created_date").val();
        let wishlist_modified_date = $("#wishlist_modified_date").val();

        let data = {
            "name": wishlist_name,
            "id": wishlist_id,
            "customer_id": wishlist_customer_id,
            "created_date": wishlist_created_date,
            "modified_date": wishlist_modified_date,
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
                type: "PUT",
                url: `/api/wishlists/${wishlist_id}`,
                contentType: "application/json",
                data: JSON.stringify(data)
            })

        ajax.done(function(res){
            update_wishlist_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Delete a Wishlist
    // ****************************************

    $("#wishlist-delete-btn").click(function () {
        let wishlist_id = $("#wishlist_id").val();
        $("#flash_message").empty();
        
        ajax = $.ajax({
            type: "DELETE",
            url: `/api/wishlists/${wishlist_id}`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_wishlist_form_data();
            flash_message("Wishlist has been deleted!");
        });
    
        ajax.fail(function(res){
            flash_message("Server error!");
        });
    });

    // ****************************************
    // Delete all Wishlist by customer ID
    // ****************************************

    $("#wishlist-delete-all-btn").click(function () {
        let customer_id = $("#wishlist_customer_id").val();
        $("#flash_message").empty();
        
        ajax = $.ajax({
            type: "DELETE",
            url: `/api/wishlists/customers/${customer_id}`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_wishlist_form_data();
            flash_message("Wishlist has been deleted!");
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });

    // ****************************************
    // Search Wishlists
    // ****************************************

    $("#wishlist-search-btn").click(function () {

        let customer_id = $("#wishlist_customer_id").val();
        let name = $("#wishlist_name").val();

        let queryString = ""

        if (customer_id) {
            queryString += 'customer_id=' + customer_id
        }
        if (name) {
            if (queryString.length > 0) {
                queryString += '&name=' + name
            } else {
                queryString += 'name=' + name
            }
        }

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/api/wishlists?${queryString}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            $("#wishlist_search_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-2">ID</th>'
            table += '<th class="col-md-2">Customer ID</th>'
            table += '<th class="col-md-2">Name</th>'
            table += '</tr></thead><tbody>'
            let firstWishlist = "";
            for(let i = 0; i < res.length; i++) {
                let wishlist = res[i];
                table +=  `<tr id="row_${i}"><td>${wishlist.id}</td><td>${wishlist.customer_id}</td><td>${wishlist.name}</td></tr>`;
                if (i == 0) {
                    firstWishlist = wishlist;
                }
            }
            table += '</tbody></table>';
            $("#wishlist_search_results").append(table);

            // copy the first result to the form
            if (firstWishlist != "") {
                update_wishlist_form_data(firstWishlist)
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

    $("#item-clear-btn").click(function () {
        $("#flash_message").empty();
        clear_wishlist_item_data()
    });


    // *************************************************
    //  Retrieve a WishlistItem
    // *************************************************
    $("#item-retrieve-btn").click(function () {

        let item_id = $("#item_id").val();
        let wishlist_id = $("#item_wishlist_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/api/wishlists/${wishlist_id}/items/${item_id}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            update_wishlist_item_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            clear_wishlist_item_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Update a WishlistItem
    // ****************************************

    $("#item-update-btn").click(function () {
        let item_id = $("#item_id").val();
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
            type: "PUT",
            url: `/api/wishlists/${wishlist_id}/items/${item_id}`,
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_wishlist_item_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
        
    });

    // ****************************************
    // Delete a WishlistItem
    // ****************************************

    $("#item-delete-btn").click(function () {

        let item_id = $("#item_id").val();
        let wishlist_id = $("#item_wishlist_id").val();
    
        $("#flash_message").empty();
    
        let ajax = $.ajax({
            type: "DELETE",
            url: `/api/wishlists/${wishlist_id}/items/${item_id}`,
            contentType: "application/json",
            data: '',
        })
    
        ajax.done(function(res){
            clear_wishlist_item_data()
            flash_message("Success");
        });
    
        ajax.fail(function(res){
            flash_message("Server error!");
        });
    });

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

        if (wishlist_id.trim() === "") {
            flash_message("Wishlist ID cannot be empty");
        }
        else {
            let ajax = $.ajax({
                type: "POST",
                url: `/api/wishlists/${wishlist_id}/items`,
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
        }
    });


     // *************************************************
    //  Move a WishlistItem
    // *************************************************
    $("#wishlist-move-btn").click(function () {

        let source_wishlist_id = $("#source_wishlist_id").val();
        let target_wishlist_id = $("#target_wishlist_id").val();
        let item_id = $("#move_item_id").val();


        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "PUT",
            url: `/wishlists/${source_wishlist_id}/items/${item_id}/move-to/${target_wishlist_id}`,
            contentType: "application/json",
        })

        ajax.done(function(res){
            //alert(res.toSource())
            update_wishlist_item_form_data(res)
            flash_message("Item has been successfully moved to target wishlist")
        });

        ajax.fail(function(res){
            clear_wishlist_item_data()
            flash_message(res.responseJSON.message)
        });

    });



    // ****************************************
    // Search filtered WishlistItem
    // ****************************************

    $("#item-search-btn").click(function () {

        let item_wishlist_id = $("#item_wishlist_id").val();
        let item_price = $("#item_price").val();
        let sort_by = $("#wishlist_sort_by").val(); // Assuming you have an input or select with id "sort_by"
        let order = $("#wishlist_sort_order").val();

        let queryString = ""

        if (item_price) {
            queryString += 'price=' + item_price
        }

        if (sort_by) {
            if (queryString) {
                queryString += '&';
            }
            queryString += 'sort_by=' + sort_by;
        }
        
        if (order) {
            if (queryString) {
                queryString += '&';
            }
            queryString += 'order=' + order;
        }

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/api/wishlists/${item_wishlist_id}/items?${queryString}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            $("#item_search_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-2">ID</th>'
            table += '<th class="col-md-2">Product ID</th>'
            table += '<th class="col-md-2">Description</th>'
            table += '<th class="col-md-2">Wishlist ID</th>'
            table += '<th class="col-md-2">Price</th>'
            table += '<th class="col-md-2">Added Date</th>'
            table += '<th class="col-md-2">Modified Date</th>'
            table += '</tr></thead><tbody>'
            let firstWishlistItem = "";
            for(let i = 0; i < res.length; i++) {
                let item = res[i];
                table +=  `<tr id="row_${i}"><td>${item.id}</td><td>${item.product_id}</td><td>${item.description}</td><td>${item.wishlist_id}</td><td>${item.price}</td><td>${item.added_date}</td><td>${item.modified_date}</td></tr>`;
                if (i == 0) {
                    firstWishlistItem = item;
                }
            }
            table += '</tbody></table>';
            $("#item_search_results").append(table);

            // copy the first result to the form
            if (firstWishlistItem != "") {
                update_wishlist_item_form_data(firstWishlistItem)
            }

            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });


})
