Feature: The customer service back-end
    As a Service Provider
    I need a RESTful customer data service
    So that I can keep track of all my customers

Background:
    Given the following customers
        | name       | street           | city           | state   | postalcode | first_name | last_name | active |
        | Home       | 123 fake rd      | Happytown      | CA      | 12345      |   Bob      | Smith     | True   |


Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Customer RESTful Service" in the title
    And I should not see "404 Not Found"

Scenario: Create a Customer
    When I visit the "Home Page"
    And I set the "First Name" to "Joe"
    And I set the "Last Name" to "DiMaggio"
    And I select "True" in the "Active" dropdown
    And I set the "Address Name" to "Home"
    And I set the "Address Street" to "123 Happy Rd"
    And I set the "Address City" to "Happytown"
    And I set the "Address State" to "AK"
    And I set the "Address Postalcode" to "54321"
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "ID" field
    And I press the "Clear" button
    Then the "ID" field should be empty
    And the "First Name" field should be empty
    And the "Address Name" field should be empty
    When I paste the "ID" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "Joe" in the "First Name" field
    And I should see "DiMaggio" in the "Last Name" field
    And I should see "True" in the "Active" dropdown
    And I should see "Home" in the "Address Name" field
    And I should see "123 Happy Rd" in the "Address Street" field
    And I should see "Happytown" in the "Address City" field
    And I should see "AK" in the "Address State" field
    And I should see "54321" in the "Address Postalcode" field
