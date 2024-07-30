Feature: The wishlist service back-end
    As a Wishlist Owner
    I need a RESTful catalog service
    So that I can keep track of all the wishlists and wishlist items

Background:

Scenario: The server is running
    When I visit the "home page"
    Then I should see "Wishlist RESTful Service" in the title
    And  I should not see "404 Not Found"

Scenario: Create a Wishlist
    When I visit the "Home Page"
    And I set the "Wishlist Name" to "My First Wishlist"
    And I set the "Wishlist Customer ID" to "Explore0001"
    And I press the "Wishlist Create" button
    Then I should see the message "Wishlist has been created!"
    When I copy the "Wishlist ID" field
    And I press the "Clear" button
    Then the "Wishlist ID" field should be empty
    And the "Wishlist Name" field should be empty
    And the "Wishlist Customer ID" field should be empty
    And the "Wishlist Item Product ID" field should be empty
    And the "Wishlist Item Name" field should be empty
    When I paste the "Wishlist Id" field
    And I press the "Wishlist Retrieve" button
    Then I should see the message "Success"
    And I should see "My First Wishlist" in the "Wishlist Name" field
    And I should see "Explore0001" in the "Wishlist Customer ID" field
