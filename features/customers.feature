Feature: Customer Management UI
    As a Business Owner
    I need a RESTful customer service
    So that I can keep track of my customers

  Background:
    Given the following customers
      | First Name | Last Name | Email           | Phone Number   | Address                                   |
      | First      | Last      | test@email.com  | 123-456-7890   | 1234 testStreet testCity, testState 10009 |
      | First1     | Last1     | test1@email.com | 123-456-7891   | 1235 testStreet testCity, testState 10009 |
      | First2     | Last2     | test2@email.com | 123-456-7892   | 1236 testStreet testCity, testState 10009 |
      | First3     | Last3     | test3@email.com | 123-456-7893   | 1237 testStreet testCity, testState 10009 |


Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Customer Administration" in the title
    And I should not see "404 Not Found"

Scenario: Create a Customer
    When I visit the "Home Page"
    And I set the "First Name" to "First"
    And I set the "Last Name" to "Last"
    And I set the "Email Address" to "test@email.com"
    And I set the "Phone Number" to "123-456-7890"
    And I set the "Address" to "1234 testStreet testCity, testState 10009"
    And I press the "Create" button
    Then I should see the message "Customer created successfully!"

Scenario: Delete a Customer
    When I visit the "Home Page"
    And I set the "First Name" to "First"
    And I press the "Search" button
    Then I should see the message "Customer found."
    When I copy the "Id" field
    And I press the "Clear" button
    And I paste the "Id" field
    And I press the "Delete" button
    Then I should see the message "Customer deleted."

Scenario: Read a Customer by ID
    When I visit the "Home Page"
    And I set the "First Name" to "First"
    And I press the "Search" button
    Then I should see the message "Customer found."
    When I copy the "Id" field
    And I press the "Clear" button
    Then the "Id" field should be empty
    And the "First Name" field should be empty
    And the "Last Name" field should be empty
    When I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see the message "Customer found."
    And I should see "First" in the "First Name" field
    And I should see "Last" in the "Last Name" field
    And I should see "test@email.com" in the "Email Address" field
    And I should see "123-456-7890" in the "Phone Number" field
    And I should see "1234 testStreet testCity, testState 10009" in the "Address" field

Scenario: Update a Customer
    When I visit the "Home Page"
    And I set the "First Name" to "First"
    And I press the "Search" button
    Then I should see the message "Customer found."
    And I should see "First" in the "First Name" field
    And I should see "Last" in the "Last Name" field
    And I should see "test@email.com" in the "Email Address" field
    When I change "Email Address" to "updated@email.com"
    And I press the "Update" button
    Then I should see the message "Customer updated successfully!"
    When I copy the "Id" field
    And I press the "Clear" button
    And I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see the message "Customer found."
    And I should see "updated@email.com" in the "Email Address" field

Scenario: List all Customers
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see the message "Customer found."
    And I should see "First" in the results
    And I should see "First1" in the results
    And I should see "First2" in the results
    And I should see "First3" in the results

Scenario: Suspend an active Customer
    Given I am viewing an active customer's details
    When I click the "Suspend" button and confirm the action
    Then I should see the message "Customer suspended successfully"
    And the "Suspended" field should be "true"

Scenario: Activate a suspended Customer
    Given I am viewing a suspended customer's details
    When I click the "Activate" button and confirm the action
    Then I should see the message "Customer activated successfully"
    And the "Suspended" field should be "false"