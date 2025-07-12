
Background:
    Given the following customers
        | First Name       | Last Name  | Email                | Phone Numer          | Address   
        | First            | Last       | test@email.com       | 123-456-7890         | 1234 testStreet testCity, testState 10009
        | First1           | Last1      | test1@email.com      | 123-456-7891         | 1235 testStreet testCity, testState 10009
        | First2           | Last2      | test2@email.com      | 123-456-7892         | 1236 testStreet testCity, testState 10009
        | First3           | Last3      | test3@email.com      | 123-456-7893         | 1237 testStreet testCity, testState 10009


Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Customer Administration" in the title
    And I should not see "404 Not Found"

Scenario: Create a Pet
    When I visit the "Home Page"
    And I set the "First Name" to "First"
    And I set the "Last Name" to "Last"
    And I set the "Email Address" to "test@email.com"
    And I set the "Phone Number" to "123-456-7890"
    And I set the "Address" to "1234 testStreet testCity, testState 10009"
    And I press the "Create" button
    Then I should see the message "Customer created successfully!"