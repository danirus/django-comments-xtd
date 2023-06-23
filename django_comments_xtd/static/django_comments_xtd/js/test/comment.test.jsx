// import django from 'django';
import React from 'react';
import { expect } from '@wdio/globals';
import { render, screen } from '@testing-library/react';

import { Comment } from "../src/comment.jsx";

import { fn, mock } from '@wdio/browser-runner';

mock('django', () => ({
  default: {
    gettext: fn(),
  }
}));


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

const onCommentCreate = () => {};

describe("Test Comment component", () => {
  it("Renders one comment without children", async () => {
    django.gettext.mockImplementation(arg => arg);
    render(
      <Comment
        data={comment_data}
        onCommentCreated={onCommentCreate}
      />
    );

    const username = screen.getByText(/Daniela/i);
    expect(username).toBeInTheDocument();
  });
});
