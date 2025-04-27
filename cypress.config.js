const { defineConfig } = require("cypress");

module.exports = defineConfig({
  e2e: {
    setupNodeEvents(on, config) {
      // implement node event listeners here
      
      // Create a shared variable to store survey data between tests
      let sharedData = {
        createdSurvey: null
      };
      
      // Register tasks to set and get shared data
      on('task', {
        setCreatedSurvey({ name, description }) {
          sharedData.createdSurvey = { name, description };
          return null;
        },
        getCreatedSurvey() {
          return sharedData.createdSurvey || {};
        }
      });
    },
    baseUrl: 'http://localhost:8000',
    viewportWidth: 1280,
    viewportHeight: 720
  },
});
