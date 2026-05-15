describe('Test /13-def-dark--muted', () => {
  beforeEach(() => {
    cy.visit('/13-def-dark--muted');
  });

  it('displays expected headers and text', () => {
    cy.get("div.intro h2")
      .should('have.text', 'Comment thread has been muted');

    cy.get("div.intro p.big")
      .should(
        "contain",
        "You will no longer receive email"
        + " notifications for comments sent to"
      );

    cy.get("div.intro p.big > a")
      .should(
        "have.attr", "href", "/article-comments-l0/one-comment-options-off/"
      )
      .should("have.text", "One comment, level 0, options off");
  });
});
