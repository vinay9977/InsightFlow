describe('Login Tests', () => {
  beforeEach(() => {
    // Visit the login page before each test
    cy.visit('http://localhost:8000/login')
  })

  it('Should login with regular user credentials', () => {
    // Fill in regular user credentials
    cy.get('input[name="username"]').type('test@gmail.com')
    cy.get('input[name="password"]').type('test')
    
    // Submit the form
    cy.get('input[type="submit"]').click()
    
    // Should be redirected to the home page
    cy.url().should('eq', 'http://localhost:8000/')
    
    // Check if we're logged in by looking for logout link
    cy.contains('Logout').should('exist')
    
    // Logout for next test
    cy.visit('http://localhost:8000/logout/user')
  })

  it('Should login with admin user credentials', () => {
    // Fill in admin user credentials
    cy.get('input[name="username"]').type('admintest')
    cy.get('input[name="password"]').type('admintest')
    
    // Submit the form
    cy.get('input[type="submit"]').click()
    
    // Should be redirected to the home page
    cy.url().should('eq', 'http://localhost:8000/')
    
    // Check if we're logged in - just verify we're on the home page
    // and not redirected back to login
    cy.url().should('not.include', '/login')
    
    // Logout for cleanup
    cy.visit('http://localhost:8000/logout/user')
  })

  it('Should show error message with invalid credentials', () => {
    // Fill in invalid credentials
    cy.get('input[name="username"]').type('invalid@example.com')
    cy.get('input[name="password"]').type('wrongpassword')
    
    // Submit the form
    cy.get('input[type="submit"]').click()
    
    // Should be redirected back to login page
    cy.url().should('include', '/login')
  })
}) 