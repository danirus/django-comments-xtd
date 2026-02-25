/* URL: http://localhost:8333/stories/article-26/
 * Loaded in `templates/stories/story_detail.html`.
 */
import { assert } from "chai";
import { enrichPage } from "../utils.mjs";

describe('HTML page with comment form', function() {
  let page;

  before(async function() {
    page = await browser.newPage();
    await enrichPage(page);
    await page.goto("http://localhost:8333/stories/article-26/");
  });

  after(async function() {
    await page.close();
  });

  it('should have an element with [data-djcx=comment-form]', async () => {
    const selector = "[data-djcx=comment-form]";
    await page.waitForSelector(selector);
    const element = await page.evaluateHandle(_sel => {
      return document.querySelector(_sel);
    }, selector);
    assert.notEqual(element, null, "[data-djcx=comment-form] does exist");
  });

  it('should have a not null window.djcx.comment_form', async () => {
    const selector = "[data-djcx=config]";
    await page.waitForSelector(selector);
    const djcx = await page.evaluate(() => window.djcx);
    assert.notEqual(djcx.comment_form, null, "djcx.comment_form is not null");
  });
});

describe('CommentForm constructor', () => {
  let page;
  let window_djcx;
  let selector;

  before(async function() {
    page = await browser.newPage();
    await enrichPage(page);
    await page.goto("http://localhost:8333/stories/article-26/");
  });

  beforeEach(async () => {
    selector = "[data-djcx=comment-form]";
    await page.waitForSelector(selector);
    window_djcx = await page.evaluate(() => window.djcx);
  });

  after(async function() {
    await page.close();
  });

  it('has a not undefined `form_wrapper_el` attribute', () => {
    assert.notEqual(
      window_djcx.comment_form.form_wrapper_el,
      undefined,
      "window.djcx.comment_form.form_wrapper_el is not undefined"
    );
  });

  it('has a not undefined `form_el` attribute', () => {
    assert.notEqual(
      window_djcx.comment_form.form_el,
      undefined,
      "window.djcx.comment_form.form_el is not undefined"
    );
  });

  it("has changed post's type to 'button'", async () => {
    const btn_type = await page.$eval(selector, elem => {
      const form = elem.querySelector("form");
      return form.elements.post.type;
    });
    assert.equal(btn_type, "button", "'post' has type 'button'");
  });

  it("has changed preview's type to 'button'", async () => {
    const btn_type = await page.$eval(selector, elem => {
      const form = elem.querySelector("form");
      return form.elements.preview.type;
    });
    assert.equal(btn_type, "button", "'preview' has type 'button'");
  });
});

  // QUnit.test("CommentForm's post button click", function(assert) {
  //   // Click on the `post` button, but the form does not contain data.
  //   const spy_post = sinon.spy(window.djcx.comment_form, "post");
  //   const spy_is_valid = sinon.spy(window.djcx.comment_form, "is_valid");
  //   const post_btn = window.djcx.comment_form.form_el.elements.post;
  //   post_btn.click();

  //   assert.true(spy_post.calledOnce, "post is called once");
  //   assert.true(spy_post.calledWith("post"), "called with argument 'post'");

  //   assert.true(spy_is_valid.calledOnce, "is_valid is called once");
  //   assert.true(spy_is_valid.returned(false), "is_valid returned false");
  // });
// });
