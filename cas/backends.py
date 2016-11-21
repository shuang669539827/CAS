from urllib import urlencode, urlopen
from urlparse import urljoin
from django.contrib.auth.models import User

import urllib2


__all__ = ['CASBackend']


def verify(ticket, service):
    """Verifies CAS 1.0 authentication ticket.

    Returns username on success and None on failure.
    """
    params = {'ticket': ticket, 'service': service}
    url = 'http://127.0.0.1:8001/validate/' + '?' + urlencode(params)
    page = urlurlopen(url)
    try:
        verified = page.readline().strip()
        if verified == 'yes':
            return page.readline().strip()
        else:
            return None
    finally:
        page.close()



class CASBackend(object):
	"""CAS authentication backend"""

	def authenticate(self, ticket, service, request):
		"""Verifies CAS ticket """

		username = verify(ticket, service)
        if not username:
            return None
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # user will have an "unusable" password
            user = User.objects.create_user(username, '')
            user.save()
        return user

    def get_user(self, user_id):
        """Retrieve the user's entry in the User model if it exists"""

        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
