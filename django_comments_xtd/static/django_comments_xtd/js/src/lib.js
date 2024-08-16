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

export function django_gettext(string) {
  var _string = import('django').then(django => {
    return django.gettext(string);
  }).catch(err => { return '' });
  if (typeof _string === 'object' && typeof _string.then === 'function') {
    return string;
  }
  return _string;
}

export function django_ngettext(singular, plural, count) {
  var _string = import('django').then(django => {
    return django.gettext(string);
  }).catch(err => { return '' });
  if (typeof _string === 'object' && typeof _string.then === 'function') {
    return (count == 1) ? singular : plural;
  }
  return _string;
}

export function django_interpolate(fmt, obj, named) {
  var _string = import('django').then(django => {
    return django.interpolate(fmt, obj, named);
  }).catch(err => { return '' });

  if (typeof _string === 'object' && typeof _string.then === 'function') {
    if (named) {
      return fmt.replace(/%\(\w+\)s/g, function(match){return String(obj[match.slice(2,-2)])});
    } else {
      return fmt.replace(/%s/g, function(match){return String(obj.shift())});
    }
  }
  return _string;
}
