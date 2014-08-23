import copy
import urllib
import facepy


def getdata(obj, key, default=None):
    if key in obj:
        return obj[key]['data']
    else:
        return default


class GraphAPI(facepy.GraphAPI):
    def __init__(self, *vargs, **kwargs):
        self.base = []
        super(GraphAPI, self).__init__(*vargs, **kwargs)

    def _segmentize_endpoint(self, endpoint):
        if not isinstance(endpoint, list):
            endpoint = [endpoint]
        return endpoint

    def _resolve_endpoint(self, endpoint, options=None):
        endpoint = self._segmentize_endpoint(endpoint)
        url = "/".join(self.base + endpoint)

        if options:
            qs = urllib.urlencode(options)
            return url + '?' + qs
        else:
            return url

    def partial(self, base):
        client = GraphAPI(self.oauth_token)
        client.base = client.base + self._segmentize_endpoint(base)
        return client

    def all(self, endpoint, paramsets, method='GET', body=False, **options):
        """ A nicer interface for batch requests to the 
        same endpoint but with different parameters, e.g. 
        different date ranges. """

        requests = []
        for params in paramsets:
            params = copy.copy(params)
            params.update(options)
            segments = self._segmentize_endpoint(endpoint)
            relative_url = params.get('relative_url', [])
            url = self._resolve_endpoint(segments + relative_url)
            request = {
                'method': method, 
                'relative_url': url, 
                }

            if body:
                request['body'] = body

            requests.append(request)

        # from pprint import pprint
        # pprint(requests)
        
        # TODO: stitch these results together, so 
        # that using `get` or `all` is transparent
        results = self.batch(requests)
        return results

    def get(self, relative_endpoint=[], *vargs, **kwargs):
        """ An endpoint can be specified as a string
         or as a list of path segments. """

        endpoint = self._resolve_endpoint(relative_endpoint)
        return super(GraphAPI, self).get(endpoint, *vargs, **kwargs)
