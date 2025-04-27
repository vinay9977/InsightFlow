describe('Authentication Tests', () => {
  // Generate unique email to avoid conflicts with existing users
  const email = `test${Math.floor(Math.random() * 10000)}@example.com`;
  const password = 'Test1234!'; // Meets complexity requirements
  const firstName = 'Test';
  const lastName = 'User';
  
  beforeEach(() => {
    // Visit the base URL before each test
    cy.visit('/');
  });

  it('should allow a user to sign up', () => {
    // Use custom signup command
    cy.signup(firstName, lastName, email, password);
    
    // After successful signup, we should be redirected to login page
    cy.url().should('include', '/login/');
    
    // Verify the page contains an indication of successful registration
    cy.get('body').should('not.contain', 'Password must include');
    cy.get('body').should('not.contain', 'Email already exists');
  });

  it('should allow a user to log in', () => {
    // Use custom login command
    cy.login(email, password);
    
    // After successful login, we should be redirected to the home page
    cy.url().should('not.include', '/login/');
    
    // Verify we can see the logout link on the page, confirming we're logged in
    cy.get('a[href="/logout/user/"]').should('exist');
  });

  it('should allow a user to log out', () => {
    // First make sure we're logged in
    cy.login(email, password);
    
    // Verify we're logged in by checking for the logout link
    cy.get('a[href="/logout/user/"]').should('exist');
    
    // Use custom logout command
    cy.logout();
    
    // Verify we're now on the login page
    cy.url().should('include', '/login/');
    
    // Verify logout was successful by checking the login form is visible
    cy.get('#username').should('exist');
    cy.get('#password').should('exist');
  });
  
  it('should show error for invalid login', () => {
    // Try to login with invalid credentials
    cy.login('invalid@example.com', 'wrongpassword');
    
    // Verify error message is shown
    cy.contains('Invalid email or password').should('be.visible');
    
    // The application redirects to /auth/ on failed login, not /login/
    cy.url().should('include', '/auth/');
  });
}); 