describe("Test /17-def-dark--react-to-comment", () => {

  beforeEach(() => {
    cy.visit("/17-def-dark--react-to-comment");
    // Requires login. Then it redirects to the target URL.
    cy.get("form [name='email']").type("isabel.azul@example.com");
    cy.get("form [name='password']").type("isabel.azul");
    cy.get("form [name='remember']").check();
    cy.get("form [name='submit']").click();
  });

  it("displays react.html headers to share  the comment", () => {
    cy.get("main article > div.container h2")
      .should("have.class", "text-center")
      .should("have.text", "Give feedback about this comment");

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

  it("does not have the css class 'comment--in-thread'", () => {
    // When displaying the comment in a single page, like it happens
    // when using the flag.html or the react.html templates, the
    // comment is displayed alone, the CSS class 'comment--in-thread'
    // should not be displayed.
    cy.get("main div.central-column > div.djcx > div.comment-box > div")
      .should("not.have.class", "comment--in-thread");
  });

  it("displays two rows of buttons, and a total of 8 buttons", () => {
    cy.get("form > div.buttons-row")
      .should("have.length", 2);

    cy.get("form > div.buttons-row button")
      .should("have.length", 8);

    cy.get("form div.buttons-row").first()
      .find("button:nth-child(3)")
      .should("have.attr", "value", "S")
      .should("contain", "Smile");
  });

  it("can receive the 'smile' reaction and then remove it", () => {
    /*
     * This test clicks on the button "SMILE", checks that the comment
     * displays the "SMILE" feedback, then clicks again on the button
     * "SMILE", and checks that the "SMILE" feedback is not displayed
     * in the comment.
     */
    // Find the 'flag' button and click on it.
    cy.get("form > div.buttons-row").first()
      .find("button:nth-child(3)")
      .should("have.attr", "value", "S")
      .should("contain", "Smile")
      .click();

    // After clicking, the user is redirected to the URL of
    // the Django object that the comment was posted to.
    console.log("location.pathname:", cy.location("pathname"));
    cy.url().should("contains", "/comments/reacted/?c=3");

    // Check that the new page displays the expected
    // headers, and the comment.
    cy.get("body > main > article h2")
      .should("have.class", "text-center")
      .should("contain", "Thanks for taking the time to participate");
    cy.get("body > main > article h6")
      .should("have.class", "text-center", "pb24")
      .should("contain", "Your feedback is already part of the comment.");
    // From e2e_project/cypress/support/helpers.
    cy.djcx.testDefCommentBox("main div.central-column > div.djcx");

    // Check that there is a div#cm-reactions-3 with three divs inside.
    // Each div inside .active-reactions corresponds to a reaction.
    // There were already two (like and heart).
    cy.get("#cm-reactions-3 > div.active-reactions > div")
      .should("have.length", 3);

    // Check that the reaction Smile has a tooltip with the expected text.
    cy.get("#cm-reactions-3 > div.active-reactions")
      .find("div[data-reaction='S'] div.tooltip")
      .should("have.length", "1")
      .should("contain", "Isabel Azul gave a Smile");

    // Check that the reaction Smile has a span.smaller with a text '1'.
    cy.get("#cm-reactions-3 > div.active-reactions div[data-reaction='S']")
      .find("span.smaller")
      .should("contain", "1");

    // Check that the reaction Smile has a span.emoji
    // with the expected emoji.
    cy.get("#cm-reactions-3 > div.active-reactions div[data-reaction='S']")
      .find(" span.emoji")
      .should("contain", "😀");

    // ------------------------------------------
    // Take the feedback back.
    cy.get("a[data-djcx='reactions-panel']").click();

    // After clicking, the user is redirected to the /react/ feedback.
    console.log("location.pathname:", cy.location("pathname"));
    cy.url().should("contains", "/comments/react/3/#");

    // Now there is a P.text-center with a different text.
    cy.get("section.reaction-form > p")
      .should("have.class", "text-center")
      .should(
        "have.text",
        "Pressed buttons correspond to your active reactions to this comment."
      );

    // There is a button with class 'active' corresponding to the
    // Smile reaction.
    cy.get("button.active")
      .should("have.attr", "value", "S")
      .click();

    // After clicking, the user is redirected to the URL of
    // the Django object that the comment was posted to.
    console.log("location.pathname:", cy.location("pathname"));
    cy.url().should("contains", "/comments/reacted/?c=3");

    // Check that there is a div#cm-reactions-3 with 2 divs inside.
    // Each div inside .active-reactions corresponds to a reaction.
    cy.get("#cm-reactions-3 > div.active-reactions > div")
      .should("have.length", 2);
  });
});
