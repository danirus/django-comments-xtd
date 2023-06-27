export function getCookie(name) {
  let cookieValue;
  if (document.cookie && document.cookie !== '') {
    var cookies = document.cookie.split(';');
    for (const cookie of cookies) {
    // for (var i = 0; i < cookies.length; i++) {
      const _cookie = cookie.trim();
      // Does this cookie string begin with the name we want?
      if (_cookie.slice(0, name.length + 1) === (name + '=')) {
        // We want the slice from the position after the "=" sign:
        // name=value, so we slice from (name.length + 2).
        cookieValue = decodeURIComponent(cookie.slice(name.length + 2));
        break;
      }
    }
  }
  return cookieValue;
}
