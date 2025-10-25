export function get_cookie(name) {
  let cookie_value;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (const cookie of cookies) {
      // Does this cookie string begin with the name we want?
      if (cookie.slice(0, name.length + 1) === (name + '=')) {
        cookie_value = decodeURIComponent(cookie.slice(name.length + 1));
        break;
      }
    }
  }
  return cookie_value;
}

export function get_login_url(config_el, is_guest) {
  const url = config_el.dataset.djcxLoginUrl;
  if ((url == undefined || url.length === 0) && is_guest) {
    throw new Error("Cannot find the [data-login-url] attribute.");
  }
  return url;
}

export function get_react_url(config_el, is_guest) {
  const url = config_el.dataset.djcxReactUrl;
  if (url == undefined || url.length === 0) {
    if (is_guest) {
      console.info("Couldn't find the data-react-url attribute, " +
        "but the user is anonymous. She has to login first in " +
        "order to post comment reactions.");
    } else {
      throw new Error("Cannot initialize reactions panel => The " +
        "[data-react-url] attribute does not exist or is empty.");
    }
  }
  return url;
}

export function get_vote_url(config_el, is_guest) {
  const url = config_el.dataset.djcxVoteUrl;
  if (url == undefined || url.length === 0) {
    if (is_guest) {
      console.info("Couldn't find the data-vote-url attribute, " +
        "but the user is anonymous. She has to login first in " +
        "order to vote for comments.");
    } else {
      throw new Error("Cannot initialize comment voting => The " +
        "[data-vote-url] attribute does not exist or is empty.");
    }
  }
  return url;
}

export function get_flag_url(config_el, is_guest) {
  const url = config_el.dataset.djcxFlagUrl;
  if (url == undefined || url.length === 0) {
    if (is_guest) {
      console.info("Couldn't find the data-flag-url attribute, " +
        "but the user is anonymous. She has to login first in " +
        "order to flag comments.");
    } else {
      throw new Error("Cannot initialize comment flagging => The " +
        "[data-flag-url] attribute does not exist or is empty.");
    }
  }
  return url;
}

// From:
// https://developer.mozilla.org/en-US/docs/Web/API/SubtleCrypto/digest
//
export async function digest_loc() {
  const href = URL.parse(globalThis.location.href);
  // Encode as (utf-8) Uint8Array.
  const uint8 = new TextEncoder().encode(href.pathname);
  const hash_buf = await globalThis.crypto.subtle.digest("SHA-256", uint8);
  // Convert buffer to byte array.
  const hash_arr = Array.from(new Uint8Array(hash_buf));
  const hash_hex = hash_arr
    .map((b) => b.toString(16).padStart(2, "0"))
    .join(""); // Convert bytes to hex string.
  return hash_hex;
}
