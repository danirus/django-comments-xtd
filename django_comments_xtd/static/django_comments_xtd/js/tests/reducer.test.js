import { create_tree, reducer } from "../src/reducer.js";

const data_test_1 = [
  {
    id: 9,
    user_name: "Administrator",
    user_url: "",
    user_moderator: true,
    user_avatar: "//avatar/e64c7d89f26bd1972efa854d13d7dd61",
    permalink: "/comments/cr/12/2/#c9",
    comment: "This is comment 9.",
    submit_date: "July 5, 2023, 7:59 a.m.",
    parent_id: 9,
    level: 0,
    is_removed: false,
    allow_reply: true,
    flags: [],
    children: [
      {
        id: 10,
        user_name: "Administrator",
        user_url: "",
        user_moderator: true,
        user_avatar: "//avatar/e64c7d89f26bd1972efa854d13d7dd61",
        permalink: "/comments/cr/12/2/#c10",
        comment: "This is comment 10.",
        submit_date: "July 5, 2023, 7:59 a.m.",
        parent_id: 9,
        level: 1,
        is_removed: false,
        allow_reply: true,
        flags: [],
        children: [],
      },
    ],
  },
  {
    id: 10,
    user_name: "Administrator",
    user_url: "",
    user_moderator: true,
    user_avatar: "//avatar/e64c7d89f26bd1972efa854d13d7dd61",
    permalink: "/comments/cr/12/2/#c10",
    comment: "This is comment 10.",
    submit_date: "July 5, 2023, 7:59 a.m.",
    parent_id: 9,
    level: 1,
    is_removed: false,
    allow_reply: true,
    flags: [],
    children: [],
  },
  {
    id: 3,
    user_name: "Administrator",
    user_url: "",
    user_moderator: true,
    user_avatar: "//avatar/e64c7d89f26bd1972efa854d13d7dd61",
    permalink: "/comments/cr/12/2/#c3",
    comment: "This is comment 3.",
    submit_date: "June 27, 2023, 2:42 p.m.",
    parent_id: 3,
    level: 0,
    is_removed: false,
    allow_reply: true,
    flags: [
      {
        flag: "like",
        user: "admin",
        id: 1,
      },
      {
        flag: "removal",
        user: "fulanito",
        id: 2,
      },
    ],
    children: [
      {
        id: 7,
        user_name: "Administrator",
        user_url: "",
        user_moderator: true,
        user_avatar: "//avatar/e64c7d89f26bd1972efa854d13d7dd61",
        permalink: "/comments/cr/12/2/#c7",
        comment: "This is comment 7.",
        submit_date: "June 29, 2023, 10:33 a.m.",
        parent_id: 3,
        level: 1,
        is_removed: false,
        allow_reply: true,
        flags: [],
        children: [],
      },
      {
        id: 8,
        user_name: "Daniela",
        user_url: "",
        user_moderator: false,
        user_avatar: "//avatar/73ad48eff53c8ac69e33a1c2",
        permalink: "/comments/cr/12/2/#c8",
        comment: "This is comment 8.",
        submit_date: "June 29, 2023, 10:35 a.m.",
        parent_id: 3,
        level: 1,
        is_removed: false,
        allow_reply: true,
        flags: [],
        children: [],
      },
    ],
  },
  {
    id: 7,
    user_name: "Administrator",
    user_url: "",
    user_moderator: true,
    user_avatar: "//avatar/e64c7d89f26bd1972efa854d13d7dd61",
    permalink: "/comments/cr/12/2/#c7",
    comment: "This is comment 7.",
    submit_date: "June 29, 2023, 10:33 a.m.",
    parent_id: 3,
    level: 1,
    is_removed: true,
    allow_reply: true,
    flags: [],
    children: [],
  },
  {
    id: 8,
    user_name: "Daniela",
    user_url: "",
    user_moderator: false,
    user_avatar: "//avatar/73ad48eff53c8ac69e33a1c2",
    permalink: "/comments/cr/12/2/#c8",
    comment: "This is comment 8.",
    submit_date: "June 29, 2023, 10:35 a.m.",
    parent_id: 3,
    level: 1,
    is_removed: false,
    allow_reply: true,
    flags: [],
    children: [],
  },
];

const expected_test_1 = {
  tree: [
    {
      id: 9,
      user_name: "Administrator",
      user_url: "",
      user_moderator: true,
      user_avatar: "//avatar/e64c7d89f26bd1972efa854d13d7dd61",
      permalink: "/comments/cr/12/2/#c9",
      comment: "This is comment 9.",
      submit_date: "July 5, 2023, 7:59 a.m.",
      parent_id: 9,
      level: 0,
      is_removed: false,
      allow_reply: true,
      flags: [],
      children: [
        {
          id: 10,
          user_name: "Administrator",
          user_url: "",
          user_moderator: true,
          user_avatar: "//avatar/e64c7d89f26bd1972efa854d13d7dd61",
          permalink: "/comments/cr/12/2/#c10",
          comment: "This is comment 10.",
          submit_date: "July 5, 2023, 7:59 a.m.",
          parent_id: 9,
          level: 1,
          is_removed: false,
          allow_reply: true,
          flags: [],
          children: [],
        },
      ],
    },
    {
      id: 3,
      user_name: "Administrator",
      user_url: "",
      user_moderator: true,
      user_avatar: "//avatar/e64c7d89f26bd1972efa854d13d7dd61",
      permalink: "/comments/cr/12/2/#c3",
      comment: "This is comment 3.",
      submit_date: "June 27, 2023, 2:42 p.m.",
      parent_id: 3,
      level: 0,
      is_removed: false,
      allow_reply: true,
      flags: [
        {
          flag: "like",
          user: "admin",
          id: 1,
        },
        {
          flag: "removal",
          user: "fulanito",
          id: 2,
        },
      ],
      children: [
        {
          id: 7,
          user_name: "Administrator",
          user_url: "",
          user_moderator: true,
          user_avatar: "//avatar/e64c7d89f26bd1972efa854d13d7dd61",
          permalink: "/comments/cr/12/2/#c7",
          comment: "This is comment 7.",
          submit_date: "June 29, 2023, 10:33 a.m.",
          parent_id: 3,
          level: 1,
          is_removed: true,
          allow_reply: true,
          flags: [],
          children: [],
        },
        {
          id: 8,
          user_name: "Daniela",
          user_url: "",
          user_moderator: false,
          user_avatar: "//avatar/73ad48eff53c8ac69e33a1c2",
          permalink: "/comments/cr/12/2/#c8",
          comment: "This is comment 8.",
          submit_date: "June 29, 2023, 10:35 a.m.",
          parent_id: 3,
          level: 1,
          is_removed: false,
          allow_reply: true,
          flags: [],
          children: [],
        },
      ],
    },
  ],
  cids: new Set([9, 10, 3, 7, 8]),
  newcids: new Set([]),
  counter: 5,
};

const data_test_2 = [
  {
    id: 9,
    user_name: "Administrator",
    user_url: "",
    user_moderator: true,
    user_avatar: "//avatar/e64c7d89f26bd1972efa854d13d7dd61",
    permalink: "/comments/cr/12/2/#c9",
    comment: "This is comment 9.",
    submit_date: "July 5, 2023, 7:59 a.m.",
    parent_id: 9,
    level: 0,
    is_removed: false,
    allow_reply: true,
    flags: [],
    children: [
      {
        id: 10,
        user_name: "Administrator",
        user_url: "",
        user_moderator: true,
        user_avatar: "//avatar/e64c7d89f26bd1972efa854d13d7dd61",
        permalink: "/comments/cr/12/2/#c10",
        comment: "This is comment 10.",
        submit_date: "July 5, 2023, 7:59 a.m.",
        parent_id: 9,
        level: 1,
        is_removed: false,
        allow_reply: true,
        flags: [],
        children: [],
      },
    ],
  },
  {
    id: 10,
    user_name: "Administrator",
    user_url: "",
    user_moderator: true,
    user_avatar: "//avatar/e64c7d89f26bd1972efa854d13d7dd61",
    permalink: "/comments/cr/12/2/#c10",
    comment: "This is comment 10.",
    submit_date: "July 5, 2023, 7:59 a.m.",
    parent_id: 9,
    level: 1,
    is_removed: false,
    allow_reply: true,
    flags: [],
    children: [],
  },
  {
    id: 3,
    user_name: "Administrator",
    user_url: "",
    user_moderator: true,
    user_avatar: "//avatar/e64c7d89f26bd1972efa854d13d7dd61",
    permalink: "/comments/cr/12/2/#c3",
    comment: "This is comment 3.",
    submit_date: "June 27, 2023, 2:42 p.m.",
    parent_id: 3,
    level: 0,
    is_removed: false,
    allow_reply: true,
    flags: [
      {
        flag: "like",
        user: "admin",
        id: 1,
      },
      {
        flag: "removal",
        user: "fulanito",
        id: 2,
      },
    ],
    children: [
      {
        id: 7,
        user_name: "Administrator",
        user_url: "",
        user_moderator: true,
        user_avatar: "//avatar/e64c7d89f26bd1972efa854d13d7dd61",
        permalink: "/comments/cr/12/2/#c7",
        comment: "This is comment 7.",
        submit_date: "June 29, 2023, 10:33 a.m.",
        parent_id: 3,
        level: 1,
        is_removed: true,
        allow_reply: true,
        flags: [],
        children: [],
      },
      {
        id: 8,
        user_name: "Daniela",
        user_url: "",
        user_moderator: false,
        user_avatar: "//avatar/73ad48eff53c8ac69e33a1c2",
        permalink: "/comments/cr/12/2/#c8",
        comment: "This is comment 8.",
        submit_date: "June 29, 2023, 10:35 a.m.",
        parent_id: 3,
        level: 1,
        is_removed: false,
        allow_reply: true,
        flags: [],
        children: [
          {
            id: 11,
            user_name: "Administrator",
            user_url: "",
            user_moderator: true,
            user_avatar: "//avatar/e64c7d89f26bd1972efa854d13d7dd61",
            permalink: "/comments/cr/12/2/#c11",
            comment: "This is comment 11.",
            submit_date: "July 5, 2023, 10:11 a.m.",
            parent_id: 8,
            level: 2,
            is_removed: false,
            allow_reply: false,
            flags: [],
            children: [],
          },
        ],
      },
    ],
  },
  {
    id: 7,
    user_name: "Administrator",
    user_url: "",
    user_moderator: true,
    user_avatar: "//avatar/e64c7d89f26bd1972efa854d13d7dd61",
    permalink: "/comments/cr/12/2/#c7",
    comment: "This is comment 7.",
    submit_date: "June 29, 2023, 10:33 a.m.",
    parent_id: 3,
    level: 1,
    is_removed: true,
    allow_reply: true,
    flags: [],
    children: [],
  },
  {
    id: 8,
    user_name: "Daniela",
    user_url: "",
    user_moderator: false,
    user_avatar: "//avatar/73ad48eff53c8ac69e33a1c2",
    permalink: "/comments/cr/12/2/#c8",
    comment: "This is comment 8.",
    submit_date: "June 29, 2023, 10:35 a.m.",
    parent_id: 3,
    level: 1,
    is_removed: false,
    allow_reply: true,
    flags: [],
    children: [
      {
        id: 11,
        user_name: "Administrator",
        user_url: "",
        user_moderator: true,
        user_avatar: "//avatar/e64c7d89f26bd1972efa854d13d7dd61",
        permalink: "/comments/cr/12/2/#c11",
        comment: "This is comment 11.",
        submit_date: "July 5, 2023, 10:11 a.m.",
        parent_id: 8,
        level: 2,
        is_removed: false,
        allow_reply: false,
        flags: [],
        children: [],
      },
    ],
  },
  {
    id: 11,
    user_name: "Administrator",
    user_url: "",
    user_moderator: true,
    user_avatar: "//avatar/e64c7d89f26bd1972efa854d13d7dd61",
    permalink: "/comments/cr/12/2/#c11",
    comment: "This is comment 11.",
    submit_date: "July 5, 2023, 10:11 a.m.",
    parent_id: 8,
    level: 2,
    is_removed: false,
    allow_reply: false,
    flags: [],
    children: [],
  },
];

const expected_test_2 = {
  tree: [
    {
      id: 9,
      user_name: "Administrator",
      user_url: "",
      user_moderator: true,
      user_avatar: "//avatar/e64c7d89f26bd1972efa854d13d7dd61",
      permalink: "/comments/cr/12/2/#c9",
      comment: "This is comment 9.",
      submit_date: "July 5, 2023, 7:59 a.m.",
      parent_id: 9,
      level: 0,
      is_removed: false,
      allow_reply: true,
      flags: [],
      children: [
        {
          id: 10,
          user_name: "Administrator",
          user_url: "",
          user_moderator: true,
          user_avatar: "//avatar/e64c7d89f26bd1972efa854d13d7dd61",
          permalink: "/comments/cr/12/2/#c10",
          comment: "This is comment 10.",
          submit_date: "July 5, 2023, 7:59 a.m.",
          parent_id: 9,
          level: 1,
          is_removed: false,
          allow_reply: true,
          flags: [],
          children: [],
        },
      ],
    },
    {
      id: 3,
      user_name: "Administrator",
      user_url: "",
      user_moderator: true,
      user_avatar: "//avatar/e64c7d89f26bd1972efa854d13d7dd61",
      permalink: "/comments/cr/12/2/#c3",
      comment: "This is comment 3.",
      submit_date: "June 27, 2023, 2:42 p.m.",
      parent_id: 3,
      level: 0,
      is_removed: false,
      allow_reply: true,
      flags: [
        {
          flag: "like",
          user: "admin",
          id: 1,
        },
        {
          flag: "removal",
          user: "fulanito",
          id: 2,
        },
      ],
      children: [
        {
          id: 7,
          user_name: "Administrator",
          user_url: "",
          user_moderator: true,
          user_avatar: "//avatar/e64c7d89f26bd1972efa854d13d7dd61",
          permalink: "/comments/cr/12/2/#c7",
          comment: "This is comment 7.",
          submit_date: "June 29, 2023, 10:33 a.m.",
          parent_id: 3,
          level: 1,
          is_removed: true,
          allow_reply: true,
          flags: [],
          children: [],
        },
        {
          id: 8,
          user_name: "Daniela",
          user_url: "",
          user_moderator: false,
          user_avatar: "//avatar/73ad48eff53c8ac69e33a1c2",
          permalink: "/comments/cr/12/2/#c8",
          comment: "This is comment 8.",
          submit_date: "June 29, 2023, 10:35 a.m.",
          parent_id: 3,
          level: 1,
          is_removed: false,
          allow_reply: true,
          flags: [],
          children: [
            {
              id: 11,
              user_name: "Administrator",
              user_url: "",
              user_moderator: true,
              user_avatar: "//avatar/e64c7d89f26bd1972efa854d13d7dd61",
              permalink: "/comments/cr/12/2/#c11",
              comment: "This is comment 11.",
              submit_date: "July 5, 2023, 10:11 a.m.",
              parent_id: 8,
              level: 2,
              is_removed: false,
              allow_reply: false,
              flags: [],
              children: [],
            },
          ],
        },
      ],
    },
  ],
  cids: new Set([9, 10, 3, 7, 8, 11]),
  newcids: new Set([11]),
  counter: 6,
};


describe("Test create_tree function", () => {
  it("Receives an empty cids from app state", () => {
    const result = create_tree(new Set(), data_test_1);
    expect(result.tree).toStrictEqual(expected_test_1.tree);
    // Expected is {9, 10, 3, 7, 8}
    expect(result.cids).toStrictEqual(expected_test_1.cids);
    expect(result.newcids).toStrictEqual(expected_test_1.newcids); // []
    expect(result.counter).toBe(expected_test_1.counter); // 5
  });

  it("Receives new data and compares it with cids from app state", () => {
    /*
     * This test starts with the cids produced in the previous test,
     * and receives data that includes a new comment (11) that is a
     * child of comment 8. In such situation, the number 11 should be
     * in newcids, so that it receives the label "new" when displayed.
     */
    const current_cids = new Set([9, 10, 3, 7, 8]);
    const result = create_tree(current_cids, data_test_2);
    expect(result.tree).toStrictEqual(expected_test_2.tree);
    // Expected is {9, 10, 3, 7, 8, 11}
    expect(result.cids).toStrictEqual(expected_test_2.cids);
    expect(result.newcids).toStrictEqual(expected_test_2.newcids); // [11]
    expect(result.counter).toBe(expected_test_2.counter); // 6
  });
});

describe("Test reducer function", () => {
  it("Checks CREATE_TREE action with test_data_1", () => {
    const action = { type: 'CREATE_TREE', data: data_test_1 }
    const prev_state = {
      tree: [],
      cids: new Set(),
      newcids: new Set(),
      counter: 0
    }
    const next_state = reducer(prev_state, action);

    // This are the same expect from the first test in this test module.
    expect(next_state.tree).toStrictEqual(expected_test_1.tree);
    // Expected is {9, 10, 3, 7, 8}
    expect(next_state.cids).toStrictEqual(expected_test_1.cids);
    expect(next_state.newcids).toStrictEqual(expected_test_1.newcids); // []
    expect(next_state.counter).toBe(expected_test_1.counter); // 5
  });

  it("Checks UPDATE_COUNTER action", () => {
    const action = { type: 'UPDATE_COUNTER', counter: 2 }
    const prev_state = {
      tree: [],
      cids: new Set(),
      newcids: new Set(),
      counter: 0
    }
    const next_state = reducer(prev_state, action);

    expect(next_state.tree).toStrictEqual(prev_state.tree);
    expect(next_state.cids).toStrictEqual(prev_state.cids);
    expect(next_state.newcids).toStrictEqual(prev_state.newcids);
    expect(next_state.counter).toBe(2);
  });

  it("Checks default action", () => {
    const prev_state = {
      tree: [],
      cids: new Set(),
      newcids: new Set(),
      counter: 0
    }
    const next_state = reducer(prev_state, {});
    expect(next_state).toStrictEqual(prev_state);
  });
});