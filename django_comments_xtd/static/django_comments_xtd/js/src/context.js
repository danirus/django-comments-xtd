import React from 'react';

export const StateContext = React.createContext({
  state: {
    tree: [],
    cids: [],
    newcids: [],
    counter: 0
  },
  dispath: () => {}
});

export const init_context_default = {
  comment_count: 0,
  allow_comments: false,
  current_user: "",
  request_name: false,
  request_email_address: false,
  is_authenticated: false,
  who_can_post: "",
  allow_flagging: false,
  allow_feedback: false,
  show_feedback: false,
  can_moderate: false,
  polling_interval: 2000,
  feedback_url: "",
  delete_url: "",
  dislike_url: "",
  like_url: "",
  login_url: "",
  reply_url: "",
  flag_url: "",
  list_url: "",
  count_url: "",
  send_url: "",
  preview_url: "",
  default_form: {
    content_type: "",
    object_pk: "",
    timestamp: "",
    security_hash: ""
  },
  default_followup: false,
  html_ud_suffix: "",
  max_thread_level: -1,
  comment_max_length: 3000,
}

export const InitContext = React.createContext(init_context_default);