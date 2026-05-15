describe("Test /16-def-dark--comment-published-js", () => {

  beforeEach(() => {
    cy.visit("/16-def-dark--comment-published-js");
    // Requires login. Then it redirects to the target URL.
    cy.get("form [name='email']").type("isabel.azul@example.com");
    cy.get("form [name='password']").type("isabel.azul");
    cy.get("form [name='remember']").check();
    cy.get("form [name='submit']").click();
  });

  it("has a form without fields nor buttons", () => {
    cy.get(".comment-form form input").should("have.length", 0);
    cy.get(".comment-form form textarea").should("have.length", 0);
    cy.get(".comment-form form button").should("have.length", 0);
  });

  it('displays expected header, alert-info and text', () => {
    cy.get(".comment-form h5")
      .should('have.text', 'Post your comment');

    cy.get(".comment-form > form > div > div")
      .should("have.class", "alert", "alert-success", "text-center")
      .should("contain", "Comment published");

    cy.get(".comment-form > form > div > p")
      .should("have.class", "text-center")
      .should("contain", "Thank you for taking the time to participate!")
      .should("contain", "Follow the link to your comment.")

    cy.get(".comment-form > form > div > p > a")
      .should("have.text", "comment")
      .and("have.attr", "href")
      .and("include", "/comments/cr/17/8/");
  });
});
