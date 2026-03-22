describe('Example Test', () => {
    before(() => {
        // either run cy.migrate() or cy.refreshDatabase().
        // it depends on your case
        cy.migrate();
        cy.refreshDatabase();

        // create a user
        // cy.createUser({username: "django-user", password: "123456789"});
    })

    it('shows "New comments are not allowed"', () => {
        cy.visit('/def-dark--comments-not-allowed');

        cy.contains('New comments are not allowed.');
    });
});
