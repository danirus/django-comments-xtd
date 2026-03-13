describe('Example Test', () => {
    before(() => {
        // either run cy.migrate() or cy.refreshDatabase().
        // it depends on your case
        cy.migrate();
        cy.refreshDatabase();

        // create a user
        // cy.createUser({username: "django-user", password: "123456789"});
    })

    it('shows a homepage', () => {
        cy.visit('/');

        cy.contains('js-tests');
    });
});