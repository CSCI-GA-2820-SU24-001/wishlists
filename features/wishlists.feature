
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
  Then I should see "Wishlist RESTful Service" in the title
  And I should not see "404 Not Found"

Scenario: Successfully update a wishlist
  When I visit the "Home Page"
  And I set the "Wishlist name" to "Birthday List"
  And I press the "wishlist search" button
#   Then I should see the message "Success"
#   And I should see "101" in the "wishlist Customer Id" field
#   When I change "wishlist Customer Id" to "102"
#   And I press the "wishlist update" button
#   Then I should see the message "Success"
#   When I copy the "wishlist ID" field
#   And I press the "wishlist clear" button
#   And I paste the "wishlist ID" field
#   And I press the "wishlist retrieve" button
#   Then I should see the message "Success"
#   And I should see "102" in the "wishlist Customer Id" field


# Background:
#     Given the following wishlists
#         | id         | customer_id   | name   | 
#         | AAAAA      | A0001         | testA  |
#         | BBBBB      | B0002         | testB  |
#         | CCCCC      | C0003         | testC  |
#         | DDDDD      | D0004         | testD  |
#     # And the following wishlist items
#     #     | wishlist_id  | product_id  | price   | description            |
#     #     | AAAAA        | 1           | 1.0     | not bad                |
#     #     | AAAAA        | 2           | 1.0     | good product           |
#     #     | CCCCC        | 3           | 3.0     | coooooooool            |
#     #     | DDDDD        | 4           | 2.5     | the best product       |


Scenario: Create a Wishlist
    When I visit the "Home Page"
    And I set the "Wishlist Name" to "My First Wishlist"
    And I set the "Wishlist Customer ID" to "Explore0001"
    And I press the "Wishlist Create" button
    # Then I should see the message "Wishlist has been created!"
    # When I copy the "Wishlist ID" field
    # And I press the "Wishlist Form Clear" button
    # Then the "Wishlist ID" field should be empty
    # And the "Wishlist Name" field should be empty
    # When I paste the "Wishlist ID" field
    # And I press the "Wishlist Retrieve" button
    # Then I should see the message "Success"
    # And I should see "My First Wishlist" in the "Wishlist Name" field
    # And I should see "Explore0001" in the "Customer ID" field

Scenario: Delete a Wishlist
    When I visit the "Home Page"
    And I set the "Wishlist Name" to "Birthday List"
    And I press the "Wishlist Search" button
    # Then I should see the message "Success"
    # When I copy the "Wishlist ID" field
    # And I press the "Wishlist Form Clear" button
    # And I paste the "Wishlist ID" field
    # And I press the "Wishlist Delete" button
    # Then I should see the message "Wishlist has been Deleted!"
    # When I press the "Wishlist Form Clear" button
    # And I paste the "Wishlist ID" field
    # And I press the "Wishlist Retrieve" button
    # Then I should not see "Success"

