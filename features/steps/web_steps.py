######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

# pylint: disable=function-redefined, missing-function-docstring
# flake8: noqa
"""
Web Steps

Steps file for web interactions with Selenium

For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.org/waits.html
"""
import re
import logging
from typing import Any
from behave import when, then, given
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions

ID_PREFIX = "customer_"


def save_screenshot(context: Any, filename: str) -> None:
    """Takes a snapshot of the web page for debugging and validation

    Args:
        context (Any): The session context
        filename (str): The message that you are looking for
    """
    # Remove all non-word characters (everything except numbers and letters)
    filename = re.sub(r"[^\w\s]", "", filename)
    # Replace all runs of whitespace with a single dash
    filename = re.sub(r"\s+", "-", filename)
    context.driver.save_screenshot(f"./captures/{filename}.png")


@when('I visit the "Home Page"')
def step_impl(context: Any) -> None:
    """Make a call to the base URL"""
    context.driver.get(context.base_url)
    # This ensures that the page is loaded and the title is visible
    # before proceeding with other steps.
    WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.visibility_of_element_located((By.TAG_NAME, "h1"))
    )
    # Uncomment next line to take a screenshot of the web page
    save_screenshot(context, "Home Page")


@then('I should see "{message}" in the title')
def step_impl(context: Any, message: str) -> None:
    """Check the document title for a message"""
    assert message in context.driver.title


@then('I should not see "{text_string}"')
def step_impl(context: Any, text_string: str) -> None:
    element = context.driver.find_element(By.TAG_NAME, "body")
    assert text_string not in element.text


@when('I set the "{element_name}" to "{text_string}"')
def step_impl(context: Any, element_name: str, text_string: str) -> None:
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = context.driver.find_element(By.ID, element_id)
    element.clear()
    element.send_keys(text_string)


@when('I select "{text}" in the "{element_name}" dropdown')
def step_impl(context: Any, text: str, element_name: str) -> None:
    # Special-case override for dropdowns not using the default ID convention
    custom_dropdown_ids = {"SuspendedStatus": "search_suspended"}

    if element_name in custom_dropdown_ids:
        element_id = custom_dropdown_ids[element_name]
    else:
        element_id = ID_PREFIX + element_name.lower().replace(" ", "_")

    element = Select(context.driver.find_element(By.ID, element_id))
    element.select_by_visible_text(text)


@then('I should see "{text}" in the "{element_name}" dropdown')
def step_impl(context: Any, text: str, element_name: str) -> None:
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = Select(context.driver.find_element(By.ID, element_id))
    assert element.first_selected_option.text == text


@then('the "{element_name}" field should be empty')
def step_impl(context: Any, element_name: str) -> None:
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = context.driver.find_element(By.ID, element_id)
    assert element.get_attribute("value") == ""


##################################################################
# These two function simulate copy and paste
##################################################################
@when('I copy the "{element_name}" field')
def step_impl(context: Any, element_name: str) -> None:
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    context.clipboard = element.get_attribute("value")
    logging.info("Clipboard contains: %s", context.clipboard)


@when('I paste the "{element_name}" field')
def step_impl(context: Any, element_name: str) -> None:
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(context.clipboard)


##################################################################
# This code works because of the following naming convention:
# The buttons have an id in the html that is the button text
# in lowercase followed by '-btn' so the Clear button has an id of
# id='clear-btn'. That allows us to lowercase the name and add '-btn'
# to get the element id of any button
##################################################################


@when('I press the "{button}" button')
def step_impl(context: Any, button: str) -> None:
    button_id = button.lower().replace(" ", "-") + "-btn"
    context.driver.find_element(By.ID, button_id).click()


@then('I should see "{name}" in the results')
def step_impl(context: Any, name: str) -> None:
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, "search_results"), name
        )
    )
    assert found


@then('I should not see "{name}" in the results')
def step_impl(context: Any, name: str) -> None:
    element = context.driver.find_element(By.ID, "search_results")
    # Split the results into lines or rows and check for exact match
    lines = element.text.splitlines()
    assert all(name != line.strip() for line in lines)


@then('I should see the message "{message}"')
def step_impl(context: Any, message: str) -> None:
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, "flash_message"), message
        )
    )
    assert found


##################################################################
# This code works because of the following naming convention:
# The id field for text input in the html is the element name
# prefixed by ID_PREFIX so the Name field has an id='customer_name'
# We can then lowercase the name and prefix with customer_ to get the id
##################################################################


@then('I should see "{text_string}" in the "{element_name}" field')
def step_impl(context: Any, text_string: str, element_name: str) -> None:
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.text_to_be_present_in_element_value(
            (By.ID, element_id), text_string
        )
    )
    assert found


@when('I change "{element_name}" to "{text_string}"')
def step_impl(context: Any, element_name: str, text_string: str) -> None:
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(text_string)


@given("I am viewing an active customer's details")
def step_impl(context):
    """
    Given step to ensure an active customer's details are displayed.
    This creates a customer, searches for it, and then retrieves its details.
    """
    # Create a customer
    context.execute_steps(
        """
        When I visit the "Home Page"
        And I set the "First Name" to "Active"
        And I set the "Last Name" to "Customer"
        And I set the "Email Address" to "active@example.com"
        And I set the "Phone Number" to "555-123-4567"
        And I set the "Address" to "123 Main St, Anytown, CA 90210"
        And I press the "Create" button
        Then I should see the message "Customer created successfully!"
        """
    )
    # Search for the created customer to get its ID
    context.execute_steps(
        """
        When I set the "First Name" to "Active"
        And I press the "Search" button
        Then I should see the message "Customer found."
        When I copy the "Id" field
        And I press the "Clear" button
        Then the "Id" field should be empty
        When I paste the "Id" field
        And I press the "Retrieve" button
        Then I should see the message "Customer found."
        And I should see "Active" in the "First Name" field
        """
    )


@given("I am viewing a suspended customer's details")
def step_impl(context):
    """
    Given step to ensure a suspended customer's details are displayed.
    This creates a customer, suspends it, searches for it, and then retrieves its details.
    """
    # Create a customer
    context.execute_steps(
        """
        When I visit the "Home Page"
        And I set the "First Name" to "Suspended"
        And I set the "Last Name" to "Customer"
        And I set the "Email Address" to "suspended@example.com"
        And I set the "Phone Number" to "999-888-7777"
        And I set the "Address" to "456 Suspended Rd, Othertown, CA 90210"
        And I press the "Create" button
        Then I should see the message "Customer created successfully!"
        """
    )
    # Suspend the newly created customer
    context.execute_steps(
        """
        When I set the "First Name" to "Suspended"
        And I press the "Search" button
        Then I should see the message "Customer found."
        When I copy the "Id" field
        When I press the "Clear" button
        And I paste the "Id" field
        And I click the "Suspend" button and confirm the action
        Then I should see the message "Customer suspended successfully"
        When I press the "Clear" button
        """
    )
    # Retrieve the suspended customer's details to ensure they are loaded
    context.execute_steps(
        """
        When I paste the "Id" field
        And I press the "Retrieve" button
        Then I should see the message "Customer found."
        And I should see "Suspended" in the "First Name" field
        And the "Suspended" field should be "true"
        """
    )


@when('I click the "{button_name}" button and confirm the action')
def step_impl(context, button_name):
    """
    Clicks a button that triggers a confirmation.
    For now, this assumes the confirmation is handled implicitly by the UI
    or is not a browser-native confirm dialog.
    """
    button_id = button_name.lower().replace(" ", "-") + "-btn"
    context.driver.find_element(By.ID, button_id).click()


@then('the "{element_name}" field should be "{value}"')
def step_impl(context, element_name, value):
    """
    Checks the value of a field, particularly useful for dropdowns like 'Suspended'.
    """
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = context.driver.find_element(By.ID, element_id)
    assert element.get_attribute("value") == value
