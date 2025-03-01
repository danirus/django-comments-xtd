(function (React, ReactDOM, django, remarkable) {
  'use strict';

  function _arrayLikeToArray(r, a) {
    (null == a || a > r.length) && (a = r.length);
    for (var e = 0, n = Array(a); e < a; e++) n[e] = r[e];
    return n;
  }
  function _arrayWithHoles(r) {
    if (Array.isArray(r)) return r;
  }
  function _arrayWithoutHoles(r) {
    if (Array.isArray(r)) return _arrayLikeToArray(r);
  }
  function _createForOfIteratorHelper(r, e) {
    var t = "undefined" != typeof Symbol && r[Symbol.iterator] || r["@@iterator"];
    if (!t) {
      if (Array.isArray(r) || (t = _unsupportedIterableToArray(r)) || e && r && "number" == typeof r.length) {
        t && (r = t);
        var n = 0,
          F = function () {};
        return {
          s: F,
          n: function () {
            return n >= r.length ? {
              done: !0
            } : {
              done: !1,
              value: r[n++]
            };
          },
          e: function (r) {
            throw r;
          },
          f: F
        };
      }
      throw new TypeError("Invalid attempt to iterate non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.");
    }
    var o,
      a = !0,
      u = !1;
    return {
      s: function () {
        t = t.call(r);
      },
      n: function () {
        var r = t.next();
        return a = r.done, r;
      },
      e: function (r) {
        u = !0, o = r;
      },
      f: function () {
        try {
          a || null == t.return || t.return();
        } finally {
          if (u) throw o;
        }
      }
    };
  }
  function _defineProperty(e, r, t) {
    return (r = _toPropertyKey(r)) in e ? Object.defineProperty(e, r, {
      value: t,
      enumerable: !0,
      configurable: !0,
      writable: !0
    }) : e[r] = t, e;
  }
  function _extends() {
    return _extends = Object.assign ? Object.assign.bind() : function (n) {
      for (var e = 1; e < arguments.length; e++) {
        var t = arguments[e];
        for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]);
      }
      return n;
    }, _extends.apply(null, arguments);
  }
  function _iterableToArray(r) {
    if ("undefined" != typeof Symbol && null != r[Symbol.iterator] || null != r["@@iterator"]) return Array.from(r);
  }
  function _iterableToArrayLimit(r, l) {
    var t = null == r ? null : "undefined" != typeof Symbol && r[Symbol.iterator] || r["@@iterator"];
    if (null != t) {
      var e,
        n,
        i,
        u,
        a = [],
        f = !0,
        o = !1;
      try {
        if (i = (t = t.call(r)).next, 0 === l) {
          if (Object(t) !== t) return;
          f = !1;
        } else for (; !(f = (e = i.call(t)).done) && (a.push(e.value), a.length !== l); f = !0);
      } catch (r) {
        o = !0, n = r;
      } finally {
        try {
          if (!f && null != t.return && (u = t.return(), Object(u) !== u)) return;
        } finally {
          if (o) throw n;
        }
      }
      return a;
    }
  }
  function _nonIterableRest() {
    throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.");
  }
  function _nonIterableSpread() {
    throw new TypeError("Invalid attempt to spread non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.");
  }
  function ownKeys(e, r) {
    var t = Object.keys(e);
    if (Object.getOwnPropertySymbols) {
      var o = Object.getOwnPropertySymbols(e);
      r && (o = o.filter(function (r) {
        return Object.getOwnPropertyDescriptor(e, r).enumerable;
      })), t.push.apply(t, o);
    }
    return t;
  }
  function _objectSpread2(e) {
    for (var r = 1; r < arguments.length; r++) {
      var t = null != arguments[r] ? arguments[r] : {};
      r % 2 ? ownKeys(Object(t), !0).forEach(function (r) {
        _defineProperty(e, r, t[r]);
      }) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(t)) : ownKeys(Object(t)).forEach(function (r) {
        Object.defineProperty(e, r, Object.getOwnPropertyDescriptor(t, r));
      });
    }
    return e;
  }
  function _slicedToArray(r, e) {
    return _arrayWithHoles(r) || _iterableToArrayLimit(r, e) || _unsupportedIterableToArray(r, e) || _nonIterableRest();
  }
  function _toConsumableArray(r) {
    return _arrayWithoutHoles(r) || _iterableToArray(r) || _unsupportedIterableToArray(r) || _nonIterableSpread();
  }
  function _toPrimitive(t, r) {
    if ("object" != typeof t || !t) return t;
    var e = t[Symbol.toPrimitive];
    if (void 0 !== e) {
      var i = e.call(t, r || "default");
      if ("object" != typeof i) return i;
      throw new TypeError("@@toPrimitive must return a primitive value.");
    }
    return ("string" === r ? String : Number)(t);
  }
  function _toPropertyKey(t) {
    var i = _toPrimitive(t, "string");
    return "symbol" == typeof i ? i : i + "";
  }
  function _unsupportedIterableToArray(r, a) {
    if (r) {
      if ("string" == typeof r) return _arrayLikeToArray(r, a);
      var t = {}.toString.call(r).slice(8, -1);
      return "Object" === t && r.constructor && (t = r.constructor.name), "Map" === t || "Set" === t ? Array.from(r) : "Arguments" === t || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(t) ? _arrayLikeToArray(r, a) : void 0;
    }
  }

  var StateContext = /*#__PURE__*/React.createContext({
    state: {
      tree: [],
      cids: [],
      newcids: [],
      counter: 0
    },
    dispath: function dispath() {}
  });
  var init_context_default = {
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
    comment_max_length: 3000
  };
  var InitContext = /*#__PURE__*/React.createContext(init_context_default);

  function create_tree(cids, data) {
    var tree = new Array();
    var corder = new Array();
    var comments = {};
    var children = {};
    var in_cids = new Set();
    var cur_cids = new Set();
    var new_cids = new Set();
    function get_children(cid) {
      return children[cid].map(function (index) {
        if (comments[index].children === undefined) {
          comments[index].children = get_children(index);
        }
        return comments[index];
      });
    }
    var _iterator = _createForOfIteratorHelper(data),
      _step;
    try {
      for (_iterator.s(); !(_step = _iterator.n()).done;) {
        var item = _step.value;
        in_cids.add(item.id);
        comments[item.id] = item;
        if (item.level === 0) {
          corder.push(item.id);
        }
        children[item.id] = [];
        if (item.parent_id !== item.id) {
          children[item.parent_id].push(item.id);
        }
      }
    } catch (err) {
      _iterator.e(err);
    } finally {
      _iterator.f();
    }
    for (var _i = 0, _corder = corder; _i < _corder.length; _i++) {
      var id = _corder[_i];
      comments[id].children = get_children(id);
      tree.push(comments[id]);
    }
    if (in_cids.size > 0) {
      if (cids.size > 0) {
        var _iterator2 = _createForOfIteratorHelper(in_cids),
          _step2;
        try {
          for (_iterator2.s(); !(_step2 = _iterator2.n()).done;) {
            var _id = _step2.value;
            if (!cids.has(_id)) {
              new_cids.add(_id);
            }
            cur_cids.add(_id);
          }
        } catch (err) {
          _iterator2.e(err);
        } finally {
          _iterator2.f();
        }
      } else {
        cur_cids = in_cids;
        new_cids = new Set();
      }
    }
    return {
      tree: tree,
      cids: cur_cids,
      newcids: new_cids,
      counter: cur_cids.size
    };
  }
  function reducer(state, action) {
    switch (action.type) {
      case 'CREATE_TREE':
        {
          return _objectSpread2(_objectSpread2({}, state), create_tree(state.cids, action.data));
        }
      case 'UPDATE_COUNTER':
        {
          return _objectSpread2(_objectSpread2({}, state), {}, {
            counter: action.counter
          });
        }
      default:
        {
          return state;
        }
    }
  }

  function getCookie(name) {
    var value;
    if (document.cookie && document.cookie !== '') {
      var all_cookies = document.cookie.split(';');
      var _iterator = _createForOfIteratorHelper(all_cookies),
        _step;
      try {
        for (_iterator.s(); !(_step = _iterator.n()).done;) {
          var cookie = _step.value;
          var content = cookie.trim();
          if (content.slice(0, name.length + 1) === name + '=') {
            value = decodeURIComponent(content.slice(name.length + 1));
            break;
          }
        }
      } catch (err) {
        _iterator.e(err);
      } finally {
        _iterator.f();
      }
    }
    return value;
  }

  function FieldIsRequired(_ref) {
    var replyTo = _ref.replyTo,
      message = _ref.message;
    return /*#__PURE__*/React.createElement("span", _extends({
      className: "form-text small invalid-feedback"
    }, replyTo > 0 && {
      style: {
        "fontSize": "0.71rem"
      }
    }), django.gettext(message));
  }
  function PreviewComment(_ref2) {
    var avatar = _ref2.avatar,
      name = _ref2.name,
      url = _ref2.url,
      comment = _ref2.comment,
      replyTo = _ref2.replyTo;
    var _useContext = React.useContext(InitContext),
      is_authenticated = _useContext.is_authenticated,
      current_user = _useContext.current_user;
    var get_heading_name = function get_heading_name() {
      if (url.length > 0) return /*#__PURE__*/React.createElement("a", {
        href: url,
        target: "_new"
      }, name);else if (is_authenticated) return current_user.split(":")[1];else return name;
    };
    var raw_markup = function raw_markup() {
      var md = new remarkable.Remarkable();
      var _raw_markup = md.render(comment);
      return {
        __html: _raw_markup
      };
    };
    return /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("hr", null), !replyTo && /*#__PURE__*/React.createElement("h5", {
      className: "text-center"
    }, django.gettext("Your comment in preview")), /*#__PURE__*/React.createElement("div", {
      className: "comment d-flex " + (replyTo > 0 ? "mt-1" : "mt-5")
    }, /*#__PURE__*/React.createElement("img", {
      className: "me-3",
      src: avatar,
      height: "48",
      width: "48"
    }), /*#__PURE__*/React.createElement("div", {
      className: "d-flex flex-column pb-3"
    }, /*#__PURE__*/React.createElement("span", {
      style: {
        fontSize: "0.8rem"
      }
    }, django.gettext("Now"), " - ", get_heading_name(), "  ", replyTo > 0 && /*#__PURE__*/React.createElement("div", {
      className: "badge badge-info"
    }, "preview")), /*#__PURE__*/React.createElement("div", {
      className: "content py-2",
      dangerouslySetInnerHTML: raw_markup()
    }))));
  }
  function CommentForm(_ref3) {
    var replyTo = _ref3.replyTo,
      onCommentCreated = _ref3.onCommentCreated;
    var _useContext2 = React.useContext(InitContext),
      comment_max_length = _useContext2.comment_max_length,
      default_followup = _useContext2.default_followup,
      default_form = _useContext2.default_form,
      is_authenticated = _useContext2.is_authenticated,
      preview_url = _useContext2.preview_url,
      request_email_address = _useContext2.request_email_address,
      request_name = _useContext2.request_name,
      send_url = _useContext2.send_url;
    var _useState = React.useState({
        previewing: false,
        submitted: false,
        avatar: undefined,
        name: "",
        email: "",
        url: "",
        comment: "",
        followup: default_followup,
        errors: {
          name: false,
          email: false,
          comment: false
        },
        alert: {
          message: "",
          cssc: ""
        },
        comment_field_error: ""
      }),
      _useState2 = _slicedToArray(_useState, 2),
      lstate = _useState2[0],
      setLstate = _useState2[1];
    var default_error = "This field is required.";
    var get_comment_length_error_msg = function get_comment_length_error_msg() {
      return "Ensure this value has at most ".concat(comment_max_length, " ") + "character (it has ".concat(lstate.comment.length, ").");
    };
    var handle_input_change = function handle_input_change(event) {
      var target = event.target;
      var value = target.type === 'checkbox' ? target.checked : target.value;
      var iname = target.name;
      var comment_field_error = "";
      if (lstate.comment_field_error.length > 0) {
        comment_field_error = get_comment_length_error_msg();
      }
      setLstate(_objectSpread2(_objectSpread2({}, lstate), {}, _defineProperty(_defineProperty({}, iname, value), "comment_field_error", comment_field_error)));
    };
    var is_valid_data = function is_valid_data() {
      var is_valid_name = true,
        is_valid_email = true,
        comment_field_error = "";
      if (!is_authenticated || request_name) is_valid_name = /^\s*$/.test(lstate.name) ? false : true;
      if (!is_authenticated || request_email_address) is_valid_email = /\S+@\S+\.\S+/.test(lstate.email) ? true : false;
      var is_valid_comment = /^\s*$/.test(lstate.comment) ? false : true;
      if (lstate.comment.length >= comment_max_length) {
        is_valid_comment = false;
        comment_field_error = get_comment_length_error_msg();
      }
      setLstate(_objectSpread2(_objectSpread2({}, lstate), {}, {
        errors: _objectSpread2(_objectSpread2({}, lstate.errors), {}, {
          name: !is_valid_name,
          email: !is_valid_email,
          comment: !is_valid_comment
        }),
        comment_field_error: comment_field_error
      }));
      return is_valid_name && is_valid_email && is_valid_comment;
    };
    var handle_submit = function handle_submit(event) {
      event.preventDefault();
      if (!is_valid_data()) {
        return;
      }
      var data = _objectSpread2(_objectSpread2({}, default_form), {}, {
        honeypot: '',
        comment: lstate.comment,
        name: lstate.name,
        email: lstate.email,
        url: lstate.url,
        followup: lstate.followup,
        reply_to: replyTo
      });
      var _promise = fetch(send_url, {
        method: 'POST',
        mode: 'cors',
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCookie("csrftoken")
        },
        body: JSON.stringify(data)
      });
      _promise.then(function (response) {
        if ([201, 202, 204, 403].includes(response.status)) {
          var css_class = "";
          var msg_202 = django.gettext("Your comment will be reviewed. Thank your for your patience.");
          var msg_204 = django.gettext("Thank you, a comment confirmation request has been sent by mail.");
          var msg_403 = django.gettext("Sorry, your comment has been rejected.");
          var message = {
            202: msg_202,
            204: msg_204,
            403: msg_403
          };
          var cssc = (replyTo > 0 ? "mb-0 " : "") + "small alert alert-";
          css_class = response.status == 403 ? cssc + "danger" : cssc + "info";
          var _errors = response.status < 300 ? {
            name: false,
            email: false,
            comment: false
          } : _objectSpread2({}, lstate.errors);
          setLstate(_objectSpread2(_objectSpread2({}, lstate), {}, {
            alert: {
              message: message[response.status],
              cssc: css_class
            },
            previewing: false,
            submitted: true,
            name: '',
            email: '',
            url: '',
            followup: false,
            comment: '',
            errors: _errors
          }));
          onCommentCreated();
        }
      });
    };
    var handle_preview = function handle_preview(event) {
      event.preventDefault();
      if (!is_valid_data()) return;
      var _promise = fetch(preview_url, {
        method: 'POST',
        mode: 'cors',
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCookie("csrftoken")
        },
        body: JSON.stringify({
          email: lstate.email
        })
      });
      _promise.then(function (response) {
        if (response.status === 200) return response.json();else throw new Error("Status ".concat(response.status));
      }).then(function (data) {
        setLstate(_objectSpread2(_objectSpread2({}, lstate), {}, {
          avatar: data.url,
          previewing: true
        }));
      })["catch"](function (error) {
        return console.error(error);
      });
    };
    var get_field_css_classes = function get_field_css_classes(field) {
      var css_classes = "row justify-content-center form-group";
      if (field === "followup") css_classes += " my-3";else css_classes += replyTo > 0 ? " my-2" : " my-3";
      if (field === "name" && lstate.errors.name || field === "email" && lstate.errors.email || field === "comment" && lstate.errors.comment) {
        css_classes += " has-danger";
      }
      return css_classes;
    };
    var get_input_css_classes = function get_input_css_classes(field) {
      var css_classes = "form-control";
      css_classes += replyTo > 0 ? " form-control-sm" : "";
      if (field === "name" && lstate.errors.name || field === "email" && lstate.errors.email || field === "comment" && lstate.errors.comment) {
        css_classes += " is-invalid";
      }
      return css_classes;
    };
    var render_comment_field = function render_comment_field() {
      return /*#__PURE__*/React.createElement("div", {
        className: get_field_css_classes("comment")
      }, /*#__PURE__*/React.createElement("div", {
        className: replyTo > 0 ? "col-12" : "col-10"
      }, /*#__PURE__*/React.createElement("textarea", {
        required: true,
        name: "comment",
        id: "id_comment",
        value: lstate.comment,
        placeholder: django.gettext("Your comment"),
        className: get_input_css_classes("comment"),
        onChange: handle_input_change
      }), lstate.errors.comment && /*#__PURE__*/React.createElement(FieldIsRequired, {
        replyTo: replyTo,
        message: lstate.comment_field_error || default_error
      })));
    };
    var render_name_field = function render_name_field() {
      if (is_authenticated && !request_name) return /*#__PURE__*/React.createElement(React.Fragment, null);
      return /*#__PURE__*/React.createElement("div", {
        className: get_field_css_classes("name")
      }, /*#__PURE__*/React.createElement("div", {
        className: "col-2 text-end"
      }, /*#__PURE__*/React.createElement("label", {
        htmlFor: "id_name",
        className: replyTo > 0 ? "form-control-sm" : "col-form-label"
      }, django.gettext("Name"))), /*#__PURE__*/React.createElement("div", {
        className: replyTo > 0 ? "col-9" : "col-7"
      }, /*#__PURE__*/React.createElement("input", {
        required: true,
        type: "text",
        name: "name",
        id: "id_name",
        value: lstate.name,
        placeholder: django.gettext('name'),
        onChange: handle_input_change,
        className: get_input_css_classes("name")
      }), lstate.errors.name && /*#__PURE__*/React.createElement(FieldIsRequired, {
        replyTo: replyTo,
        message: "This field is required."
      })));
    };
    var render_email_field = function render_email_field() {
      if (is_authenticated && !request_email_address) return /*#__PURE__*/React.createElement(React.Fragment, null);
      var help_cssc = "form-text small";
      help_cssc += lstate.errors.email ? " invalid-feedback" : "";
      return /*#__PURE__*/React.createElement("div", {
        className: get_field_css_classes("email")
      }, /*#__PURE__*/React.createElement("div", {
        className: "col-2 text-end"
      }, /*#__PURE__*/React.createElement("label", {
        htmlFor: "id_name",
        className: replyTo > 0 ? "form-control-sm" : "col-form-label"
      }, django.gettext("Mail"))), /*#__PURE__*/React.createElement("div", {
        className: replyTo > 0 ? "col-9" : "col-7"
      }, /*#__PURE__*/React.createElement("input", {
        required: true,
        type: "text",
        name: "email",
        id: "id_email",
        value: lstate.email,
        placeholder: django.gettext('mail address'),
        onChange: handle_input_change,
        className: get_input_css_classes("email")
      }), /*#__PURE__*/React.createElement("span", _extends({
        className: help_cssc
      }, replyTo > 0 && {
        style: {
          "fontSize": "0.71rem"
        }
      }), django.gettext('Required for comment verification.'))));
    };
    var render_url_field = function render_url_field() {
      if (is_authenticated) return /*#__PURE__*/React.createElement(React.Fragment, null);
      return /*#__PURE__*/React.createElement("div", {
        className: get_field_css_classes("url")
      }, /*#__PURE__*/React.createElement("div", {
        className: "col-2 text-end"
      }, /*#__PURE__*/React.createElement("label", {
        htmlFor: "id_url",
        className: replyTo > 0 ? "form-control-sm" : "col-form-label"
      }, django.gettext("Link"))), /*#__PURE__*/React.createElement("div", {
        className: replyTo > 0 ? "col-9" : "col-7"
      }, /*#__PURE__*/React.createElement("input", {
        type: "text",
        name: "url",
        id: "id_url",
        value: lstate.url,
        placeholder: django.gettext("url your name links to (optional)"),
        onChange: handle_input_change,
        className: get_input_css_classes("url")
      })));
    };
    var render_followup_field = function render_followup_field() {
      var elem_id = replyTo > 0 ? "_".concat(replyTo) : "id_followup";
      var cssc = "form-check d-flex justify-content-center align-items-center";
      return /*#__PURE__*/React.createElement("div", {
        className: get_field_css_classes("followup")
      }, /*#__PURE__*/React.createElement("div", {
        className: replyTo > 0 ? "col-10" : "col-7"
      }, /*#__PURE__*/React.createElement("div", {
        className: cssc
      }, /*#__PURE__*/React.createElement("input", {
        name: "followup",
        type: "checkbox",
        id: elem_id,
        onChange: handle_input_change,
        className: "form-check-input",
        checked: lstate.followup
      }), /*#__PURE__*/React.createElement("label", {
        htmlFor: elem_id,
        className: "ps-2 form-check-label" + (replyTo > 0 && " small")
      }, "\xA0", django.gettext("Notify me about follow-up comments")))));
    };
    return /*#__PURE__*/React.createElement("div", null, lstate.previewing && /*#__PURE__*/React.createElement(PreviewComment, {
      avatar: lstate.avatar,
      name: lstate.name,
      url: lstate.url,
      comment: lstate.comment,
      replyTo: replyTo
    }), /*#__PURE__*/React.createElement("div", {
      className: replyTo === 0 ? "card mt-4 mb-5" : "card mt-2"
    }, /*#__PURE__*/React.createElement("div", {
      className: "card-body"
    }, replyTo === 0 && /*#__PURE__*/React.createElement("h4", {
      className: "card-title text-center pb-3"
    }, django.gettext("Post your comment")), lstate.alert.message && lstate.alert.message.length > 0 && /*#__PURE__*/React.createElement("div", {
      className: lstate.alert.cssc
    }, lstate.alert.message), (!lstate.submitted || replyTo === 0) && /*#__PURE__*/React.createElement("form", {
      method: "POST",
      onSubmit: handle_submit
    }, /*#__PURE__*/React.createElement("fieldset", null, /*#__PURE__*/React.createElement("input", {
      type: "hidden",
      name: "content_type",
      defaultValue: default_form.content_type
    }), /*#__PURE__*/React.createElement("input", {
      type: "hidden",
      name: "object_pk",
      defaultValue: default_form.object_pk
    }), /*#__PURE__*/React.createElement("input", {
      type: "hidden",
      name: "timestamp",
      defaultValue: default_form.timestamp
    }), /*#__PURE__*/React.createElement("input", {
      type: "hidden",
      name: "security_hash",
      defaultValue: default_form.security_hash
    }), /*#__PURE__*/React.createElement("input", {
      type: "hidden",
      name: "reply_to",
      defaultValue: replyTo
    }), /*#__PURE__*/React.createElement("div", {
      style: {
        display: 'none'
      }
    }, /*#__PURE__*/React.createElement("input", {
      type: "text",
      name: "honeypot",
      defaultValue: ""
    })), render_comment_field(), render_name_field(), render_email_field(), render_url_field(), render_followup_field()), /*#__PURE__*/React.createElement("div", {
      className: "row my-2 form-group" + (replyTo > 0 ? " mb-0" : "")
    }, /*#__PURE__*/React.createElement("div", {
      className: "d-flex justify-content-center"
    }, /*#__PURE__*/React.createElement("button", {
      type: "submit",
      name: "post",
      className: "btn btn-primary me-1" + (replyTo > 0 ? " btn-sm" : "")
    }, django.gettext("send")), /*#__PURE__*/React.createElement("button", {
      name: "preview",
      className: "btn btn-secondary" + (replyTo > 0 ? " btn-sm" : ""),
      onClick: handle_preview
    }, django.gettext("preview"))))))));
  }

  // --------------------------------------------------------------------
  function UserPart(_ref) {
    var userName = _ref.userName,
      userUrl = _ref.userUrl,
      isRemoved = _ref.isRemoved,
      userModerator = _ref.userModerator;
    var user = React.useMemo(function () {
      return userUrl && !isRemoved ? /*#__PURE__*/React.createElement("a", {
        href: userUrl,
        className: "text-decoration-none",
        title: "User's link"
      }, userName) : userName;
    }, [userUrl, isRemoved]);
    var moderator = React.useMemo(function () {
      if (userModerator) {
        var label = django.gettext("moderator");
        return /*#__PURE__*/React.createElement("span", null, "\xA0", /*#__PURE__*/React.createElement("span", {
          className: "badge text-bg-secondary"
        }, label));
      } else return /*#__PURE__*/React.createElement(React.Fragment, null);
    }, [userModerator]);
    return /*#__PURE__*/React.createElement("span", null, user, moderator);
  }

  // --------------------------------------------------------------------
  // The TopRightPart displays:
  //  * The "flag this comment" link, and
  //  * The "remove this comment" link.

  function TopRightPart(_ref2) {
    var allowFlagging = _ref2.allowFlagging,
      canModerate = _ref2.canModerate,
      commentId = _ref2.commentId,
      deleteUrl = _ref2.deleteUrl,
      flagUrl = _ref2.flagUrl,
      isAuthenticated = _ref2.isAuthenticated,
      isRemoved = _ref2.isRemoved,
      loginUrl = _ref2.loginUrl,
      userRequestedRemoval = _ref2.userRequestedRemoval,
      removalCount = _ref2.removalCount;
    var flagging_count = React.useMemo(function () {
      if (isAuthenticated && canModerate && removalCount > 0) {
        var fmts = django.ngettext("%s user has flagged this comment as inappropriate.", "%s users have flagged this comment as inappropriate.", removalCount);
        var text = django.interpolate(fmts, [removalCount]);
        return /*#__PURE__*/React.createElement("span", {
          className: "small text-danger",
          title: text
        }, removalCount);
      } else {
        return /*#__PURE__*/React.createElement(React.Fragment, null);
      }
    }, [isAuthenticated, canModerate, removalCount]);
    var flagging_html = React.useMemo(function () {
      if (!allowFlagging) return /*#__PURE__*/React.createElement(React.Fragment, null);
      var inapp_msg = "";
      if (userRequestedRemoval) {
        inapp_msg = django.gettext("I flagged it as inappropriate");
        return /*#__PURE__*/React.createElement(React.Fragment, null, flagging_count, "\xA0", /*#__PURE__*/React.createElement("i", {
          className: "bi bi-flag text-danger",
          title: inapp_msg
        }));
      } else {
        var url = isAuthenticated ? flagUrl.replace('0', commentId) : loginUrl + "?next=" + flagUrl.replace('0', commentId);
        inapp_msg = django.gettext("flag comment as inappropriate");
        return /*#__PURE__*/React.createElement(React.Fragment, null, flagging_count, "\xA0", /*#__PURE__*/React.createElement("a", {
          className: "text-decoration-none",
          href: url
        }, /*#__PURE__*/React.createElement("i", {
          className: "bi bi-flag",
          title: inapp_msg
        })));
      }
    }, [allowFlagging, userRequestedRemoval]);
    var moderate_html = React.useMemo(function () {
      if (isAuthenticated && canModerate) {
        var remove_msg = django.gettext("remove comment");
        var url = deleteUrl.replace('0', commentId);
        return /*#__PURE__*/React.createElement("a", {
          className: "text-decoration-none",
          href: url
        }, /*#__PURE__*/React.createElement("i", {
          className: "bi bi-trash",
          title: remove_msg
        }));
      } else {
        return /*#__PURE__*/React.createElement(React.Fragment, null);
      }
    }, [isAuthenticated, canModerate]);
    if (isRemoved) return /*#__PURE__*/React.createElement(React.Fragment, null);
    return /*#__PURE__*/React.createElement("div", {
      className: "d-inline"
    }, flagging_html, " ", moderate_html);
  }

  // --------------------------------------------------------------------
  // The FeedbackPart displays:
  //  * The "flag this comment" link, and
  //  * The "remove this comment" link.

  function FeedbackPart(_ref3) {
    var allowFeedback = _ref3.allowFeedback,
      commentId = _ref3.commentId,
      currentUser = _ref3.currentUser,
      onLikeClicked = _ref3.onLikeClicked,
      onDislikeClicked = _ref3.onDislikeClicked,
      showFeedback = _ref3.showFeedback,
      userLikeList = _ref3.userLikeList,
      userDislikeList = _ref3.userDislikeList;
    var cur_user_id = currentUser.split(":")[0];
    var get_user_list = function get_user_list(dir) {
      return dir === "like" ? userLikeList : userDislikeList;
    };
    var get_feedback_chunk = function get_feedback_chunk(dir) {
      if (!allowFeedback) return /*#__PURE__*/React.createElement(React.Fragment, null);
      var user_list = _toConsumableArray(get_user_list(dir));
      var userids = new Set(user_list.map(function (item) {
        return item.split(":")[0];
      }));
      var usernames = user_list.map(function (item) {
        return item.split(":")[1];
      });
      var click_hdl = dir == 'like' ? onLikeClicked : onDislikeClicked;
      var icon = dir == 'like' ? 'hand-thumbs-up' : 'hand-thumbs-down';
      icon += userids.has(cur_user_id) ? '-fill' : '';
      var class_icon = "bi bi-" + icon;
      var title = dir == 'like' ? django.gettext('I like it') : django.gettext('I dislike it');
      return /*#__PURE__*/React.createElement(React.Fragment, null, showFeedback && user_list.length > 0 && /*#__PURE__*/React.createElement("a", {
        className: "small text-decoration-none",
        "data-bs-html": "true",
        "data-bs-toggle": "tooltip",
        "data-bs-title": usernames.join("<br/>"),
        role: "button"
      }, user_list.length), /*#__PURE__*/React.createElement("a", {
        href: "#",
        onClick: click_hdl
      }, /*#__PURE__*/React.createElement("i", {
        className: class_icon,
        title: title
      })));
    };
    var likeFeedback = get_feedback_chunk("like");
    var dislikeFeedback = get_feedback_chunk("dislike");
    return allowFeedback ? /*#__PURE__*/React.createElement("div", {
      id: "feedback-".concat(commentId),
      className: "d-inline small"
    }, likeFeedback, "\xA0", /*#__PURE__*/React.createElement("span", {
      className: "text-muted"
    }, "\u22C5"), "\xA0", dislikeFeedback) : /*#__PURE__*/React.createElement(React.Fragment, null);
  }

  // --------------------------------------------------------------------
  // The ReplyFormPart displays:
  //  * The "reply" link. (it can be precedeed with a &bull;)
  //  * The "reply" form.

  function ReplyFormPart(_ref4) {
    var allowFeedback = _ref4.allowFeedback,
      commentId = _ref4.commentId,
      level = _ref4.level,
      maxThreadLevel = _ref4.maxThreadLevel,
      onCommentCreated = _ref4.onCommentCreated,
      onReplyClick = _ref4.onReplyClick,
      replyFormVisible = _ref4.replyFormVisible,
      replyUrl = _ref4.replyUrl;
    var url = replyUrl.replace('0', commentId);
    var label = django.gettext("Reply");
    if (level >= maxThreadLevel) return /*#__PURE__*/React.createElement(React.Fragment, null);
    return /*#__PURE__*/React.createElement(React.Fragment, null, allowFeedback ? /*#__PURE__*/React.createElement("span", null, "\xA0\xA0", /*#__PURE__*/React.createElement("span", {
      className: "text-muted"
    }, "\u2022"), "\xA0\xA0", /*#__PURE__*/React.createElement("a", {
      className: "small text-decoration-none",
      onClick: onReplyClick,
      href: url
    }, label)) : /*#__PURE__*/React.createElement("a", {
      className: "small text-decoration-none",
      onClick: onReplyClick,
      href: url
    }, label), replyFormVisible ? /*#__PURE__*/React.createElement(CommentForm, {
      replyTo: commentId,
      onCommentCreated: onCommentCreated
    }) : /*#__PURE__*/React.createElement(React.Fragment, null));
  }

  // --------------------------------------------------------------------
  // The CommentBodyPart component.

  function CommentBodyPart(_ref5) {
    var allowFeedback = _ref5.allowFeedback,
      comment = _ref5.comment,
      isRemoved = _ref5.isRemoved;
    var rawMarkup = React.useMemo(function () {
      var md = new remarkable.Remarkable();
      var _markup = md.render(comment);
      return {
        __html: _markup
      };
    }, [comment]);
    var extra_space = allowFeedback ? "py-1" : "pt-1 pb-3";
    if (isRemoved) {
      var cls = "text-muted ".concat(extra_space);
      return /*#__PURE__*/React.createElement("p", {
        className: cls
      }, /*#__PURE__*/React.createElement("em", null, comment));
    } else {
      var _cls = "content ".concat(extra_space);
      return /*#__PURE__*/React.createElement("div", {
        className: _cls,
        dangerouslySetInnerHTML: rawMarkup
      });
    }
  }

  // --------------------------------------------------------------------
  function reduce_flags(data, current_user) {
    var result = {
      like: [],
      dislike: [],
      removal: {
        is_active: false,
        count: 0
      }
    };
    var _iterator = _createForOfIteratorHelper(data),
      _step;
    try {
      for (_iterator.s(); !(_step = _iterator.n()).done;) {
        var item = _step.value;
        var user = [item.id, item.user].join(":");
        switch (item.flag) {
          case "like":
            {
              result.like.push(user);
              break;
            }
          case "dislike":
            {
              result.dislike.push(user);
              break;
            }
          case "removal":
            {
              result.removal.count += 1;
              result.removal.is_active = user === current_user ? true : false;
              break;
            }
        }
      }
    } catch (err) {
      _iterator.e(err);
    } finally {
      _iterator.f();
    }
    return result;
  }
  function Comment(props) {
    var _data$children;
    var data = props.data;
    var _useContext = React.useContext(InitContext),
      allow_feedback = _useContext.allow_feedback,
      allow_flagging = _useContext.allow_flagging,
      can_moderate = _useContext.can_moderate,
      current_user = _useContext.current_user,
      delete_url = _useContext.delete_url,
      dislike_url = _useContext.dislike_url,
      feedback_url = _useContext.feedback_url,
      flag_url = _useContext.flag_url,
      is_authenticated = _useContext.is_authenticated,
      like_url = _useContext.like_url,
      login_url = _useContext.login_url,
      max_thread_level = _useContext.max_thread_level,
      reply_url = _useContext.reply_url,
      show_feedback = _useContext.show_feedback,
      who_can_post = _useContext.who_can_post;
    var _useContext2 = React.useContext(StateContext),
      state = _useContext2.state;
    var newcids = state.newcids;
    var _flags = reduce_flags(data.flags, current_user);
    var _useState = React.useState({
        current_user: current_user,
        removal: _flags.removal.is_active,
        removal_count: _flags.removal.count,
        like_users: _flags.like,
        dislike_users: _flags.dislike,
        is_reply_form_visible: false
      }),
      _useState2 = _slicedToArray(_useState, 2),
      lstate = _useState2[0],
      setLstate = _useState2[1];
    var handle_comment_created = function handle_comment_created() {
      props.onCommentCreated();
      if (is_authenticated) {
        setLstate(_objectSpread2(_objectSpread2({}, lstate), {}, {
          is_reply_form_visible: false
        }));
      }
    };
    var handle_reply_click = function handle_reply_click(event) {
      event.preventDefault();
      if (who_can_post === 'users' && !is_authenticated) {
        return window.location.href = "".concat(login_url, "?next=").concat(reply_url.replace('0', data.id));
      }
      setLstate(_objectSpread2(_objectSpread2({}, lstate), {}, {
        is_reply_form_visible: !lstate.is_reply_form_visible
      }));
    };
    var post_feedback = function post_feedback(flag) {
      var _promise = fetch(feedback_url, {
        method: 'POST',
        mode: 'cors',
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCookie("csrftoken")
        },
        body: JSON.stringify({
          comment: data.id,
          flag: flag
        })
      });
      _promise.then(function (response) {
        var _like_users = new Set(lstate.like_users);
        var _dislike_users = new Set(lstate.dislike_users);
        switch (response.status) {
          case 201:
            {
              if (flag == 'like') {
                _like_users.add(current_user);
                _dislike_users["delete"](current_user);
              } else if (flag == 'dislike') {
                _like_users["delete"](current_user);
                _dislike_users.add(current_user);
              }
              setLstate(_objectSpread2(_objectSpread2({}, lstate), {}, {
                like_users: _toConsumableArray(_like_users),
                dislike_users: _toConsumableArray(_dislike_users)
              }));
              break;
            }
          case 204:
            {
              if (flag == 'like') {
                _like_users["delete"](current_user);
              } else if (flag == 'dislike') {
                _dislike_users["delete"](current_user);
              }
              setLstate(_objectSpread2(_objectSpread2({}, lstate), {}, {
                like_users: _toConsumableArray(_like_users),
                dislike_users: _toConsumableArray(_dislike_users)
              }));
              break;
            }
          case 400:
            {
              response.json().then(function (data) {
                console.error(data);
              });
              break;
            }
        }
      });
    };
    var action_like = function action_like(event) {
      event.preventDefault();
      if (is_authenticated) {
        return post_feedback('like');
      }
      var redirect = "".concat(login_url, "?next=").concat(like_url.replace('0', data.id));
      return window.location.href = redirect;
    };
    var action_dislike = function action_dislike(event) {
      event.preventDefault();
      if (is_authenticated) {
        return post_feedback('dislike');
      }
      var redirect = "".concat(login_url, "?next=").concat(dislike_url.replace('0', data.id));
      return window.location.href = redirect;
    };
    React.useEffect(function () {
      var qs_tooltip = '[data-bs-toggle="tooltip"]';
      var tooltipTriggerList = document.querySelectorAll(qs_tooltip);
      _toConsumableArray(tooltipTriggerList).map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
      });
    }, [lstate]);
    return /*#__PURE__*/React.createElement("div", {
      id: "c".concat(data.id),
      className: "comment d-flex"
    }, /*#__PURE__*/React.createElement("img", {
      src: data.user_avatar,
      className: "me-3",
      height: "48",
      width: "48"
    }), /*#__PURE__*/React.createElement("div", {
      className: "d-flex flex-column flex-grow-1 pb-3"
    }, /*#__PURE__*/React.createElement("h6", {
      className: "comment-header mb-1 d-flex justify-content-between",
      style: {
        fontSize: "0.8rem"
      }
    }, /*#__PURE__*/React.createElement("div", {
      className: "d-inline flex-grow-1"
    }, newcids.has(data.id) && /*#__PURE__*/React.createElement("span", null, /*#__PURE__*/React.createElement("span", {
      className: "badge text-bg-success"
    }, "new"), "\xA0-\xA0"), data.submit_date, "\xA0-\xA0", /*#__PURE__*/React.createElement(UserPart, {
      userName: data.user_name,
      userUrl: data.user_url,
      isRemoved: data.is_removed,
      userModerator: data.user_moderator
    }), "\xA0\xA0", /*#__PURE__*/React.createElement("a", {
      className: "permalink text-decoration-none",
      title: django.gettext("comment permalink"),
      href: data.permalink
    }, "\xB6")), /*#__PURE__*/React.createElement(TopRightPart, {
      allowFlagging: allow_flagging,
      canModerate: can_moderate,
      commentId: data.id,
      deleteUrl: delete_url,
      flagUrl: flag_url,
      isAuthenticated: is_authenticated,
      isRemoved: data.is_removed,
      loginUrl: login_url,
      userRequestedRemoval: lstate.removal,
      removalCount: lstate.removal_count
    })), /*#__PURE__*/React.createElement(CommentBodyPart, {
      allowFeedback: allow_feedback,
      comment: data.comment,
      isRemoved: data.is_removed
    }), !data.is_removed && /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement(FeedbackPart, {
      allowFeedback: allow_feedback,
      commentId: data.id,
      currentUser: current_user,
      onLikeClicked: action_like,
      onDislikeClicked: action_dislike,
      showFeedback: show_feedback,
      userLikeList: lstate.like_users,
      userDislikeList: lstate.dislike_users
    }), /*#__PURE__*/React.createElement(ReplyFormPart, {
      allowFeedback: allow_feedback,
      commentId: data.id,
      level: data.level,
      maxThreadLevel: max_thread_level,
      onCommentCreated: handle_comment_created,
      onReplyClick: handle_reply_click,
      replyFormVisible: lstate.is_reply_form_visible,
      replyUrl: reply_url
    })), data.children.length > 0 && /*#__PURE__*/React.createElement("div", {
      className: "pt-3"
    }, (_data$children = data.children) === null || _data$children === void 0 ? void 0 : _data$children.map(function (item) {
      return /*#__PURE__*/React.createElement(Comment, {
        key: item.id,
        data: item,
        onCommentCreated: props.onCommentCreated
      });
    }))));
  }

  function CommentCounter(_ref) {
    var counter = _ref.counter;
    var text = React.useMemo(function () {
      var fmts = django.ngettext("%s comment.", "%s comments.", counter);
      return django.interpolate(fmts, [counter]);
    }, [counter]);
    return counter > 0 ? /*#__PURE__*/React.createElement("h5", {
      className: "text-center"
    }, text) : /*#__PURE__*/React.createElement(React.Fragment, null);
  }
  function CommentFormWrapper(_ref2) {
    var replyTo = _ref2.replyTo,
      onCommentCreated = _ref2.onCommentCreated;
    var _useContext = React.useContext(InitContext),
      allow_comments = _useContext.allow_comments,
      who_can_post = _useContext.who_can_post,
      is_authenticated = _useContext.is_authenticated,
      html_id_suffix = _useContext.html_id_suffix;
    if (allow_comments) {
      if (who_can_post === 'all' || who_can_post === 'users' && is_authenticated) {
        return /*#__PURE__*/React.createElement(CommentForm, {
          replyTo: replyTo,
          onCommentCreated: onCommentCreated
        });
      }
      var _id = "only-users-can-post-".concat(html_id_suffix);
      var elem = document.getElementById(_id);
      return elem ? /*#__PURE__*/React.createElement("div", {
        dangerouslySetInnerHTML: {
          __html: elem.innerHTML
        }
      }) : /*#__PURE__*/React.createElement("h5", {
        className: "mt-4 mb-5 text-center text-info"
      }, django.gettext("Only registered users can post comments."));
    }
    return /*#__PURE__*/React.createElement("h4", {
      className: "mt-4 mb-5 text-center text-secondary"
    }, django.gettext("Comments are disabled for this article."));
  }
  function UpdateAlert(_ref3) {
    var counter = _ref3.counter,
      cids = _ref3.cids,
      _onClick = _ref3.onClick;
    var diff = counter - cids.size;
    if (diff > 0) {
      var fmts = django.ngettext("There is %s new comment.", "There are %s new comments.", diff);
      var message = django.interpolate(fmts, [diff]);
      return /*#__PURE__*/React.createElement("div", {
        className: "alert alert-info" + " d-flex justify-content-between align-items-center"
      }, /*#__PURE__*/React.createElement("p", {
        className: "mb-0"
      }, message), /*#__PURE__*/React.createElement("button", {
        type: "button",
        className: "btn btn-secondary btn-xs",
        onClick: function onClick() {
          return _onClick();
        }
      }, "update"));
    } else return /*#__PURE__*/React.createElement(React.Fragment, null);
  }
  function CommentBox() {
    var _useContext2 = React.useContext(InitContext),
      count_url = _useContext2.count_url,
      list_url = _useContext2.list_url,
      polling_interval = _useContext2.polling_interval;
    var _useContext3 = React.useContext(StateContext),
      state = _useContext3.state,
      dispatch = _useContext3.dispatch;
    var counter = state.counter,
      cids = state.cids,
      tree = state.tree;
    var load_comments = function load_comments() {
      var _promise = fetch(list_url);
      _promise.then(function (response) {
        return response.json();
      }).then(function (data) {
        dispatch({
          type: 'CREATE_TREE',
          data: data
        });
      })["catch"](function (error) {
        return console.error(error);
      });
    };
    var load_count = function load_count() {
      var _promise = fetch(count_url);
      _promise.then(function (response) {
        return response.json();
      }).then(function (data) {
        dispatch({
          type: 'UPDATE_COUNTER',
          counter: data.count
        });
      })["catch"](function (error) {
        return console.error(error);
      });
    };
    React.useEffect(function () {
      if (polling_interval > 0) {
        setInterval(load_count, polling_interval);
      }
      load_comments();
    }, [polling_interval]);
    return /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement(CommentCounter, {
      counter: counter
    }), /*#__PURE__*/React.createElement(CommentFormWrapper, {
      replyTo: 0,
      onCommentCreated: load_comments
    }), /*#__PURE__*/React.createElement(UpdateAlert, {
      counter: counter,
      cids: cids,
      onClick: load_comments
    }), /*#__PURE__*/React.createElement("div", {
      className: "comment-tree"
    }, tree.map(function (item) {
      return /*#__PURE__*/React.createElement(Comment, {
        key: item.id,
        data: item,
        onCommentCreated: load_comments
      });
    })));
  }

  /*
   * props is an object containing all the attributes sent
   * by the get_commentbox_props templatetag (a django-comments-xtd tag).
   * It happens to be the output of the function commentbox_props, in the
   * module django_comments_xtd/frontend.py.
   * Here in JavaScript the structure of the props matches the
   * InitContext, in the context.js module.
   */

  function App(props) {
    var initial_state = {
      tree: [],
      cids: new Set(),
      newcids: new Set(),
      counter: props.comment_count
    };
    var _useReducer = React.useReducer(reducer, initial_state),
      _useReducer2 = _slicedToArray(_useReducer, 2),
      state = _useReducer2[0],
      dispatch = _useReducer2[1];
    return /*#__PURE__*/React.createElement(StateContext.Provider, {
      value: {
        state: state,
        dispatch: dispatch
      }
    }, /*#__PURE__*/React.createElement(InitContext.Provider, {
      value: props
    }, /*#__PURE__*/React.createElement(CommentBox, null)));
  }

  var rootElement = document.getElementById('comments');
  if (!rootElement) throw new Error('Failed to find the element with id="comments".');
  ReactDOM.createRoot(rootElement).render(/*#__PURE__*/React.createElement(React.StrictMode, null, /*#__PURE__*/React.createElement(App, _objectSpread2(_objectSpread2({}, window.comments_props), window.comments_props_override))));

})(React, ReactDOM, django, remarkable);
//# sourceMappingURL=django-comments-xtd-2.10.4.js.map
