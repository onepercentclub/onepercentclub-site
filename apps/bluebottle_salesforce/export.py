import csv
import logging
from bluebottle.projects.models import ProjectBudgetLine
from bluebottle.payments.models import OrderPayment
import os
from registration.models import RegistrationProfile
from django.utils import timezone
from django.conf import settings
from apps.cowry_docdata.models import payment_method_mapping
from apps.fund.models import Donation, DonationStatuses
from apps.recurring_donations.models import MonthlyDonor
from apps.vouchers.models import Voucher, VoucherStatuses
from apps.organizations.models import Organization, OrganizationMember
from bluebottle.fundraisers.models import Fundraiser
from bluebottle.tasks.models import Task, TaskMember
from bluebottle.projects.models import Project
from bluebottle.members.models import Member

logger = logging.getLogger('bluebottle.salesforce')


def generate_organizations_csv_file(path, loglevel):
    logger.setLevel(loglevel)
    error_count = 0
    success_count = 0

    filename = 'BLUE2SFDC_Organizations.csv'
    with open(os.path.join(path, filename), 'wb') as csv_outfile:
        csvwriter = csv.writer(csv_outfile, quoting=csv.QUOTE_MINIMAL)

        csvwriter.writerow(["Organization_External_Id__c",
                            "Name",
                            "BillingStreet",
                            "BillingCity",
                            "BillingState",
                            "BillingCountry",
                            "BillingPostalCode",
                            "E_mail_address__c",
                            "Phone",
                            "Website",
                            "Twitter__c",
                            "Facebook__c",
                            "Skype__c",
                            "Tags__c",
                            "Bank_account_name__c",
                            "Bank_account_address__c",
                            "Bank_account_postalcode__c",
                            "Bank_account_city__c",
                            "Bank_account_country__c",
                            "Bank_account_IBAN__c",
                            "Bank_SWIFT__c",
                            "Bank_account_number__c",
                            "Bank_bankname__c",
                            "Bank_address__c",
                            "Bank_postalcode__c",
                            "Bank_city__c",
                            "Bank_country__c",
                            "Organization_created_date__c",
                            "Deleted__c"])

        organizations = Organization.objects.all()

        logger.info("Exporting {0} Organization objects to {1}".format(organizations.count(), filename))

        for organization in organizations:
            try:
                billing_street = organization.address_line1 + " " + organization.address_line2

                if organization.country:
                    billing_country = organization.country.name
                else:
                    billing_country = ''

                if organization.account_bank_country:
                    bank_country = organization.account_bank_country.name
                else:
                    bank_country = ''

                if organization.account_holder_country:
                    bank_account_country = organization.account_holder_country.name
                else:
                    bank_account_country = ''

                tags = ""
                for tag in organization.tags.all():
                    tags = str(tag) + ", " + tags

                deleted = ""
                if organization.deleted:
                    deleted = organization.deleted.strftime("%Y-%m-%dT%H:%M:%S.000Z")

                csvwriter.writerow([organization.id,
                                    organization.name.encode("utf-8"),
                                    billing_street.encode("utf-8"),
                                    organization.city[:40].encode("utf-8"),
                                    organization.state.encode("utf-8"),
                                    billing_country.encode("utf-8"),
                                    organization.postal_code.encode("utf-8"),
                                    organization.email.encode("utf-8"),
                                    organization.phone_number.encode("utf-8"),
                                    organization.website.encode("utf-8"),
                                    organization.twitter.encode("utf-8"),
                                    organization.facebook.encode("utf-8"),
                                    organization.skype.encode("utf-8"),
                                    tags.encode("utf-8"),
                                    organization.account_holder_name.encode("utf-8"),
                                    organization.account_holder_address.encode("utf-8"),
                                    organization.account_holder_postal_code.encode("utf-8"),
                                    organization.account_holder_city.encode("utf-8"),
                                    bank_account_country.encode("utf-8"),
                                    organization.account_iban.encode("utf-8"),
                                    organization.account_bic.encode("utf-8"),
                                    organization.account_number.encode("utf-8"),
                                    organization.account_bank_name.encode("utf-8"),
                                    organization.account_bank_address.encode("utf-8"),
                                    organization.account_bank_postal_code.encode("utf-8"),
                                    organization.account_bank_city.encode("utf-8"),
                                    bank_country.encode("utf-8"),
                                    organization.created.date().strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                                    deleted])
                success_count += 1
            except Exception as e:
                error_count += 1
                logger.error("Error while saving organization id {0}: ".format(organization.id) + str(e))

    return success_count, error_count


def generate_users_csv_file(path, loglevel):
    logger.setLevel(loglevel)
    error_count = 0
    success_count = 0

    filename = 'BLUE2SFDC_Users.csv'
    with open(os.path.join(path, filename), 'wb') as csv_outfile:
        csvwriter = csv.writer(csv_outfile, quoting=csv.QUOTE_ALL)

        csvwriter.writerow(["Contact_External_Id__c",
                            "Category1__c",
                            "FirstName",
                            "LastName",
                            "Gender__c",
                            "Username__c",
                            "Active__c",
                            "Deleted__c",
                            "Member_since__c",
                            "Location__c",
                            "Birthdate",
                            "Email",
                            "Website__c",
                            "Picture_Location__c",
                            "Tags__c",
                            "MailingCity",
                            "MailingStreet",
                            "MailingCountry",
                            "MailingPostalCode",
                            "MailingState",
                            "Receive_newsletter__c",
                            "Primary_language__c",
                            "Available_to_share_time_and_knowledge__c",
                            "Available_to_donate__c",
                            "Availability__c",
                            "Facebook__c",
                            "Twitter__c",
                            "Skype__c",
                            "Has_Activated_Account__c",
                            "Date_Joined__c",
                            "Date_Last_Login__c",
                            "Account_number__c",
                            "Account_holder__c",
                            "Account_city__c",
                            "Account_IBAN__c",
                            "Account_Active_Recurring_Debit__c",
                            "Phone"])

        users = Member.objects.all()

        logger.info("Exporting {0} User objects to {1}".format(users.count(), filename))

        for user in users:
            try:
                if user.address:
                    mailing_city = user.address.city
                    mailing_street = user.address.line1 + ' ' + user.address.line2
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

                if user.last_name.strip():
                    last_name = user.last_name
                else:
                    last_name = "1%MEMBER"

                gender = ""
                if user.gender == "male":
                    gender = Member.Gender.values['male'].title()
                elif user.gender == "female":
                    gender = Member.Gender.values['female'].title()

                date_deleted = ""
                if user.deleted:
                    date_deleted = user.deleted.date().strftime("%Y-%m-%dT%H:%M:%S.000Z")

                birth_date = ""
                if user.birthdate:
                    birth_date = user.birthdate.strftime("%Y-%m-%dT%H:%M:%S.000Z")

                tags = ""
                for tag in user.tags.all():
                    tags = str(tag) + ", " + tags

                date_joined = ""
                member_since = ""
                if user.date_joined:
                    member_since = user.date_joined.date().strftime("%Y-%m-%dT%H:%M:%S.000Z")
                    date_joined = user.date_joined.strftime("%Y-%m-%dT%H:%M:%S.000Z")

                last_login = ""
                if user.last_login:
                    last_login = user.last_login.strftime("%Y-%m-%dT%H:%M:%S.000Z")

                has_activated = False
                try:
                    rp = RegistrationProfile.objects.get(id=user.id)
                    if rp.activation_key == RegistrationProfile.ACTIVATED:
                        has_activated = True
                except RegistrationProfile.DoesNotExist:
                    if not user.is_active and user.date_joined == user.last_login:
                        has_activated = False
                    else:
                        has_activated = True

                try:
                    monthly_donor = MonthlyDonor.objects.get(user=user)
                    bank_account_city = monthly_donor.city
                    bank_account_holder = monthly_donor.name
                    bank_account_number = ''
                    bank_account_iban = monthly_donor.iban
                    bank_account_active = monthly_donor.active
                except MonthlyDonor.DoesNotExist:
                    bank_account_city = ''
                    bank_account_holder = ''
                    bank_account_number = ''
                    bank_account_iban = ''
                    bank_account_active = False

                availability = user.available_time

                csvwriter.writerow([user.id,
                                    Member.UserType.values[user.user_type].title(),
                                    user.first_name.encode("utf-8"),
                                    last_name.encode("utf-8"),
                                    gender,
                                    user.username.encode("utf-8"),
                                    int(user.is_active),
                                    date_deleted,
                                    member_since,
                                    user.location.encode("utf-8"),
                                    birth_date,
                                    user.email.encode("utf-8"),
                                    user.website.encode("utf-8"),
                                    user.picture,
                                    tags.encode("utf-8"),
                                    mailing_city.encode("utf-8"),
                                    mailing_street.encode("utf-8"),
                                    mailing_country.encode("utf-8"),
                                    mailing_postal_code.encode("utf-8"),
                                    mailing_state.encode("utf-8"),
                                    int(user.newsletter),
                                    user.primary_language.encode("utf-8"),
                                    int(user.share_time_knowledge),
                                    int(user.share_money),
                                    availability,
                                    user.facebook.encode("utf-8"),
                                    user.twitter.encode("utf-8"),
                                    user.skypename.encode("utf-8"),
                                    int(has_activated),
                                    date_joined,
                                    last_login,
                                    bank_account_number,
                                    bank_account_holder.encode("utf-8"),
                                    bank_account_city.encode("utf-8"),
                                    bank_account_iban.encode("utf-8"),
                                    int(bank_account_active),
                                    user.phone_number.encode("utf-8")])
                success_count += 1
            except Exception as e:
                error_count += 1
                logger.error("Error while saving user id {0}: ".format(user.id) + str(e))

    return success_count, error_count


def generate_projects_csv_file(path, loglevel):
    logger.setLevel(loglevel)
    error_count = 0
    success_count = 0

    filename = 'BLUE2SFDC_Projects.csv'
    with open(os.path.join(path, filename), 'wb') as csv_outfile:
        csvwriter = csv.writer(csv_outfile, quoting=csv.QUOTE_ALL)

        csvwriter.writerow(["Project_External_ID__c",
                            "Project_name__c",
                            "NumerOfPeopleReachedDirect__c",
                            "VideoURL__c",
                            "Date_project_deadline__c",
                            "Is_Campaign__c",
                            "Amount_requested__c",
                            "Amount_at_the_moment__c",
                            "Amount_still_needed__c",
                            "Allow_Overfunding__c",
                            "Date_plan_submitted",
                            "Date_Started__c",
                            "Date_Ended__c",
                            "Date_Funded__c",
                            "Picture_Location__c",
                            "Project_Owner__c",
                            "Organization__c",
                            "Country_in_which_the_project_is_located__c",
                            "Theme__c",
                            "Status_project__c",
                            "Project_created_date__c",
                            "Project_updated_date__c",
                            "Tags__c",
                            "Partner_Organization__c",
                            "Slug__c",
                            "Region__c",
                            "Sub_region__c",
                            "Donation_total__c",
                            "Donation_oo_total__c",
                            "Supporter_count__c",
                            "Supporter_oo_count__c"])

        projects = Project.objects.all()
        logger.info("Exporting {0} Project objects to {1}".format(projects.count(), filename))

        for project in projects:

            country = ''
            region = ''
            sub_region = ''
            if project.country:
                country = project.country.name.encode("utf-8")
                region = project.country.subregion.region.name.encode("utf-8")
                sub_region = project.country.subregion.name.encode("utf-8")

            status = ''
            if project.status:
                status = project.status.name.encode("utf-8")

            organization_id = ''
            if project.organization:
                organization_id = project.organization.id

            video_url = ''
            if project.video_url:
                video_url = project.video_url

            tags = ""
            deadline = ""
            date_submitted = ""
            date_started = ""
            date_ended = ""
            date_funded = ""
            theme = ""
            if project.deadline:
                deadline = project.deadline.date().strftime("%Y-%m-%dT%H:%M:%S.000Z")
            if project.date_submitted:
                date_submitted = project.date_submitted.date().strftime("%Y-%m-%dT%H:%M:%S.000Z")
            if project.campaign_started:
                date_started = project.campaign_started.date().strftime("%Y-%m-%dT%H:%M:%S.000Z")
            if project.campaign_ended:
                date_ended = project.campaign_ended.date().strftime("%Y-%m-%dT%H:%M:%S.000Z")
            if project.campaign_funded:
                date_funded = project.campaign_funded.date().strftime("%Y-%m-%dT%H:%M:%S.000Z")
            for tag in project.tags.all():
                tags = str(tag) + ", " + tags
            if project.theme:
                theme = project.theme.name

            partner_organization_name = ""
            if project.partner_organization:
                partner_organization_name = project.partner_organization.name

            csvwriter.writerow([project.id,
                                project.title.encode("utf-8"),
                                project.reach,
                                video_url.encode("utf-8"),
                                deadline,
                                int(project.is_campaign),
                                "%01.2f" % (project.amount_asked or 0),
                                "%01.2f" % (project.amount_donated or 0),
                                "%01.2f" % (project.amount_needed or 0),
                                int(project.allow_overfunding),
                                date_submitted,
                                date_started,
                                date_ended,
                                date_funded,
                                project.image,
                                project.owner.id,
                                organization_id,
                                country,
                                theme,
                                status,
                                project.created.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                                project.updated.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                                tags[:255],
                                partner_organization_name.encode("utf-8"),
                                project.slug,
                                region,
                                sub_region,
                                "%01.2f" % ((project.get_money_total(['paid', 'pending'])) / 100),
                                "%01.2f" % ((project.get_money_total(['paid', 'pending'])) / 100),
                                project.supporters_count(),
                                project.supporters_count(True)])
            success_count += 1
    return success_count, error_count


def generate_projectbudgetlines_csv_file(path, loglevel):
    logger.setLevel(loglevel)
    error_count = 0
    success_count = 0

    filename = 'BLUE2SFDC_Projectbudgetlines.csv'
    with open(os.path.join(path, filename), 'wb') as csv_outfile:
        csvwriter = csv.writer(csv_outfile, quoting=csv.QUOTE_ALL)

        csvwriter.writerow(["Project_Budget_External_ID__c", "Project__c", "Costs__c", "Description__c"])

        budget_lines = ProjectBudgetLine.objects.all()

        logger.info("Exporting {0} ProjectBudgetLine objects to {1}".format(budget_lines.count(), filename))

        for budget_line in budget_lines:
            try:
                csvwriter.writerow([budget_line.id,
                                    budget_line.project.id,
                                    '%01.2f' % (float(budget_line.amount) / 100),
                                    budget_line.description.encode("utf-8")])
                success_count += 1
            except Exception as e:
                error_count += 1
                logger.error("Error while saving projectbudgetline id {0}: ".format(budget_line.id) + str(e))

    return success_count, error_count


def generate_donations_csv_file(path, loglevel):
    logger.setLevel(loglevel)
    error_count = 0
    success_count = 0

    filename = 'BLUE2SFDC_Donations.csv'
    with open(os.path.join(path, filename), 'wb') as csv_outfile:
        csvwriter = csv.writer(csv_outfile, quoting=csv.QUOTE_ALL)

        csvwriter.writerow(["Donation_External_ID__c",
                            "Donor__c",
                            "Project__c",
                            "Amount",
                            "CloseDate",
                            "Name",
                            "StageName",
                            "Type",
                            "Donation_created_date__c",
                            "Donation_updated_date__c",
                            "Donation_ready_date__c",
                            "Payment_method__c",
                            "RecordTypeId",
                            "Fundraiser__c"])

        donations = Donation.objects.all()

        logger.info("Exporting {0} Donation objects to {1}".format(donations.count(), filename))

        t = 0
        for donation in donations:
            t += 1
            logger.debug("writing donation {0}/{1}: {2}".format(t, donations.count(), donation.id))

            try:
                donor_id = ''
                if donation.user:
                    donor_id = donation.user.id

                project_id = ''
                if donation.project:
                    project_id = donation.project.id

                fundraiser_id = ''
                if donation.fundraiser:
                    fundraiser_id = donation.fundraiser.id

                if donation.user and donation.user.get_full_name() != '':
                    name = donation.user.get_full_name()
                else:
                    name = "Anonymous"

                donation_ready = ''
                if donation.ready:
                    donation_ready = donation.ready.strftime("%Y-%m-%dT%H:%M:%S.000Z")

                # Get the payment method from the associated order / payment
                payment_method = payment_method_mapping['']  # Maps to Unknown for DocData.
                if donation.order:
                    lp = OrderPayment.get_latest_by_order(donation.order)
                    if lp and lp.payment_method in payment_method_mapping:
                        payment_method = payment_method_mapping[lp.payment_method]

                csvwriter.writerow([donation.id,
                                    donor_id,
                                    project_id,
                                    '%01.2f' % (float(donation.amount) / 100),
                                    donation.created.date().strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                                    name.encode("utf-8"),
                                    DonationStatuses.values[donation.status].title(),
                                    donation.order.order_type,
                                    donation.created.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                                    donation.updated.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                                    donation_ready,
                                    payment_method.encode("utf-8"),
                                    '012A0000000ZK6FIAW',
                                    fundraiser_id])

                success_count += 1
            except Exception as e:
                error_count += 1
                logger.error("Error while saving donation id {0}: ".format(donation.id) + str(e))

    return success_count, error_count


def generate_vouchers_csv_file(path, loglevel):
    logger.setLevel(loglevel)
    error_count = 0
    success_count = 0

    filename = 'BLUE2SFDC_Vouchers_{0}.csv'.format(timezone.localtime(timezone.now()).strftime('%Y%m%d'))
    with open(os.path.join(path, filename), 'wb') as csv_outfile:
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

                csvwriter.writerow([voucher.id,
                                    voucher.sender.id,
                                    '%01.2f' % (float(voucher.amount) / 100),
                                    voucher.created.date(),
                                    name.encode("utf-8"),
                                    voucher.message.encode("utf-8"),
                                    VoucherStatuses.values[voucher.status].title(),
                                    '012A0000000BxfHIAS'])
                success_count += 1
            except Exception as e:
                error_count += 1
                logger.error("Error while saving voucher id {0}: ".format(voucher.id) + str(e))

    return success_count, error_count


def generate_tasks_csv_file(path, loglevel):
    logger.setLevel(loglevel)
    error_count = 0
    success_count = 0

    filename = 'BLUE2SFDC_Tasks.csv'
    with open(os.path.join(path, filename), 'wb') as csv_outfile:
        csvwriter = csv.writer(csv_outfile, quoting=csv.QUOTE_ALL)

        csvwriter.writerow(["Task_External_ID__c",
                            "Project__c",
                            "Deadline__c",
                            "Location_of_the_task__c",
                            "Task_expertise__c",
                            "Task_status__c",
                            "Title__c",
                            "Task_created_date__c",
                            "Tags__c",
                            "Effort__c",
                            "People_Needed__c",
                            "Author__c",
                            "Date_realized__c"])

        tasks = Task.objects.all()

        logger.info("Exporting {0} Task objects to {1}".format(tasks.count(), filename))

        for task in tasks:

            tags = ""
            for tag in task.tags.all():
                tags = str(tag) + ", " + tags

            skill = ''
            if task.skill:
                skill = task.skill.name.encode("utf-8")

            author = ''
            if task.author:
                author = task.author.id

            date_realized = ''
            if task.status == 'realized' and task.date_status_change:
                date_realized = task.date_status_change.strftime("%Y-%m-%dT%H:%M:%S.000Z")

            try:
                csvwriter.writerow([task.id,
                                    task.project.id,
                                    task.deadline.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                                    task.location.encode("utf-8"),
                                    skill,
                                    task.status.encode("utf-8"),
                                    task.title.encode("utf-8"),
                                    task.created.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                                    tags,
                                    task.time_needed.encode("utf-8"),
                                    task.people_needed,
                                    author,
                                    date_realized])
                success_count += 1
            except Exception as e:
                error_count += 1
                logger.error("Error while saving task id {0}: ".format(task.id) + str(e))

    return success_count, error_count


def generate_taskmembers_csv_file(path, loglevel):
    logger.setLevel(loglevel)
    error_count = 0
    success_count = 0

    filename = 'BLUE2SFDC_Taskmembers.csv'
    with open(os.path.join(path, filename), 'wb') as csv_outfile:
        csvwriter = csv.writer(csv_outfile, quoting=csv.QUOTE_ALL)

        csvwriter.writerow(["Task_Member_External_ID__c",
                            "Contacts__c",
                            "X1_CLUB_Task__c",
                            "Status__c",
                            "Taskmember_Created_Date__c"])

        taskmembers = TaskMember.objects.all()

        logger.info("Exporting {0} TaskMember objects to {1}".format(taskmembers.count(), filename))

        for taskmember in taskmembers:
            try:
                csvwriter.writerow([taskmember.id,
                                    taskmember.member.id,
                                    taskmember.task.id,
                                    taskmember.status.encode("utf-8"),
                                    taskmember.created.strftime("%Y-%m-%dT%H:%M:%S.000Z")])
                success_count += 1
            except Exception as e:
                error_count += 1
                logger.error("Error while saving taskmember id {0}: ".format(taskmember.id) + str(e))

    return success_count, error_count


def generate_fundraisers_csv_file(path, loglevel):
    logger.setLevel(loglevel)
    error_count = 0
    success_count = 0

    filename = 'BLUE2SFDC_Fundraisers.csv'
    with open(os.path.join(path, filename), 'wb') as csv_outfile:
        csvwriter = csv.writer(csv_outfile, quoting=csv.QUOTE_ALL)

        csvwriter.writerow(["Fundraiser_External_ID__c",
                            "Name",
                            "Owner__c",
                            "Project__c",
                            "Picture_Location__c",
                            "VideoURL__c",
                            "Amount__c",
                            "Amount_at_the_moment__c",
                            "Deadline__c",
                            "Created__c"])

        fundraisers = Fundraiser.objects.all()

        logger.info("Exporting {0} Fundraiser objects to {1}".format(fundraisers.count(), filename))

        for fundraiser in fundraisers:
            try:
                csvwriter.writerow([fundraiser.id,
                                    fundraiser.title.encode("utf-8"),
                                    fundraiser.owner.id,
                                    fundraiser.project.id,
                                    fundraiser.image,
                                    fundraiser.video_url,
                                    '%01.2f' % (float(fundraiser.amount) / 100),
                                    '%01.2f' % (float(fundraiser.amount_donated) / 100),
                                    fundraiser.deadline.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                                    fundraiser.created.strftime("%Y-%m-%dT%H:%M:%S.000Z")])
                success_count += 1
            except Exception as e:
                error_count += 1
                logger.error("Error while saving fundraiser id {0}: ".format(fundraiser.id) + str(e))

    return success_count, error_count


def generate_organizationmember_csv_file(path, loglevel):
    logger.setLevel(loglevel)
    error_count = 0
    success_count = 0

    filename = 'BLUE2SFDC_Organizationmembers.csv'
    with open(os.path.join(path, filename), 'wb') as csv_outfile:
        csvwriter = csv.writer(csv_outfile, quoting=csv.QUOTE_ALL)

        csvwriter.writerow(["Organization_Member_External_Id__c",
                            "Contact__c",
                            "Account__c",
                            "Role__c"])

        orgmembers = OrganizationMember.objects.all()

        logger.info("Exporting {0} OrganizationMember objects to {1}".format(orgmembers.count(), filename))

        for orgmember in orgmembers:
            try:
                csvwriter.writerow([orgmember.id,
                                    orgmember.user.id,
                                    orgmember.organization.id,
                                    orgmember.function.encode("utf-8")])
                success_count += 1
            except Exception as e:
                error_count += 1
                logger.error("Error while saving organization member id {0}: ".format(orgmember.id) + str(e))

    return success_count, error_count