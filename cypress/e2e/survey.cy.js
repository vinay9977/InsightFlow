describe('Survey Creation Test', () => {
  // Regular user credentials
  const email = `test${Math.floor(Math.random() * 10000)}@example.com`;
  const password = 'Test1234!';
  const firstName = 'Test';
  const lastName = 'User';
  
  // Admin credentials
  const adminUsername = 'admin';
  const adminPassword = 'admin';
  
  // Survey details
  const surveyName = `Test Survey ${Math.floor(Math.random() * 10000)}`;
  const surveyDescription = 'This is a test survey created by Cypress';
  const questionText = 'What is your favorite color?';
  
  // Generate a random color for the answer
  const colors = ['Red', 'Blue', 'Green', 'Yellow', 'Purple', 'Orange', 'Pink', 'Black', 'White', 'Teal'];
  const randomColor = colors[Math.floor(Math.random() * colors.length)];
  
  // Multi-select question details
  const multiSelectQuestion = 'In what programming language is this project written?';
  const multiSelectKey = 'Python';
  const multiSelectHelpText = 'Starts with P';
  const choices = [
    'JavaScript',
    'Python',
    'Java',
    'C++',
    'Ruby'
  ];
  
  before(() => {
    // Create a test user account before running the tests
    cy.signup(firstName, lastName, email, password);
    
    // Store the user credentials for other tests
    cy.task('setCreatedSurvey', { name: null, description: null });
  });
  
  it('should create a new survey and add a text question', () => {
    // Login as regular user
    cy.login(email, password);
    
    // Verify we're logged in by checking for the logout link
    cy.get('a[href="/logout/user/"]').should('exist');
    
    // Open the sidebar using our custom command
    cy.openSidebar();
    
    // Look for the Survey link in the sidebar
    cy.get('#sidebar').contains('Survey').click();
    
    // We should be redirected to admin login
    cy.url().should('include', '/admin/login/');
    
    // Login as admin using our custom command
    cy.adminLogin(adminUsername, adminPassword);
    
    // After admin login, we should be at the survey page
    cy.url().should('include', '/survey/');
    
    // CLEANUP: Delete existing test surveys before creating a new one
    cy.log('Cleaning up existing test surveys...');
    
    // Check if there's a search box available
    cy.get('body').then(($body) => {
      // Try to find a search input
      if ($body.find('input[type="search"]').length > 0) {
        // Clear any existing search and search for test surveys
        cy.get('input[type="search"]').clear().type('Test Survey').type('{enter}');
        cy.wait(1000); // Wait for search results
      } else if ($body.find('input[placeholder*="search"]').length > 0) {
        // Try alternative search input
        cy.get('input[placeholder*="search"]').clear().type('Test Survey').type('{enter}');
        cy.wait(1000); // Wait for search results
      } else if ($body.find('input').length > 0) {
        // Try the first input field that might be a search box
        cy.log('Could not find dedicated search box, trying first input field');
        cy.get('input').first().clear().type('Test Survey').type('{enter}');
        cy.wait(1000); // Wait for search results
      }
    });
    
    // Recursive function to delete test surveys one by one
    const deleteTestSurvey = () => {
      // Check if there are any test surveys
      cy.get('body').then($body => {
        if ($body.find('div:contains("Test Survey")').length > 0) {
          cy.log('Found test survey to delete');
          
          // Get the first survey card
          cy.contains('div', 'Test Survey').first().parents('div').first().then($surveyCard => {
            cy.log('Found survey card, hovering to reveal delete button');
            
            // First trigger hover on the survey card
            cy.wrap($surveyCard).trigger('mouseover');
            
            // Wait a bit for hover effect
            cy.wait(200);
            
            // Instead of using the delete button and modal, extract the delete URL directly
            $surveyCard.find('[data-mdb-object_delete_url]').each((i, el) => {
              const deleteUrl = Cypress.$(el).attr('data-mdb-object_delete_url');
              if (deleteUrl) {
                cy.log(`Found delete URL: ${deleteUrl}`);
                // Visit the delete URL directly
                cy.visit(deleteUrl);
                cy.wait(1000);
                
                // Recursively try to delete the next one
                deleteTestSurvey();
              }
            });
            
            // If we can't find the delete URL attribute, try the traditional approach but simpler
            if (!$surveyCard.find('[data-mdb-object_delete_url]').length) {
              cy.log('Could not find delete URL, trying button click approach');
              // Try to find the delete button
              cy.get('[data-te-target="#modalDelete"]').first().click({force: true});
              
              // Wait for page to reload - we'll just continue whether the modal works or not
              cy.wait(1000);
              
              // Try to just reload the page and check if surveys still exist
              cy.reload();
              cy.wait(1000);
              
              // Recursively check if there are still surveys to delete
              deleteTestSurvey();
            }
          });
        } else {
          cy.log('No more test surveys found to delete');
        }
      });
    };
    
    // Start the recursive deletion process
    deleteTestSurvey();
    
    // Click "Add Survey" button
    cy.contains('Add Survey').click();
    
    // Fill out the survey form manually
    cy.get('input[name="name"]').type(surveyName);
    cy.get('textarea[name="description"]').type(surveyDescription);
    
    // Toggle options
    cy.get('input[name="duplicate_entry"]').check();
    cy.get('input[name="can_anonymous_user"]').check();
    
    // Add success content
    cy.get('textarea[name="success_page_content"]').type('Thank you for completing the survey!');
    
    // Handle start date and end date fields
    const today = new Date();
    const startDate = today.toISOString().slice(0, 16);
    
    const endDate = new Date(today);
    endDate.setDate(endDate.getDate() + 7);
    const formattedEndDate = endDate.toISOString().slice(0, 16);
    
    // Fill in dates
    cy.get('input[name="start_date"]').type(startDate);
    cy.get('input[name="end_date"]').type(formattedEndDate);
    
    // Submit the form
    cy.get('button[type="submit"]').click();
    
    // Wait for form submission and redirect
    cy.wait(1000);
    
    // Verify we're on the survey form page
    cy.url().should('include', '/forms/');
    
    // The page should contain the survey name
    cy.contains(surveyName).should('exist');
    
    // Store the survey details for other tests
    cy.task('setCreatedSurvey', { name: surveyName, description: surveyDescription });
    
    // Add a text question to the survey - Step 1: Click add question button
    cy.get('[data-te-target="#addQuestion"]').click();
    
    // Wait for modal to be visible
    cy.get('#addQuestion').should('be.visible');
    
    // Log the modal HTML structure for debugging
    cy.get('#addQuestion').then($modal => {
      cy.log('Modal HTML:');
      cy.log($modal.html());
    });
    
    // Try different selectors for the text question type
    cy.get('#addQuestion').within(() => {
      // Look for any links inside the modal and log them
      cy.get('a').then($links => {
        cy.log(`Found ${$links.length} links in the modal`);
        $links.each((index, link) => {
          cy.log(`Link ${index}: ${Cypress.$(link).text()} - HTML: ${Cypress.$(link).prop('outerHTML')}`);
        });
      });
      
      // Try clicking the first link in the modal
      cy.get('a').first().click();
    });
    
    // Step 3: Fill in the question form
    cy.get('input[name="label"]').type(questionText);
    cy.get('input[name="key"]').type(`${randomColor}`);
    cy.get('input[name="help_text"]').type(`It has to be ${randomColor}`);
    cy.get('input[name="required"]').check();
    
    // Step 4: Submit the question form
    cy.get('button[type="submit"]').click();
    
    // Step 5: Verify the question was added
    cy.contains(questionText).should('exist');
    
    // Now add a multi-select question
    // Step 1: Click add question button again
    cy.get('[data-te-target="#addQuestion"]').click();
    
    // Wait for modal to be visible
    cy.get('#addQuestion').should('be.visible');
    
    // Step 2: Find and click the multi-select option (type_field = 4)
    cy.get('#addQuestion').within(() => {
      // Look for links and find the one for multi-select
      cy.get('a').then($links => {
        // Find multi-select link (should be 5th option, index 4)
        cy.get('a').eq(4).click(); // Multi-select has TYPE_FIELD.multi_select = 4
      });
    });
    
    // Step 3: Fill in the multi-select question form
    cy.get('input[name="label"]').type(multiSelectQuestion);
    cy.get('input[name="key"]').type(multiSelectKey);
    
    // Add the first 3 choices
    cy.get('[name="choices_1"]').type(choices[0]);
    cy.get('[name="choices_2"]').type(choices[1]);
    cy.get('[name="choices_3"]').type(choices[2]);
    
    // Click the button to add more fields
    cy.get('#djf-btn-add-field').click();
    cy.get('#djf-btn-add-field').click();
    
    // Add the remaining 2 choices
    cy.get('[name="choices_4"]').type(choices[3]);
    cy.get('[name="choices_5"]').type(choices[4]);
    
    // Add help text
    cy.get('input[name="help_text"]').type(multiSelectHelpText);
    
    // Make it required
    cy.get('input[name="required"]').check();
    
    // Submit the multi-select question form
    cy.get('button[type="submit"]').click();
    
    // Verify both questions were added successfully
    cy.contains(questionText).should('exist');
    cy.contains(multiSelectQuestion).should('exist');
    
    // Log the survey info for debugging
    cy.log(`Created survey: ${surveyName}`);
    cy.log(`Random color used: ${randomColor}`);
  });
}); 