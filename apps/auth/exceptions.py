from social.exceptions import SocialAuthBaseException


class EmailExists(SocialAuthBaseException):
    """ The email address is already registered in the database """
    def __str__(self):
        return "This email has already been registered"