describe("Test /08-def-dark--bad-form", () => {
  // This page submits the form via javascript, and should return
  // a HTTP 400 error. Cypress does not check that, but the result
  // displayed by the 400 error.

  beforeEach(() => {
    cy.visit("/08-def-dark--bad-form");
  });

  it("contains h6 saying that an errors has happened", () => {
    cy.get(".comment-form form > div.col1-2 > h6", {timeout: 1000})
      .should("have.class", "text-center")
      .should("contain", "An error has happened.");
  });

  it("contains alert on comment security verification", () => {
    cy.get(".comment-form form > div.col1-2 > div", {timeout: 1000})
      .should("have.class", "alert", "alert-error", "text-center")
      .should("contain", "The comment form failed security verification");
  });

  it("has a form without fields", () => {
    cy.get(".comment-form form", {timeout: 1000})
      .get("input")
      .should("have.length", 0);

    cy.get(".comment-form form", {timeout: 1000})
      .get("textare")
      .should("have.length", 0);
  });
});
