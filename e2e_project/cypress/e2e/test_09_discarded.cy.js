describe("Test /09-def-dark--discarded", () => {
  beforeEach(() => {
    cy.visit("/09-def-dark--discarded");
  });

  it("displays messages indicating that the comment is discarded", () => {
    cy.get("main div.container h1")
      .should("have.text", "Comment automatically discarded");

    cy.get("main div.container p")
      .should(
        "have.text",
        "Sorry, your comment has been automatically discarded."
      );
  });

  it("display the comment that has been discarded", () => {
    cy.djcx.testDefCommentBox("main div.central-column > div.djcx");
  });
});
