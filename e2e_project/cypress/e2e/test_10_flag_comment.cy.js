describe("Test /10-def-dark--flag-comment", () => {

  beforeEach(() => {
    cy.visit("/10-def-dark--flag-comment");
    // Requires login. Then it redirects to the target URL.
    cy.get("form [name='email']").type("isabel.azul@example.com");
    cy.get("form [name='password']").type("isabel.azul");
    cy.get("form [name='remember']").check();
    cy.get("form [name='submit']").click();
  });

  it("displays flag.html headers to flag the comment", () => {
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

  it("displays the comment that is ready to be flagged", () => {
    /*
     * This test is provided via a helper, because it is
     * a test that happens in other e2e use cases.
     */
    // From e2e_project/cypress/support/helpers.
    cy.djcx.testDefCommentBox("main div.central-column > div.djcx");
  });

  it("flag and unflag the comment", () => {
    /*
     * This test flags the comment and then removes the flag.
     */
    // Find the 'flag' button and click on it.
    cy.get("form button[type='submit']")
      .should("have.attr", "value", "flag")
      .should("have.text", "flag")
      .click();

    // After flagging the user is redirected to the URL of
    // the Django object that the comment was posted to.
    console.log("location.pathname:", cy.location("pathname"));
    cy.url().should(
      "contains", "/story-comments-l1/reply-to-comment/#comment-3"
    );

    // Check that there is a div#cm-flags-3 with two divs inside.
    cy.get("#cm-flags-3 > div").should("have.length", 2);

    // Check that inside the 1st ".tip-container"
    // there is a div with a badge a number one.
    cy.get("#cm-flags-3 > div.tip-container:first-child div:first-child")
      .should("have.class", "badge", "badge-red")
      .should("have.text", "1");

    // Check that inside the 1st ".tip-container"
    // there is a div with flag in red.
    cy.get("#cm-flags-3 > div.tip-container:first-child div:last-child")
      .should("have.class", "tooltip")
      .should(
        "have.text", "One user has flagged this comment as inappropriate."
      );

    // Check that the flag is a link to remove the /flag/ url.
    cy.get("#cm-flags-3 > div.tip-container:last-child a")
      .should("have.attr", "data-djcx-action", "flag")
      .should("have.attr", "data-comment", "3")
      .should("have.attr", "href", "/comments/flag/3/#comment-3")
      .should("have.text", "⚑");

    // Check what says the tooltip next to the previous link.
    cy.get("#cm-flags-3 > div.tip-container:last-child div.tooltip")
      .should("have.text", "You have flagged this comment as inappropriate.")

    // Click on the link to go back to the flag url.
    cy.get("#cm-flags-3 > div.tip-container:last-child a").click();

    console.log("location.pathname:", cy.location("pathname"));
    cy.url().should(
      "contains", "/comments/flag/3/#comment-3"
    );

    // Now the header says...
    cy.get("main article > div.container h2")
      .should("have.class", "text-center")
      .should("have.text", "You already flagged this comment.");

    // Find the 'flag' button and click on it.
    cy.get("form button[type='submit']")
      .should("have.attr", "value", "flag")
      .should("have.text", "remove flag")
      .click();
  });
});
