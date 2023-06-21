export function getCookie(name) {
  let cookieValue;
  if (document.cookie && document.cookie !== '') {
    var cookies = document.cookie.split(';');
    for (const cookie of cookies) {
    // for (var i = 0; i < cookies.length; i++) {
      const _cookie = cookie.trim();
      // Does this cookie string begin with the name we want?
      if (_cookie.slice(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.slice(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
