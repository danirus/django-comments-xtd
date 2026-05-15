cy.djcx = {
  testDefCommentBox: (div_djcx_selector) => {
    /*
     * Test that there is a comment-box as defined in the following
     * templates:
     *  - django_comments_xtd/templates/comments/flag.html
     *  - django_comments_xtd/templates/comments/reply.html
     */
    cy.log(`djcx.testDefCommentBox (start): ${div_djcx_selector}`);

    cy.get(`${div_djcx_selector} > div`)
      .should("have.class", "comment-box");

    // It has a <div class="comment">[...]</div>
    cy.get(`${div_djcx_selector} > div.comment-box > div`)
      .should("have.class", "comment");

    // The <div class="comment">[...]</div> has 3 direct children.
    cy.get(`${div_djcx_selector} > div.comment-box`)
      .get("div.comment > div")
      .should("have.length", 3);

    // The 1st direct children of the div.comment is the div.header.
    cy.get(`${div_djcx_selector} > div.comment-box`)
      .get("div.comment > div:nth-child(1)")
      .should("have.class", "header");

    // The 2nd direct children of the div.comment is the div.body.
    cy.get(`${div_djcx_selector} > div.comment-box`)
      .get("div.comment > div:nth-child(2)")
      .should("have.class", "body", "body-bordered");

    // The 3rd direct children of the div.comment is the div.feedback.
    cy.get(`${div_djcx_selector} > div.comment-box`)
      .get("div.comment > div:nth-child(3)")
      .should("have.class", "feedback", "feedback-bordered");

    cy.log(`djcx.testDefCommentBox (end): ${div_djcx_selector}`);
  }
}
