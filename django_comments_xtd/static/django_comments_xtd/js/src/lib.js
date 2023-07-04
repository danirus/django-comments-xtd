export function getCookie(name) {
  let value;
  if (document.cookie && document.cookie !== '') {
    const all_cookies = document.cookie.split(';');
    for (const cookie of all_cookies) {
      const content = cookie.trim();
      if (content.slice(0, name.length + 1) === (name + '=')) {
        value = decodeURIComponent(content.slice(name.length + 1));
        break;
      }
    }
  }
  return value;
}
