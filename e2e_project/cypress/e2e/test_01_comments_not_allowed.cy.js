describe('Test /01-def-dark--comments-not-allowed', () => {
  beforeEach(() => {
    cy.visit('/01-def-dark--comments-not-allowed');
  });

  it('displays "New comments are not allowed"', () => {
    cy.contains('New comments are not allowed.');
  });
});
