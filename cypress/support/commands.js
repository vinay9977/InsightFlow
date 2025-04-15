// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************

// Login command for regular user
Cypress.Commands.add('loginAsUser', () => {
  cy.visit('/login')
  cy.get('input[name="username"]').type('test@gmail.com')
  cy.get('input[name="password"]').type('test')
  cy.get('input[type="submit"]').click()
})

// Login command for admin user
Cypress.Commands.add('loginAsAdmin', () => {
  cy.visit('/login')
  cy.get('input[name="username"]').type('admintest')
  cy.get('input[name="password"]').type('admintest')
  cy.get('input[type="submit"]').click()
})

// Logout command
Cypress.Commands.add('logout', () => {
  cy.visit('/logout/user')
}) 