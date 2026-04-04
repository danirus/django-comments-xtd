describe("Test /10-def-dark--flag-comment", () => {

  beforeEach(() => {
    cy.visit("/10-def-dark--flag-comment");
    // Requires login. Then it redirects to the target URL.
    cy.get("form [name='email']").type("isabel.azul@example.com");
    cy.get("form [name='password']").type("isabel.azul");
    cy.get("form [name='remember']").check();
    cy.get("form [name='submit']").click();
  });

  it("displays flag.html headers", () => {
    cy.get("main article > div.container h2")
      .should("have.class", "text-center")
      .should("have.text", "Flag this comment?");

    cy.get("main article > div.container h6")
      .should("have.class", "text-center", "pb24")
      .should("contain", "Comment sent to:");

    cy.get("main article > div.container h6 a")
      .should("have.attr", "href", "/story-comments-l1/reply-to-comment/")
      .should("have.text", "Reply To Comment");
  });

  it("displays the comment that could be flagged", () => {
    // From e2e_project/cypress/support/helpers.
    cy.djcx.testDefCommentBox("main div.central-column > div.djcx");
  });
});
