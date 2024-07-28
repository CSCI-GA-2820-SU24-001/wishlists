Feature: The wishlist store service back-end
    As a Wishlist Store Owner
    I need a RESTful catalog service
    So that I can keep track of all my wishlists

Background:

Scenario: The server is running
    When I visit the "home page"
    Then I should see "Wishlist Demo RESTful Service" in the title
    And  I should not see "404 Not Found"
