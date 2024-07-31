Feature: The wishlist store service back-end
  As a Wishlist Store Owner
  I need a RESTful catalog service
  So that I can keep track of all my wishlists

Background:
  Given the following wishlists exist:
    | id  | name          | customer_id | created_date | modified_date |
    | 1   | Birthday List | 101         | 2023-01-01   | 2023-06-01    |
    | 2   | Christmas     | 102         | 2023-02-01   | 2023-06-01    |

Scenario: The server is running
  When I visit the "Home Page"
  Then I should see "Wishlist Demo RESTful Service" in the title
  And I should not see "404 Not Found"

Scenario: Successfully update a wishlist
  When I visit the "Home Page"
  And I set the "name" to "Birthday List"
  And I press the "wishlist-search" button
  Then I should see the message "Success"
  And I should see "101" in the "Customer Id" field
  When I change "Customer Id" to "102"
  And I press the "wishlist-update" button
  Then I should see the message "Success"
  When I copy the "ID" field
  And I press the "wishlist-clear" button
  And I paste the "ID" field
  And I press the "retrieve" button
  Then I should see the message "Success"
  And I should see "102" in the "Customer Id" field
