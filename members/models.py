from django.db import models


class Type(models.Model):
    """
    Member Type
    Can be either Guest, Person, Company, Group, Foundation (organization).
    """

    id = models.IntegerField(primary_key=True)
    label = models.CharField(max_length=32)
    label_en = models.CharField(max_length=65, blank=True)
    label_es = models.CharField(max_length=65, blank=True)

    class Meta:
        db_table = u'mem_types'

    def __unicode__(self):
        return self.label_en


class Member(models.Model):
    """ Member """

    id = models.BigIntegerField(primary_key=True)
    email = models.CharField(max_length=255)
    username = models.CharField(max_length=40)
    password = models.CharField(max_length=40)
    created = models.DateTimeField()
    updated = models.DateTimeField()
    deleted = models.DateTimeField(null=True, blank=True)
    admin = models.SmallIntegerField()
    accepte_user = models.SmallIntegerField()
    type = models.ForeignKey(Type)
    activated = models.BooleanField()
    ignore_activity = models.SmallIntegerField()
    validated = models.NullBooleanField(null=True, blank=True)
    hash = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = u'mem_members'

    def fullname(self):
        """ return first + lastname or username if no profile set """
        if self.profile():
            return self.profile().fullname()
        return self.username

    def profile(self):
        """ Try to load a profile or return None """
        if self.profile_set.count():
            return self.profile_set.all()[0];
        return None

    def donations(self):
        """ Get all donations (successful or not) """
        donations = self.donation_set.all()
        return donations

    def donation_count(self):
        """ The number of succesful donation by this member """
        return self.donation_set.filter(status='closed').count()

    def project_count(self):
        """ The number of projects this member is supporting """
        """ DOES NOT WORK YET """
        return self.donation_set.filter(status='closed').count()


class Profile(models.Model):
    """
    Member Profile contains extra data.
    Not all Members have a profile set!
    """

    id = models.BigIntegerField(primary_key=True)
    member = models.ForeignKey(Member, verbose_name='member')
    firstname = models.CharField(max_length=100, blank=True)
    lastname = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=100, blank=True)
    about = models.TextField(blank=True)
    why = models.TextField(blank=True)
    website = models.CharField(max_length=255, blank=True)
    newsletter = models.CharField(max_length=1, blank=True)
    birthdate = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=100, blank=True)
    zipcode = models.CharField(max_length=20, blank=True)
    billingname = models.CharField(max_length=255, blank=True)
    billingnumber = models.CharField(max_length=10, blank=True)
    billingcity = models.CharField(max_length=255, blank=True)
    created = models.DateTimeField()
    updated = models.DateTimeField()
    deleted = models.DateTimeField(null=True, blank=True)
    gender = models.CharField(max_length=1, blank=True)
    photo = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255, blank=True)
    country = models.ForeignKey('system.Country', null=True, blank=True)
    recurring_donation_amount = models.DecimalField(
        null=True, max_digits=12, decimal_places=2, blank=True)
    authorize_capture = models.SmallIntegerField()
    contribution = models.CharField(max_length=255, blank=True)
    available_time = models.CharField(max_length=255, blank=True)
    working_location = models.CharField(max_length=255, blank=True)
    primary_language = models.CharField(max_length=6, blank=True)
    facebook_id = models.CharField(max_length=255, blank=True)
    facebook_connect_enabled = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = u'mem_profile'

    def __unicode__(self):
        return self.firstname

    def fullname(self):
        return self.firstname + ' ' + self.lastname


class Activation(models.Model):
    """ For use in register process?? """

    id = models.BigIntegerField(primary_key=True)
    member = models.ForeignKey(Member, unique=True)
    hash = models.CharField(max_length=40, unique=True)
    created = models.DateTimeField()
    invitor_id = models.BigIntegerField(null=True, blank=True)
    invitor_id1 = models.BigIntegerField(null=True, blank=True)

    class Meta:
        db_table = u'mem_activations'


class Alert(models.Model):
    """ Member Alert. Stores prefs for email alerts """
    """ Might be better to put this in profile ?? """

    id = models.IntegerField(primary_key=True)
    member = models.ForeignKey(Member, unique=True)
    mail_friends_invite = models.NullBooleanField(null=True, blank=True)
    mail_profile_newmessage = models.NullBooleanField(null=True, blank=True)
    mail_new_donation = models.NullBooleanField(null=True, blank=True)
    mail_profile_new_public_message = models.NullBooleanField(
        null=True, blank=True)

    class Meta:
        db_table = u'mem_alert'


class Language(models.Model):
    """ Languages selected by user """
    """ Change language_code into proper Locale? """

    id = models.BigIntegerField(primary_key=True)
    member = models.ForeignKey(Member)
    language_code = models.CharField(max_length=6)

    class Meta:
        db_table = u'mem_languages'


class Invite(models.Model):
    """ Friendrequest from one Member to another """

    id = models.IntegerField(primary_key=True)
    from_member = models.ForeignKey(Member, related_name='inviter')
    to_member = models.ForeignKey(Member, related_name='invitee')
    text = models.TextField()
    created = models.DateTimeField()
    status = models.SmallIntegerField(null=True, blank=True)
    title = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = u'mem_invite'


class PasswordRequest(models.Model):
    """ Used to store a Password-lost hash """
    """ Probably Django has some standard solution for this """

    id = models.BigIntegerField(primary_key=True)
    member = models.ForeignKey(Member)
    hash = models.CharField(max_length=40)
    created = models.DateTimeField()
    updated = models.DateTimeField()
    hash2 = models.CharField(max_length=40, blank=True)
    hash3 = models.CharField(max_length=40, blank=True)

    class Meta:
        db_table = u'mem_password_requests'


class Message(models.Model):
    """ Message from one Member to another """
    """ Messages can be private or on the public wall of a user """

    id = models.IntegerField(primary_key=True)
    to_member = models.ForeignKey(Member, related_name='receiver')
    from_member = models.ForeignKey(Member, related_name='sender')
    visibility = models.SmallIntegerField()
    title = models.CharField(max_length=255)
    text = models.TextField()
    created = models.DateTimeField()
    read = models.DateTimeField(null=True, blank=True)
    deleted = models.DateTimeField(null=True, blank=True)
    archived = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = u'mem_message'


class MemberTag(models.Model):
    """ Tags for a Member """

    member = models.ForeignKey(Member)
    tag = models.ForeignKey('system.Tag')

    class Meta:
        db_table = u'mem_tags'


