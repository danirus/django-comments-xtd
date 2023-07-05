import React, { useReducer } from 'react';
import { act } from 'react-dom/test-utils';
import { fireEvent, render, screen } from '@testing-library/react';

import { reducer } from '../src/reducer.js';
import {
  init_context_default,
  InitContext,
  StateContext,
} from '../src/context.js';
import {
  reduce_flags,
  Comment,
  FeedbackPart,
  ReplyFormPart,
  UserPart,
  TopRightPart,
  CommentBodyPart
} from "../src/comment.jsx";


const initial_state = {
  tree: [],
  cids: new Set(),
  newcids: new Set(),
  counter: 1
};

// --------------------------------------------------------------------
// Test function reduce_flags.

describe("Test reduce_flags function", () => {
  it("receives an empty array", () => {
    const result = reduce_flags([], "");
    const expected = {
      like: [],
      dislike: [],
      removal: { is_active: false, count: 0 }
    }

    expect(result).toEqual(expected);
  });

  it("receives a like flag from the actual current_user", () => {
    const incoming_flags = [
      { flag: "like", user: "admin", id: 1 },
    ]
    const result = reduce_flags(incoming_flags, "1:admin");
    const expected = {
      like: ['1:admin'],
      dislike: [],
      removal: { is_active: false, count: 0 }
    }

    expect(result).toEqual(expected);
  });

  it("receives a like flag not from the actual current_user", () => {
    const incoming_flags = [
      { flag: "like", user: "fulanito", id: 2 },
    ]
    const result = reduce_flags(incoming_flags, "1:admin");
    const expected = {
      like: ['2:fulanito'],
      dislike: [],
      removal: { is_active: false, count: 0 }
    }

    expect(result).toEqual(expected);
  });

  it("receives a dislike flag from the actual current_user", () => {
    const incoming_flags = [
      { flag: "dislike", user: "admin", id: 1 },
    ]
    const result = reduce_flags(incoming_flags, "1:admin");
    const expected = {
      like: [],
      dislike: ['1:admin'],
      removal: { is_active: false, count: 0 }
    }

    expect(result).toEqual(expected);
  });

  it("receives a dislike flag not from the actual current_user", () => {
    const incoming_flags = [
      { flag: "dislike", user: "fulanito", id: 2 },
    ]
    const result = reduce_flags(incoming_flags, "1:admin");
    const expected = {
      like: [],
      dislike: ['2:fulanito'],
      removal: { is_active: false, count: 0 }
    }

    expect(result).toEqual(expected);
  });

  it("receives a removal flag from the actual current_user", () => {
    const incoming_flags = [
      { flag: "removal", user: "admin", id: 1 },
    ]
    const result = reduce_flags(incoming_flags, "1:admin");
    const expected = {
      like: [],
      dislike: [],
      removal: { is_active: true, count: 1 }
    }

    expect(result).toEqual(expected);
  });

  it("receives a removal flag from a different current_user", () => {
    const incoming_flags = [
      { flag: "removal", user: "eva", id: 2 },
    ]
    const result = reduce_flags(incoming_flags, "1:admin");
    const expected = {
      like: [],
      dislike: [],
      removal: { is_active: false, count: 1 }
    }

    expect(result).toEqual(expected);
  });
});


// --------------------------------------------------------------------
// Test <UserPart /> component.

describe("Test <UserPart />", () => {
  it("Shows the username", () => {
    render(
      <UserPart
        userName="Lena Rosenthal"
        userUrl=""
        isRemoved={false}
        userModerator={false}
      />
    );

    const user_link = screen.queryByTitle(/user's link/);
    expect(user_link).toBeNull();

    const username = screen.getByText(/lena rosenthal/i);
    expect(username).toBeInTheDocument();

    const moderator = screen.queryByText(/moderator/i);
    expect(moderator).toBeNull();
  });

  it("Shows that the username is also a moderator", () => {
    render(
      <UserPart
        userName="Lena Rosenthal"
        userUrl=""
        isRemoved={false}
        userModerator={true}
      />
    );

    const user_link = screen.queryByTitle(/user's link/);
    expect(user_link).toBeNull();

    const username = screen.getByText(/lena rosenthal/i);
    expect(username).toBeInTheDocument();

    const moderator = screen.getByText(/moderator/i);
    expect(moderator).toBeInTheDocument();
    expect(moderator).toHaveClass("badge");
  });

  it("Shows the user name as a link", () => {
    render(
      <UserPart
        userName="Lena Rosenthal"
        userUrl="https://lena.rosenthal.page"
        isRemoved={false}
        userModerator={false}
      />
    );

    const user_link = screen.getByTitle(/user's link/i);
    expect(user_link).toBeInTheDocument();
    expect(user_link).toHaveClass("text-decoration-none");

    const username = screen.getByText(/lena rosenthal/i);
    expect(username).toBeInTheDocument();

    const moderator = screen.queryByText(/moderator/i);
    expect(moderator).toBeNull();
  });

  it("Shows the name and moderator label when comment is removed", () => {
    render(
      <UserPart
        userName="Lena Rosenthal"
        userUrl="https://lena.rosenthal.page"
        isRemoved={true}
        userModerator={true}
      />
    );

    const user_link = screen.queryByTitle(/user's link/);
    expect(user_link).toBeNull();

    const username = screen.getByText(/lena rosenthal/i);
    expect(username).toBeInTheDocument();

    const moderator = screen.getByText(/moderator/i);
    expect(moderator).toBeInTheDocument();
  });
});

// --------------------------------------------------------------------
// Test TopRightPart component.

describe("Test <TopRightPart />", () => {
  it("Shows nothing if !isAuthenticated and !allowFlagging", () => {
    render(
      <TopRightPart
        allowFlagging={false}
        canModerate={false}
        commentId={1}
        deleteUrl="/delete/0"
        flagUrl="/flag/0"
        isAuthenticated={false}
        isRemoved={false}
        loginUrl="/login"
        userRequestedRemoval={false}
        removalCount={27}
      />
    );

    const removal_count = screen.queryByText("27");
    expect(removal_count).toBeNull();

    const i_flagged_it = screen.queryByText("I flagged it as inappropriate");
    expect(i_flagged_it).toBeNull();

    const flag_comment = screen.queryByTitle("flag comment as inappropriate");
    expect(flag_comment).toBeNull();

    const remove_comment = screen.queryByTitle("remove comment");
    expect(remove_comment).toBeNull();
  });

  it("Shows 'flag comment as inappropriate' with login URL", () => {
    const { container } = render(
      <TopRightPart
        allowFlagging={true}  // This makes the 'flag comment...' to appear.
        canModerate={false}
        commentId={1}
        deleteUrl="/delete/0"
        flagUrl="/flag/0"
        isAuthenticated={false}
        isRemoved={false}
        loginUrl="/login"
        userRequestedRemoval={false}
        removalCount={27}
      />
    );

    const removal_count = screen.queryByText("27");
    expect(removal_count).toBeNull();

    const i_flagged_it = screen.queryByText("I flagged it as inappropriate");
    expect(i_flagged_it).toBeNull();

    const flag_comment = screen.queryByTitle("flag comment as inappropriate");
    expect(flag_comment).toBeInTheDocument();

    // Find the link and check the url.
    const link = container.querySelector('a.text-decoration-none');
    expect(link).not.toBeNull();
    expect(link.getAttribute("href")).toEqual("/login?next=/flag/1")

    const remove_comment = screen.queryByTitle("remove comment");
    expect(remove_comment).toBeNull();
  });

  it("Shows how many users have flagged the comment", () => {
    const { container } = render(
      <TopRightPart
        allowFlagging={true}  // This makes the 'flag comment...' to appear.
        canModerate={true}  // Required to show how many flags have received.
        commentId={1}
        deleteUrl="/delete/0"
        flagUrl="/flag/0"
        isAuthenticated={true}  // Req. to show how many flags have received.
        isRemoved={false}
        loginUrl="/login"
        userRequestedRemoval={false}
        removalCount={27}
      />
    );

    const removal_count = screen.queryByText("27");
    expect(removal_count).toBeInTheDocument();

    const i_flagged_it = screen.queryByText("I flagged it as inappropriate");
    expect(i_flagged_it).toBeNull();

    const flag_link = container.querySelector('a[href="/flag/1"]');
    const flag_icon = flag_link.firstChild;
    expect(flag_icon.getAttribute("title")).toEqual(
      "flag comment as inappropriate");
    expect(flag_link).toBeInTheDocument();

    const delete_link = container.querySelector('a[href="/delete/1"]');
    const delete_icon = delete_link.firstChild;
    expect(delete_icon.getAttribute("title")).toEqual("remove comment");
    expect(delete_link).toBeInTheDocument();
  });

  it("Shows flag in text-danger as user request removal", () => {
    render(
      <TopRightPart
        allowFlagging={true}
        canModerate={false}
        commentId={1}
        deleteUrl="/delete/0"
        flagUrl="/flag/0"
        isAuthenticated={false}
        isRemoved={false}
        loginUrl="/login"
        userRequestedRemoval={true}
        removalCount={27}
      />
    );

    const removal_count = screen.queryByText("27");
    expect(removal_count).toBeNull();

    const i_flagged_it = screen.getByTitle("I flagged it as inappropriate");
    expect(i_flagged_it).toBeInTheDocument();
  });

  it("Shows nothing if it isRemoved", () => {
    const { container } = render(
      <TopRightPart
        allowFlagging={true}
        canModerate={true}
        commentId={1}
        deleteUrl="/delete/0"
        flagUrl="/flag/0"
        isAuthenticated={true}
        isRemoved={true}
        loginUrl="/login"
        userRequestedRemoval={true}
        removalCount={27}
      />
    );

    expect(container.firstChild).toBeNull();
  });
});


// --------------------------------------------------------------------
// Test FeedbackPart component.

describe("Test <FeedbackPart />", () => {
  it("Shows nothing if !allowFeedback", () => {
    const { container } = render(
      <FeedbackPart
        allowFeedback={false}  // Only with this to false it won't render.
        commentId={1}
        currentUser={"1:admin"}
        onLikeClicked={() => {}}
        onDislikeClicked={() => {}}
        showFeedback={false}
        userLikeList={[]}
        userDislikeList={[]}
      />
    );

    expect(container.firstChild).toBeNull();
    const like_link = container.querySelector("i.bi-hand-thumbs-up");
    expect(like_link).toBeNull();
    const dislike_link = container.querySelector("i.bi-hand-thumbs-down");
    expect(dislike_link).toBeNull();
  });

  it("Does not show users who liked/disliked, as showFeedback=false", () => {
    const { container } = render(
      <FeedbackPart
        allowFeedback={true}
        commentId={1}
        currentUser={"1:admin"}
        onLikeClicked={() => {}}
        onDislikeClicked={() => {}}
        showFeedback={false}
        userLikeList={[]}
        userDislikeList={[]}
      />
    );

    const tooltips = container.querySelectorAll("a[data-bs-toggle='tooltip']");
    expect(tooltips.length).toEqual(0);
  });

  it("Shows users who liked/disliked, as showFeedback=true", () => {
    const { container } = render(
      <FeedbackPart
        allowFeedback={true}
        commentId={1}
        currentUser={"1:admin"}
        onLikeClicked={() => {}}
        onDislikeClicked={() => {}}
        showFeedback={true}
        userLikeList={["2:eva"]}
        userDislikeList={["3:laura"]}
      />
    );

    const tooltips = container.querySelectorAll("a[data-bs-toggle='tooltip']");
    expect(tooltips.length).toEqual(2);
  });

  it("Shows a different icon when currentUser is in userLikeList", () => {
    const { container } = render(
      <FeedbackPart
        allowFeedback={true}
        commentId={1}
        currentUser={"1:admin"}
        onLikeClicked={() => {}}
        onDislikeClicked={() => {}}
        showFeedback={true}
        userLikeList={["1:admin", "2:eva"]}
        userDislikeList={["3:laura"]}
      />
    );

    const tooltips = container.querySelectorAll("a[data-bs-toggle='tooltip']");
    expect(tooltips.length).toEqual(2);

    const like_link = container.querySelector("i.bi-hand-thumbs-up-fill");
    expect(like_link).toBeInTheDocument();
  });

  it("Has two clickable like and dislike links", () => {
    const likeHandler = jest.fn();
    const dislikeHandler = jest.fn();

    const { container } = render(
      <FeedbackPart
        allowFeedback={true}
        commentId={1}
        currentUser={"1:admin"}
        onLikeClicked={() => likeHandler()}
        onDislikeClicked={() => dislikeHandler()}
        showFeedback={false}
        userLikeList={[]}
        userDislikeList={[]}
      />
    );

    const like_link = container.querySelector("i.bi-hand-thumbs-up");
    const dislike_link = container.querySelector("i.bi-hand-thumbs-down");
    expect(like_link).toBeInTheDocument();
    expect(dislike_link).toBeInTheDocument();

    expect(likeHandler).not.toHaveBeenCalled();
    expect(dislikeHandler).not.toHaveBeenCalled();

    fireEvent.click(like_link);
    expect(likeHandler).toHaveBeenCalled();
    fireEvent.click(dislike_link);
    expect(dislikeHandler).toHaveBeenCalled();
  });
});


// --------------------------------------------------------------------
// Test ReplyLinkPart component.

describe("Test <ReplyFormPart />", () => {
  it("Shows nothing if level >= maxThreadLevel", () => {
    const { container } = render(
      <ReplyFormPart
        allowFeedback={false}
        commentId={1}
        level={0}
        maxThreadLevel={0}
        onCommentCreated={() => {}}
        onReplyClick={() => {}}
        replyFormVisible={false}
        replyUrl="/reply/0"
      />
    );

    expect(container.firstChild).toBeNull();
  });

  it("Shows the reply comment form", () => {
    const { container } = render(
      <ReplyFormPart
        allowFeedback={true}
        commentId={1}
        level={0}
        maxThreadLevel={1}
        onCommentCreated={() => {}}
        onReplyClick={() => {}}
        replyFormVisible={true}
        replyUrl="/reply/0"
      />
    );

    const form = container.querySelector("form");
    expect(form).toBeInTheDocument();
  });
});


// --------------------------------------------------------------------
// Test CommentBodyPart component.

describe("Test <CommentBodyPart />", () => {
  it("Shows comment wrapped in <em> when the isRemoved", () => {
    const { container } = render(
      <CommentBodyPart
        allowFeedback={false}
        comment="This comment has been removed."
        isRemoved={true}
      />
    );

    const em_elem = container.querySelector("em");
    expect(em_elem).toBeInTheDocument();
    const comment = screen.getByText("This comment has been removed.");
    expect(comment).toBeInTheDocument();
  });

  it("Shows comment not wrapped in <em> when isRemoved is false", () => {
    const { container } = render(
      <CommentBodyPart
        allowFeedback={true}
        comment="This comment has NOT been removed."
        isRemoved={false}
      />
    );

    const em_elem = container.querySelector("em");
    expect(em_elem).toBeNull();
    const comment = screen.getByText("This comment has NOT been removed.");
    expect(comment).toBeInTheDocument();
  });
});


// --------------------------------------------------------------------
// Test Comment component.

const comment_data = {
  "id": 1,
  "user_name": "Daniela",
  "user_url": "",
  "user_moderator": false,
  "user_avatar": ("//www.gravatar.com/avatar/" +
    "7736a08481eef8523e806cc98ea36192?s=48&d=identicon"),
  "permalink": "/comments/cr/12/2/#c1",
  "comment": "The comment",
  "submit_date": "June 23, 2023, 7:53 a.m.",
  "parent_id": 1,
  "level": 0,
  "is_removed": false,
  "allow_reply": true,
  "flags": [],
  "children": []
}


describe("Test <Comment /> with comment_data", () => {
  afterEach(() => {
    jest.restoreAllMocks();
  });

  it("Renders 1 comment based on comment_data", () => {
    // Renders a comment:
    //  * Without flags
    //  * Without children
    //  * Without user URL
    //  * Without user moderator
    //  * Without allow reply
    const TestComp = () => {
      const [ state, dispatch ] = useReducer(reducer, initial_state);
      return (
        <StateContext.Provider value={{ state, dispatch }}>
          <InitContext.Provider value={init_context_default}>
            <Comment
              data={comment_data}
              onCommentCreated={() => {}}
            />
          </InitContext.Provider>
        </StateContext.Provider>
      );
    }

    render(<TestComp />);

    const username = screen.getByText(/daniela/i);
    expect(username).toBeInTheDocument();
  });

  it("Tests that handle_reply_link redirects to login", async () => {
    if (window.location)
      delete window.location;
    window.location = {};
    const set_href = jest.fn(href => href);
    Object.defineProperty(window.location, 'href', {
      set: set_href
    });
    const props = {
      ...init_context_default,
      is_authenticated: false,
      max_thread_level: 2,  // It has to be > level given in comment_data.
      who_can_post: "users",
    }

    const TestComp = () => {
      const [ state, dispatch ] = useReducer(reducer, initial_state);
      return (
        <StateContext.Provider value={{ state, dispatch }}>
          <InitContext.Provider value={props}>
            <Comment
              data={comment_data}
              onCommentCreated={() => commentCreatedHandler()}
            />
          </InitContext.Provider>
        </StateContext.Provider>
      );
    }
    render(<TestComp />);

    const reply_link = screen.getByText(/reply/i);
    expect(reply_link).toBeInTheDocument();
    await act(async () => {
      fireEvent.click(reply_link);
    });

    expect(set_href).toHaveBeenCalled();
  });

  it("Tests that handle_comment_created is called", async () => {
    /*
     * This test renders a comment with a 'reply' link that when
     * clicked displays a reply form. After submitting the reply form
     * it checks that Comment's component handle_comment_created
     * function is called.
     */
    global.fetch = jest.fn().mockImplementation(
      (url, options) => Promise.resolve({
        url,
        status: 201,
        options: { ...options }
      })
    );
    const commentCreatedHandler = jest.fn();
    const props = {
      ...init_context_default,
      max_thread_level: 2  // It has to be > level given in comment_data.
    }

    const TestComp = () => {
      const [ state, dispatch ] = useReducer(reducer, initial_state);
      return (
        <StateContext.Provider value={{ state, dispatch }}>
          <InitContext.Provider value={props}>
            <Comment
              data={comment_data}
              onCommentCreated={() => commentCreatedHandler()}
            />
          </InitContext.Provider>
        </StateContext.Provider>
      );
    }
    const { container } = render(<TestComp />);

    const reply_link = screen.getByText(/reply/i);
    expect(reply_link).toBeInTheDocument();
    await act(async () => {
      fireEvent.click(reply_link);
    });

    // Fill the form.
    const comment_field = container.querySelector("[name=comment]");
    fireEvent.change(comment_field, {target: {value: "Fulanito de Tal"}});
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
  });

  it("Tests that handle_comment_created is called (part II)", async () => {
    /*
     * This test renders a comment with a 'reply' link that when
     * clicked displays a reply form. After submitting the reply form
     * it checks that Comment's component handle_comment_created
     * function is called. The difference with the previous test
     * is that this one passes is_authenticated as true, so the
     * reply form doesn't render the name and email fields.
     */
    global.fetch = jest.fn().mockImplementation(
      (url, options) => Promise.resolve({
        url,
        status: 201,
        options: { ...options }
      })
    );
    const commentCreatedHandler = jest.fn();
    const props = {
      ...init_context_default,
      is_authenticated: true,
      max_thread_level: 2  // It has to be > level given in comment_data.
    }

    const TestComp = () => {
      const [ state, dispatch ] = useReducer(reducer, initial_state);
      return (
        <StateContext.Provider value={{ state, dispatch }}>
          <InitContext.Provider value={props}>
            <Comment
              data={comment_data}
              onCommentCreated={() => commentCreatedHandler()}
            />
          </InitContext.Provider>
        </StateContext.Provider>
      );
    }

    const { container } = render(<TestComp />);

    const reply_link = screen.getByText(/reply/i);
    expect(reply_link).toBeInTheDocument();
    await act(async () => {
      fireEvent.click(reply_link);
    });

    // Fill the form.
    const comment_field = container.querySelector("[name=comment]");
    fireEvent.change(comment_field, {target: {value: "Fulanito de Tal"}});

    const post_button = container.querySelector("[name=post]");
    expect(post_button).toBeInTheDocument();

    await act(async () => {
      fireEvent.click(post_button);
    });
    expect(global.fetch).toHaveBeenCalled();
    expect(commentCreatedHandler).toHaveBeenCalled();
  });

  it("Tests that action_like calls post_feedback with 201", async () => {
    global.fetch = jest.fn().mockImplementation(
      (url, options) => Promise.resolve({
        url,
        status: 201,
        options: { ...options }
      })
    );
    const props = {
      ...init_context_default,
      is_authenticated: true,
      allow_feedback: true,
      show_feedback: true
    }

    const TestComp = () => {
      const [ state, dispatch ] = useReducer(reducer, initial_state);
      return (
        <StateContext.Provider value={{ state, dispatch }}>
          <InitContext.Provider value={props}>
            <Comment
              data={comment_data}
              onCommentCreated={() => {}}
            />
          </InitContext.Provider>
        </StateContext.Provider>
      );
    }

    const { container } = render(<TestComp />);

    const like_link = container.querySelector("i.bi-hand-thumbs-up");
    expect(like_link).toBeInTheDocument();

    const own_like_link_1 = container.querySelector("i.bi-hand-thumbs-up-fill");
    expect(own_like_link_1).toBeNull();

    await act(async () => {
      fireEvent.click(like_link);
    });

    expect(global.fetch).toHaveBeenCalled();
    const own_like_link_2 = container.querySelector("i.bi-hand-thumbs-up-fill");
    expect(own_like_link_2).toBeInTheDocument();
  });

  it("Tests that action_like calls post_feedback with 204", async () => {
    global.fetch = jest.fn().mockImplementation(
      (url, options) => Promise.resolve({
        url,
        status: 204,
        options: { ...options }
      })
    );
    const props = {
      ...init_context_default,
      is_authenticated: true,
      current_user: "1:admin",
      allow_feedback: true,
      show_feedback: true
    }
    const comment_data_xtd = {
      ...comment_data,
      flags: [{id: 1, user: "admin", flag: "like"}]
    }

    const TestComp = () => {
      const [ state, dispatch ] = useReducer(reducer, initial_state);
      return (
        <StateContext.Provider value={{ state, dispatch }}>
          <InitContext.Provider value={props}>
            <Comment
              data={comment_data_xtd}
              onCommentCreated={() => {}}
            />
          </InitContext.Provider>
        </StateContext.Provider>
      );
    }

    const { container } = render(<TestComp />);

    let own_like_link = container.querySelector("i.bi-hand-thumbs-up-fill");
    expect(own_like_link).toBeInTheDocument();

    await act(async () => {
      fireEvent.click(own_like_link);
    });

    expect(global.fetch).toHaveBeenCalled();
    own_like_link = container.querySelector("i.bi-hand-thumbs-up-fill");
    expect(own_like_link).toBeNull();

    let like_link = container.querySelector("i.bi-hand-thumbs-up");
    expect(like_link).toBeInTheDocument();
  });

  it("Tests that action_dislike calls post_feedback with 201", async () => {
    global.fetch = jest.fn().mockImplementation(
      (url, options) => Promise.resolve({
        url,
        status: 201,
        options: { ...options }
      })
    );
    const props = {
      ...init_context_default,
      is_authenticated: true,
      allow_feedback: true,
      show_feedback: true
    }

    const TestComp = () => {
      const [ state, dispatch ] = useReducer(reducer, initial_state);
      return (
        <StateContext.Provider value={{ state, dispatch }}>
          <InitContext.Provider value={props}>
            <Comment
              data={comment_data}
              onCommentCreated={() => {}}
            />
          </InitContext.Provider>
        </StateContext.Provider>
      );
    }

    const { container } = render(<TestComp />);

    const dislike_link = container.querySelector("i.bi-hand-thumbs-down");
    expect(dislike_link).toBeInTheDocument();

    const own_dislike_1 = container.querySelector("i.bi-hand-thumbs-down-fill");
    expect(own_dislike_1).toBeNull();

    await act(async () => {
      fireEvent.click(dislike_link);
    });

    expect(global.fetch).toHaveBeenCalled();
    const own_dislike_2 = container.querySelector("i.bi-hand-thumbs-down-fill");
    expect(own_dislike_2).toBeInTheDocument();
  });

  it("Tests that action_dislike calls post_feedback with 204", async () => {
    global.fetch = jest.fn().mockImplementation(
      (url, options) => Promise.resolve({
        url,
        status: 204,
        options: { ...options }
      })
    );
    const props = {
      ...init_context_default,
      is_authenticated: true,
      current_user: "1:admin",
      allow_feedback: true,
      show_feedback: true
    }
    const comment_data_xtd = {
      ...comment_data,
      flags: [{id: 1, user: "admin", flag: "dislike"}]
    }

    const TestComp = () => {
      const [ state, dispatch ] = useReducer(reducer, initial_state);
      return (
        <StateContext.Provider value={{ state, dispatch }}>
          <InitContext.Provider value={props}>
            <Comment
              data={comment_data_xtd}
              onCommentCreated={() => commentCreatedHandler()}
            />
          </InitContext.Provider>
        </StateContext.Provider>
      );
    }

    const { container } = render(<TestComp />);

    let own_dislike = container.querySelector("i.bi-hand-thumbs-down-fill");
    expect(own_dislike).toBeInTheDocument();

    await act(async () => {
      fireEvent.click(own_dislike);
    });

    expect(global.fetch).toHaveBeenCalled();
    own_dislike = container.querySelector("i.bi-hand-thumbs-down-fill");
    expect(own_dislike).toBeNull();

    let dislike_link = container.querySelector("i.bi-hand-thumbs-down");
    expect(dislike_link).toBeInTheDocument();
  });

  it("Tests that action_like triggers window.location.href", async () => {
    if (window.location)
      delete window.location;
    window.location = {};
    let redirect_to = "";
    const set_href = jest.fn(href => redirect_to = href);
    Object.defineProperty(window.location, 'href', {
      set: set_href
    });
    const props = {
      ...init_context_default,
      is_authenticated: false,
      allow_feedback: true,
      show_feedback: true,
      login_url: "/login",
      like_url: "/like/0"
    }

    const TestComp = () => {
      const [ state, dispatch ] = useReducer(reducer, initial_state);
      return (
        <StateContext.Provider value={{ state, dispatch }}>
          <InitContext.Provider value={props}>
            <Comment
              data={comment_data}
              onCommentCreated={() => {}}
            />
          </InitContext.Provider>
        </StateContext.Provider>
      );
    }

    const { container } = render(<TestComp />);

    const like_link = container.querySelector("i.bi-hand-thumbs-up");
    expect(like_link).toBeInTheDocument();

    await act(async () => {
      fireEvent.click(like_link);
    });

    expect(set_href).toHaveBeenCalled();
    expect(redirect_to).toBe("/login?next=/like/1");
  });

  it("Tests that action_dislike triggers window.location.href", async () => {
    if (window.location)
      delete window.location;
    window.location = {};
    let redirect_to = "";
    const set_href = jest.fn(href => redirect_to = href);
    Object.defineProperty(window.location, 'href', {
      set: set_href
    });
    const props = {
      ...init_context_default,
      is_authenticated: false,
      allow_feedback: true,
      show_feedback: true,
      login_url: "/login",
      dislike_url: "/dislike/0"
    }
    const TestComp = () => {
      const [ state, dispatch ] = useReducer(reducer, initial_state);
      return (
        <StateContext.Provider value={{ state, dispatch }}>
          <InitContext.Provider value={props}>
            <Comment
              data={comment_data}
              onCommentCreated={() => {}}
            />
          </InitContext.Provider>
        </StateContext.Provider>
      );
    }
    const { container } = render(<TestComp />);

    const dislike_link = container.querySelector("i.bi-hand-thumbs-down");
    expect(dislike_link).toBeInTheDocument();

    await act(async () => {
      fireEvent.click(dislike_link);
    });

    expect(set_href).toHaveBeenCalled();
    expect(redirect_to).toBe("/login?next=/dislike/1");
  });
});
