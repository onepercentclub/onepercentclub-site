# from apps.bluebottle_salesforce.models import ProjectCountry
from django.db import models
from salesforce.models import SalesforceModel
from djchoices import DjangoChoices, ChoiceItem
from django.utils.translation import ugettext as _

# TODO: Change to Django EMail field instead CharField
# TODO: Create a Django function/method for CURRENCY decimal


class OpportunityPaymentMethod(DjangoChoices):
    dire = ChoiceItem('Direct Debit (Online)', label=_("Direct Debit (Online)"))
    idea = ChoiceItem('iDEAL', label=_("iDEAL"))
    mass = ChoiceItem('Mastercard', label=_("Mastercard"))
    over = ChoiceItem('Overboeking', label=_("Overboeking"))
    visa = ChoiceItem('VISA', label=_("VISA"))


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
    email_address = models.EmailField(max_length=80, db_column='E_mail_address__c')
    phone = models.CharField(max_length=40, db_column='Phone')
    website = models.URLField(max_length=255, db_column='Website')

    # SF Layout: Bank Account section.
    address_bank = models.CharField(max_length=255, db_column='Address_bank__c')
    bank_account_name = models.CharField(max_length=255, db_column='Bank_account_name__c')
    bank_account_number = models.CharField(max_length=40, db_column='Bank_account_number__c')
    bank_name = models.CharField(max_length=60, db_column='Bankname__c')
    bic_swift = models.CharField(max_length=40, db_column='BIC_SWIFT__c')
    country_bank = models.CharField(max_length=60, db_column='Country_bank__c')
    iban_number = models.CharField(max_length=255, db_column='IBAN_number__c')

    # SF Layout: Description section.
    description = models.CharField(max_length=32000, db_column='Description')

    # SF Layout: System Information.
    created_date = models.DateField(db_column='Organization_created_date__c')

    class Meta:
        db_table = 'Account'


class SalesforceContact(SalesforceModel):
    """
    Default Salesforce Contact model.
    """
    class ContactCategory1(DjangoChoices):
        stichting = ChoiceItem('Stichting')
        bedrijf = ChoiceItem('Bedrijf')
        particulier = ChoiceItem('Particulier')
        vereniging = ChoiceItem('Vereniging')
        school = ChoiceItem('School')

    class ContactGender(DjangoChoices):
        m = ChoiceItem('m')
        f = ChoiceItem('f')

    # SF Layout: Subscription section.
    category1 = models.CharField(max_length=255, db_column='Category1__c', choices=ContactCategory1.choices, help_text=_("Category"))
    email = models.CharField(max_length=80, db_column='Email')
    member_1_club = models.BooleanField(db_column='Member_1_club__c', default=True)
    user_name = models.CharField(max_length=255, db_column='Username__c')
    is_active = models.BooleanField(db_column='Active__c')

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
    gender = models.CharField(max_length=20, db_column='Gender__c', choices=ContactGender.choices, help_text=_("Gender"))
    mailing_city = models.CharField(max_length=40, db_column='MailingCity')
    mailing_country = models.CharField(max_length=40, db_column='MailingCountry')
    mailing_postal_code = models.CharField(max_length=20, db_column='MailingPostalCode')
    mailing_street = models.CharField(max_length=20, db_column='MailingStreet')
    mailing_state = models.CharField(max_length=80, db_column='MailingState')

    # SF Layout: My Skills section.
    which_1_would_you_like_to_contribute = models.CharField(max_length=32000, db_column='Which_1_would_you_like_to_contribute__c')
    available_time = models.CharField(max_length=255, db_column='Available_time__c')
    where = models.CharField(max_length=255, db_column='Where__c')

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

    class Meta:
        db_table = 'Contact'


class SalesforceProject(SalesforceModel):
    """
    Custom Salesforce Project__c model. For Onepercentclub the mapping is named 1%CLUB Project(s).
    """
    class ProjectStatus(DjangoChoices):
        closed = ChoiceItem('Closed', label=_("Closed"))
        created = ChoiceItem('Created', label=_("Created"))
        done = ChoiceItem('Done', label=_("Done"))
        validated = ChoiceItem('Validated', label=_("Validated"))

    # TODO Talk to Margreet about this: new website is leading -
    class ProjectCountry(DjangoChoices):
        afghanistan = ChoiceItem('Afghanistan', label=_("Afghanistan"))
        akrotiri = ChoiceItem('Akrotiri', label=_("Akrotiri"))
        albania = ChoiceItem('Albania', label=_("Albania"))
        algeria = ChoiceItem('Algeria', label=_("Algeria"))
        american_samoa = ChoiceItem('American Samoa', label=_("American Samoa"))
        andorra = ChoiceItem('Andorra', label=_("Andorra"))
        angola = ChoiceItem('Angola', label=_("Angola"))
        anguilla = ChoiceItem('Anguilla', label=_("Anguilla"))
        antarctica = ChoiceItem('Antarctica', label=_("Antarctica"))
        antigua_and_barbuda = ChoiceItem('Antigua and Barbuda', label=_("Antigua and Barbuda"))
        argentina = ChoiceItem('Argentina', label=_("Argentina"))
        armenia = ChoiceItem('Armenia', label=_("Armenia"))
        aruba = ChoiceItem('Aruba', label=_("Aruba"))
        ashmore_and_cartier_islands = ChoiceItem('Ashmore and Cartier Islands', label=_("Ashmore and Cartier Islands"))
        australia = ChoiceItem('Australia', label=_("Australia"))
        austria = ChoiceItem('Austria', label=_("Austria"))
        azerbaijan = ChoiceItem('Azerbaijan', label=_("Azerbaijan"))
        bahamas_the = ChoiceItem('Bahamas, The', label=_("Bahamas, The"))
        bahrain = ChoiceItem('Bahrain', label=_("Bahrain"))
        bangladesh = ChoiceItem('Bangladesh', label=_("Bangladesh"))
        barbados = ChoiceItem('Barbados', label=_("Barbados"))
        bassas_da_india = ChoiceItem('Bassas da India', label=_("Bassas da India"))
        belarus = ChoiceItem('Belarus', label=_("Belarus"))
        belgium = ChoiceItem('Belgium', label=_("Belgium"))
        belize = ChoiceItem('Belize', label=_("Belize"))
        benin = ChoiceItem('Benin', label=_("Benin"))
        bermuda = ChoiceItem('Bermuda', label=_("Bermuda"))
        bhutan = ChoiceItem('Bhutan', label=_("Bhutan"))
        bolivia = ChoiceItem('Bolivia', label=_("Bolivia"))
        bosnia_and_herzegovina = ChoiceItem('Bosnia and Herzegovina', label=_("Bosnia and Herzegovina"))
        botswana = ChoiceItem('Botswana', label=_("Botswana"))
        bouvet_island = ChoiceItem('Bouvet Island', label=_("Bouvet Island"))
        brazil = ChoiceItem('Brazil', label=_("Brazil"))
        british_indian_ocean_territory = ChoiceItem('British Indian Ocean Territory',label=_("British Indian Ocean Territory"))
        british_virgin_islands = ChoiceItem('British Virgin Islands', label=_("British Virgin Islands"))
        brunei = ChoiceItem('Brunei', label=_("Brunei"))
        bulgaria = ChoiceItem('Bulgaria', label=_("Bulgaria"))
        burkina_faso = ChoiceItem('Burkina Faso', label=_("Burkina Faso"))
        burma = ChoiceItem('Burma', label=_("Burma"))
        burundi = ChoiceItem('Burundi', label=_("Burundi"))
        cambodia = ChoiceItem('Cambodia', label=_("Cambodia"))
        cameroon = ChoiceItem('Cameroon', label=_("Cameroon"))
        canada = ChoiceItem('Canada', label=_("Canada"))
        cape_verde = ChoiceItem('Cape Verde', label=_("Cape Verde"))
        cayman_islands = ChoiceItem('Cayman Islands', label=_("Cayman Islands"))
        central_african_republic = ChoiceItem('Central African Republic', label=_("Central African Republic"))
        chad = ChoiceItem('Chad', label=_("Chad"))
        chile = ChoiceItem('Chile', label=_("Chile"))
        china = ChoiceItem('China', label=_("China"))
        christmas_island = ChoiceItem('Christmas Island', label=_("Christmas Island"))
        clipperton_island = ChoiceItem('Clipperton Island', label=_("Clipperton Island"))
        cocos_keeling_islands = ChoiceItem('Cocos (Keeling) Islands', label=_("Cocos (Keeling) Islands"))
        colombia = ChoiceItem('Colombia', label=_("Colombia"))
        comoros = ChoiceItem('Comoros', label=_("Comoros"))
        congo_democratic_republic_of_the = ChoiceItem('Congo, Democratic Republic of the',
                                                      label=_("Congo, Democratic Republic of the"))
        congo_republic_of_the = ChoiceItem('Congo, Republic of the', label=_("Congo, Republic of the"))
        cook_islands = ChoiceItem('Cook Islands', label=_("Cook Islands"))
        coral_sea_islands = ChoiceItem('Coral Sea Islands', label=_("Coral Sea Islands"))
        costa_rica = ChoiceItem('Costa Rica', label=_("Costa Rica"))
        cote_d_ivoire = ChoiceItem('Cote d\'Ivoire', label=_("Cote d'Ivoire"))
        croatia = ChoiceItem('Croatia', label=_("Croatia"))
        cuba = ChoiceItem('Cuba', label=_("Cuba"))
        cyprus = ChoiceItem('Cyprus', label=_("Cyprus"))
        czech_republic = ChoiceItem('Czech Republic', label=_("Czech Republic"))
        denmark = ChoiceItem('Denmark', label=_("Denmark"))
        dhekelia = ChoiceItem('Dhekelia', label=_("Dhekelia"))
        djibouti = ChoiceItem('Djibouti', label=_("Djibouti"))
        dominica = ChoiceItem('Dominica', label=_("Dominica"))
        dominican_republic = ChoiceItem('Dominican Republic', label=_("Dominican Republic"))
        ecuador = ChoiceItem('Ecuador', label=_("Ecuador"))
        egypt = ChoiceItem('Egypt', label=_("Egypt"))
        el_salvador = ChoiceItem('El Salvador', label=_("El Salvador"))
        equatorial_guinea = ChoiceItem('Equatorial Guinea', label=_("Equatorial Guinea"))
        eritrea = ChoiceItem('Eritrea', label=_("Eritrea"))
        estonia = ChoiceItem('Estonia', label=_("Estonia"))
        ethiopia = ChoiceItem('Ethiopia', label=_("Ethiopia"))
        europa_island = ChoiceItem('Europa Island', label=_("Europa Island"))
        falkland_islands_islas_malvinas = ChoiceItem('Falkland Islands (Islas Malvinas)',
                                                     label=_("Falkland Islands (Islas Malvinas)"))
        faroe_islands = ChoiceItem('Faroe Islands', label=_("Faroe Islands"))
        fiji = ChoiceItem('Fiji', label=_("Fiji"))
        finland = ChoiceItem('Finland', label=_("Finland"))
        france = ChoiceItem('France', label=_("France"))
        french_guiana = ChoiceItem('French Guiana', label=_("French Guiana"))
        french_polynesia = ChoiceItem('French Polynesia', label=_("French Polynesia"))
        french_southern_and_antarctic_lands = ChoiceItem('French Southern and Antarctic Lands',
                                                         label=_("French Southern and Antarctic Lands"))
        gabon = ChoiceItem('Gabon', label=_("Gabon"))
        gambia_the = ChoiceItem('Gambia, The', label=_("Gambia, The"))
        gaza_strip = ChoiceItem('Gaza Strip', label=_("Gaza Strip"))
        georgia = ChoiceItem('Georgia', label=_("Georgia"))
        germany = ChoiceItem('Germany', label=_("Germany"))
        ghana = ChoiceItem('Ghana', label=_("Ghana"))
        gibraltar = ChoiceItem('Gibraltar', label=_("Gibraltar"))
        glorioso_islands = ChoiceItem('Glorioso Islands', label=_("Glorioso Islands"))
        greece = ChoiceItem('Greece', label=_("Greece"))
        greenland = ChoiceItem('Greenland', label=_("Greenland"))
        grenada = ChoiceItem('Grenada', label=_("Grenada"))
        guadeloupe = ChoiceItem('Guadeloupe', label=_("Guadeloupe"))
        guam = ChoiceItem('Guam', label=_("Guam"))
        guatemala = ChoiceItem('Guatemala', label=_("Guatemala"))
        guernsey = ChoiceItem('Guernsey', label=_("Guernsey"))
        guinea = ChoiceItem('Guinea', label=_("Guinea"))
        guinea_bissau = ChoiceItem('Guinea-Bissau', label=_("Guinea-Bissau"))
        guyana = ChoiceItem('Guyana', label=_("Guyana"))
        haiti = ChoiceItem('Haiti', label=_("Haiti"))
        heard_island_and_mcdonald_islands = ChoiceItem('Heard Island and McDonald Islands',
                                                       label=_("Heard Island and McDonald Islands"))
        holy_see_vatican_city = ChoiceItem('Holy See (Vatican City)', label=_("Holy See (Vatican City)"))
        honduras = ChoiceItem('Honduras', label=_("Honduras"))
        hong_kong = ChoiceItem('Hong Kong', label=_("Hong Kong"))
        hungary = ChoiceItem('Hungary', label=_("Hungary"))
        iceland = ChoiceItem('Iceland', label=_("Iceland"))
        india = ChoiceItem('India', label=_("India"))
        indonesia = ChoiceItem('Indonesia', label=_("Indonesia"))
        iran = ChoiceItem('Iran', label=_("Iran"))
        iraq = ChoiceItem('Iraq', label=_("Iraq"))
        ireland = ChoiceItem('Ireland', label=_("Ireland"))
        isle_of_man = ChoiceItem('Isle of Man', label=_("Isle of Man"))
        israel = ChoiceItem('Israel', label=_("Israel"))
        italy = ChoiceItem('Italy', label=_("Italy"))
        jamaica = ChoiceItem('Jamaica', label=_("Jamaica"))
        jan_mayen = ChoiceItem('Jan Mayen', label=_("Jan Mayen"))
        japan = ChoiceItem('Japan', label=_("Japan"))
        jersey = ChoiceItem('Jersey', label=_("Jersey"))
        jordan = ChoiceItem('Jordan', label=_("Jordan"))
        juan_de_nova_island = ChoiceItem('Juan de Nova Island', label=_("Juan de Nova Island"))
        kazakhstan = ChoiceItem('Kazakhstan', label=_("Kazakhstan"))
        kenya = ChoiceItem('Kenya', label=_("Kenya"))
        kiribati = ChoiceItem('Kiribati', label=_("Kiribati"))
        korea_north = ChoiceItem('Korea, North', label=_("Korea, North"))
        korea_south = ChoiceItem('Korea, South', label=_("Korea, South"))
        kuwait = ChoiceItem('Kuwait', label=_("Kuwait"))
        kyrgyzstan = ChoiceItem('Kyrgyzstan', label=_("Kyrgyzstan"))
        laos = ChoiceItem('Laos', label=_("Laos"))
        latvia = ChoiceItem('Latvia', label=_("Latvia"))
        lebanon = ChoiceItem('Lebanon', label=_("Lebanon"))
        lesotho = ChoiceItem('Lesotho', label=_("Lesotho"))
        liberia = ChoiceItem('Liberia', label=_("Liberia"))
        libya = ChoiceItem('Libya', label=_("Libya"))
        liechtenstein = ChoiceItem('Liechtenstein', label=_("Liechtenstein"))
        lithuania = ChoiceItem('Lithuania', label=_("Lithuania"))
        luxembourg = ChoiceItem('Luxembourg', label=_("Luxembourg"))
        macau = ChoiceItem('Macau', label=_("Macau"))
        macedonia = ChoiceItem('Macedonia', label=_("Macedonia"))
        madagascar = ChoiceItem('Madagascar', label=_("Madagascar"))
        malawi = ChoiceItem('Malawi', label=_("Malawi"))
        malaysia = ChoiceItem('Malaysia', label=_("Malaysia"))
        maldives = ChoiceItem('Maldives', label=_("Maldives"))
        mali = ChoiceItem('Mali', label=_("Mali"))
        malta = ChoiceItem('Malta', label=_("Malta"))
        marshall_islands = ChoiceItem('Marshall Islands', label=_("Marshall Islands"))
        martinique = ChoiceItem('Martinique', label=_("Martinique"))
        mauritania = ChoiceItem('Mauritania', label=_("Mauritania"))
        mauritius = ChoiceItem('Mauritius', label=_("Mauritius"))
        mayotte = ChoiceItem('Mayotte', label=_("Mayotte"))
        mexico = ChoiceItem('Mexico', label=_("Mexico"))
        micronesia_federated_states_of = ChoiceItem('Micronesia, Federated States of',
                                                    label=_("Micronesia, Federated States of"))
        moldova = ChoiceItem('Moldova', label=_("Moldova"))
        monaco = ChoiceItem('Monaco', label=_("Monaco"))
        mongolia = ChoiceItem('Mongolia', label=_("Mongolia"))
        montserrat = ChoiceItem('Montserrat', label=_("Montserrat"))
        morocco = ChoiceItem('Morocco', label=_("Morocco"))
        mozambique = ChoiceItem('Mozambique', label=_("Mozambique"))
        namibia = ChoiceItem('Namibia', label=_("Namibia"))
        nauru = ChoiceItem('Nauru', label=_("Nauru"))
        navassa_island = ChoiceItem('Navassa Island', label=_("Navassa Island"))
        nepal = ChoiceItem('Nepal', label=_("Nepal"))
        netherlands = ChoiceItem('Netherlands', label=_("Netherlands"))
        netherlands_antilles = ChoiceItem('Netherlands Antilles', label=_("Netherlands Antilles"))
        new_caledonia = ChoiceItem('New Caledonia', label=_("New Caledonia"))
        new_zealand = ChoiceItem('New Zealand', label=_("New Zealand"))
        nicaragua = ChoiceItem('Nicaragua', label=_("Nicaragua"))
        niger = ChoiceItem('Niger', label=_("Niger"))
        nigeria = ChoiceItem('Nigeria', label=_("Nigeria"))
        niue = ChoiceItem('Niue', label=_("Niue"))
        norfolk_island = ChoiceItem('Norfolk Island', label=_("Norfolk Island"))
        northern_mariana_islands = ChoiceItem('Northern Mariana Islands', label=_("Northern Mariana Islands"))
        norway = ChoiceItem('Norway', label=_("Norway"))
        oman = ChoiceItem('Oman', label=_("Oman"))
        pakistan = ChoiceItem('Pakistan', label=_("Pakistan"))
        palau = ChoiceItem('Palau', label=_("Palau"))
        panama = ChoiceItem('Panama', label=_("Panama"))
        papua_new_guinea = ChoiceItem('Papua New Guinea', label=_("Papua New Guinea"))
        paracel_islands = ChoiceItem('Paracel Islands', label=_("Paracel Islands"))
        paraguay = ChoiceItem('Paraguay', label=_("Paraguay"))
        peru = ChoiceItem('Peru', label=_("Peru"))
        philippines = ChoiceItem('Philippines', label=_("Philippines"))
        pitcairn_islands = ChoiceItem('Pitcairn Islands', label=_("Pitcairn Islands"))
        poland = ChoiceItem('Poland', label=_("Poland"))
        portugal = ChoiceItem('Portugal', label=_("Portugal"))
        puerto_rico = ChoiceItem('Puerto Rico', label=_("Puerto Rico"))
        qatar = ChoiceItem('Qatar', label=_("Qatar"))
        reunion = ChoiceItem('Reunion', label=_("Reunion"))
        romania = ChoiceItem('Romania', label=_("Romania"))
        russia = ChoiceItem('Russia', label=_("Russia"))
        rwanda = ChoiceItem('Rwanda', label=_("Rwanda"))
        saint_helena = ChoiceItem('Saint Helena', label=_("Saint Helena"))
        saint_kitts_and_nevis = ChoiceItem('Saint Kitts and Nevis', label=_("Saint Kitts and Nevis"))
        saint_lucia = ChoiceItem('Saint Lucia', label=_("Saint Lucia"))
        saint_pierre_and_miquelon = ChoiceItem('Saint Pierre and Miquelon', label=_("Saint Pierre and Miquelon"))
        saint_vincent_and_the_grenadines = ChoiceItem('Saint Vincent and the Grenadines',
                                                      label=_("Saint Vincent and the Grenadines"))
        samoa = ChoiceItem('Samoa', label=_("Samoa"))
        san_marino = ChoiceItem('San Marino', label=_("San Marino"))
        sao_tome_and_principe = ChoiceItem('Sao Tome and Principe', label=_("Sao Tome and Principe"))
        saudi_arabia = ChoiceItem('Saudi Arabia', label=_("Saudi Arabia"))
        senegal = ChoiceItem('Senegal', label=_("Senegal"))
        serbia_and_montenegro = ChoiceItem('Serbia and Montenegro', label=_("Serbia and Montenegro"))
        seychelles = ChoiceItem('Seychelles', label=_("Seychelles"))
        sierra_leone = ChoiceItem('Sierra Leone', label=_("Sierra Leone"))
        singapore = ChoiceItem('Singapore', label=_("Singapore"))
        slovakia = ChoiceItem('Slovakia', label=_("Slovakia"))
        slovenia = ChoiceItem('Slovenia', label=_("Slovenia"))
        solomon_islands = ChoiceItem('Solomon Islands', label=_("Solomon Islands"))
        somalia = ChoiceItem('Somalia', label=_("Somalia"))
        south_africa = ChoiceItem('South Africa', label=_("South Africa"))
        south_georgia_and_the_south_sandwich_islands = ChoiceItem('South Georgia and the South Sandwich Islands',
                                                                  label=_("South Georgia and the South Sandwich Islands"))
        spain = ChoiceItem('Spain', label=_("Spain"))
        spratly_islands = ChoiceItem('Spratly Islands', label=_("Spratly Islands"))
        sri_lanka = ChoiceItem('Sri Lanka', label=_("Sri Lanka"))
        sudan = ChoiceItem('Sudan', label=_("Sudan"))
        suriname = ChoiceItem('Suriname', label=_("Suriname"))
        svalbard = ChoiceItem('Svalbard', label=_("Svalbard"))
        swaziland = ChoiceItem('Swaziland', label=_("Swaziland"))
        sweden = ChoiceItem('Sweden', label=_("Sweden"))
        switzerland = ChoiceItem('Switzerland', label=_("Switzerland"))
        syria = ChoiceItem('Syria', label=_("Syria"))
        taiwan = ChoiceItem('Taiwan', label=_("Taiwan"))
        tajikistan = ChoiceItem('Tajikistan', label=_("Tajikistan"))
        tanzania = ChoiceItem('Tanzania', label=_("Tanzania"))
        thailand = ChoiceItem('Thailand', label=_("Thailand"))
        timor_leste = ChoiceItem('Timor-Leste', label=_("Timor-Leste"))
        togo = ChoiceItem('Togo', label=_("Togo"))
        tokelau = ChoiceItem('Tokelau', label=_("Tokelau"))
        tonga = ChoiceItem('Tonga', label=_("Tonga"))
        trinidad_and_tobago = ChoiceItem('Trinidad and Tobago', label=_("Trinidad and Tobago"))
        tromelin_island = ChoiceItem('Tromelin Island', label=_("Tromelin Island"))
        tunisia = ChoiceItem('Tunisia', label=_("Tunisia"))
        turkey = ChoiceItem('Turkey', label=_("Turkey"))
        turkmenistan = ChoiceItem('Turkmenistan', label=_("Turkmenistan"))
        turks_and_caicos_islands = ChoiceItem('Turks and Caicos Islands', label=_("Turks and Caicos Islands"))
        tuvalu = ChoiceItem('Tuvalu', label=_("Tuvalu"))
        uganda = ChoiceItem('Uganda', label=_("Uganda"))
        ukraine = ChoiceItem('Ukraine', label=_("Ukraine"))
        united_arab_emirates = ChoiceItem('United Arab Emirates', label=_("United Arab Emirates"))
        united_kingdom = ChoiceItem('United Kingdom', label=_("United Kingdom"))
        united_states = ChoiceItem('United States', label=_("United States"))
        uruguay = ChoiceItem('Uruguay', label=_("Uruguay"))
        uzbekistan = ChoiceItem('Uzbekistan', label=_("Uzbekistan"))
        vanuatu = ChoiceItem('Vanuatu', label=_("Vanuatu"))
        venezuela = ChoiceItem('Venezuela', label=_("Venezuela"))
        vietnam = ChoiceItem('Vietnam', label=_("Vietnam"))
        virgin_islands = ChoiceItem('Virgin Islands', label=_("Virgin Islands"))
        wake_island = ChoiceItem('Wake Island', label=_("Wake Island"))
        wallis_and_futuna = ChoiceItem('Wallis and Futuna', label=_("Wallis and Futuna"))
        west_bank = ChoiceItem('West Bank', label=_("West Bank"))
        western_sahara = ChoiceItem('Western Sahara', label=_("Western Sahara"))
        yemen = ChoiceItem('Yemen', label=_("Yemen"))
        zambia = ChoiceItem('Zambia', label=_("Zambia"))
        zimbabwe = ChoiceItem('Zimbabwe', label=_("Zimbabwe"))

    # SF Layout: 1%CLUB Project Detail section.
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

    # SF Layout: Summary Project Details section.
    country_in_which_the_project_is_located = models.CharField(max_length=255,
                                                               db_column='Country_in_which_the_project_is_located__c',
                                                               choices=ProjectCountry.choices,
                                                               help_text=_("Country in which the project is located"))
    describe_the_project_in_one_sentence = models.CharField(max_length=50000, db_column='Describe_the_project_in_one_sentence__c')
    describe_where_the_money_is_needed_for = models.CharField(max_length=15000, db_column='Describe_where_the_money_is_needed_for__c')
    project_url = models.URLField(max_length=255, db_column='Projecturl__c')

    # SF Layout: Extensive project information section.
    third_half_project = models.BooleanField(db_column='third_half_project__c')
    organization_account = models.ForeignKey(SalesforceOrganization, db_column='Organization__c')
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

    # SF Layout: Project Team Information section.
    project_created_date = models.DateField(db_column='Project_created_date__c')

    # SF Layout: International Payment section.

    # SF Layout: Other section.
    external_id = models.CharField(max_length=255, db_column='Project_External_ID__c')

    class Meta:
        db_table = 'Project__c'


class SalesforceProjectBudget(SalesforceModel):
    """
    Custom Salesforce Project_Budget__c model. For Onepercentclub the mapping is named Project Budget.
    """
    class ProjectBudgetCategory(DjangoChoices):
        contruction = ChoiceItem('Construction materials', label=_("Construction materials"))
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
    project_budget_external_id = models.CharField(max_length=255, db_column='Project_Budget_External_ID__c')
    # Master detail reference: project = models.CharField(max_length=255, db_column='Project__c')

    class Meta:
        db_table = 'Project_Budget__c'


class SalesforceDonation(SalesforceModel):
    """
    Default Salesforce Opportunity model. For Onepercentclub the mapping is named Donation(s).
    """
    class OpportunityStageName(DjangoChoices):
        new = ChoiceItem('New', label=_("New"))
        sta = ChoiceItem('Started', label=_("Started"))
        pos = ChoiceItem('Posted', label=_("Posted"))
        wit = ChoiceItem('Withdrawn', label=_("Withdrawn"))
        tra = ChoiceItem('Transfered', label=_("Transfered"))

    # SF Layout: Donation Information section.
    amount = models.CharField(max_length=255, db_column='Amount')
    close_date = models.DateField(db_column='CloseDate')
    name = models.CharField(max_length=120, db_column='Name')
    payment_method = models.CharField(max_length=255,
                                      db_column='Payment_method__c',
                                      choices=OpportunityPaymentMethod.choices,
                                      help_text=_("PaymentMethod"))
    organization = models.ForeignKey(SalesforceOrganization, db_column='Project_Organization__c')
    project = models.ForeignKey(SalesforceProject, db_column='Project__c')
    stage_name = models.CharField(max_length=40, db_column='StageName', choices=OpportunityStageName.choices, help_text=_("StageName"))
    donation_type = models.CharField(max_length=1000, db_column='Type')

    # SF Layout: Additional Information section.

    # SF Layout: Description Information section.

    # SF Layout: System Information section.
    donation_created_date = models.DateField(db_column='Donation_created_date__c')

    # SF: Other.
    # TODO: check the maximum positive integer..Note!!!! id will be newly generated
    external_id = models.CharField(max_length=255, db_column='Donation_External_ID__c')
    receiver = models.ForeignKey(SalesforceContact, db_column='Receiver__c')

    class Meta:
        db_table = 'Opportunity'


# TODO: Ask github if different recordtypes on Opportunity for example is the intended behaviour.
# Currently if db_table = Opportunity is supplied the syncdb will fail!
# class SalesforceVoucher(SalesforceModel):
#     """
#     Default Salesforce Opportunity model. For Onepercentclub the mapping is named Vouchers(s).
#     """
#     # SF Layout: Donation Information section.
#     amount = models.CharField(max_length=255, db_column='Amount')
#     close_date = models.DateField(db_column='CloseDate')
#     name = models.CharField(max_length=120, db_column='Name')
#     payment_method = models.CharField(max_length=255,
#                                       db_column='Payment_method__c',
#                                       choices=OpportunityPaymentMethod.choices,
#                                       help_text=_("PaymentMethod"))
#     project = models.CharField(max_length=255, db_column='Project__c')
#     purchaser = models.CharField(max_length=255, db_column='Purchaser__c')
#     stage_name = models.CharField(max_length=255, db_column='StageName')
#     voucher_type = models.CharField(max_length=255, db_column='Type')
#     record_type = models.CharField(max_length=255, db_column='RecordType')
#
#     # SF Layout: Additional Information section.
#     description = models.CharField(max_length=32000, db_column='Description')
#
#     # SF Layout: System Information section.
#     receiver = models.CharField(max_length=255, db_column='Receiver__c')
#
#     # SF Other.
#     voucher_id = models.CharField(max_length=255, db_column='ID')
#     donation_external_id = models.CharField(max_length=255, db_column='Donation_External_ID__c')
#
#     class Meta:
#         db_table = 'Opportunity'


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
    project = models.CharField(max_length=255, db_column='Project__c')
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

    # SF: Other
    external_id = models.CharField(max_length=255, db_column='Task_External_ID__c')

    class Meta:
        db_table = 'onepercentclubTasks__c'


class SalesforceTaskMembers(SalesforceModel):
    """
    Custom Salesforce Task_Members__c model. For Onepercentclub the mapping is named Task Member(s).
    The table is used as a joined table which relates to Tasks to the Contacts.
    """
    # SF Layout: Information section.
    #Master detail: contacts = models.CharField(max_length=255, db_column='Contacts__c')
    #Master detail: x1_club_task = models.CharField(max_length=255, db_column='X1_CLUB_Task__c')
    task_member_external_id = models.CharField(max_length=100, db_column='Task_Member_External_ID__c')

    class Meta:
        db_table = 'Task_Members__c'


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
