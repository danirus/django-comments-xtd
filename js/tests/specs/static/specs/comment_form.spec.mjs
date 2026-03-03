/* URL: http://localhost:8333/stories/article-26/
 * Loaded in `templates/stories/story_detail.html`.
 */

QUnit.module('On window.djcx.comment_form', hooks => {
  QUnit.test('element with [data-djcx=comment-form] exists', assert => {
    /*
     * The HTML element with the attribute data-djcx="comment-form" has
     * to be created in the template where we use render_xtdcomment_form.
     * See the templates/specs/loggedoutspec_detail.html to find it.
     * File js/src/commenting.js expects [data-djcx=comment-form] to exist.
     */
    assert.notEqual(
      document.querySelector("[data-djcx=comment-form]"),
      null,
      "[data-djcx=comment-form] does exist"
    );
  });

  QUnit.test('window.djcx.comment_form is not null', assert => {
    /*
     * File js/src/commenting.js assigns an instance of CommentForm to
     * globalThis.djcx.comment_form, so it should noy be null.
     */
    assert.notEqual(
      window.djcx.comment_form,
      null,
      "window.djcx.comment_form is not null"
    );
  });
});

QUnit.module("On CommentForm constructor", hooks => {
  hooks.afterEach(function() {
    sinon.restore();
  });

  QUnit.test("form_wrapper_el exists", assert => {
    /*
     * In js/src/commenting.js an instance of the class CommentForm
     * is assigned to globalThis.djcx.comment_form. The attribute
     * form_wrapper_el should match the element with
     * "[data-djcx=comment-form]".
     */
    const expected = document.querySelector("[data-djcx=comment-form]");
    assert.equal(
      expected,
      window.djcx.comment_form.form_wrapper_el,
      "this.form_wrapper_el is the expected element"
    );
  });

  QUnit.test("form_el exists", assert => {
    /*
     * In js/src/commenting.js an instance of the class CommentForm
     * is assigned to globalThis.djcx.comment_form. The attribute
     * form_el should match the form element that is a child element
     * of "[data-djcx=comment-form]".
     */
    const expected = document.querySelector("[data-djcx=comment-form] form");
    assert.equal(
      expected,
      window.djcx.comment_form.form_el,
      "this.form_el is the expected element"
    );
  });

  QUnit.test("post button is of type button", assert => {
    const form = document.querySelector("[data-djcx=comment-form] form");
    const btn = form.elements.post;
    assert.equal(btn.type, "button", "'post' has type 'button'");
  });

  QUnit.test("preview button is of type button", assert => {
    const form = document.querySelector("[data-djcx=comment-form] form");
    const btn = form.elements.preview;
    assert.equal(btn.type, "button", "'preview' has type 'button'");
  });

  QUnit.test("clicking on post calls method post('post')", assert => {
    // Click on the `post` button, but the form does not contain data.
    const spy_post_f = sinon.spy(window.djcx.comment_form, "post");
    const spy_is_valid = sinon.spy(window.djcx.comment_form, "is_valid");
    const post_btn = window.djcx.comment_form.form_el.elements.post;
    post_btn.click();

    assert.true(spy_post_f.calledOnce, "post is called once");
    assert.true(spy_post_f.calledWith("post"), "called with argument 'post'");

    assert.true(spy_is_valid.calledOnce, "is_valid is called once");
    assert.true(
      spy_is_valid.returned(false),
      "is_valid returned false, as fields are empty"
    );
  });

  QUnit.test("clicking on preview calls method post('preview')", assert => {
    // Click on the `post` button, but the form does not contain data.
    const spy_post_f = sinon.spy(window.djcx.comment_form, "post");
    const spy_is_valid = sinon.spy(window.djcx.comment_form, "is_valid");
    const preview_btn = window.djcx.comment_form.form_el.elements.preview;
    preview_btn.click();

    assert.true(spy_post_f.calledOnce, "preview is called once");
    assert.true(
      spy_post_f.calledWith("preview"),
      "called with argument 'preview'"
    );

    assert.true(spy_is_valid.calledOnce, "is_valid is called once");
    assert.true(
      spy_is_valid.returned(false),
      "is_valid returned false, as fields are empty"
    );
  });
});

QUnit.module("On CommentForm.disable_btns", hooks => {
  /*
   * Test the method `disable_btns` of the `CommentForm` class.
   */
  hooks.afterEach(function() {
    sinon.restore();
  });

  QUnit.test("called with `true` disables post and preview", assert => {
    const comment_form = window.djcx.comment_form;
    comment_form.disable_btns(true);
    assert.equal(
      comment_form.form_el.elements.post.disabled, true,
      "CommentForm post button is disabled"
    );
    assert.equal(
      comment_form.form_el.elements.preview.disabled, true,
      "CommentForm preview button is disabled"
    );
  });

  QUnit.test("called with `false` enables post and preview", assert => {
    const comment_form = window.djcx.comment_form;
    comment_form.disable_btns(false);
    assert.equal(
      comment_form.form_el.elements.post.disabled, false,
      "CommentForm post button is not disabled"
    );
    assert.equal(
      comment_form.form_el.elements.preview.disabled, false,
      "CommentForm preview button is not disabled"
    );
  });

  QUnit.test("when disabled, clicking does not call `post`", assert => {
    /*
     * Neither post button nor preview button call the `post` method
     * of the class `CommentForm` when clicked, if we have previously
     * called `disable_btns(true)`.
     */
    const spy_post_f = sinon.spy(window.djcx.comment_form, "post");
    const comment_form = window.djcx.comment_form;
    const post_btn = comment_form.form_el.elements.post;
    comment_form.disable_btns(true);  // Disable post and preview.
    post_btn.click();  // Click on post should not do anything.
    assert.true(spy_post_f.notCalled, "post is not called");

    const preview_btn = comment_form.form_el.elements.preview;
    preview_btn.click();  // Click on post should not do anything.
    assert.true(spy_post_f.notCalled, "post is not called");
  });
});

QUnit.module("On CommentForm.is_valid", hooks => {
  let comment_form;

  hooks.beforeEach(() => {
    /*
     * Empty form fields `comment`, `name` and `email` before every test.
     */
    comment_form = window.djcx.comment_form;
    comment_form.form_el.querySelector("[name=comment]").textContent = "";
    comment_form.form_el.querySelector("[name=name]").value = "";
    comment_form.form_el.querySelector("[name=email]").value = "";
  });

  hooks.afterEach(function() {
    sinon.restore();
  });

  hooks.after(() => {
    /*
     * Just to be sure, empty the fields again after the test group ends.
     */
    comment_form.form_el.querySelector("[name=comment]").textContent = "";
    comment_form.form_el.querySelector("[name=name]").value = "";
    comment_form.form_el.querySelector("[name=email]").value = "";
  });

  QUnit.test("returns false when fields are empty", assert => {
    assert.false(comment_form.is_valid(), "is_valid returned false");
  });
  QUnit.test("returns true when fields have valid content", assert => {
    const { form_el } = comment_form;
    form_el.querySelector("[name=comment]").textContent = "A short comment";
    form_el.querySelector("[name=name]").value = "Fulanito de Tal";
    form_el.querySelector("[name=email]").value = "fulanito@detal.es";
    assert.true(comment_form.is_valid(), "is_valid returned true");
  });

  QUnit.test("returns false when any required field is not valid", assert => {
    /*
     * Required fields are `comment`, `name` and `email`.
     * If `name` is empty, `is_valid` returns `false`.
     */
    const { form_el } = comment_form;
    form_el.querySelector("[name=comment]").textContent = "A short comment";
    form_el.querySelector("[name=email]").value = "fulanito@detal.es";
    assert.false(comment_form.is_valid(), "is_valid returned false");

    // If `comment` is empty, `is_valid` returns `false`.
    form_el.querySelector("[name=name]").textContent = "Fulanito de Tal";
    form_el.querySelector("[name=email]").value = "fulanito@detal.es";
    assert.false(comment_form.is_valid(), "is_valid returned false");

    // If `email` is empty, `is_valid` returns `false`.
    form_el.querySelector("[name=comment]").textContent = "A short comment";
    form_el.querySelector("[name=name]").textContent = "Fulanito de Tal";
    assert.false(comment_form.is_valid(), "is_valid returned false");
  });
});

QUnit.module("On CommentForm.post", hooks => {
  let comment_form;

  hooks.beforeEach(() => {
    /*
     * Feed fields `comment`, `name` and `email` before every test.
     */
    comment_form = window.djcx.comment_form;
    const { form_el } = comment_form;
    form_el.querySelector("[name=comment]").textContent = "The comment";
    form_el.querySelector("[name=name]").value = "Fulanito de Tal";
    form_el.querySelector("[name=email]").value = "fulanito@example.com";
  });

  hooks.afterEach(function() {
    sinon.restore();
  });

  QUnit.test("fetch not called if required field not valid", async (assert) => {
    const spy_is_valid_f = sinon.spy(window.djcx.comment_form, "is_valid");
    const spy_fetch_f = sinon.spy(window, "fetch");

    const { form_el } = comment_form;
    form_el.querySelector("[name=comment]").textContent = "";  // Empty.

    assert.equal(await comment_form.post("post"), null, "post returns null");
    assert.true(spy_is_valid_f.calledOnce, "is_valid has been called");
    assert.true(spy_is_valid_f.returned(false), "is_valid returned false");
    assert.true(spy_fetch_f.notCalled, "fetch has not been called");
  });

  QUnit.test("fetch is called and preview is displayed", async (assert) => {
    /*
     * If button preview is clicked, and the form is valid, fetch will be
     * called. Then, the response will be handled in `handle_response`
     * and [data-djcx=preview] element will be visible.
     */
    const spy_handle_resp_f = sinon.spy(comment_form, "handle_response");
    // Call `post("preview")`.
    // It should return false, to prevent calling form's action.
    assert.false(await comment_form.post("preview"), "post returns false");
    assert.true(spy_handle_resp_f.calledOnce, "handle_response is called");

    const { form_wrapper_el } = comment_form;
    const preview = form_wrapper_el.querySelector("[data-djcx=preview]");
    assert.notEqual(preview, null, "element [data-djcx=preview] exists");
  });

  QUnit.test("fetch is called and comment is sent", async (assert) => {
    /*
     * If button post is clicked, and the form is valid, fetch will be
     * called. Then, the response will be handled in `handle_response`
     * and [data-djcx=preview] element will be visible.
     */
    const spy_handle_resp_f = sinon.spy(comment_form, "handle_response");

    // Call `post("post")`.
    // It should return false, to prevent calling form's action.
    assert.equal(await comment_form.post("post"), false, "post returns false");
    assert.true(spy_handle_resp_f.calledOnce, "handle_response is called");

    const { form_wrapper_el, form_el } = comment_form;
    const preview = form_wrapper_el.querySelector("[data-djcx=preview]");
    assert.equal(preview, null, "element [data-djcx=preview] doesn't exist");
    assert.true(
      form_el.textContent.includes("Comment confirmation requested"),
      "comment form is replaced with a confirmation message"
    );
  });
});
