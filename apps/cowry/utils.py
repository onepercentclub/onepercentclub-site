import pycurl
import cStringIO as StringIO
from urllib2 import HTTPError

def urlopen(url, data=None):
    """
    Wrapper for getting URL's - this is handy as the default Python
    behaviour is not to do proper checks on SSL.
    """

    result = StringIO.StringIO()

    curl = pycurl.Curl()
    curl.setopt(pycurl.SSL_VERIFYPEER, 1)
    curl.setopt(pycurl.SSL_VERIFYHOST, 2)
    curl.setopt(pycurl.URL, url)
    curl.setopt(pycurl.WRITEFUNCTION, result.write)

    if data:
        curl.setopt(pycurl.POSTFIELDS, data)

    curl.perform()

    # Reset the 'file' pointer
    result.seek(0)
    
    return_code = str(curl.getinfo(pycurl.RESPONSE_CODE))
    # Catch 4xx and 5xx error codes
    if return_code[0] in ('4', '5'):
        raise HTTPError(url, pycurl.HTTP_CODE, 'Error in HTTP request', None, result)

    return result