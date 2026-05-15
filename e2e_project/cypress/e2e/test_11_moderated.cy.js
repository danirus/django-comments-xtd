describe('Test /11-def-dark--moderated', () => {
  beforeEach(() => {
    cy.visit('/11-def-dark--moderated');
  });

  it('displays expected headers and text', () => {
    cy.get("div.intro h2")
      .should('have.text', 'Comment in moderation');

    cy.get("div.intro p.big")
      .should("contain", "Your comment is in moderation.")
      .should("contain", "It needs to be reviewed before publication.")
      .should("contain", "Thank you for your patience and understanding.");

    cy.get("div.intro > p:last-child")
      .should("contain", "Go back to: One comment, level 0, options off");

    cy.get("div.intro > p:last-child > a")
      .should(
        "have.attr", "href", "/article-comments-l0/one-comment-options-off/"
      )
      .should("have.text", "One comment, level 0, options off");
  });
});
