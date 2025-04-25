// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************
//
//
// -- This is a parent command --
// Cypress.Commands.add('login', (email, password) => { ... })
//
//
// -- This is a child command --
// Cypress.Commands.add('drag', { prevSubject: 'element'}, (subject, options) => { ... })
//
//
// -- This is a dual command --
// Cypress.Commands.add('dismiss', { prevSubject: 'optional'}, (subject, options) => { ... })
//
//
// -- This will overwrite an existing command --
// Cypress.Commands.overwrite('visit', (originalFn, url, options) => { ... })

// Custom command for logging in
Cypress.Commands.add('login', (email, password) => {
  cy.visit('/login/');
  cy.get('#username').type(email);
  cy.get('#password').type(password);
  cy.get('button[type="submit"]').click();
  // Wait for the request to complete
  cy.wait(500);
});

// Custom command for signing up
Cypress.Commands.add('signup', (firstName, lastName, email, password) => {
  cy.visit('/register/');
  cy.get('#fname').type(firstName);
  cy.get('#lname').type(lastName);
  cy.get('#email').type(email);
  cy.get('#cpass').type(password);
  cy.get('#cnpass').type(password);
  cy.get('button[type="submit"]').click();
  // Wait for the request to complete
  cy.wait(500);
});

// Custom command for logging out
Cypress.Commands.add('logout', () => {
  // Look for the logout link in the top navigation and handle multiple elements
  cy.get('a[href="/logout/user/"]').first().click({ force: true });
  // Wait for the redirect to complete
  cy.wait(500);
  // Verify we're on the login page
  cy.url().should('include', '/login/');
});

// Custom command to open the sidebar
Cypress.Commands.add('openSidebar', () => {
  // Click the toggle button to open the sidebar
  cy.get('#toggle-sidebar-btn').click();
  
  // Wait for the sidebar animation to complete
  cy.wait(500);
  
  // Verify the sidebar is visible
  cy.get('#sidebar').should('be.visible');
});

// Custom command for admin login
Cypress.Commands.add('adminLogin', (username, password) => {
  cy.get('#id_username').type(username);
  cy.get('#id_password').type(password);
  
  // The admin login page uses an input type="submit" instead of a button
  cy.get('input[type="submit"]').click();
  
  // Wait for the request to complete
  cy.wait(500);
});

// Custom command for creating a survey
Cypress.Commands.add('createSurvey', (surveyName, surveyDescription, options = {}) => {
  // Navigate to the create survey page
  cy.contains('Add Survey').click();
  
  // Fill out the required survey form fields
  cy.get('input[name="name"]').type(surveyName);
  cy.get('textarea[name="description"]').type(surveyDescription);
  
  // Set optional fields if provided
  if (options.duplicateEntry) {
    cy.get('input[name="duplicate_entry"]').check();
  }
  
  if (options.anonymousUser) {
    cy.get('input[name="can_anonymous_user"]').check();
  }
  
  // Handle notification email using a different approach
  // The actual field might be a custom widget or a div with editable content
  const notificationEmail = options.notificationEmail || 'notify@example.com';
  
  // Look for possible selectors for the notification email field
  cy.get('body').then($body => {
    // Try to find the widget that might be responsible for the email input
    if ($body.find('.choices__input').length > 0) {
      // If it's using Choices.js
      cy.get('.choices__input').type(notificationEmail + '{enter}');
    } else if ($body.find('[contenteditable="true"]').length > 0) {
      // If it's using a contenteditable element
      cy.get('[contenteditable="true"]').type(notificationEmail);
    } else if ($body.find('.token-input').length > 0) {
      // If it's using a token input
      cy.get('.token-input').type(notificationEmail + '{enter}');
    } else {
      // If all else fails, try to set the value directly using jQuery
      cy.get('input[name="notification_to"]').invoke('val', notificationEmail).trigger('change');
    }
  });

  if (options.successContent) {
    cy.get('textarea[name="success_page_content"]').type(options.successContent);
  }
  
  // Handle start date and end date fields (datetime-local inputs)
  const todayDate = new Date();
  
  // Format start date (today)
  const startDate = todayDate.toISOString().slice(0, 16);
  
  // Format end date (7 days from today)
  const endDate = new Date(todayDate);
  endDate.setDate(endDate.getDate() + 7);
  const formattedEndDate = endDate.toISOString().slice(0, 16);
  
  // Fill in dates
  cy.get('input[name="start_date"]').type(startDate);
  cy.get('input[name="end_date"]').type(formattedEndDate);
  
  // Submit the form
  cy.get('button[type="submit"]').click();
  
  // Wait for the submit to complete and redirect
  cy.wait(1000);
  
  // Verify we're on the survey form page
  cy.url().should('include', '/forms/');
  
  // The page should contain the survey name
  cy.contains(surveyName).should('exist');
  
  // Store the survey name in the Cypress environment
  Cypress.env('currentSurveyName', surveyName);
});

// Custom command to get the latest created survey name
Cypress.Commands.add('getLatestSurveyName', () => {
  return Cypress.env('currentSurveyName');
});