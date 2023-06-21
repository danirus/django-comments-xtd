function create_tree(cids, data) {
  console.log()
  const tree = new Array();
  const corder = new Array();
  const comments = {};
  const children = {};
  let in_cids = [], cur_cids = [], new_cids = [];

  function get_children(cid) {
    return children[cid].map(index => {
      if (comments[index].children === undefined) {
        comments[index].children = get_children(index);
      }
      return comments[index];
    });
  }

  for (const item of data) {
    in_cids.push(item.id);
    comments[item.id] = item;
    if (item.level === 0) {
      corder.push(item.id);
    }
    children[item.id] = [];
    if (item.parent_id !== item.id) {
      children[item.parent_id].push(item.id);
    }
  }

  for (const id of corder) {
    comments[id].children = get_children(id);
    tree.push(comments[id]);
  }

  if (in_cids.length > 0) {
    if (cids.length > 0) {
      for (const id of in_cids) {
        if (cids.includes(id)) {
          new_cids.push(id);
        }
        cur_cids.push(id);
      }
    } else {
      cur_cids = in_cids;
      new_cids = [];
    }
  }

  return {
    tree,
    cids: cur_cids,
    newcids: new_cids,
    counter: cur_cids.length
  }
}

export function reducer(state, action) {
  switch (action.type) {
    case 'CREATE_TREE': {
      return {
        ...state,
        ...create_tree(state.cids, action.data)
      }
    }
    case 'UPDATE_COUNTER': {
      return {
        ...state,
        counter: action.counter,
      }
    }
    default: {
      return state;
    }
  }
}
