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

    # SF Layout: Account details section.
    legal_status = models.CharField(max_length=10000, db_column='Legal_status__c')
    name = models.CharField(max_length=255, db_column='Name')
    organization_type = models.CharField(max_length=40, db_column="Type", choices=AccountType.choices ,help_text=("Type"))

    # SF Layout: Address Information section.
    external_id = models.CharField(max_length=255, db_column='Organization_External_ID__c')
    billing_city = models.CharField(max_length=40, db_column='BillingCity')
    billing_street = models.CharField(max_length=255, db_column='BillingStreet')
    billing_postal_code = models.CharField(max_length=20, db_column='BillingPostalCode')
    billing_country = models.CharField(max_length=80, db_column='BillingCountry')
    email_address = models.EmailField(max_length=80, db_column='E_mail_address__c')
    phone = models.CharField(max_length=40, db_column='Phone')
    website = models.URLField(max_length=255, db_column='Website')

    # SF Layout: Bank Account section.
    address_bank = models.CharField(max_length=255, db_column='Address_bank__c')
    bank_account_name = models.CharField(max_length=255, db_column='Bank_account_name__c')
    bank_account_number = models.CharField(max_length=40, db_column='Bank_account_number__c')
    bank_name = models.CharField(max_length=255, db_column='Bankname__c')
    bic_swift = models.CharField(max_length=40, db_column='BIC_SWIFT__c')
    country_bank = models.CharField(max_length=60, db_column='Country_bank__c')
    iban_number = models.CharField(max_length=255, db_column='IBAN_number__c')

    # SF Layout: Description section.
    description = models.CharField(max_length=32000, db_column='Description')

    # SF Layout: System Information.
    created_date = models.DateField(db_column='Organization_created_date__c')

    class Meta:
        db_table = 'Account'
        managed = False


class SalesforceContact(SalesforceModel):
    """
    Default Salesforce Contact model.
    """
    # SF Layout: Subscription section.
    category1 = models.CharField(max_length=255, db_column='Category1__c')
    email = models.EmailField(max_length=80, db_column='Email')
    member_1_club = models.BooleanField(db_column='Member_1_club__c', default=True)
    user_name = models.CharField(max_length=255, db_column='Username__c')
    is_active = models.BooleanField(db_column='Active__c')
    has_activated = models.BooleanField(db_column='Has_Activated_Account__c')
    close_date = models.DateField(db_column='Deleted__c')

    # SF Layout: Profile section.
    first_name = models.CharField(max_length=40, db_column='FirstName')
    last_name = models.CharField(max_length=80, db_column='LastName', null=False, blank=False)
    member_since = models.DateField(db_column='Member_since__c')
    why_one_percent_member = models.CharField(max_length=32000, db_column='Why_onepercent_member__c')
    about_me_us = models.CharField(max_length=3200, db_column='About_me_us__c')
    location = models.CharField(max_length=100, db_column='Location__c')
    # The default: Organization(Account) will be 'Individual' as current.
    # - Future purpose deactivate and put the Organization website group value
    #   organization_account = models.ForeignKey(SalesforceOrganization, db_column='AccountId')
    website = models.CharField(max_length=255, db_column='Website__c')
    last_login = models.DateTimeField(db_column='Date_Last_Login__c')
    date_joined = models.DateTimeField(db_column='Date_Joined__c')

    # Bank details
    bank_account_number = models.CharField(max_length=30, db_column='Account_number__c')
    bank_account_holder = models.CharField(max_length=60, db_column='Account_holder__c')
    bank_account_city = models.CharField(max_length=50, db_column='Account_city__c')

    # SF Layout: Contact Information section.
    activity_number = models.CharField(max_length=255, db_column='Activity_number__c')

    # SF Layout: Contact Activity section.
    amount_of_single_donations = models.CharField(max_length=255, db_column='Amount_of_single_donations__c')
    has_n_friends = models.CharField(max_length=255, db_column='Has_n_friends__c')
    has_given_n_vouchers = models.CharField(max_length=255, db_column='Has_given_n_1_VOUCHERS__c')
    is_doing_n_tasks = models.CharField(max_length=255, db_column='Is_doing_n_tasks__c')
    number_of_donations = models.CharField(max_length=255, db_column='Number_of_donations__c')
    support_n_projects = models.CharField(max_length=255, db_column='Support_n_projects__c')
    total_amount_of_donations = models.CharField(max_length=255, db_column='Total_amount_of_donations__c')
    total_number_of_received_messages = models.CharField(max_length=255, db_column='Total_number_of_received_messages__c')
    total_number_of_sent_messages = models.CharField(max_length=255, db_column='Total_number_of_sent_messages__c')

    # SF Layout: Administrative (private) section.
    birth_date = models.DateField(db_column='Birthdate')
    gender = models.CharField(max_length=20, db_column='Gender__c')
    mailing_city = models.CharField(max_length=40, db_column='MailingCity')
    mailing_country = models.CharField(max_length=40, db_column='MailingCountry')
    mailing_postal_code = models.CharField(max_length=20, db_column='MailingPostalCode')
    mailing_street = models.CharField(max_length=20, db_column='MailingStreet')
    mailing_state = models.CharField(max_length=80, db_column='MailingState')

    # SF Layout: My Skills section.
    # The field 'Which_1_would_you_like_to_contribute__c' has been replaced by 'available_to_share_knowledge' and
    # 'available_to_donate'
    # which_1_would_you_like_to_contribute = models.CharField(max_length=32000, db_column=
    # 'Which_1_would_you_like_to_contribute__c')
    available_time = models.CharField(max_length=255, db_column='Available_time__c')
    where = models.CharField(max_length=255, db_column='Where__c')
    available_to_donate = models.BooleanField(db_column='Available_to_donate__c')
    available_to_share_time_and_knowledge = models.BooleanField(db_column='Available_to_share_time_and_knowledge__c')
    availability = models.CharField(max_length=255, db_column='Availability__c')

    # SF Layout: My Settings section.
    receive_emails_for_friend_invitations = models.BooleanField(db_column='Receive_emails_for_friend_invitations__c')
    receive_newsletter = models.BooleanField(db_column='Receive_newsletter__c')
    email_after_a_new_message = models.BooleanField(db_column='Email_after_a_new_message__c')
    email_after_a_new_public_message = models.BooleanField(db_column='Email_after_a_new_public_message__c')
    primary_language = models.CharField(max_length=255, db_column='Primary_language__c')

    # SF Layout: All expertise section.
    administration_finance = models.BooleanField(db_column='Administration_Finance__c')
    agriculture_environment = models.BooleanField(db_column='Agriculture_Environment__c')
    architecture = models.BooleanField(db_column='Architecture__c')
    computer_ict = models.BooleanField(db_column='Computer_ICT__c')
    design = models.BooleanField(db_column='Design__c')
    economy_business = models.BooleanField(db_column='Economy_Business__c')
    education = models.BooleanField(db_column='Education__c')
    fund_raising = models.BooleanField(db_column='Fundraising__c')
    graphic_design = models.BooleanField(db_column='Graphic_Design__c')
    health = models.BooleanField(db_column='Health__c')
    internet_research = models.BooleanField(db_column='Internet_Research__c')
    law_and_politics = models.BooleanField(db_column='Law_and_Politics__c')
    marketing_pr = models.BooleanField(db_column='Marketing_PR__c')
    online_marketing = models.BooleanField(db_column='Online_Marketing__c')
    photo_video = models.BooleanField(db_column='Photo_Video__c')
    physics_technique = models.BooleanField(db_column='Physics_Technique__c')
    presentations = models.BooleanField(db_column='Presentations__c')
    project_management = models.BooleanField(db_column='Project_Management__c')
    psychology = models.BooleanField(db_column='Psychology__c')
    social_work = models.BooleanField(db_column='Social_Work__c')
    sport_and_development = models.BooleanField(db_column='Sport_and_Development__c')
    tourism = models.BooleanField(db_column='Tourism__c')
    trade_transport = models.BooleanField(db_column='Trade_Transport__c')
    translating_writing = models.BooleanField(db_column='Translating_Writing__c')
    web_development = models.BooleanField(db_column='Web_development__c')
    writing_proposals = models.BooleanField(db_column='Writing_proposals__c')

    # SF: Other.
    external_id = models.CharField(max_length=255, db_column='Contact_External_ID__c')
    tags = models.CharField(max_length=255, db_column='Tags__c')

    # SF: Additional requirement not implemented yet - SFDC - Sheet 1
    amount_of_available_time = models.CharField(max_length=255, db_column='Amount_of_available_time__c')
    industry_employed_in = models.CharField(max_length=255, db_column='Industry_employed_in__c')
    nationality = models.CharField(max_length=255, db_column='Nationality__c')
    follows_1_club_at_twitter = models.BooleanField(db_column='Follows_1_CLUB_at_Twitter__c')
    likes_1_club_at_facebook = models.BooleanField(db_column='Likes_1_CLUB_at_Facebook__c')
    interested_in_theme = models.CharField(max_length=255, db_column='Interested_in_theme__c')
    interested_in_target_group = models.CharField(max_length=255, db_column='Interested_in_target_group__c')
    preferred_channel_for_interaction = models.CharField(max_length=255, db_column='Preferred_channel_for_interaction__c')

    # SF: Additional requirement not implemented yet - SFDC - Sheet 2
    date_of_last_donation = models.DateField(db_column='Date_of_last_donation__c')
    total_amount_of_one_off_donation = models.PositiveIntegerField(max_length=11, db_column='Total_amount_of_one_off_donation__c')
    number_of_one_off_donations = models.PositiveIntegerField(max_length=8, db_column='Number_of_one_off_donations__c')
    total_amount_of_recurring_donations = models.PositiveIntegerField(max_length=11, db_column='Total_amount_of_recurring_donations__c')
    number_of_recurring_donation = models.PositiveIntegerField(max_length=8, db_column='Number_of_recurring_donation__c')
    number_of_received_campaigns = models.PositiveIntegerField(max_length=6, db_column='Number_of_received_campaigns__c')

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

    # SF Layout: 1%CLUB Project Detail section.
    amount_at_the_moment = models.CharField(max_length=255, db_column='Amount_at_the_moment__c')
    amount_requested = models.CharField(max_length=255, db_column='Amount_requested__c')
    amount_still_needed = models.CharField(max_length=255, db_column='Amount_still_needed__c')
    # Should it be 255 like the Project model on new Website
    project_name = models.CharField(max_length=80, db_column='Project_name__c')
    project_owner = models.ForeignKey(SalesforceContact, db_column='Project_Owner__c')
    status_project = models.CharField(max_length=255,
                                      db_column='Status_project__c',
                                      choices=ProjectStatus.choices,
                                      help_text=_("Status project"))
    target_group_s_of_the_project = models.CharField(max_length=20000, db_column='Target_group_s_of_the_project__c')

    # SF Layout: Summary Project Details section.
    country_in_which_the_project_is_located = models.CharField(max_length=255,
                                                               db_column='Country_in_which_the_project_is_located__c')
    describe_the_project_in_one_sentence = models.CharField(max_length=50000, db_column='Describe_the_project_in_one_sentence__c')
    describe_where_the_money_is_needed_for = models.CharField(max_length=15000, db_column='Describe_where_the_money_is_needed_for__c')
    project_url = models.URLField(max_length=255, db_column='Projecturl__c')

    # SF Layout: Extensive project information section.
    third_half_project = models.BooleanField(db_column='third_half_project__c')
    organization_account = models.ForeignKey(SalesforceOrganization, db_column='Organization__c', null=True)
    comments = models.CharField(max_length=32000, db_column='Comments__c')
    contribution_project_in_reducing_poverty = models.CharField(max_length=32000,
                                                                db_column='Contribution_project_in_reducing_poverty__c')
    earth_charther_project = models.BooleanField(db_column='Earth_Charther_project__c')
    extensive_project_description = models.CharField(max_length=32000, db_column='Extensive_project_description__c')
    project_goals = models.CharField(max_length=20000, db_column='Project_goals__c')
    sustainability = models.CharField(max_length=20000, db_column='Sustainability__c')

    # SF Layout: Project planning and budget section.
    additional_explanation_of_budget = models.CharField(max_length=32000,
                                                        db_column='Additional_explanation_of_budget__c')
    end_date_of_the_project = models.DateField(db_column='End_date_of_the_project__c')
    expected_funding_through_other_resources = models.CharField(max_length=20000, db_column='Expected_funding_through_other_resources__c')
    expected_project_results = models.CharField(max_length=32000, db_column='Expected_project_results__c')
    funding_received_through_other_resources = models.CharField(max_length=20000, db_column='Funding_received_through_other_resources__c')
    need_for_volunteers = models.CharField(max_length=32000, db_column='Need_for_volunteers__c')
    other_way_people_can_contribute = models.CharField(max_length=32000, db_column='Other_way_people_can_contribute__c')
    project_activities_and_timetable = models.CharField(max_length=32000, db_column='Project_activities_and_timetable__c')
    starting_date_of_the_project = models.DateField(db_column='Starting_date_of_the_project__c')

    # SF Layout: Millennium Goals section.
    #Multipicklist: ?? - millennium_goals = models.CharField(max_length=255, db_column='MILLENNIUM_GOALS__C')

    # SF Layout: Tags section.
    tags = models.CharField(max_length=20000, db_column='Tags__c')

    # SF Layout: Referrals section.
    name_referral_1 = models.CharField(max_length=255, db_column='Name_referral_1__c')
    name_referral_2 = models.CharField(max_length=255, db_column='Name_referral_2__c')
    name_referral_3 = models.CharField(max_length=255, db_column='Name_referral_3__c')
    description_referral_1 = models.CharField(max_length=32000, db_column='Description_referral_1__c')
    description_referral_2 = models.CharField(max_length=32000, db_column='Description_referral_2__c')
    description_referral_3 = models.CharField(max_length=32000, db_column='Description_referral_3__c')
    email_address_referral_1 = models.EmailField(max_length=80, blank=True, null=True, db_column='E_mail_address_referral_1__c')
    email_address_referral_2 = models.EmailField(max_length=80, blank=True, null=True, db_column='E_mail_address_referral_2__c')
    email_address_referral_3 = models.EmailField(max_length=80, blank=True, null=True, db_column='E_mail_address_referral_3__c')
    relation_referral_1_with_project_org = models.CharField(max_length=32000, db_column='Relation_referral_1_with_project_org__c')
    relation_referral_2_with_project_org = models.CharField(max_length=32000, db_column='Relation_referral_2_with_project_org__c')
    relation_referral_3_with_project_org = models.CharField(max_length=32000, db_column='Relation_referral_3_with_project_org__c')

    # Phase dates
    date_pitch_created = models.DateField(db_column='Date_pitch_created__c')
    date_pitch_submitted = models.DateField(db_column='Date_pitch_submitted__c')
    date_pitch_approved = models.DateField(db_column='Date_pitch_approved__c')
    date_pitch_rejected = models.DateField(db_column='Date_pitch_rejected__c')
    date_plan_submitted = models.DateField(db_column='Date_plan_submitted__c')
    date_plan_approved = models.DateField(db_column='Date_plan_approved__c')
    date_plan_rejected = models.DateField(db_column='Date_plan_rejected__c')
    date_project_act = models.DateField(db_column='Date_project_act__c')
    date_project_realized = models.DateField(db_column='Date_project_realized__c')
    date_project_failed = models.DateField(db_column='Date_project_failed__c')
    date_project_result = models.DateField(db_column='Date_project_result__c')

    # SF Layout: Project Team Information section.
    project_created_date = models.DateField(db_column='Project_created_date__c')
    date_project_deadline = models.DateField(db_column='Date_project_deadline__c')

    # SF Layout: Other section.
    external_id = models.CharField(max_length=255, db_column='Project_External_ID__c')

    # SF: Additional requirement not implemented yet - SFDC - Sheet 1
    number_of_people_reached_direct = models.PositiveIntegerField(max_length=18, db_column='NumberOfPeopleReachedDirect__c')
    number_of_people_reached_indirect = models.PositiveIntegerField(max_length=18, db_column='NumberOfPeopleReachedIndirect__c')
    # theme = models.CharField(max_length=255, db_column='Theme__c')
    target_group = models.CharField(max_length=255, db_column='Target_group__c')

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

    # SF Layout: Information section
    category = models.CharField(max_length=255, db_column='Category__c', choices=ProjectBudgetCategory.choices, help_text=_("Category"))
    costs = models.CharField(max_length=255, db_column='Costs__c')
    description = models.CharField(max_length=32000, db_column='Description__c')
    external_id = models.CharField(max_length=255, db_column='Project_Budget_External_ID__c')
    project = models.ForeignKey(SalesforceProject, db_column='Project__c')

    class Meta:
        db_table = 'Project_Budget__c'
        managed = False


payment_method_mapping = {
    'IDEAL': 'iDEAL',
    'MASTERCARD': 'Mastercard',
    'VISA': 'Visa',
    'DIRECT_DEBIT': 'Direct debit',
    'ideal-rabobank-1procentclub_nl': 'iDEAL',
    'paypal-1procentclub_nl': 'PayPal',
    'omnipay-ems-visa-1procentclub_nl': 'Visa',
    'banksys-mrcash-1procentclub_nl': 'Other',
    'ing-ideal-1procentclub_nl': 'iDEAL',
    'SOFORT_UEBERWEISUNG-SofortUeberweisung-1procentclub_nl': 'Other',
    'ideal-ing-1procentclub_nl': 'iDEAL',
    'system-banktransfer-nl': 'Bank transfer',
    'directdebitnc-online-nl': 'Direct debit',
    'directdebitnc2-online-nl': 'Direct debit',
    'omnipay-ems-maestro-1procentclub_nl': 'Other',
    '': 'Unknown',
    'omnipay-ems-mc-1procentclub_nl': 'Mastercard',
    'EBANKING': 'Other',
    'SOFORT_UEBERWEISUNG': 'Other',
    'MAESTRO': 'Other',
    'MISTERCASH': 'Other',
}


class SalesforceOpportunity(SalesforceModel):
    """
    Default abstract Salesforce Opportunity model. Used for Donation(s) / Voucher(s).
    """
    # SF Layout: Donation Information section.
    amount = models.CharField(max_length=255, db_column='Amount')
    close_date = models.DateField(db_column='CloseDate')
    opportunity_type = models.CharField(max_length=40,
                                        db_column='Type')
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
    # SF Layout: Donation Information section.
    # organization = models.ForeignKey(SalesforceOrganization, db_column='Project_Organization__c')

    # SF Layout: Additional Information section.

    # SF Layout: Description Information section.

    # SF Layout: System Information section.
    donation_created_date = models.DateField(db_column='Donation_created_date__c')

    # SF: Other.
    external_id_donation = models.CharField(max_length=255, db_column='Donation_External_ID__c')
    receiver = models.ForeignKey(SalesforceContact, db_column='Receiver__c', null=True)

    class Meta:
        managed = False
        db_table = 'Opportunity'


class SalesforceVoucher(SalesforceOpportunity):
    """
    Child of the Opportunity for Onepercentclub the mapping is named Voucher(s).
    """
    # SF Layout: Donation Information section.
    purchaser = models.ForeignKey(SalesforceContact, db_column='Purchaser__c', related_name='contact_purchasers')

    # SF Layout: Additional Information section.
    description = models.CharField(max_length=32000, db_column='Description')

    # SF Layout: System Information section.
    receiver = models.ForeignKey(SalesforceContact, db_column='Receiver__c', related_name='contact_receivers', null=True)

    # SF Other.
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

    # SF Layout: Information section.
    project = models.ForeignKey(SalesforceProject, db_column='Project__c')
    deadline = models.CharField(max_length=10000, db_column='Deadline__c')
    effort = models.CharField(max_length=10000, db_column='Effort__c')
    extended_task_description = models.CharField(max_length=32000, db_column='Extended_task_description__c')
    location_of_the_task = models.CharField(max_length=10000, db_column='Location_of_the_task__c')
    short_task_description = models.CharField(max_length=10000, db_column='Short_task_description__c')
    task_expertise = models.CharField(max_length=10000, db_column='Task_expertise__c')
    task_status = models.CharField(max_length=40, db_column='Task_status__c', choices=TaskStatus.choices, help_text=_("TaskStatus"))
    title = models.CharField(max_length=255, db_column='Title__c')
    task_created_date = models.DateField(max_length=255, db_column='Task_created_date__c')
    tags = models.CharField(max_length=400, db_column='Tags__c')

    # SF Layout: System Information section.

    # SF: Additional requirement not implemented yet - SFDC - Sheet 1
    effort_in_hours_del = models.PositiveIntegerField(max_length=19, db_column='EffortInHours_del__c')

    # SF: Other
    external_id = models.CharField(max_length=255, db_column='Task_External_ID__c')

    class Meta:
        db_table = 'onepercentclubTasks__c'
        managed = False


class SalesforceTaskMembers(SalesforceModel):
    """
    Custom Salesforce Task_Members__c model. For Onepercentclub the mapping is named Task Member(s).
    The table is used as a joined table which relates to Tasks to the Contacts.
    """
    # SF Layout: Information section.
    contacts = models.ForeignKey(SalesforceContact, db_column='Contacts__c')
    x1_club_task = models.ForeignKey(SalesforceTask, db_column='X1_CLUB_Task__c')
    external_id = models.CharField(max_length=100, db_column='Task_Member_External_ID__c')

    class Meta:
        db_table = 'Task_Members__c'
        managed = False


class SalesforceLoginHistory(SalesforceModel):
    """
    Custom X1_CLUB_Login_History__c model. For Onepercentclub the mapping is named 1%CLUB Login History.
    New mapping to be added later on.
    """

    # SF: Additional requirement not implemented yet - Website (back office) - Sheet 3
    bounce_rate_from_first_page = models.CharField(max_length=6, db_column='Bounce_rate_from_first_page__c')
    contacts = models.ForeignKey(SalesforceContact, db_column='Contacts__c')
    engagement_on_facebook = models.PositiveIntegerField(max_length=8, db_column='Engagement_on_Facebook__c')
    engagement_on_twitter = models.PositiveIntegerField(max_length=8, db_column='Engagement_on_Twitter__c')
    number_of_pageviews = models.PositiveIntegerField(max_length=8, db_column='Number_of_pageviews__c')
    online_engagement_blogs = models.PositiveIntegerField(max_length=8, db_column='Online_engagement_blogs__c')
    online_engagement_projects = models.PositiveIntegerField(max_length=8, db_column='Online_engagement_projects__c')
    online_engagement_reactions_to_members = models.PositiveIntegerField(max_length=8, db_column='Online_engagement_reactions_to_members__c')
    online_engagement_tasks = models.PositiveIntegerField(max_length=8, db_column='Online_engagement_tasks__c')
    preferred_navigation_path = models.PositiveIntegerField(max_length=255, db_column='Preferred_navigation_path__c')
    shares_via_social_media = models.PositiveIntegerField(max_length=8, db_column='Shares_via_social_media__c')
    size_of_basket = models.PositiveIntegerField(max_length=8, db_column='Size_of_basket__c')
    time_on_website = models.PositiveIntegerField(max_length=6, db_column='Time_on_website__c')

    class Meta:
        db_table = 'X1_CLUB_Login_History__c'
        managed = False


# Other Salesforce models available from Force.com IDE (Eclipse based)
# - ActivityHistory, AddtionalNumber, AggregateResult
# - ApexClass, ApexComponent, ApexLog, ApexTestQueueItem, ApexTestResult, ApexTrigger
# - Approval, Asset, AssetFeed, AssignmentRule, AsyncApexJob, Attachment, AuthProvider
# - BrandTemplate, Bug_Feed, Bug__c, BusinessHours, BusinessProcess
# - CallCenter, Campaign, CampaignFeed, CampaignMember, CampaignMemberStatus, CampaignShare
# - Case, CaseComment, CaseContactRole, CaseFeed, CaseHistory, CaseShare, CaseSolution, CaseTeamMember
# - CaseTeamRole, CaseTeamTemplate, CaseTeamTemplateMember, CaseTeamTemplateRecord
# - CategoryData, CategoryNode, CategoryNodeLocalization, ChatterActivity, ClientBrowser
# - CollaborationGroup, CollaborationGroupFeed, CollaborationGroupMember, CollaborationGrouopMemberRequest
# And so on
