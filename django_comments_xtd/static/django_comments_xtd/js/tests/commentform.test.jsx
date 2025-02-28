import React from 'react';
import { act } from 'react-dom/test-utils';
import { fireEvent, render, screen } from '@testing-library/react';

import {
  CommentForm,
  FieldIsRequired,
  PreviewComment,
} from "../src/commentform.jsx";
import { InitContext, init_context_default } from '../src/context.js';


// --------------------------------------------------------------------
// Test <FieldIsRequired ... /> component.

describe("Test <FieldIsRequired />", () => {
  it("Renders a <span> with 'This field is required.' text", () => {
    const { container } = render(
      <FieldIsRequired replyTo={0} message={"This field is required."} />
    );

    const span_elem = container.querySelector("span");
    expect(span_elem).toHaveClass("form-text")
    expect(span_elem).toHaveClass("small");
    expect(span_elem).toHaveClass("invalid-feedback");

    const text_elem = screen.getByText("This field is required.");
    expect(text_elem).toBeInTheDocument();
  });

  it("Renders a <span> with a explicit style attribute", () => {
    const { container } = render(
      <FieldIsRequired replyTo={1} message={"This field is required."} />
    );

    const span_elem = container.querySelector("span");
    expect(span_elem).toHaveClass("form-text")
    expect(span_elem).toHaveClass("small");
    expect(span_elem).toHaveClass("invalid-feedback");

    const style_attr = span_elem.getAttribute("style");
    expect(style_attr).toEqual("font-size: 0.71rem;");

    const text_elem = screen.getByText("This field is required.");
    expect(text_elem).toBeInTheDocument();
  });
});


// --------------------------------------------------------------------
// Test <PreviewComment ... /> component.

describe("Test <PreviewComment />", () => {
  it("Renders comment in preview, w/o URL, with replyTo=0", () => {
    const name = "Fulanito de Tal";
    const avatar = "/images/the/avatar.jpg";
    const comment = "This is the comment of Fulanito de Tal";
    const { container } = render(
      <PreviewComment
        avatar={avatar}
        name={name}
        url=""
        comment={comment}
        replyTo={0}
      />
    );

    const h5_elem = container.querySelector("h5");
    expect(h5_elem).toBeInTheDocument();
    expect(h5_elem).toHaveClass("text-center");

    const h5_text = screen.getByText("Your comment in preview");
    expect(h5_text).toBeInTheDocument();

    const image_elem = container.querySelector("img");
    expect(image_elem).toBeInTheDocument();
    const image_src = image_elem.getAttribute("src");
    expect(image_src).toBe(avatar);

    const name_text = screen.getByText(`Now - ${name}`);
    expect(name_text).toBeInTheDocument();

    const content_elem = container.querySelector(".content");
    expect(content_elem).toBeInTheDocument();

    const comment_text = screen.getByText(comment);
    expect(comment_text).toBeInTheDocument();
  });

  it("Renders comment in preview, with URL, with replyTo=1", () => {
    const url = "https://family.detal/fulanito"
    const name = "Fulanito de Tal";
    const avatar = "/images/the/avatar.jpg";
    const comment = "This is the comment of Fulanito de Tal";
    const { container } = render(
      <PreviewComment
        avatar={avatar}
        name={name}
        url={url}
        comment={comment}
        replyTo={1}
      />
    );

    const h5_elem = container.querySelector("h5");
    expect(h5_elem).toBeNull();

    const h5_text = screen.queryByText("Your comment in preview");
    expect(h5_text).toBeNull();

    const image_elem = container.querySelector("img");
    expect(image_elem).toBeInTheDocument();
    const image_src = image_elem.getAttribute("src");
    expect(image_src).toBe(avatar);

    const link_elem = container.querySelector("a");
    expect(link_elem).toBeInTheDocument();
    const link_href = link_elem.getAttribute("href");
    expect(link_href).toBe(url);

    const content_elem = container.querySelector(".content");
    expect(content_elem).toBeInTheDocument();

    const comment_text = screen.getByText(comment);
    expect(comment_text).toBeInTheDocument();
  });

  it("Renders comment with the username given in the InitContext", () => {
    const username = "fulanito";
    const props = {
      ...init_context_default,
      is_authenticated: true,
      current_user: `3:${username}`
    }
    const url = "";  // To make use of name given in context' current_user.
    const name = "Fulanito de Tal";
    const avatar = "/images/the/avatar.jpg";
    const comment = "This is the comment of Fulanito de Tal";

    const { container } = render(
      <InitContext.Provider value={props}>
        <PreviewComment
          avatar={avatar}
          name={name}
          url={url}
          comment={comment}
          replyTo={1}
        />
      </InitContext.Provider>
    );

    const h5_elem = container.querySelector("h5");
    expect(h5_elem).toBeNull();

    const h5_text = screen.queryByText("Your comment in preview");
    expect(h5_text).toBeNull();

    const image_elem = container.querySelector("img");
    expect(image_elem).toBeInTheDocument();
    const image_src = image_elem.getAttribute("src");
    expect(image_src).toBe(avatar);

    const username_text = screen.getByText(`Now - ${username}`);
    expect(username_text).toBeInTheDocument();

    const link_elem = container.querySelector("a");
    expect(link_elem).toBeNull();

    const content_elem = container.querySelector(".content");
    expect(content_elem).toBeInTheDocument();

    const comment_text = screen.getByText(comment);
    expect(comment_text).toBeInTheDocument();
  });
});


// --------------------------------------------------------------------
// Test <CommentForm ... /> component.

describe("Test <CommentForm />", () => {
  let default_form;
  let props;

  beforeEach(() => {
    default_form = {
      content_type: "articles.article",
      object_pk: "1",
      timestamp: "1688391157",
      security_hash: "the-security-hash",
    };
    props = {
      ...init_context_default,
      comment_max_length: 140,
      default_form
    };
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  it("Renders the CommentForm component", () => {
    const commentCreatedHandler = jest.fn();
    const { container } = render(
      <InitContext.Provider value={props}>
        <CommentForm
          replyTo={0}
          onCommentCreated={() => commentCreatedHandler()}
        />
      </InitContext.Provider>
    );

    const h4_text = screen.getByText(/post your comment/i);
    expect(h4_text).toBeInTheDocument();

    const content_type_field = container.querySelector("[name=content_type]");
    expect(content_type_field.value).toEqual(default_form.content_type);
    expect(content_type_field.type).toEqual("hidden");
    const object_pk_field = container.querySelector("[name=object_pk]");
    expect(object_pk_field.value).toEqual(default_form.object_pk);
    expect(object_pk_field.type).toEqual("hidden");
    const timestamp_field = container.querySelector("[name=timestamp]");
    expect(timestamp_field.value).toEqual(default_form.timestamp);
    expect(timestamp_field.type).toEqual("hidden");
    const security_hash_field = container.querySelector("[name=security_hash]");
    expect(security_hash_field.value).toEqual(default_form.security_hash);
    expect(security_hash_field.type).toEqual("hidden");

    const honeypot_field = container.querySelector("[name=honeypot]");
    expect(honeypot_field.value).toEqual("");
    expect(honeypot_field.type).toEqual("text");

    const comment_field = container.querySelector("[name=comment]");
    expect(comment_field.required).toEqual(true);
    expect(comment_field.type).toEqual("textarea");

    const name_field = container.querySelector("[name=name]");
    expect(name_field.required).toEqual(true);
    expect(name_field.type).toEqual("text");

    const email_field = container.querySelector("[name=email]");
    expect(email_field.required).toEqual(true);
    expect(email_field.type).toEqual("text");

    const url_field = container.querySelector("[name=url]");
    expect(url_field.required).toEqual(false);
    expect(url_field.type).toEqual("text");

    const followup_field = container.querySelector("[name=followup]");
    expect(followup_field.required).toEqual(false);
    expect(followup_field.type).toEqual("checkbox");
    expect(followup_field.checked).toEqual(false);
    fireEvent.click(followup_field);
    expect(followup_field.checked).toEqual(true);

    const post_button = container.querySelector("[name=post]");
    expect(post_button).toBeInTheDocument();
    expect(post_button.type).toEqual("submit");

    const preview_button = container.querySelector("[name=preview]");
    expect(preview_button).toBeInTheDocument();
    expect(preview_button.type).toEqual("submit");
  });

  it("Submits with comment field empty does not call fetch", async () => {
    global.fetch = jest.fn();
    const { container } = render(
      <InitContext.Provider value={props}>
        <CommentForm
          replyTo={0}
          onCommentCreated={() => commentCreatedHandler()}
        />
      </InitContext.Provider>
    );

    const comment_field = container.querySelector("[name=comment]");
    fireEvent.change(comment_field, {target: {value: " "}}); // Fails validate.
    const name_field = container.querySelector("[name=name]");
    fireEvent.change(name_field, {target: {value: "Fulanito de Tal"}});
    const email_field = container.querySelector("[name=email]");
    fireEvent.change(email_field, {target: {value: "fulanito@example.com"}});

    const post_button = container.querySelector("[name=post]");
    expect(post_button).toBeInTheDocument();
    await act(async () => {
      fireEvent.click(post_button);
    });

    expect(global.fetch).not.toHaveBeenCalled();
    expect(comment_field).toBeInTheDocument();
    const field_is_required = comment_field.nextSibling;
    expect(field_is_required.nodeName).toEqual("SPAN");
    expect(field_is_required.textContent).toEqual("This field is required.");
  });

  it("Submits with comment field too long displays error", async () => {
    global.fetch = jest.fn();
    const { container } = render(
      <InitContext.Provider value={props}>
        <CommentForm
          replyTo={0}
          onCommentCreated={() => commentCreatedHandler()}
        />
      </InitContext.Provider>
    );

    const long_comment = (
      "Cras faucibus vitae nisi sit amet semper. Aenean varius, neque sit"
      + " amet porta malesuada, odio est laoreet tellus, non fermentum nunc"
      + " ex et est. Sed consequat sit amet turpis ut congue. Aenean"
      + " convallis quis ex a porta."
    );

    const comment_error_msg = (
      `Ensure this value has at most 140 character`
      + ` (it has ${long_comment.length}).`
    );

    const comment_field = container.querySelector("[name=comment]");
    fireEvent.change(comment_field, {target: {value: long_comment}});
    const name_field = container.querySelector("[name=name]");
    fireEvent.change(name_field, {target: {value: "Fulanito de Tal"}});
    const email_field = container.querySelector("[name=email]");
    fireEvent.change(email_field, {target: {value: "fulanito@example.com"}});

    const post_button = container.querySelector("[name=post]");
    expect(post_button).toBeInTheDocument();
    await act(async () => {
      fireEvent.click(post_button);
    });

    expect(global.fetch).not.toHaveBeenCalled();
    expect(comment_field).toBeInTheDocument();
    const field_is_required = comment_field.nextSibling;
    expect(field_is_required.nodeName).toEqual("SPAN");
    expect(field_is_required.textContent).toEqual(comment_error_msg);
  });

  it("Submits with name field empty does not call fetch", async () => {
    global.fetch = jest.fn();
    const { container } = render(
      <InitContext.Provider value={props}>
        <CommentForm
          replyTo={0}
          onCommentCreated={() => commentCreatedHandler()}
        />
      </InitContext.Provider>
    );

    const comment_field = container.querySelector("[name=comment]");
    fireEvent.change(comment_field, {target: {value: "The comment content"}});
    const name_field = container.querySelector("[name=name]");
    fireEvent.change(name_field, {target: {value: " "}}); // Fails validate.
    const email_field = container.querySelector("[name=email]");
    fireEvent.change(email_field, {target: {value: "fulanito@example.com"}});

    const post_button = container.querySelector("[name=post]");
    expect(post_button).toBeInTheDocument();
    await act(async () => {
      fireEvent.click(post_button);
    });

    expect(global.fetch).not.toHaveBeenCalled();
    expect(name_field).toBeInTheDocument();
    const field_is_required = name_field.nextSibling;
    expect(field_is_required.nodeName).toEqual("SPAN");
    expect(field_is_required.textContent).toEqual("This field is required.");
  });

  it("Validates name if is_authenticated but request_name=true", async () => {
    global.fetch = jest.fn();
    const commentCreatedHandler = jest.fn();
    props = {
      ...props,
      is_authenticated: true,
      request_name: true,
    }
    const { container } = render(
      <InitContext.Provider value={props}>
        <CommentForm
          replyTo={0}
          onCommentCreated={() => commentCreatedHandler()}
        />
      </InitContext.Provider>
    );

    const comment_field = container.querySelector("[name=comment]");
    fireEvent.change(comment_field, {target: {value: "The comment content"}});
    const name_field = container.querySelector("[name=name]");
    fireEvent.change(name_field, {target: {value: " "}}); // Fails validate.

    const post_button = container.querySelector("[name=post]");
    expect(post_button).toBeInTheDocument();
    await act(async () => {
      fireEvent.click(post_button);
    });

    expect(global.fetch).not.toHaveBeenCalled();
    expect(name_field).toBeInTheDocument();
    const field_is_required = name_field.nextSibling;
    expect(field_is_required.nodeName).toEqual("SPAN");
    expect(field_is_required.textContent).toEqual("This field is required.");
  });

  it("Submits with invalid email field does not call fetch", async () => {
    global.fetch = jest.fn();
    const { container } = render(
      <InitContext.Provider value={props}>
        <CommentForm
          replyTo={0}
          onCommentCreated={() => commentCreatedHandler()}
        />
      </InitContext.Provider>
    );

    const comment_field = container.querySelector("[name=comment]");
    fireEvent.change(comment_field, {target: {value: "The comment content"}});
    const name_field = container.querySelector("[name=name]");
    fireEvent.change(name_field, {target: {value: "Fulanito de Tal"}});
    const email_field = container.querySelector("[name=email]");
    // The next value for the email field causes validation to fail.
    fireEvent.change(email_field, {target: {value: "fulanito@example"}});

    const post_button = container.querySelector("[name=post]");
    expect(post_button).toBeInTheDocument();
    await act(async () => {
      fireEvent.click(post_button);
    });

    expect(global.fetch).not.toHaveBeenCalled();
    expect(email_field).toBeInTheDocument();
    const field_is_required = email_field.nextSibling;
    expect(field_is_required.nodeName).toEqual("SPAN");
    expect(field_is_required.textContent).toEqual(
      "Required for comment verification.");
  });

  it("Validates email if is_authenticated but request_email=true", async () => {
    global.fetch = jest.fn();
    const commentCreatedHandler = jest.fn();
    props = {
      ...props,
      is_authenticated: true,
      request_email_address: true,
    }
    const { container } = render(
      <InitContext.Provider value={props}>
        <CommentForm
          replyTo={0}
          onCommentCreated={() => commentCreatedHandler()}
        />
      </InitContext.Provider>
    );

    const comment_field = container.querySelector("[name=comment]");
    fireEvent.change(comment_field, {target: {value: "The comment content"}});
    const email_field = container.querySelector("[name=email]");
    // The next value for the email field causes validation to fail.
    fireEvent.change(email_field, {target: {value: "fulanito@example"}});

    const post_button = container.querySelector("[name=post]");
    expect(post_button).toBeInTheDocument();
    await act(async () => {
      fireEvent.click(post_button);
    });

    expect(global.fetch).not.toHaveBeenCalled();
    expect(email_field).toBeInTheDocument();
    const field_is_required = email_field.nextSibling;
    expect(field_is_required.nodeName).toEqual("SPAN");
    expect(field_is_required.textContent).toEqual(
      "Required for comment verification.");
  });

  it("Submits after filling in the form calls fetch", async () => {
    global.fetch = jest.fn().mockImplementation(
      (url, options) => Promise.resolve({
        url,
        status: 201,
        options: { ...options }
      })
    );
    const commentCreatedHandler = jest.fn();
    const { container } = render(
      <InitContext.Provider value={props}>
        <CommentForm
          replyTo={0}
          onCommentCreated={() => commentCreatedHandler()}
        />
      </InitContext.Provider>
    );

    const comment_field = container.querySelector("[name=comment]");
    fireEvent.change(comment_field, {target: {value: "The comment content"}});
    const name_field = container.querySelector("[name=name]");
    fireEvent.change(name_field, {target: {value: "Fulanito de Tal"}});
    const email_field = container.querySelector("[name=email]");
    fireEvent.change(email_field, {target: {value: "fulanito@example.com"}});

    const post_button = container.querySelector("[name=post]");
    expect(post_button).toBeInTheDocument();
    await act(async () => {
      fireEvent.click(post_button);
    });
    expect(global.fetch).toHaveBeenCalled();
    expect(commentCreatedHandler).toHaveBeenCalled();

    // Because the response.status is 201, there
    // is no message to show to the user.
    const alert_elem = container.querySelector(".alert-info");
    expect(alert_elem).toBeNull();
  });

  it("Returns 403 after filling in the form and submitting it", async () => {
    global.fetch = jest.fn().mockImplementation(
      (url, options) => Promise.resolve({
        url,
        status: 403,
        options: { ...options }
      })
    );
    const commentCreatedHandler = jest.fn();
    const { container } = render(
      <InitContext.Provider value={props}>
        <CommentForm
          replyTo={0}
          onCommentCreated={() => commentCreatedHandler()}
        />
      </InitContext.Provider>
    );

    const comment_field = container.querySelector("[name=comment]");
    fireEvent.change(comment_field, {target: {value: "The comment content"}});
    const name_field = container.querySelector("[name=name]");
    fireEvent.change(name_field, {target: {value: "Fulanito de Tal"}});
    const email_field = container.querySelector("[name=email]");
    fireEvent.change(email_field, {target: {value: "fulanito@example.com"}});

    const post_button = container.querySelector("[name=post]");
    expect(post_button).toBeInTheDocument();
    await act(async () => {
      fireEvent.click(post_button);
    });
    expect(global.fetch).toHaveBeenCalled();
    expect(commentCreatedHandler).toHaveBeenCalled();

    // Because the response.status is 403, there
    // is an alert-danger message to show to the user.
    const alert_elem = container.querySelector(".alert-danger");
    expect(alert_elem).toBeInTheDocument();
    expect(alert_elem.textContent).toBe(
      "Sorry, your comment has been rejected."
    );
  });

  it("Previews the comment", async () => {
    global.fetch = jest.fn().mockImplementation(
      (url, _) => Promise.resolve({
        url,
        status: 200,
        json: () => Promise.resolve({ url: "/avatar-image"})
      })
    );
    const { container } = render(
      <InitContext.Provider value={props}>
        <CommentForm
          replyTo={0}
          onCommentCreated={() => {}}
        />
      </InitContext.Provider>
    );

    const comment_field = container.querySelector("[name=comment]");
    fireEvent.change(comment_field, {target: {value: "The comment content"}});
    const name_field = container.querySelector("[name=name]");
    fireEvent.change(name_field, {target: {value: "Fulanito de Tal"}});
    const email_field = container.querySelector("[name=email]");
    fireEvent.change(email_field, {target: {value: "fulanito@example.com"}});

    const preview_button = container.querySelector("[name=preview]");
    expect(preview_button).toBeInTheDocument();
    await act(async () => {
      fireEvent.click(preview_button);
    });
    expect(global.fetch).toHaveBeenCalled();
    const h5_preview_header = container.querySelector("h5.text-center");
    expect(h5_preview_header).toBeInTheDocument();
    expect(h5_preview_header.textContent).toBe("Your comment in preview");
    const img_elem = container.querySelector("img");
    expect(img_elem).toBeInTheDocument();
    expect(img_elem.getAttribute("src")).toEqual("/avatar-image");
  });

  it("Fails to preview due to not valid name field", async () => {
    global.fetch = jest.fn();
    const { container } = render(
      <InitContext.Provider value={props}>
        <CommentForm
          replyTo={0}
          onCommentCreated={() => {}}
        />
      </InitContext.Provider>
    );

    const comment_field = container.querySelector("[name=comment]");
    fireEvent.change(comment_field, {target: {value: "The comment content"}});
    const name_field = container.querySelector("[name=name]");
    fireEvent.change(name_field, {target: {value: "  "}});  // Fails validation.
    const email_field = container.querySelector("[name=email]");
    fireEvent.change(email_field, {target: {value: "fulanito@example.com"}});

    const preview_button = container.querySelector("[name=preview]");
    expect(preview_button).toBeInTheDocument();
    await act(async () => {
      fireEvent.click(preview_button);
    });
    expect(global.fetch).not.toHaveBeenCalled();
    expect(name_field).toBeInTheDocument();
    const field_is_required = name_field.nextSibling;
    expect(field_is_required.nodeName).toEqual("SPAN");
    expect(field_is_required.textContent).toEqual("This field is required.");
  });
});
