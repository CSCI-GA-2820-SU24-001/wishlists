Feature: The wishlist service back-end
    As a Wishlist Owner
    I need a RESTful catalog service
    So that I can keep track of all the wishlists and wishlist items

Background:
    Given the following wishlists
        | id    | customer_id | name  | 
        | AAAAA | A0001       | testA |
        | BBBBB | B0002       | testB |
        | CCCCC | C0003       | testC |
        | DDDDD | D0004       | testD |
    And the following wishlist items
        | wishlist_id | product_id | price | description      |
        | AAAAA       | 1          | 1.0   | not bad          |
        | AAAAA       | 2          | 1.0   | good product     |
        | CCCCC       | 3          | 3.0   | coooooooool      |
        | DDDDD       | 4          | 2.5   | the best product |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Wishlist RESTful Service" in the title
    And I should not see "404 Not Found"

Scenario: Create a Wishlist
    When I visit the "Home Page"
    And I set the "Wishlist Name" to "My First Wishlist"
    And I set the "Wishlist Customer ID" to "Explore0001"
    And I press the "Wishlist Create" button
    Then I should see the message "Wishlist has been created!"
    When I copy the "Wishlist ID" field
    And I press the "Wishlist Form Clear" button
    Then the "Wishlist ID" field should be empty
    And the "Wishlist Name" field should be empty
    When I paste the "Wishlist ID" field
    And I press the "Wishlist Retrieve" button
    Then I should see the message "Success"
    And I should see "My First Wishlist" in the "Wishlist Name" field
    And I should see "Explore0001" in the "Customer ID" field

Scenario: Update a Wishlist
    When I visit the "Home Page"
    And I set the "Wishlist Name" to "Birthday List"
    And I press the "Wishlist Search" button
    Then I should see the message "Success"
    And I should see "101" in the "Wishlist Customer ID" field
    When I change "Wishlist Customer ID" to "102"
    And I press the "Wishlist Update" button
    Then I should see the message "Success"
    When I copy the "Wishlist ID" field
    And I press the "Wishlist Form Clear" button
    And I paste the "Wishlist ID" field
    And I press the "Wishlist Retrieve" button
    Then I should see the message "Success"
    And I should see "102" in the "Wishlist Customer ID" field

Scenario: Delete a Wishlist
    When I visit the "Home Page"
    And I set the "Wishlist Name" to "Birthday List"
    And I press the "Wishlist Search" button
    Then I should see the message "Success"
    When I copy the "Wishlist ID" field
    And I press the "Wishlist Form Clear" button
    And I paste the "Wishlist ID" field
    And I press the "Wishlist Delete" button
    Then I should see the message "Wishlist has been deleted!"
    When I press the "Wishlist Form Clear" button
    And I paste the "Wishlist ID" field
    And I press the "Wishlist Retrieve" button
    Then I should not see "Success"

Scenario: Create a Wishlist Item
    When I visit the "Home Page"
    And I set the "Wishlist Name" to "My First Wishlist"
    And I set the "Wishlist Customer ID" to "Explore0001"
    And I press the "Wishlist Create" button
    Then I should see the message "Wishlist has been created!"
    When I copy the "Wishlist ID" field
    And I set the "Item Product ID" to "1357"
    And I set the "Item Price" to "99.80"
    And I set the "Item Description" to "The newest version!"
    And I paste the "Item Wishlist ID" field
    And I press the "Item Create" button
    Then I should see the message "An item has been created!"
    When I copy the "Wishlist ID" field
    And I press the "Wishlist Form Clear" button
    Then the "Wishlist ID" field should be empty
    And the "Wishlist Name" field should be empty
    When I paste the "Wishlist ID" field
    And I press the "Wishlist Retrieve" button
    Then I should see the message "Success"
    And I should see "My First Wishlist" in the "Wishlist Name" field
    And I should see "Explore0001" in the "Customer ID" field

Scenario: Retrieve a Wishlist
    When I visit the "Home Page"
    And I press the "Wishlist List" button
    Then I should see the message "Success"
    When I copy the "Wishlist ID" field
    And I press the "Wishlist Form Clear" button
    And I paste the "Wishlist ID" field
    And I press the "Wishlist Retrieve" button
    Then I should see the message "Success"
    And I should see "testA" in the "Wishlist Name" field
    And I should see "A0001" in the "Customer ID" field

Scenario: Search for Wishlist by Customer ID
    When I visit the "Home Page"
    And I set the "Wishlist Customer ID" to "A0001"
    And I press the "Wishlist Search" button
    Then I should see the message "Success"
    And I should see "testA" in the "Wishlist" results
    And I should not see "testB" in the "Wishlist" results
    And I should not see "testC" in the "Wishlist" results
    And I should not see "testD" in the "Wishlist" results

Scenario: Search for Wishlist by Name
    When I visit the "Home Page"
    And I set the "Wishlist Name" to "testA"
    And I press the "Wishlist Search" button
    Then I should see the message "Success"
    And I should see "testA" in the "Wishlist" results
    And I should not see "testB" in the "Wishlist" results
    And I should not see "testC" in the "Wishlist" results
    And I should not see "testD" in the "Wishlist" results

Scenario: Search for Wishlist by Customer ID and Name
    When I visit the "Home Page"
    And I set the "Wishlist Customer ID" to "A0001"
    And I set the "Wishlist Name" to "testA"
    And I press the "Wishlist Search" button
    Then I should see the message "Success"
    And I should see "testA" in the "Wishlist" results
    And I should not see "testB" in the "Wishlist" results
    And I should not see "testC" in the "Wishlist" results
    And I should not see "testD" in the "Wishlist" results