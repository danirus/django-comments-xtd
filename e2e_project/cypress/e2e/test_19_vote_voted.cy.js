describe("Test /19-def-dark--vote-on-comment", () => {

  beforeEach(() => {
    cy.visit("/19-def-dark--vote-on-comment");
    // Requires login. Then it redirects to the target URL.
    cy.get("form [name='email']").type("isabel.azul@example.com");
    cy.get("form [name='password']").type("isabel.azul");
    cy.get("form [name='remember']").check();
    cy.get("form [name='submit']").click();
  });

  it("displays vote.html headers", () => {
    cy.get("main article > div.container h2")
      .should("have.class", "text-center")
      .should("have.text", "Vote on this comment");

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

  it("displays one row of buttons with 2 buttons", () => {
    cy.get("form > div.buttons-row")
      .should("have.length", 1);

    cy.get("form > div.buttons-row button")
      .should("have.length", 2);

    cy.get("form div.buttons-row")
      .find("button:nth-child(1)")
      .should("have.attr", "value", "+")  // +1 vote.
      .should("contain", "+1");

    cy.get("form div.buttons-row")
      .find("button:nth-child(2)")
      .should("have.attr", "value", "-")  // +1 vote.
      .should("contain", "-1");
  });

  it("can receive a positive vote and then remove it", () => {
    /*
     * This test clicks on the button "SMILE", checks that the comment
     * displays the "SMILE" feedback, then clicks again on the button
     * "SMILE", and checks that the "SMILE" feedback is not displayed
     * in the comment.
     */

    // Before starting the process of voting and removing the vote,
    // check that the comment does not have a positive vote from the
    // beginning.
    cy.get("#cm-votes-3 > div.vote").first()
      .find("a")
      .should("have.class", "vote-up")
      .should("have.attr", "title", "Vote up")
      .should("have.attr", "href", "/comments/vote/3/");

    // Find the 'flag' button and click on it.
    cy.get("form > div.buttons-row")
      .find("button:nth-child(1)")
      .should("have.attr", "value", "+")
      .should("contain", "+1")
      .click();

    // After clicking, the user is redirected to the "voted" template.
    console.log("location.pathname:", cy.location("pathname"));
    cy.url().should("contains", "/comments/voted/?c=3");

    // Check that the new page displays the expected
    // headers, and the comment.
    cy.get("body > main > article h2")
      .should("have.class", "text-center")
      .should("contain", "Thanks for taking the time to participate");
    cy.get("body > main > article h6")
      .should("have.class", "text-center", "pb24")
      .should("contain", "Your vote already changed the comment's score.");
    // From e2e_project/cypress/support/helpers.
    cy.djcx.testDefCommentBox("main div.central-column > div.djcx");

    // Check that there is a div#cm-votes-3 with two divs inside with
    // the class 'vote', and a span with class 'vote-score'.
    cy.get("#cm-votes-3 > div.vote")
      .should("have.length", 2);

    // The first 'div.vote' contains a div with class 'vote-up'.
    cy.get("#cm-votes-3 > div.vote").first()
      .find("a")
      .should("have.class", "vote-up")
      .should("have.attr", "title", "Your vote is positive")
      .should("have.attr", "href", "/comments/vote/3/");

    // And a tooltip with "Your vote is positive".
    cy.get("#cm-votes-3 > div.vote").first()
      .find("div")
      .should("have.class", "tooltip")
      .should("contain", "Your vote is positive");

    // The second 'div.vote' contains a div with class 'vote-down'.
    cy.get("#cm-votes-3 > div.vote").last()
      .find("a")
      .should("have.class", "vote-down")
      .should("have.attr", "title", "Vote down")
      .should("have.attr", "href", "/comments/vote/3/");

    // In between the 'div.vote', there is a div.vote-score with the text 1.
    cy.get("#cm-votes-3 > span.vote-score")
      .should("have.text", "1");

    // ------------------------------------------
    // Revert the feedback back.
    cy.get("a[data-djcx-action='vote-up']").click();

    // After clicking, the user is redirected to the /vote/ feedback.
    console.log("location.pathname:", cy.location("pathname"));
    cy.url().should("contains", "/comments/vote/3/");

    // Now there is a P.text-center with a different text.
    cy.get("section.vote-form > p")
      .should("have.class", "text-center")
      .should(
        "have.text",
        "The pressed button corresponds to your current vote to this comment."
      );

    // Click on the button with the attr value equal '+'.
    cy.get("div.buttons-row button:first-child")
      .should("have.attr", "value", "+")
      .click();

    // After clicking, the user is redirected to the 'voted' view.
    console.log("location.pathname:", cy.location("pathname"));
    cy.url().should("contains", "/comments/voted/?c=3");

    // Check that there is a div#cm-votes-3 with a div-score and text 0.
    cy.get("#cm-votes-3 > span.vote-score")
      .should("have.text", 0);

  });
});
