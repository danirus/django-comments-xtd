describe("Test /07-def-dark--reply-ii", () => {

  beforeEach(() => {
    cy.visit("/07-def-dark--reply-ii");
  });

  // ---------------------------------------------------
  // The next 4 test cases are copy-pasted from test_06.

  it("contains a 'span.vline' vertical line", () => {
    cy.get("div.djcx div.cmthread")
      .should("have.class", "cmthread--narrow", "cmthread--l0");

    cy.get("div.djcx div.cmthread > *")
      .should("have.length", 2);

    cy.get("div.djcx div.cmthread > *:first-child")
      .should("have.class", "vline");
  });

  it("contains a 'thread-group' with the comment", () => {
    // The comment receiving the reply.
    cy.get("div.djcx div.cmthread div.thread-group")
      .get("div.comment-box")
      .get("div.comment")
      .should("have.class", "comment--in-thread");
  });

  it("contains a 'thread-group' with a 'reply-box' and a 'hline-l0'", () => {
    // The reply form.
    cy.get("div.djcx div.cmthread  div.thread-group")
      .get("div.reply-box > div")
      .should("have.length", 2);

    cy.get("div.djcx div.cmthread div.thread-group")
      .get("div.reply-box > div:first-child")
      .should("have.class", "hline-l0");
  });

  it("contains a 'thread-group', a 'reply-box' and the 'reply-form'", () => {
    cy.get("div.djcx div.thread-group")
      .get("div.reply-box")
      .get("div.content")
      .get("section.reply-form form")
      .should("have.attr", "method", "POST")
      .should("have.attr", "autocomplete", "off")
      .should("have.attr", "action", "/comments/post/");
  });

  // ---------------------------------------------------
  // This test is the only new test case in this module.

  it("contains an 'active-reactions' div", () => {
    // The feedback div.
    cy.get("div.djcx div.thread-group")
      .get("div.comment-box")
      .get("div.comment")
      .get("div.feedback")
      .should("have.class", "feedback-bordered");

    // The feedback div must have two children:
    // * the reactions already selected by users, and
    // * the link to allow a user to react.

    // This is the reactions already selected.
    cy.get("div.djcx div.thread-group")
      .get("div.comment-box")
      .get("div.comment")
      .get("div.feedback")
      .get("div.active-reactions")
      .should("be.visible");
  });

  it("contains 5 finger-up reactions", () => {
    cy.get("div.djcx div.thread-group")
      .get("div.comment-box")
      .get("div.comment")
      .get("div.feedback")
      .get("div.active-reactions")
      .get("div.reaction:first-child span.smaller")
      .should("have.text", "5");

    cy.get("div.djcx div.thread-group")
      .get("div.comment-box")
      .get("div.comment")
      .get("div.feedback")
      .get("div.active-reactions")
      .get("div.reaction:first-child span.emoji")
      .should("have.text", "👍");

    cy.get("div.djcx div.thread-group")
      .get("div.comment-box")
      .get("div.comment")
      .get("div.feedback")
      .get("div.active-reactions")
      .get("div.reaction:first-child > div")
      .should("have.class", "tooltip");
  });

  it("contains 2 heart reactions", () => {
    cy.get("div.djcx div.thread-group")
      .get("div.comment-box")
      .get("div.comment")
      .get("div.feedback")
      .get("div.active-reactions")
      .get("div.reaction:last-child span.smaller")
      .should("have.text", "2");

    cy.get("div.djcx div.thread-group")
      .get("div.comment-box")
      .get("div.comment")
      .get("div.feedback")
      .get("div.active-reactions")
      .get("div.reaction:last-child span.emoji")
      .should("have.text", "❤️");

    cy.get("div.djcx div.thread-group")
      .get("div.comment-box")
      .get("div.comment")
      .get("div.feedback")
      .get("div.active-reactions")
      .get("div.reaction:last-child > div")
      .should("have.class", "tooltip");
  });
});
