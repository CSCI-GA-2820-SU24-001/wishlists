Feature: The wishlist store service back-end
    As a Wishlist Store Owner
    I need a RESTful catalog service
    So that I can keep track of all my pets

Background:
    Given the server is started

Scenario: The server is running
    When I visit the "home page"
    Then I should see "Wishlist Demo REST API Service"
    And  I should not see "404 Not Found"