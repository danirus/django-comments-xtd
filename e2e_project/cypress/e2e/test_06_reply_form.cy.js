describe("Test /06-def-light--reply", () => {

  beforeEach(() => {
    cy.visit("/06-def-light--reply");
  });

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
    cy.get("div.djcx div.cmthread div.thread-group")
      .get("div.reply-box")
      .get("div.content")
      .get("section.reply-form form")
      .should("have.attr", "method", "POST")
      .should("have.attr", "autocomplete", "off")
      .should("have.attr", "action", "/comments/post/");
  });
});
