import urllib

from django.core.urlresolvers import reverse


def link_to(value, url_name, view_args=(), view_kwargs={}, query={}, short_description=None):
    """
    Return admin field with link to named view with view_args/view_kwargs
    or view_[kw]args(obj) methods and HTTP GET parameters.

    Parameters:

      * value: function(object) or string for object proeprty name
      * url_name: name used to reverse() view
      * view_args: () or function(object) -> () returing view params
      * view_kwargs: {} or function(object) -> {} returing view params
      * query: {} or function(object) -> {} returning HTTP GET params
      * short_description: string with description, defaults to
        'value'/property name
    """

    def prop(self, obj):
        # Replace view_args methods by result of function callss
        if callable(view_args):
            args = view_args(obj)
        else:
            args = view_args

        if callable(view_kwargs):
            kwargs = view_kwargs(obj)
        else:
            kwargs = view_kwargs

        # Construct URL
        url = reverse(url_name, args=args, kwargs=kwargs)

        if callable(query):
            params = query(obj)
        else:
            params = query

        # Append query parameters
        if params:
            url += '?' + urllib.urlencode(params)

        # Get value
        if callable(value):
            # Call value getter
            new_value = value(obj)
        else:
            # String, assume object property
            assert isinstance(value, basestring)
            new_value = getattr(obj, value)

        return u'<a href="{0}">{1}</a>'.format(url, new_value)

    # Decorate function
    prop.allow_tags = True

    if not short_description:
        # No short_description set, use property name
        assert isinstance(value, basestring)
        short_description = value
    prop.short_description = short_description

    return prop
