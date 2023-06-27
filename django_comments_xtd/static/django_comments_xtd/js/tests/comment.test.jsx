import React from 'react';
import { render, screen } from '@testing-library/react';

import {
  reduce_flags,
  Comment,
  UserPart,
  TopRightPart
} from "../src/comment.jsx";


// --------------------------------------------------------------------
// Test function reduce_flags.

describe("Test reduce_flags function", () => {
  it("receives an empty array", () => {
    const result = reduce_flags([], "");
    const expected = {
      like: { is_active: false, users: [] },
      dislike: { is_active: false, users: [] },
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
      like: { is_active: true, users: ['1:admin'] },
      dislike: { is_active: false, users: [] },
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
      like: { is_active: false, users: ['2:fulanito'] },
      dislike: { is_active: false, users: [] },
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
      like: { is_active: false, users: [] },
      dislike: { is_active: true, users: ['1:admin'] },
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
      like: { is_active: false, users: [] },
      dislike: { is_active: false, users: ['2:fulanito'] },
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
      like: { is_active: false, users: [] },
      dislike: { is_active: false, users: [] },
      removal: { is_active: true, count: 1 }
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
    const { debug } =
    render(
      <TopRightPart
        allowFlagging={false}
        canModerate={true}
        commentId={1}
        deleteUrl="/delete"
        flagUrl="/flag"
        isAuthenticated={false}
        isRemoved={false}
        loginUrl="/login"
        removal={false}
        removalCount={27}
      />
    );
    debug();

    const removal_count = screen.queryByText("27");
    expect(removal_count).toBeNull();

    const i_flagged_it = screen.queryByText("I flagged it as inappropriate");
    expect(i_flagged_it).toBeNull();

    const flag_comment = screen.queryByTitle("flag comment as inappropriate");
    expect(flag_comment).toBeNull();

    const remove_comment = screen.queryByTitle("remove comment");
    expect(remove_comment).toBeNull();
  });
});