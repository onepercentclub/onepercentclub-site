# from apps.bluebottle_salesforce.models import ProjectCountry
from django.db import models
from salesforce.models import SalesforceModel
from djchoices import DjangoChoices, ChoiceItem
from django.utils.translation import ugettext as _

# TODO: remove the DjangoChoices or add it if needed to a Helper file.


class SalesforceOrganization(SalesforceModel):
    """
    Default Salesforce Account model. For Onepercentclub the mapping is named Organization(s).
    There are also other Salesforce models related to Account: AccountContactRole, AccountFeed, AccountHistory,
                                                               AccountPartner, AccountShare
    """
    class AccountType(DjangoChoices):
        business = ChoiceItem('Business', label=_("Business"))
        fund = ChoiceItem('Fund', label=_("Fund"))
        international = ChoiceItem('International Cooperation', label=_("International Cooperation"))
        network = ChoiceItem('Network', label=_("Network"))
        supplier = ChoiceItem('Supplier', label=_("Supplier"))
        individual = ChoiceItem('Individual', label=_("Individual"))
        percent_idea = ChoiceItem('1%IDEA', label=_("1%IDEA"))
        government = ChoiceItem('Government & Politics', label=_("Individual"))
        media_pr = ChoiceItem('Media / PR', label=_("Media / PR"))

    legal_status = models.CharField(max_length=10000, db_column='Legal_status__c')
    name = models.CharField(max_length=255, db_column='Name')
    organization_type = models.CharField(max_length=40, db_column="Type", choices=AccountType.choices,
                                         help_text=("Type"))
    external_id = models.CharField(max_length=255, db_column='Organization_External_ID__c')
    billing_city = models.CharField(max_length=40, db_column='BillingCity')
    billing_street = models.CharField(max_length=255, db_column='BillingStreet')
    billing_postal_code = models.CharField(max_length=20, db_column='BillingPostalCode')
    billing_country = models.CharField(max_length=80, db_column='BillingCountry')
    billing_state = models.CharField(max_length=20, db_column='BillingState')
    email_address = models.EmailField(max_length=80, db_column='E_mail_address__c')
    phone = models.CharField(max_length=40, db_column='Phone')
    website = models.URLField(max_length=255, db_column='Website')
    bank_account_address = models.CharField(max_length=255, db_column='Bank_account_address__c')
    bank_account_name = models.CharField(max_length=255, db_column='Bank_account_name__c')
    bank_account_number = models.CharField(max_length=40, db_column='Bank_account_number__c')
    bank_account_iban = models.CharField(max_length=255, db_column='Bank_account_IBAN__c')
    bank_account_postalcode = models.CharField(max_length=20, db_column='Bank_account_postalcode__c')
    bank_account_city = models.CharField(max_length=255, db_column='Bank_account_city__c')
    bank_account_country = models.CharField(max_length=60, db_column='Bank_account_country__c')
    bank_name = models.CharField(max_length=255, db_column='Bank_bankname__c')
    bank_bic_swift = models.CharField(max_length=40, db_column='Bank_SWIFT__c')
    bank_address = models.CharField(max_length=255, db_column='Bank_address__c')
    bank_postalcode = models.CharField(max_length=20, db_column='Bank_postalcode__c')
    bank_city = models.CharField(max_length=255, db_column='Bank_city__c')
    bank_country = models.CharField(max_length=60, db_column='Bank_country__c')
    twitter = models.CharField(max_length=255, db_column='Twitter__c')
    facebook = models.CharField(max_length=255, db_column='Facebook__c')
    tags = models.CharField(max_length=255, db_column='Tags__c')
    skype = models.CharField(max_length=255, db_column='Skype__c')
    created_date = models.DateField(db_column='Organization_created_date__c')
    deleted_date = models.DateTimeField(db_column='Deleted__c')

    class Meta:
        db_table = 'Account'
        managed = False


class SalesforceContact(SalesforceModel):
    """
    Default Salesforce Contact model.
    """
    category1 = models.CharField(max_length=255, db_column='Category1__c')
    email = models.EmailField(max_length=80, db_column='Email')
    member_1_club = models.BooleanField(db_column='Member_1_club__c', default=True)
    user_name = models.CharField(max_length=255, db_column='Username__c')
    is_active = models.BooleanField(db_column='Active__c')
    has_activated = models.BooleanField(db_column='Has_Activated_Account__c')
    deleted_date = models.DateField(db_column='Deleted__c')
    first_name = models.CharField(max_length=40, db_column='FirstName')
    last_name = models.CharField(max_length=80, db_column='LastName', null=False, blank=False)
    member_since = models.DateField(db_column='Member_since__c')
    why_one_percent_member = models.CharField(max_length=32000, db_column='Why_onepercent_member__c')
    about_me_us = models.CharField(max_length=3200, db_column='About_me_us__c')
    location = models.CharField(max_length=100, db_column='Location__c')
    picture_location = models.CharField(max_length=255, db_column='Picture_Location__c')
    website = models.CharField(max_length=255, db_column='Website__c')
    last_login = models.DateTimeField(db_column='Date_Last_Login__c')
    date_joined = models.DateTimeField(db_column='Date_Joined__c')
    bank_account_number = models.CharField(max_length=30, db_column='Account_number__c')
    bank_account_holder = models.CharField(max_length=60, db_column='Account_holder__c')
    bank_account_city = models.CharField(max_length=50, db_column='Account_city__c')
    bank_account_iban = models.CharField(max_length=40, db_column='Account_IBAN__c')
    bank_account_active_recurring_debit = models.BooleanField(db_column='Account_Active_Recurring_Debit__c')
    has_n_friends = models.CharField(max_length=255, db_column='Has_n_friends__c')
    has_given_n_vouchers = models.CharField(max_length=255, db_column='Has_given_n_1_VOUCHERS__c')
    number_of_donations = models.CharField(max_length=255, db_column='Number_of_donations__c')
    support_n_projects = models.CharField(max_length=255, db_column='Support_n_projects__c')
    total_amount_of_donations = models.CharField(max_length=255, db_column='Total_amount_of_donations__c')
    birth_date = models.DateField(db_column='Birthdate')
    gender = models.CharField(max_length=20, db_column='Gender__c')
    mailing_city = models.CharField(max_length=40, db_column='MailingCity')
    mailing_country = models.CharField(max_length=40, db_column='MailingCountry')
    mailing_postal_code = models.CharField(max_length=20, db_column='MailingPostalCode')
    mailing_street = models.CharField(max_length=20, db_column='MailingStreet')
    mailing_state = models.CharField(max_length=80, db_column='MailingState')
    phone = models.CharField(max_length=40, db_column='Phone')
    facebook = models.CharField(max_length=50, db_column='Facebook__c')
    twitter = models.CharField(max_length=250, db_column='Twitter__c')
    skype = models.CharField(max_length=255, db_column='Skype__c')
    available_time = models.CharField(max_length=255, db_column='Available_time__c')
    where = models.CharField(max_length=255, db_column='Where__c')
    availability = models.CharField(max_length=255, db_column='Availability__c')
    receive_newsletter = models.BooleanField(db_column='Receive_newsletter__c')
    primary_language = models.CharField(max_length=255, db_column='Primary_language__c')
    external_id = models.CharField(max_length=255, db_column='Contact_External_ID__c')
    tags = models.CharField(max_length=255, db_column='Tags__c')

    class Meta:
        db_table = 'Contact'
        managed = False


class SalesforceProject(SalesforceModel):
    """
    Custom Salesforce Project__c model. For Onepercentclub the mapping is named 1%CLUB Project(s).
    """
    class ProjectStatus(DjangoChoices):
        closed = ChoiceItem('Closed', label=_("Closed"))
        created = ChoiceItem('Created', label=_("Created"))
        done = ChoiceItem('Done', label=_("Done"))
        validated = ChoiceItem('Validated', label=_("Validated"))

    amount_at_the_moment = models.CharField(max_length=255, db_column='Amount_at_the_moment__c')
    amount_requested = models.CharField(max_length=255, db_column='Amount_requested__c')
    amount_still_needed = models.CharField(max_length=255, db_column='Amount_still_needed__c')
    project_name = models.CharField(max_length=80, db_column='Project_name__c')
    project_owner = models.ForeignKey(SalesforceContact, db_column='Project_Owner__c')
    status_project = models.CharField(max_length=255,
                                      db_column='Status_project__c',
                                      choices=ProjectStatus.choices,
                                      help_text=_("Status project"))
    target_group_s_of_the_project = models.CharField(max_length=20000, db_column='Target_group_s_of_the_project__c')
    country_in_which_the_project_is_located = models.CharField(max_length=255,
                                                               db_column='Country_in_which_the_project_is_located__c')
    region = models.CharField(max_length=100, db_column='Region__c')
    sub_region = models.CharField(max_length=100, db_column='Sub_region__c')
    describe_the_project_in_one_sentence = models.CharField(max_length=50000,
                                                            db_column='Describe_the_project_in_one_sentence__c')
    story = models.CharField(max_length=32768, db_column='Story__c')
    third_half_project = models.BooleanField(db_column='third_half_project__c')
    organization_account = models.ForeignKey(SalesforceOrganization, db_column='Organization__c', null=True)
    comments = models.CharField(max_length=32000, db_column='Comments__c')
    contribution_project_in_reducing_poverty = models.CharField(max_length=32000,
                                                                db_column='Contribution_project_in_reducing_poverty__c')
    earth_charther_project = models.BooleanField(db_column='Earth_Charther_project__c')
    sustainability = models.CharField(max_length=20000, db_column='Sustainability__c')
    additional_explanation_of_budget = models.CharField(max_length=32000,
                                                        db_column='Additional_explanation_of_budget__c')
    tags = models.CharField(max_length=255, db_column='Tags__c')
    slug = models.CharField(max_length=100, db_column='Slug__c')
    partner_organization = models.CharField(max_length=255, db_column='Partner_Organization__c')
    video_url = models.CharField(max_length=255, db_column='VideoURL__c')
    picture_location = models.CharField(max_length=255, db_column='Picture_Location__c')
    story = models.CharField(max_length=32768, db_column='Story__c')
    date_started = models.DateField(db_column='Date_Started__c')
    date_funded = models.DateField(db_column='Date_Funded__c')
    date_ended = models.DateField(db_column='Date_Ended__c')
    is_campaign = models.BooleanField(db_column='Is_Campaign__c')
    allow_overfunding = models.BooleanField(db_column='Allow_Overfunding__c')
    name_referral_1 = models.CharField(max_length=255, db_column='Name_referral_1__c')
    name_referral_2 = models.CharField(max_length=255, db_column='Name_referral_2__c')
    name_referral_3 = models.CharField(max_length=255, db_column='Name_referral_3__c')
    description_referral_1 = models.CharField(max_length=32000, db_column='Description_referral_1__c')
    description_referral_2 = models.CharField(max_length=32000, db_column='Description_referral_2__c')
    description_referral_3 = models.CharField(max_length=32000, db_column='Description_referral_3__c')
    email_address_referral_1 = models.EmailField(max_length=80, blank=True, null=True,
                                                 db_column='E_mail_address_referral_1__c')
    email_address_referral_2 = models.EmailField(max_length=80, blank=True, null=True,
                                                 db_column='E_mail_address_referral_2__c')
    email_address_referral_3 = models.EmailField(max_length=80, blank=True, null=True,
                                                 db_column='E_mail_address_referral_3__c')
    relation_referral_1_with_project_org = models.CharField(max_length=32000,
                                                            db_column='Relation_referral_1_with_project_org__c')
    relation_referral_2_with_project_org = models.CharField(max_length=32000,
                                                            db_column='Relation_referral_2_with_project_org__c')
    relation_referral_3_with_project_org = models.CharField(max_length=32000,
                                                            db_column='Relation_referral_3_with_project_org__c')
    date_plan_submitted = models.DateField(db_column='Date_plan_submitted__c')
    project_created_date = models.DateTimeField(db_column='Project_created_date__c')
    project_updated_date = models.DateTimeField(db_column='Project_updated_date__c')
    date_project_deadline = models.DateField(db_column='Date_project_deadline__c')
    external_id = models.CharField(max_length=255, db_column='Project_External_ID__c')
    number_of_people_reached_direct = models.PositiveIntegerField(max_length=18,
                                                                  db_column='NumberOfPeopleReachedDirect__c')
    number_of_people_reached_indirect = models.PositiveIntegerField(max_length=18,
                                                                  db_column='NumberOfPeopleReachedIndirect__c')
    theme = models.CharField(max_length=255, db_column='Theme__c')
    donation_total = models.CharField(max_length=20, db_column='Donation_total__c')
    supporter_count = models.PositiveIntegerField(max_length=8, db_column='Supporter_count__c')
    donation_oo_total = models.CharField(max_length=20, db_column='Donation_oo_total__c')
    supporter_oo_count = models.PositiveIntegerField(max_length=8, db_column='Supporter_oo_count__c')

    class Meta:
        db_table = 'Project__c'
        managed = False


class SalesforceProjectBudget(SalesforceModel):
    """
    Custom Salesforce Project_Budget__c model. For Onepercentclub the mapping is named Project Budget.
    """
    class ProjectBudgetCategory(DjangoChoices):
        construction = ChoiceItem('Construction materials', label=_("Construction materials"))
        agriculture = ChoiceItem('Agriculture materials', label=_("Agriculture materials"))
        school_supplies = ChoiceItem('School supplies', label=_("School supplies"))
        communication = ChoiceItem('Communication materials', label=_("Communication materials"))
        other_materials = ChoiceItem('Other materials', label=_("Other materials"))
        tools = ChoiceItem('Tools', label=_("Tools"))
        transport = ChoiceItem('Transport', label=_("Transport"))
        training = ChoiceItem('Training', label=_("Training"))
        labor = ChoiceItem('Labor', label=_("Labor"))
        marketing_communication = ChoiceItem('Marketing/Communcation', label=_("Marketing/Communcation"))
        administration_costs = ChoiceItem('Adminstration Costs', label=_("Adminstration Costs"))
        overhead = ChoiceItem('Overhead', label=_("Overhead"))
        other = ChoiceItem('Other', label=_("Other"))

    category = models.CharField(max_length=255, db_column='Category__c', choices=ProjectBudgetCategory.choices, help_text=_("Category"))
    costs = models.CharField(max_length=255, db_column='Costs__c')
    description = models.CharField(max_length=32000, db_column='Description__c')
    external_id = models.CharField(max_length=255, db_column='Project_Budget_External_ID__c')
    project = models.ForeignKey(SalesforceProject, db_column='Project__c')

    class Meta:
        db_table = 'Project_Budget__c'
        managed = False


class SalesforceFundraiser(SalesforceModel):
    """
    Custom Fundraiser__c model.
    """
    amount = models.CharField(max_length=100, db_column='Amount__c')
    owner = models.ForeignKey(SalesforceContact, db_column='Owner__c')
    created = models.DateTimeField(db_column='Created__c')
    deadline = models.DateField(db_column='Deadline__c')
    description = models.CharField(max_length=131072, db_column='Description__c')
    external_id = models.CharField(max_length=255, db_column='Fundraiser_External_ID__c')
    picture_location = models.CharField(max_length=255, db_column='Picture_Location__c')
    project = models.ForeignKey(SalesforceProject, db_column='Project__c')
    video_url = models.CharField(max_length=255, db_column='VideoURL__c')
    name = models.CharField(max_length=80, db_column='Name')
    amount_at_the_moment = models.CharField(max_length=100, db_column='Amount_at_the_moment__c')

    class Meta:
        db_table = 'Fundraiser__c'
        managed = False


class SalesforceOpportunity(SalesforceModel):
    """
    Default abstract Salesforce Opportunity model. Used for Donation(s) / Voucher(s).
    """
    amount = models.CharField(max_length=255, db_column='Amount')
    close_date = models.DateField(db_column='CloseDate')
    type = models.CharField(max_length=40, db_column='Type')
    name = models.CharField(max_length=120, db_column='Name')
    payment_method = models.CharField(max_length=255,
                                      db_column='Payment_method__c',
                                      help_text=_("PaymentMethod"))
    project = models.ForeignKey(SalesforceProject, db_column='Project__c', null=True)
    stage_name = models.CharField(max_length=40,
                                  db_column='StageName')
    record_type = models.CharField(max_length=255, db_column='RecordTypeId')

    class Meta:
        abstract = True
        managed = False


class SalesforceDonation(SalesforceOpportunity):
    """
    Child of the Opportunity for Onepercentclub the mapping is named Donation(s).
    """

    donation_created_date = models.DateTimeField(db_column='Donation_created_date__c')
    donation_updated_date = models.DateTimeField(db_column='Donation_updated_date__c')
    donation_ready_date = models.DateTimeField(db_column='Donation_ready_date__c')
    external_id_donation = models.CharField(max_length=255, db_column='Donation_External_ID__c')
    donor = models.ForeignKey(SalesforceContact, db_column='Receiver__c', null=True)
    fundraiser = models.ForeignKey(SalesforceFundraiser, db_column='Fundraiser__c', null=True)

    class Meta:
        managed = False
        db_table = 'Opportunity'


class SalesforceVoucher(SalesforceOpportunity):
    """
    Child of the Opportunity for Onepercentclub the mapping is named Voucher(s).
    """
    purchaser = models.ForeignKey(SalesforceContact, db_column='Purchaser__c', related_name='contact_purchasers')
    description = models.CharField(max_length=32000, db_column='Description')
    receiver = models.ForeignKey(SalesforceContact, db_column='Receiver__c', related_name='contact_receivers', null=True)
    external_id_voucher = models.CharField(max_length=255, db_column='Voucher_External_ID__c')

    class Meta:
        managed = False
        db_table = 'Opportunity'


class SalesforceTask(SalesforceModel):
    """
    Custom Salesforce onepercentclubTasks__c model. For Onepercentclub the mapping is named 1%CLUB Task(s).
    """
    class TaskStatus(DjangoChoices):
        open = ChoiceItem('Open', label=_("Open"))
        running = ChoiceItem('Running', label=_("Running"))
        closed = ChoiceItem('Closed', label=_("Closed"))
        realized = ChoiceItem('Realized', label=_("Realized"))

    project = models.ForeignKey(SalesforceProject, db_column='Project__c')
    deadline = models.DateField(db_column='Deadline__c')
    effort = models.CharField(max_length=200, db_column='Effort__c')
    extended_task_description = models.CharField(max_length=32000, db_column='Extended_task_description__c')
    location_of_the_task = models.CharField(max_length=200, db_column='Location_of_the_task__c')
    task_expertise = models.CharField(max_length=100, db_column='Task_expertise__c')
    task_status = models.CharField(max_length=40, db_column='Task_status__c', choices=TaskStatus.choices, help_text=_("TaskStatus"))
    title = models.CharField(max_length=100, db_column='Title__c')
    task_created_date = models.DateField(db_column='Task_created_date__c')
    tags = models.CharField(max_length=255, db_column='Tags__c')
    date_realized = models.DateField(db_column='Date_realized__c')
    author = models.ForeignKey(SalesforceContact, db_column='Author__c')
    people_needed = models.CharField(max_length=10, db_column='People_Needed__c')
    end_goal = models.CharField(max_length=5000, db_column='End_Goal__c')

    external_id = models.CharField(max_length=255, db_column='Task_External_ID__c')

    class Meta:
        db_table = 'onepercentclubTasks__c'
        managed = False


class SalesforceTaskMembers(SalesforceModel):
    """
    Custom Salesforce Task_Members__c model. For Onepercentclub the mapping is named Task Member(s).
    The table is used as a joined table which relates to Tasks to the Contacts.
    """
    contacts = models.ForeignKey(SalesforceContact, db_column='Contacts__c')
    x1_club_task = models.ForeignKey(SalesforceTask, db_column='X1_CLUB_Task__c')
    external_id = models.CharField(max_length=100, db_column='Task_Member_External_ID__c')
    motivation = models.CharField(max_length=5000, db_column='Motivation__c')
    status = models.CharField(max_length=255, db_column='Status__c')
    taskmember_created_date = models.DateField(db_column='Taskmember_Created_Date__c')

    class Meta:
        db_table = 'Task_Members__c'
        managed = False


class SalesforceOrganizationMember(SalesforceModel):
    """
    Custom Salesforce Organization_Member__c object.
    The object is used as a junction object that connects Account and Contact.
    """
    contact = models.ForeignKey(SalesforceContact, db_column='Contact__c')
    organization = models.ForeignKey(SalesforceOrganization, db_column='Organization__c')
    role = models.CharField(max_length=20, db_column='Role__c')
    external_id = models.CharField(max_length=100, db_column='Organization_Member_External_Id__c')

    class Meta:
        db_table = 'Organization_Member__c'
        managed = False


class SalesforceLogItem(SalesforceModel):
    """
    Custom Salesforce Log_Item__c object.
    The object is used to store log data from external and internal sources.
    """
    entered = models.DateTimeField(db_column='Entered__c')
    errors = models.PositiveIntegerField(max_length=18, db_column='Errors__c')
    message = models.CharField(max_length=32000, db_column='Message__c')
    source = models.CharField(max_length=255, db_column='Source__c')
    source_extended = models.CharField(max_length=255, db_column='Source_Extended__c')
    successes = models.PositiveIntegerField(max_length=18, db_column='Successes__c')

    class Meta:
        db_table = 'Log_Item__c'
        managed = False


class SalesforceLoginHistory(SalesforceModel):
    """
    Custom Login_History__c model. For Onepercentclub the mapping is named 1%CLUB Login History.
    New mapping to be added later on.
    """

    bounce_rate_from_first_page = models.CharField(max_length=6, db_column='Bounce_rate_from_first_page__c')
    contacts = models.ForeignKey(SalesforceContact, db_column='Contacts__c')
    engagement_on_facebook = models.PositiveIntegerField(max_length=8, db_column='Engagement_on_Facebook__c')
    engagement_on_twitter = models.PositiveIntegerField(max_length=8, db_column='Engagement_on_Twitter__c')
    number_of_pageviews = models.PositiveIntegerField(max_length=8, db_column='Number_of_pageviews__c')
    online_engagement_blogs = models.PositiveIntegerField(max_length=8, db_column='Online_engagement_blogs__c')
    online_engagement_projects = models.PositiveIntegerField(max_length=8, db_column='Online_engagement_projects__c')
    online_engagement_reactions_to_members = models.PositiveIntegerField(max_length=8, db_column='Online_engagement_'
                                                                                                 'reactions_to_'
                                                                                                 'members__c')
    online_engagement_tasks = models.PositiveIntegerField(max_length=8, db_column='Online_engagement_tasks__c')
    preferred_navigation_path = models.PositiveIntegerField(max_length=255, db_column='Preferred_navigation_path__c')
    shares_via_social_media = models.PositiveIntegerField(max_length=8, db_column='Shares_via_social_media__c')
    size_of_basket = models.PositiveIntegerField(max_length=8, db_column='Size_of_basket__c')
    time_on_website = models.PositiveIntegerField(max_length=6, db_column='Time_on_website__c')

    class Meta:
        db_table = 'X1_CLUB_Login_History__c'
        managed = False
