function _django() {
  return {
    gettext: (arg) => arg,
    ngettext: (singular, plural, count) => {
      return (count == 1) ? singular : plural;
    },
    interpolate: (fmt, obj, named) => {
      return named
        ? fmt.replace(
          /%\(\w+\)s/g,
          function (match) { return String(obj[match.slice(2,-2)]) }
        )
        : fmt.replace(
          /%s/g,
          function(match){ return String(obj.shift()) }
        )
    }
  }
};

const django = _django();

export default django;

