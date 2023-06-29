import React from 'react';
import { fireEvent, render, screen } from '@testing-library/react';

import {
  reduce_flags,
  Comment,
  FeedbackPart,
  ReplyFormPart,
  UserPart,
  TopRightPart
} from "../src/comment.jsx";


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
// Test Comment component.

const comment_data_1 = {
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

const onCommentCreate = () => {};

describe("Test <Comment /> with comment_data_1", () => {
  // Renders a comment:
  //  * Without flags
  //  * Without children
  //  * Without user URL
  //  * Without user moderator
  //  * Without allow reply
  it("Renders 1 comment based on comment_data_1", () => {
    render(
      <Comment
        data={comment_data_1}
        onCommentCreated={onCommentCreate}
      />
    );

    const username = screen.getByText(/daniela/i);
    expect(username).toBeInTheDocument();
  });
});

// --------------------------------------------------------------------
// Test UserPart component.

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
    const like_link = container.querySelector("i[hand-thumbs-up]");
    expect(like_link).toBeNull();
    const dislike_link = container.querySelector("i[hand-thumbs-down]");
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

  it("Shows clickable reply link with correct URL", () => {
    const replyClickHandler = jest.fn();

    const { container } = render(
      <ReplyFormPart
        allowFeedback={false}
        commentId={1}
        level={0}
        maxThreadLevel={1}
        onCommentCreated={() => {}}
        onReplyClick={() => replyClickHandler()}
        replyFormVisible={false}
        replyUrl="/reply/0"
      />
    );

    const reply_link = container.querySelector("a");
    expect(reply_link).toBeInTheDocument();

    const url = reply_link.getAttribute("href");
    expect(url).toEqual("/reply/1");

    fireEvent.click(reply_link);
    expect(replyClickHandler).toHaveBeenCalled();

    expect(container.firstChild.tagName).toEqual("A");
  });

  it("Shows clickable reply link with correct URL prefixed with &bull", () => {
    const replyClickHandler = jest.fn();

    const { container } = render(
      <ReplyFormPart
        allowFeedback={true}
        commentId={1}
        level={0}
        maxThreadLevel={1}
        onCommentCreated={() => {}}
        onReplyClick={() => replyClickHandler()}
        replyFormVisible={false}
        replyUrl="/reply/0"
      />
    );

    const reply_link = container.querySelector("a");
    expect(reply_link).toBeInTheDocument();

    const url = reply_link.getAttribute("href");
    expect(url).toEqual("/reply/1");

    fireEvent.click(reply_link);
    expect(replyClickHandler).toHaveBeenCalled();

    expect(container.firstChild.tagName).toEqual("SPAN");
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
