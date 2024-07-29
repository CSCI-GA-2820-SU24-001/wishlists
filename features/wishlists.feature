Feature: The wishlist service back-end
  As a wishlist manager
  I need a RESTful catalog service
  So that I can keep track of all the wishlists and wishlist items

Background:
  Given the following wishlists
    | name        | customer_id                          |
    | Birthday    | 123e4567-e89b-12d3-a456-426614174000 |
    | Anniversary | 123e4567-e89b-12d3-a456-426614174001 |
    | Christmas   | 123e4567-e89b-12d3-a456-426614174002 |
    | New Year    | 123e4567-e89b-12d3-a456-426614174003 |
  And the following wishlist items
    | wishlist_id | product_id | price | description |
    | Birthday    | 1          | 50.0  | Phone       |
    | Anniversary | 2          | 100.0 | Laptop      |
    | Christmas   | 3          | 20.0  | Book        |
    | New Year    | 4          | 15.0  | Pen         |

Scenario: The server is running
  When I visit the "Home Page"
  Then I should see "Wishlists RESTful Service" in the title
  And I should not see "404 Not Found"

Scenario: Delete a Wishlist
  Given the following wishlists
    | name        | customer_id                          |
    | Birthday    | 123e4567-e89b-12d3-a456-426614174000 |
    | Anniversary | 123e4567-e89b-12d3-a456-426614174001 |
    | Christmas   | 123e4567-e89b-12d3-a456-426614174002 |
    | New Year    | 123e4567-e89b-12d3-a456-426614174003 |
  And the following wishlist items
    | wishlist_id | product_id | price | description |
    | Birthday    | 1          | 50.0  | Phone       |
    | Anniversary | 2          | 100.0 | Laptop      |
    | Christmas   | 3          | 20.0  | Book        |
    | New Year    | 4          | 15.0  | Pen         |
  When I visit the "Home Page"
  And I set the "Wishlist Name" to "Birthday"
  And I press the "Wishlist Search" button
  Then I should see the message "Success"
  When I copy the "Wishlist ID" field
  And I press the "Wishlist Form Clear" button
  And I paste the "Wishlist ID" field
  And I press the "Wishlist Delete" button
  Then I should see the message "Wishlist has been Deleted!"
  When I press the "Wishlist Form Clear" button
  And I paste the "Wishlist ID" field
  And I press the "Wishlist Retrieve" button
  Then I should not see "Success"
