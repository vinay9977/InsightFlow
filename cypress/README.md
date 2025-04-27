# Cypress Tests for InsightFlow

This directory contains Cypress tests for the InsightFlow application. Currently, it includes tests for:

## Authentication Tests
- Sign up
- Login
- Logout
- Invalid login handling

## Survey Management Tests
- Survey creation (requires admin access)
- Adding different question types
- Test survey cleanup and deletion

## Running the Tests

### Prerequisites

1. Make sure you have Node.js and npm installed
2. Ensure the Django development server is running on port 8000
3. Make sure all dependencies are installed
4. Ensure the admin user exists with username 'admin' and password 'admin'

### Installation

If you haven't already, install the Cypress dependencies:

```bash
npm install
```

### Running Tests

There are several ways to run the tests:

#### Headless Mode (Command Line)

```bash
npx cypress run
```

#### Interactive Mode (Cypress Test Runner)

```bash
npx cypress open
```

This will open the Cypress Test Runner where you can select which tests to run.

### Test Structure

- `e2e/auth.cy.js` - Authentication tests
- `e2e/survey.cy.js` - Survey management tests

### Custom Commands

We've defined several custom commands to make writing tests easier:

- `cy.login(email, password)` - Logs in a user
- `cy.signup(firstName, lastName, email, password)` - Signs up a new user
- `cy.logout()` - Logs out the currently logged in user
- `cy.openSidebar()` - Opens the sidebar navigation panel
- `cy.adminLogin(username, password)` - Logs in to the admin panel
- `cy.createSurvey(name, description, options)` - Creates a new survey with the given parameters

## Adding More Tests

When adding more tests, consider:

1. Creating custom commands for common actions
2. Organizing tests into logical groups
3. Using descriptive test and assertion names
4. Generating unique data for test users to avoid conflicts

## Configuration

The configuration for Cypress is in `cypress.config.js` at the root of the project. It includes:

- Base URL (pointing to the Django development server)
- Viewport size settings
- Any other custom configuration 