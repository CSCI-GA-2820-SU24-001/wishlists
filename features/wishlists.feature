
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
        | AAAAA       | 2          | 2.0   | good product     |
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
    And I should see "Explore0001" in the "Wishlist Customer ID" field

Scenario: Update a Wishlist
    When I visit the "Home Page"
    And I set the "Wishlist Name" to "testA"
    And I press the "Wishlist Search" button
    Then I should see the message "Success"
    And I should see "A0001" in the "Wishlist Customer ID" field
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
    And I set the "Wishlist Name" to "My First Wishlist"
    And I set the "Wishlist Customer ID" to "Explore0001"
    And I press the "Wishlist Create" button
    Then I should see the message "Wishlist has been created!"
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
    And I set the "Item Price" to "99.8"
    And I set the "Item Description" to "The newest version!"
    And I paste the "Item Wishlist ID" field
    And I press the "Item Create" button
    Then I should see the message "An item has been created!"
    When I copy the "Item ID" and "Item Wishlist ID" fields
    And I press the "Item Clear" button
    Then the "Item ID" field should be empty
    And the "Item Product ID" field should be empty
    And the "Item Price" field should be empty
    And the "Item Description" field should be empty
    And the "Item Wishlist ID" field should be empty
    And the "Item Added Date" field should be empty
    And the "Item Modified Date" field should be empty
    When I paste the "Item ID" and "Item Wishlist ID" fields
    And I press the "Item Retrieve" button
    Then I should see the message "Success"
    And I should see "1357" in the "Item Product ID" field
    And I should see "99.8" in the "Item Price" field
    And I should see "The newest version!" in the "Item Description" field

Scenario: Update a Wishlist Item
    When I visit the "Home Page"
    And I set the "Wishlist Name" to "My First Wishlist"
    And I set the "Wishlist Customer ID" to "Explore0001"
    And I press the "Wishlist Create" button
    Then I should see the message "Wishlist has been created!"
    When I copy the "Wishlist ID" field
    And I set the "Item Product ID" to "1357"
    And I set the "Item Price" to "99.8"
    And I set the "Item Description" to "The newest version!"
    And I paste the "Item Wishlist ID" field
    And I press the "Item Create" button
    Then I should see the message "An item has been created!"
    When I copy the "Item ID" and "Item Wishlist ID" fields
    And I press the "Item Clear" button
    Then the "Item ID" field should be empty
    And the "Item Product ID" field should be empty
    And the "Item Price" field should be empty
    And the "Item Description" field should be empty
    And the "Item Wishlist ID" field should be empty
    And the "Item Added Date" field should be empty
    And the "Item Modified Date" field should be empty
    When I paste the "Item ID" and "Item Wishlist ID" fields
    And I set the "Item Product ID" to "1357"
    And I set the "Item Price" to "109.8"
    And I set the "Item Description" to "The updated version!"
    And I press the "Item Update" button
    Then I should see the message "Success"
    And I should see "1357" in the "Item Product ID" field
    And I should see "109.8" in the "Item Price" field
    And I should see "The updated version!" in the "Item Description" field

Scenario: Delete a Wishlist Item
    When I visit the "Home Page"
    And I set the "Wishlist Name" to "My First Wishlist"
    And I set the "Wishlist Customer ID" to "Explore0001"
    And I press the "Wishlist Create" button
    Then I should see the message "Wishlist has been created!"
    When I copy the "Wishlist ID" field
    And I set the "Item Product ID" to "1357"
    And I set the "Item Price" to "99.8"
    And I set the "Item Description" to "The newest version!"
    And I paste the "Item Wishlist ID" field
    And I press the "Item Create" button
    Then I should see the message "An item has been created!"
    When I copy the "Item ID" and "Item Wishlist ID" fields
    And I press the "Item Clear" button
    Then the "Item ID" field should be empty
    And the "Item Product ID" field should be empty
    And the "Item Price" field should be empty
    And the "Item Description" field should be empty
    And the "Item Wishlist ID" field should be empty
    And the "Item Added Date" field should be empty
    And the "Item Modified Date" field should be empty
    When I paste the "Item ID" and "Item Wishlist ID" fields
    And I press the "Item Delete" button
    Then I should see the message "Success"
    When I paste the "Item ID" and "Item Wishlist ID" fields
    And I press the "Item Retrieve" button
    Then I should see the message "404 Not Found"

# Scenario: Retrieve a Wishlist
#     When I visit the "Home Page"
#     And I press the "Wishlist List" button
#     Then I should see the message "Success"
#     When I copy the "Wishlist ID" field
#     And I press the "Wishlist Form Clear" button
#     And I paste the "Wishlist ID" field
#     And I press the "Wishlist Retrieve" button
#     Then I should see the message "Success"
#     And I should see "testA" in the "Wishlist Name" field
#     And I should see "A0001" in the "Customer ID" field

Scenario: Search for Wishlist by Customer ID
    When I visit the "Home Page"
    And I set the "Wishlist Customer ID" to "A0001"
    And I press the "Wishlist Search" button
    Then I should see the message "Success"
    And I should see "testA" in the "Wishlist" results
    And I should not see "testB" in the "Wishlist" results
    And I should not see "testC" in the "Wishlist" results
    And I should not see "testD" in the "Wishlist" results

Scenario: Delete All Wishlist by Customer ID
    When I visit the "Home Page"
    And I set the "Wishlist Name" to "My First Wishlist"
    And I set the "Wishlist Customer ID" to "Explore0001"
    And I press the "Wishlist Create" button
    Then I should see the message "Wishlist has been created!"
    When I set the "Wishlist Name" to "My Second Wishlist"
    And I set the "Wishlist Customer ID" to "Explore0001"
    And I press the "Wishlist Create" button
    Then I should see the message "Wishlist has been created!"
    When I copy the "Wishlist Customer ID" field
    And I paste the "Wishlist Customer ID" field
    And I press the "Wishlist Delete All" button
    Then I should see the message "Wishlist has been deleted!"
    When I press the "Wishlist Form Clear" button
    And I paste the "Wishlist Customer ID" field
    And I press the "Wishlist Search" button
    Then I should not see "Explore0001" in the "Wishlist" results

Scenario: Search filtered Wishlist Item
    When I visit the "Home Page"
    And I set the "Wishlist Name" to "My First Wishlist"
    And I set the "Wishlist Customer ID" to "Explore0001"
    And I press the "Wishlist Create" button
    Then I should see the message "Wishlist has been created!"
    When I copy the "Wishlist ID" field
    And I set the "Item Product ID" to "1234"
    And I set the "Item Price" to "100"
    And I set the "Item Description" to "Item with price 100"
    And I paste the "Item Wishlist ID" field
    And I press the "Item Create" button
    Then I should see the message "An item has been created!"
    When I copy the "Item Wishlist ID" field
    And I set the "Item Product ID" to "2345"
    And I set the "Item Price" to "200"
    And I set the "Item Description" to "Item with price 200"
    And I paste the "Item Wishlist ID" field
    And I press the "Item Create" button
    Then I should see the message "An item has been created!"
    When I copy the "Item Wishlist ID" field
    And I set the "Item Product ID" to "3456"
    And I set the "Item Price" to "300"
    And I set the "Item Description" to "Item with price 300"
    And I paste the "Item Wishlist ID" field
    And I press the "Item Create" button
    Then I should see the message "An item has been created!"
    When I copy the "Item Wishlist ID" field
    And I press the "Item Clear" button
    And I paste the "Item Wishlist ID" field
    And I set the "Item Price" to "250"
    And I press the "Item Search" button
    Then I should see the message "Success"
    And I should see "100" in the "Item" results
    And I should see "200" in the "Item" results
    And I should not see "300" in the "Item" results

# Scenario: Search for Wishlist by Name
#     When I visit the "Home Page"
#     And I set the "Wishlist Name" to "testA"
#     And I press the "Wishlist Search" button
#     Then I should see the message "Success"
#     And I should see "testA" in the "Wishlist" results
#     And I should not see "testB" in the "Wishlist" results
#     And I should not see "testC" in the "Wishlist" results
#     And I should not see "testD" in the "Wishlist" results

# Scenario: Search for Wishlist by Customer ID and Name
#     When I visit the "Home Page"
#     And I set the "Wishlist Customer ID" to "A0001"
#     And I set the "Wishlist Name" to "testA"
#     And I press the "Wishlist Search" button
#     Then I should see the message "Success"
#     And I should see "testA" in the "Wishlist" results
#     And I should not see "testB" in the "Wishlist" results
#     And I should not see "testC" in the "Wishlist" results
#     And I should not see "testD" in the "Wishlist" results
