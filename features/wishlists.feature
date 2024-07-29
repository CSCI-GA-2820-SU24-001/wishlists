Feature: The wishlist store service back-end
  As a Wishlist Store Owner
  I need a RESTful catalog service
  So that I can keep track of all my wishlists

  Background:
    Given the server is running

  Scenario: The server is running
    When I visit the "home page"
    Then I should see "Wishlist Demo RESTful Service" in the title
    And I should not see "404 Not Found"

  Scenario: Delete a Wishlist Item
    When I visit the "Home Page"
    And I set the "Wishlist Item Name" to "Marco"
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
