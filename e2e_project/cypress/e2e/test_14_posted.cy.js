describe('Test /14-def-dark--posted', () => {
  beforeEach(() => {
    cy.visit('/14-def-dark--posted');
  });

  it('displays expected headers and text', () => {
    cy.get("div.intro h2")
      .should('have.text', 'Comment confirmation requested');

    cy.get("div.intro p.big")
      .should(
        "contain",
        "A confirmation message has been sent to your email address."
        + " Please, click on the link in the"
        + " message to confirm your comment."
      );

    cy.get("div.intro p:last-child")
      .should("contain", "Go back to: Article One with Comments-L0");

    cy.get("div.intro p:last-child a")
      .should(
        "have.attr", "href", "/article-comments-l0/article-one-comments-l0/"
      )
      .should("have.text", "Article One with Comments-L0");
  });
});
