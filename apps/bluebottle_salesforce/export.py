import csv
import logging
import os
from django.utils import timezone
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from apps.fund.models import Donation, DonationStatuses, Voucher, VoucherStatuses, OrderItem
from apps.organizations.models import Organization, OrganizationAddress
from apps.accounts.models import BlueBottleUser
from apps.projects.models import Project, ProjectCampaign, ProjectPitch, ProjectPlan, ProjectBudgetLine, ProjectPhases
from apps.tasks.models import Task, TaskMember

logger = logging.getLogger(__name__)

# TODO get field names from model for csv header from SalesforceDonation._meta.fields


def generate_organizations_csv_file(loglevel):
    logger.setLevel(loglevel)
    error_count = 0
    success_count = 0

    filename = 'BLUE2SFDC_Organizations_{0}.csv'.format(timezone.localtime(timezone.now()).strftime('%Y%m%d'))
    with open(os.path.join(settings.PROJECT_ROOT, filename), 'wb') as csv_outfile:
        csvwriter = csv.writer(csv_outfile, quoting=csv.QUOTE_ALL)

        csvwriter.writerow(["Organization_External_Id__c", "Name", "Legal_status__c", "Description", "BillingCity",
                            "BillingStreet", "BillingPostalCode", "BillingCountry", "E_mail_address__c", "Phone",
                            "Website", "Address_bank__c", "Bank_account_name__c", "Bank_account_number__c",
                            "Bankname__c", "BIC_SWIFT__c", "Country_bank__c", "IBAN_number__c",
                            "Organization_created_date__c"])

        organizations = Organization.objects.all()

        logger.info("Exporting {0} Organization objects to {1}".format(organizations.count(), filename))

        # Ignore address type and only use first address.
        # When multiple address types are supported in the website, extend this function
        for organization in organizations:
            try:
                billing_city = ''
                billing_street = ''
                billing_postal_code = ''
                billing_country = ''
                try:
                    organizationaddress = OrganizationAddress.objects.get(organization=organization)
                    billing_city = organizationaddress.city
                    billing_street = organizationaddress.line1 + " " + organizationaddress.line2
                    billing_postal_code = organizationaddress.postal_code
                    if organizationaddress.country:
                        billing_country = organizationaddress.country.name
                    else:
                        billing_country = ''
                except OrganizationAddress.DoesNotExist:
                    pass
                except OrganizationAddress.MultipleObjectsReturned:
                    logger.warn("Organization id {0} has multiple addresses, this is not supported.".format(
                        organization.id))

                if organization.account_bank_country:
                    bank_country = organization.account_bank_country.name
                else:
                    bank_country = ''

                csvwriter.writerow([organization.id,
                                    organization.name.encode("utf-8"),
                                    organization.legal_status.encode("utf-8"),
                                    organization.description.encode("utf-8"),
                                    billing_city.encode("utf-8"),
                                    billing_street.encode("utf-8"),
                                    billing_postal_code.encode("utf-8"),
                                    billing_country.encode("utf-8"),
                                    organization.email.encode("utf-8"),
                                    organization.phone_number.encode("utf-8"),
                                    organization.website.encode("utf-8"),
                                    organization.account_bank_address.encode("utf-8"),
                                    organization.account_bank_name.encode("utf-8"),
                                    organization.account_number.encode("utf-8"),
                                    organization.name.encode("utf-8"),
                                    organization.account_bic.encode("utf-8"),
                                    bank_country.encode("utf-8"),
                                    organization.account_iban.encode("utf-8"),
                                    organization.created.date()])
                success_count += 1
            except Exception as e:
                error_count += 1
                logger.error("Error while saving organization id {0}: ".format(organization.id) + str(e))

    return success_count, error_count


def generate_users_csv_file(loglevel):
    logger.setLevel(loglevel)
    error_count = 0
    success_count = 0

    filename = 'BLUE2SFDC_Users_{0}.csv'.format(timezone.localtime(timezone.now()).strftime('%Y%m%d'))
    with open(os.path.join(settings.PROJECT_ROOT, filename), 'wb') as csv_outfile:
        csvwriter = csv.writer(csv_outfile, quoting=csv.QUOTE_ALL)

        csvwriter.writerow(["Contact_External_Id__c", "Category1__c", "FirstName", "LastName", "Gender__c",
                            "Username__c", "Active__c", "Deleted__c", "Member_since__c", "Why_onepercent_member__c",
                            "About_me_us__c", "Location__c", "Birthdate", "Email", "Website__c", "MailingCity",
                            "MailingStreet", "MailingCountry", "MailingPostalCode", "MailingState",
                            "Receive_newsletter__c", "Primary_language__c"])

        users = BlueBottleUser.objects.all()

        logger.info("Exporting {0} User objects to {1}".format(users.count(), filename))

        for user in users:
            try:
                if user.address:
                    mailing_city = user.address.city
                    mailing_street = user.address.line1 + '\n' + user.address.line2
                    if user.address.country:
                        mailing_country = user.address.country.name
                    else:
                        mailing_country = ''
                    mailing_postal_code = user.address.postal_code
                    mailing_state = user.address.state
                else:
                    mailing_city = ''
                    mailing_street = ''
                    mailing_country = ''
                    mailing_postal_code = ''
                    mailing_state = ''

                if user.last_name:
                    last_name = user.last_name
                else:
                    last_name = "1%MEMBER"

                gender = ""
                if user.gender == "male":
                    gender = BlueBottleUser.Gender.values['male'].title()
                elif user.gender == "female":
                    gender = BlueBottleUser.Gender.values['female'].title()

                date_deleted = ""
                if user.deleted:
                    date_deleted = user.deleted.date()

                date_joined = ""
                if user.date_joined:
                    date_joined = user.date_joined.date()

                csvwriter.writerow([user.id,
                                    BlueBottleUser.UserType.values[user.user_type].title(),
                                    user.first_name.encode("utf-8"),
                                    last_name.encode("utf-8"),
                                    gender,
                                    user.username.encode("utf-8"),
                                    user.is_active,
                                    date_deleted,
                                    date_joined,
                                    user.why.encode("utf-8"),
                                    user.about.encode("utf-8"),
                                    user.location.encode("utf-8"),
                                    user.birthdate,
                                    user.email.encode("utf-8"),
                                    user.website.encode("utf-8"),
                                    mailing_city.encode("utf-8"),
                                    mailing_street.encode("utf-8"),
                                    mailing_country.encode("utf-8"),
                                    mailing_postal_code.encode("utf-8"),
                                    mailing_state.encode("utf-8"),
                                    user.newsletter,
                                    user.primary_language.encode("utf-8")])
                success_count += 1
            except Exception as e:
                error_count += 1
                logger.error("Error while saving user id {0}: ".format(user.id) + str(e))

    return success_count, error_count


def generate_projects_csv_file(loglevel):
    logger.setLevel(loglevel)
    error_count = 0
    success_count = 0

    filename = 'BLUE2SFDC_Projects_{0}.csv'.format(timezone.localtime(timezone.now()).strftime('%Y%m%d'))
    with open(os.path.join(settings.PROJECT_ROOT, filename), 'wb') as csv_outfile:
        csvwriter = csv.writer(csv_outfile, quoting=csv.QUOTE_ALL)

        csvwriter.writerow(["Project_External_ID__c", "Project_name__c", "Project_Owner__c", "Status_project__c",
                            "Country_in_which_the_project_is_located__c", "Describe_the_project_in_one_sentence__c",
                            "Organization__c", "NumberOfPeopleReachedDirect__c", "Amount_at_the_moment__c",
                            "Amount_requested__c", "Amount_still_needed__c", "Project_created_date__c"])

        projects = Project.objects.all()

        logger.info("Exporting {0} Project objects to {1}".format(projects.count(), filename))

        for project in projects:
            try:
                try:
                    project_campaign = ProjectCampaign.objects.get(project=project)
                    amount_at_the_moment = project_campaign.money_donated
                    amount_requested = project_campaign.money_asked
                    amount_still_needed = project_campaign.money_needed
                except ProjectCampaign.DoesNotExist:
                    amount_at_the_moment = ''
                    amount_requested = ''
                    amount_still_needed = ''

                try:
                    project_pitch = ProjectPitch.objects.get(project=project)
                    if project_pitch.country:
                        country_in_which_the_project_is_located = project_pitch.country.name
                    else:
                        country_in_which_the_project_is_located = ''
                    describe_the_project_in_one_sentence = project_pitch.title
                except ProjectPitch.DoesNotExist:
                    country_in_which_the_project_is_located = ''
                    describe_the_project_in_one_sentence = ''

                try:
                    project_plan = ProjectPlan.objects.get(project=project)
                    # TODO: determine what should be in project target_group?
                    # sfproject.target_group = project.fundphase.impact_group
                    number_of_people_reached_direct = project_plan.reach
                except ProjectPlan.DoesNotExist:
                    number_of_people_reached_direct = ''

                organization_id = ''
                try:
                    project_plan = ProjectPlan.objects.get(project=project)
                    if project_plan.organization:
                        organization_id = project_plan.organization.id
                except ProjectPlan.DoesNotExist:
                    pass

                csvwriter.writerow([project.id,
                                    project.title.encode("utf-8"),
                                    project.owner.id,
                                    ProjectPhases.values[project.phase].title(),
                                    country_in_which_the_project_is_located.encode("utf-8"),
                                    describe_the_project_in_one_sentence.encode("utf-8"),
                                    organization_id,
                                    number_of_people_reached_direct,
                                    amount_at_the_moment,
                                    amount_requested,
                                    amount_still_needed,
                                    project.created.date()])
                success_count += 1
            except Exception as e:
                error_count += 1
                logger.error("Error while saving project id {0}: ".format(project.id) + str(e))

    return success_count, error_count


def generate_projectbudgetlines_csv_file(loglevel):
    logger.setLevel(loglevel)
    error_count = 0
    success_count = 0

    filename = 'BLUE2SFDC_Projectbudgetlines_{0}.csv'.format(timezone.localtime(timezone.now()).strftime('%Y%m%d'))
    with open(os.path.join(settings.PROJECT_ROOT, filename), 'wb') as csv_outfile:
        csvwriter = csv.writer(csv_outfile, quoting=csv.QUOTE_ALL)

        csvwriter.writerow(["Project_Budget_External_ID__c", "Project__c", "Costs__c", "Description__c"])

        budget_lines = ProjectBudgetLine.objects.all()

        logger.info("Exporting {0} ProjectBudgetLine objects to {1}".format(budget_lines.count(), filename))

        for budget_line in budget_lines:
            try:
                csvwriter.writerow([budget_line.id,
                                    budget_line.project_plan.id,
                                    '%01.2f' % (float(budget_line.amount) / 100),
                                    budget_line.description.encode("utf-8")])
                success_count += 1
            except Exception as e:
                error_count += 1
                logger.error("Error while saving projectbudgetline id {0}: ".format(budget_line.id) + str(e))

    return success_count, error_count


def generate_donations_csv_file(loglevel):
    logger.setLevel(loglevel)
    error_count = 0
    success_count = 0

    filename = 'BLUE2SFDC_Donations_{0}.csv'.format(timezone.localtime(timezone.now()).strftime('%Y%m%d'))
    with open(os.path.join(settings.PROJECT_ROOT, filename), 'wb') as csv_outfile:
        csvwriter = csv.writer(csv_outfile, quoting=csv.QUOTE_ALL)

        csvwriter.writerow(["Donation_External_ID__c", "Receiver__c", "Project__c", "Amount", "CloseDate", "Name",
                            "StageName", "Type", "Donation_created_date__c", "Payment_method__c", "RecordTypeId"])

        donations = Donation.objects.all()

        logger.info("Exporting {0} Donation objects to {1}".format(donations.count(), filename))

        for donation in donations:
            try:
                receiver_id = ''
                if donation.user:
                    receiver_id = donation.user.id

                project_id = ''
                if donation.project:
                    project_id = donation.project.id

                if donation.user and donation.user.get_full_name() != '':
                    name = donation.user.get_full_name()
                else:
                    name = "1%MEMBER"

                # Get the payment method from the associated order / payment
                oi = OrderItem.objects.filter(object_id=donation.id).get(
                    content_type=ContentType.objects.get_for_model(Donation))
                lp = oi.order.latest_payment
                if lp:
                    payment_method = lp.latest_docdata_payment.docdata_payment_method
                else:
                    payment_method = ''

                csvwriter.writerow([donation.id,                                            # Donation_External_ID__c
                                    receiver_id,                                            # Receiver__c
                                    project_id,                                             # Project__c
                                    '%01.2f' % (float(donation.amount) / 100),              # Amount
                                    donation.created.date(),                                # CloseDate
                                    name.encode("utf-8"),                                   # Name
                                    DonationStatuses.values[donation.status].title(),       # StageName
                                    donation.DonationTypes.values[donation.donation_type].title(),  # Type
                                    donation.created.date(),                                # Donation_created_date__c
                                    payment_method.encode("utf-8"),                         # Payment_method__c
                                    '012A0000000ZK6FIAW'])                                  # RecordTypeId

                success_count += 1
            except Exception as e:
                error_count += 1
                logger.error("Error while saving donation id {0}: ".format(donation.id) + str(e))

    return success_count, error_count


def generate_vouchers_csv_file(loglevel):
    logger.setLevel(loglevel)
    error_count = 0
    success_count = 0

    filename = 'BLUE2SFDC_Vouchers_{0}.csv'.format(timezone.localtime(timezone.now()).strftime('%Y%m%d'))
    with open(os.path.join(settings.PROJECT_ROOT, filename), 'wb') as csv_outfile:
        csvwriter = csv.writer(csv_outfile, quoting=csv.QUOTE_ALL)

        csvwriter.writerow(["Voucher_External_ID__c", "Purchaser__c", "Amount", "CloseDate", "Name", "Description",
                            "StageName", "RecordTypeId"])

        vouchers = Voucher.objects.all()

        logger.info("Exporting {0} Voucher objects to {1}".format(vouchers.count(), filename))

        for voucher in vouchers:
            try:

                if voucher.sender and voucher.sender.get_full_name() != '':
                    name = voucher.sender.get_full_name()
                else:
                    name = "1%MEMBER"

                csvwriter.writerow([voucher.id,                                             # Voucher_External_ID__c
                                    voucher.sender.id,                                      # Purchaser__c
                                    '%01.2f' % (float(voucher.amount) / 100),               # Amount
                                    voucher.created.date(),                                 # CloseDate
                                    name.encode("utf-8"),                                   # Name
                                    voucher.message.encode("utf-8"),                        # Description
                                    VoucherStatuses.values[voucher.status].title(),         # StageName
                                    '012A0000000BxfHIAS'])                                  # RecordTypeId
                success_count += 1
            except Exception as e:
                error_count += 1
                logger.error("Error while saving voucher id {0}: ".format(voucher.id) + str(e))

    return success_count, error_count


def generate_tasks_csv_file(loglevel):
    logger.setLevel(loglevel)
    error_count = 0
    success_count = 0

    filename = 'BLUE2SFDC_Tasks_{0}.csv'.format(timezone.localtime(timezone.now()).strftime('%Y%m%d'))
    with open(os.path.join(settings.PROJECT_ROOT, filename), 'wb') as csv_outfile:
        csvwriter = csv.writer(csv_outfile, quoting=csv.QUOTE_ALL)

        csvwriter.writerow(["Task_External_ID__c", "Project__c", "Deadline__c", "Effort__c",
                            "Extended_task_description__c", "Location_of_the_task__c", "Task_expertise__c",
                            "Task_status__c", "Title__c", "Task_created_date__c", "Tags__c"])

        tasks = Task.objects.all()

        logger.info("Exporting {0} Task objects to {1}".format(tasks.count(), filename))

        for task in tasks:

            tags = ""
            for tag in task.tags.all():
                tags = str(tag) + ", " + tags

            try:
                csvwriter.writerow([task.id,
                                    task.project.id,
                                    task.deadline.date(),
                                    task.time_needed.encode("utf-8"),
                                    task.description.encode("utf-8"),
                                    task.location.encode("utf-8"),
                                    task.expertise.encode("utf-8"),
                                    task.status.encode("utf-8"),
                                    task.title.encode("utf-8"),
                                    task.created.date(),
                                    tags])
                success_count += 1
            except Exception as e:
                error_count += 1
                logger.error("Error while saving task id {0}: ".format(task.id) + str(e))

    return success_count, error_count


def generate_taskmembers_csv_file(loglevel):
    logger.setLevel(loglevel)
    error_count = 0
    success_count = 0

    filename = 'BLUE2SFDC_Taskmembers_{0}.csv'.format(timezone.localtime(timezone.now()).strftime('%Y%m%d'))
    with open(os.path.join(settings.PROJECT_ROOT, filename), 'wb') as csv_outfile:
        csvwriter = csv.writer(csv_outfile, quoting=csv.QUOTE_ALL)

        csvwriter.writerow(["Task_Member_External_ID__c", "Contacts__c", "X1_CLUB_Task__c"])

        taskmembers = TaskMember.objects.all()

        logger.info("Exporting {0} TaskMember objects to {1}".format(taskmembers.count(), filename))

        for taskmember in taskmembers:
            try:
                csvwriter.writerow([taskmember.id,
                                    taskmember.member.id,
                                    taskmember.task.id])
                success_count += 1
            except Exception as e:
                error_count += 1
                logger.error("Error while saving taskmember id {0}: ".format(taskmember.id) + str(e))

    return success_count, error_count