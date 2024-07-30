Feature: The wishlist store service back-end
    As a Wishlist Store Owner
    I need a RESTful catalog service
    So that I can keep track of all the wishlists and wishlist items

Background:

Scenario: The server is running
    When I visit the "home page"
    Then I should see "Wishlist Demo RESTful Service" in the title
    And  I should not see "404 Not Found"

Scenario: Create a Wishlist
    When I visit the "Home Page"
    And I set the "Shopcart total price" to "10"
    And I press the "Shopcart Create" button
    Then I should see the message "Shopcart has been Created!"
    When I copy the "Shopcart ID" field
    And I press the "Shopcart Form Clear" button
    Then the "Shopcart ID" field should be empty
    And the "Shopcart Item product ID" field should be empty
    And the "Shopcart Item name" field should be empty
    And the "Shopcart total price" field should be empty
    When I paste the "Shopcart Id" field
    And I press the "Shopcart Retrieve" button
    Then I should see the message "Success"
    And I should see "10" in the "Shopcart total price" field
