import logging
from bluebottle.utils.utils import get_project_model
from django.contrib.auth import get_user_model
from registration.models import RegistrationProfile
from apps.cowry_docdata.models import payment_method_mapping
from apps.projects.models import ProjectBudgetLine
from apps.organizations.models import Organization
from apps.tasks.models import Task, TaskMember
from apps.fund.models import Donation, DonationStatuses, RecurringDirectDebitPayment
from apps.vouchers.models import Voucher, VoucherStatuses

from apps.bluebottle_salesforce.models import SalesforceOrganization, SalesforceContact, SalesforceProject, \
    SalesforceDonation, SalesforceProjectBudget, SalesforceTask, SalesforceTaskMembers, SalesforceVoucher
from bluebottle.bb_projects.models import ProjectPhase

USER_MODEL = get_user_model()
PROJECT_MODEL = get_project_model()


logger = logging.getLogger('bluebottle.salesforce')


def sync_organizations(dry_run, sync_from_datetime, loglevel):
    logger.setLevel(loglevel)
    error_count = 0
    success_count = 0

    organizations = Organization.objects.all()
    if sync_from_datetime:
        organizations = organizations.filter(updated__gte=sync_from_datetime)

    logger.info("Syncing {0} Organization objects.".format(organizations.count()))

    for organization in organizations:
        logger.debug("Syncing Organization: {0}".format(organization.id))

        # Find the corresponding SF organization.
        try:
            sforganization = SalesforceOrganization.objects.get(external_id=organization.id)
        except SalesforceOrganization.DoesNotExist:
            sforganization = SalesforceOrganization()

        # SF Layout: Account details section.
        sforganization.name = organization.name

        # sforganization.legal_status = organization.legal_status
        # sforganization.description = organization.description

        # SF Layout: Contact Information section. Ignore address type and only use first address.
        # When multiple address types are supported in the website, extend this function
        sforganization.billing_city = organization.city[:40]
        sforganization.billing_street = organization.address_line1 + " " + organization.address_line2
        sforganization.billing_postal_code = organization.postal_code
        if organization.country:
            sforganization.billing_country = organization.country.name
        else:
            sforganization.billing_country = ''

        # E-mail addresses for organizations are currently left out because source data is not validated
        # sforganization.email_address = organization.email
        sforganization.phone = organization.phone_number
        sforganization.website = organization.website

        # SF Layout: Bank Account section.
        sforganization.address_bank = organization.account_bank_address
        sforganization.bank_account_name = organization.name
        sforganization.bank_account_number = organization.account_number
        sforganization.bank_name = organization.account_bank_name
        sforganization.bic_swift = organization.account_bic
        sforganization.country_bank = str(organization.account_bank_country)
        sforganization.iban_number = organization.account_iban

        # SF Layout: System Information.
        sforganization.external_id = organization.id
        sforganization.created_date = organization.created

        # Save the object to Salesforce
        if not dry_run:
            try:
                sforganization.save()
                success_count += 1
            except Exception as e:
                error_count += 1
                logger.error("Error while saving organization id {0}: ".format(organization.id) + str(e))

    return success_count, error_count


def sync_users(dry_run, sync_from_datetime, loglevel):
    logger.setLevel(loglevel)
    error_count = 0
    success_count = 0

    users = USER_MODEL.objects.all()

    if sync_from_datetime:
        users = users.filter(updated__gte=sync_from_datetime)

    logger.info("Syncing {0} User objects.".format(users.count()))

    for user in users:
        logger.debug("Syncing User: {0}".format(user.id))

        # Find the corresponding SF user.
        try:
            contact = SalesforceContact.objects.get(external_id=user.id)
        except SalesforceContact.DoesNotExist:
            contact = SalesforceContact()

        # Determine and set user type (person, group, foundation, school, company, ... )
        contact.category1 = USER_MODEL.UserType.values[user.user_type].title()

        # SF Layout: Profile section.
        contact.first_name = user.first_name
        if user.last_name.strip():
            contact.last_name = user.last_name
        else:
            contact.last_name = "1%MEMBER"

        if user.gender == "male":
            contact.gender = USER_MODEL.Gender.values['male'].title()
        elif user.gender == "female":
            contact.gender = USER_MODEL.Gender.values['female'].title()
        else:
            contact.gender = ""

        if user.time_available:
            contact.availability = user.time_available.type or ""

        contact.user_name = user.username
        contact.is_active = user.is_active
        contact.close_date = user.deleted
        contact.member_since = user.date_joined
        contact.date_joined = user.date_joined
        contact.last_login = user.last_login
        contact.why_one_percent_member = user.why
        contact.about_me_us = user.about
        contact.location = user.location
        contact.birth_date = user.birthdate
        contact.available_to_share_time_and_knowledge = user.share_time_knowledge
        contact.available_to_donate = user.share_money

        # SF Layout: Contact Information section.
        contact.email = user.email
        contact.website = user.website

        # Bank details of recurring payments
        try:
            recurring_payment = RecurringDirectDebitPayment.objects.get(user=user)
            contact.bank_account_city = recurring_payment.city
            contact.bank_account_holder = recurring_payment.name
            contact.bank_account_number = recurring_payment.account
        except RecurringDirectDebitPayment.DoesNotExist:
            contact.bank_account_city = ''
            contact.bank_account_holder = ''
            contact.bank_account_number = ''

        # Determine if the user has activated himself, by default assume not
        # if this is a legacy record, by default assume it has activated
        contact.has_activated = False
        try:
            rp = RegistrationProfile.objects.get(user_id=user.id)
            contact.tags = rp.activation_key
            if rp.activation_key == RegistrationProfile.ACTIVATED:
                contact.has_activated = True
        except RegistrationProfile.DoesNotExist:
            if not user.is_active and user.date_joined == user.last_login:
                contact.has_activated = False
            else:
                contact.has_activated = True

        if user.address:
            contact.mailing_city = user.address.city
            contact.mailing_street = user.address.line1 + '\n' + user.address.line2
            if user.address.country:
                contact.mailing_country = user.address.country.name
            else:
                contact.mailing_country = ''
            contact.mailing_postal_code = user.address.postal_code
            contact.mailing_state = user.address.state
        else:
            contact.mailing_city = ''
            contact.mailing_street = ''
            contact.mailing_country = ''
            contact.mailing_postal_code = ''
            contact.mailing_state = ''

        # The default: Organization(Account) will be 'Individual' without setting a specific value
        # contact.organization_account = SalesforceOrganization.objects.get(external_id=contact.organization.id)

        # SF Layout: My Settings section.
        contact.receive_newsletter = user.newsletter
        contact.primary_language = user.primary_language

        # SF: Other
        contact.external_id = user.id

        # Save the object to Salesforce
        if not dry_run:
            try:
                contact.save()
                success_count += 1
            except Exception as e:
                error_count += 1
                logger.error("Error while saving contact id {0}: ".format(user.id) + str(e))

    return success_count, error_count


def sync_projects(dry_run, sync_from_datetime, loglevel):
    logger.setLevel(loglevel)
    error_count = 0
    success_count = 0

    projects = PROJECT_MODEL.objects.all()

    if sync_from_datetime:
        projects = projects.filter(updated__gte=sync_from_datetime)

    logger.info("Syncing {0} Project objects.".format(projects.count()))

    for project in projects:
        logger.debug("Syncing Project: {0}".format(project.id))

        # Find the corresponding SF project.
        try:
            sfproject = SalesforceProject.objects.get(external_id=project.id)
        except SalesforceProject.DoesNotExist:
            sfproject = SalesforceProject()

        # SF Layout: 1%CLUB Project Detail section.
        sfproject.amount_at_the_moment = "%01.2f" % (project.amount_donated or 0)
        sfproject.amount_requested = "%01.2f" % (project.amount_asked or 0)
        sfproject.amount_still_needed = "%01.2f" % (project.amount_needed or 0)

        if project.deadline:
            sfproject.date_project_deadline = project.deadline.date()

        try:
            sfproject.project_owner = SalesforceContact.objects.get(external_id=project.owner.id)
        except SalesforceContact.DoesNotExist:
            logger.error("Unable to find contact id {0} in Salesforce for project id {1}".format(project.owner.id,
                                                                                                 project.id))

        sfproject.project_name = project.title

        # SF Layout: Summary Project Details section.

        if project.country:
            sfproject.country_in_which_the_project_is_located = project.country.name.encode("utf-8")

        sfproject.describe_the_project_in_one_sentence = project.pitch[:5000]
        sfproject.extensive_project_description = project.story

        if project.status:
            sfproject.status_project = project.status.name.encode("utf-8")

        sfproject.tags = ""
        for tag in project.tags.all():
            sfproject.tags = str(tag) + ", " + sfproject.tags

        sfproject.target_group_s_of_the_project = 0 #project.for_who
        sfproject.number_of_people_reached_direct = 0 #project.reach
        sfproject.describe_where_the_money_is_needed_for = project.amount_needed
        sfproject.sustainability = "" #project.future
        sfproject.contribution_project_in_reducing_poverty = "" #project.effects

        # Set status dates
        # FIXME: These are the dates available now
        # created: date the project was first created
        # updated: last change
        # deadline: Deadline for the campaign
        # date_submitted
        # campaign_started
        # campaign_funded: 100% funded (funding continues)
        # campaign_ended: Campaigns stops (might be prior to deadline)

        sfproject.date_plan_submitted = project.date_submitted
        sfproject.date_plan_approved = project.campaign_started
        sfproject.date_plan_rejected = project.date_submitted

        sfproject.date_pitch_created = project.created
        sfproject.date_pitch_submitted = project.date_submitted
        sfproject.date_pitch_approved = project.campaign_started
        sfproject.date_pitch_rejected = project.date_submitted

        sfproject.date_project_act = project.campaign_ended
        sfproject.date_project_realized = project.campaign_ended
        sfproject.date_project_failed = project.campaign_ended
        sfproject.date_project_result = project.campaign_ended

        if project.organization:
            try:
                sfproject.organization_account = SalesforceOrganization.objects.get(
                    external_id=project.organization_id)
            except SalesforceOrganization.DoesNotExist:
                logger.error("Unable to find organization id {0} in Salesforce for project id {1}".format(
                    project.organization.id, project.id))

        sfproject.project_url = "http://www.onepercentclub.com/en/#!/projects/{0}".format(project.slug)

        # SF Layout: Other section.
        sfproject.external_id = project.id

        # Save the object to Salesforce
        if not dry_run:
            try:
                sfproject.save()
                success_count += 1
            except Exception as e:
                error_count += 1
                logger.error("Error while saving project id {0}: ".format(project.id) + str(e))

    return success_count, error_count


def sync_projectbudgetlines(dry_run, sync_from_datetime, loglevel):
    logger.setLevel(loglevel)
    error_count = 0
    success_count = 0

    budget_lines = ProjectBudgetLine.objects.all()

    if sync_from_datetime:
        budget_lines = budget_lines.filter(updated__gte=sync_from_datetime)

    logger.info("Syncing {0} BudgetLine objects.".format(budget_lines.count()))

    for budget_line in budget_lines:
        logger.debug("Syncing BudgetLine: {0}".format(budget_line.id))

        # Find the corresponding SF budget lines.
        try:
            sfbudget_line = SalesforceProjectBudget.objects.get(external_id=budget_line.id)
        except SalesforceProjectBudget.DoesNotExist:
            sfbudget_line = SalesforceProjectBudget()

        # SF Layout: Information section
        sfbudget_line.costs = "%01.2f" % (budget_line.amount / 100)
        sfbudget_line.description = budget_line.description
        sfbudget_line.external_id = budget_line.id

        try:
            sfbudget_line.project = SalesforceProject.objects.get(external_id=budget_line.project.id)
        except SalesforceProject.DoesNotExist:
            logger.error("Unable to find project id {0} in Salesforce for budget line id {1}".format(
                budget_line.project.id, budget_line.id))

        # Save the object to Salesforce
        if not dry_run:
            try:
                sfbudget_line.save()
                success_count += 1
            except Exception as e:
                error_count += 1
                logger.error("Error while saving budget line id {0}: ".format(budget_line.id) + str(e))

    return success_count, error_count


def sync_donations(dry_run, sync_from_datetime, loglevel):
    logger.setLevel(loglevel)
    error_count = 0
    success_count = 0

    donations = Donation.objects.all()
    if sync_from_datetime:
        donations = donations.filter(updated__gte=sync_from_datetime)

    logger.info("Syncing {0} Donation objects.".format(donations.count()))

    for donation in donations:
        logger.debug("Syncing Donation: {0}".format(donation.id))

        # Find the corresponding SF donation.
        try:
            sfdonation = SalesforceDonation.objects.get(external_id_donation=donation.id)
        except SalesforceDonation.DoesNotExist:
            sfdonation = SalesforceDonation()

        # Initialize Salesforce objects.
        if donation.user:
            try:
                sfContact = SalesforceContact.objects.get(external_id=donation.user.id)
                sfdonation.receiver = sfContact
            except SalesforceContact.DoesNotExist:
                logger.error("Unable to find contact id {0} in Salesforce for donation id {1}".format(
                    donation.user.id, donation.id))
        if donation.project:
            try:
                sfProject = SalesforceProject.objects.get(external_id=donation.project.id)
                sfdonation.project = sfProject
            except SalesforceProject.DoesNotExist:
                logger.error("Unable to find project id {0} in Salesforce for donation id {1}".format(
                    donation.project.id, donation.id))

        # SF Layout: Donation Information section.
        sfdonation.amount = "%01.2f" % (float(donation.amount) / 100)
        sfdonation.close_date = donation.created.date()

        if donation.user and donation.user.get_full_name() != '':
            sfdonation.name = donation.user.get_full_name()
        else:
            sfdonation.name = "1%MEMBER"

        # Get the payment method from the associated order / payment
        sfdonation.payment_method = payment_method_mapping['']  # Maps to Unknown for DocData.
        if donation.order:
            lp = donation.order.latest_payment
            if lp and lp.latest_docdata_payment:
                if lp.latest_docdata_payment.payment_method in payment_method_mapping:
                    sfdonation.payment_method = payment_method_mapping[lp.latest_docdata_payment.payment_method]

        sfdonation.stage_name = DonationStatuses.values[donation.status].title()
        sfdonation.opportunity_type = donation.DonationTypes.values[donation.donation_type].title()

        # SF Layout: System Information section.
        sfdonation.donation_created_date = donation.created.date()
        sfdonation.external_id_donation = donation.id
        sfdonation.record_type = "012A0000000ZK6FIAW"

        # Save the object to Salesforce
        if not dry_run:
            try:
                sfdonation.save()
                success_count += 1
            except Exception as e:
                error_count += 1
                logger.error("Error while saving donation id {0}: ".format(donation.id) + str(e))

    return success_count, error_count


def sync_vouchers(dry_run, sync_from_datetime, loglevel):
    logger.setLevel(loglevel)
    error_count = 0
    success_count = 0

    vouchers = Voucher.objects.all()
    if sync_from_datetime:
        vouchers = vouchers.filter(updated__gte=sync_from_datetime)

    logger.info("Syncing {0} Voucher objects.".format(vouchers.count()))

    for voucher in vouchers:
        logger.debug("Syncing Voucher: {0}".format(voucher.id))

        # Find the corresponding SF vouchers.
        try:
            sfvoucher = SalesforceVoucher.objects.get(external_id_voucher=voucher.id)
        except SalesforceVoucher.DoesNotExist:
            sfvoucher = SalesforceVoucher()

        # Initialize the Contact object that refers to the voucher purchaser
        try:
            sfvoucher.purchaser = SalesforceContact.objects.get(external_id=voucher.sender_id)
        except SalesforceContact.DoesNotExist:
            logger.error("Unable to find purchaser contact id {0} in Salesforce for voucher id {1}".format(
                voucher.sender_id, voucher.id))

        # TODO: There should be a voucher.project.id, else remove from (parent) models
        # sfvoucher.project = SalesforceProject.objects.get(external_id=1)

        # TODO: There should be a voucher.receiver.id, , else remove from (parent) models
        # sfvoucher.receiver = SalesforceContact.objects.get(external_id=1)

        # SF Layout: Donation Information section.
        sfvoucher.amount = "%01.2f" % (float(voucher.amount) / 100)
        sfvoucher.close_date = voucher.created
        sfvoucher.description = voucher.message
        # sfvoucher.stage_name exists as state: "In progress", however this has been shifted to Donation?
        sfvoucher.stage_name = VoucherStatuses.values[voucher.status].title()

        #sfvoucher.payment_method = ""

        if sfvoucher.purchaser and sfvoucher.purchaser.last_name:
            if sfvoucher.purchaser.first_name:
                sfvoucher.name = sfvoucher.purchaser.first_name + " " + sfvoucher.purchaser.last_name
            else:
                sfvoucher.name = sfvoucher.purchaser.last_name
        else:
            sfvoucher.name = "1%MEMBER"

        # sfvoucher.name exist in production: "NOT YET USED 1%VOUCHER" when stage_name is "In progress"
        # sfvoucher.opportunity_type = ""

        # SF Other.
        sfvoucher.external_id_voucher = voucher.id
        sfvoucher.record_type = "012A0000000BxfHIAS"

        # Save the object to Salesforce
        if not dry_run:
            try:
                sfvoucher.save()
                success_count += 1
            except Exception as e:
                error_count += 1
                logger.error("Error while saving voucher id {0}: ".format(voucher.id) + str(e))

    return success_count, error_count


def sync_tasks(dry_run, sync_from_datetime, loglevel):
    logger.setLevel(loglevel)
    error_count = 0
    success_count = 0

    tasks = Task.objects.all()
    if sync_from_datetime:
        tasks = tasks.filter(updated__gte=sync_from_datetime)

    logger.info("Syncing {0} Task objects.".format(tasks.count()))

    for task in tasks:
        logger.debug("Syncing Task: {0}".format(task.id))

        # Find the corresponding SF tasks.
        try:
            sftask = SalesforceTask.objects.get(external_id=task.id)
        except SalesforceTask.DoesNotExist:
            sftask = SalesforceTask()

        # SF Layout: Information section.
        try:
            sftask.project = SalesforceProject.objects.get(external_id=task.project.id)
        except SalesforceProject.DoesNotExist:
            logger.error("Unable to find project id {0} in Salesforce for task id {1}".format(task.project.id, task.id))

        sftask.deadline = task.deadline.strftime("%d %B %Y")
        sftask.effort = task.time_needed
        sftask.extended_task_description = task.description
        sftask.location_of_the_task = task.location

        if task.skill:
            sftask.task_expertise = task.skill.name.encode("utf-8")

        sftask.task_status = task.status
        sftask.title = task.title
        sftask.task_created_date = task.created

        sftask.tags = ""
        for tag in task.tags.all():
            sftask.tags = str(tag) + ", " + sftask.tags

        # SF: Other
        sftask.external_id = task.id

        # Save the object to Salesforce
        if not dry_run:
            try:
                sftask.save()
                success_count += 1
            except Exception as e:
                error_count += 1
                logger.error("Error while saving task id {0}: ".format(task.id) + str(e))

    return success_count, error_count


def sync_taskmembers(dry_run, sync_from_datetime, loglevel):
    logger.setLevel(loglevel)
    error_count = 0
    success_count = 0

    task_members = TaskMember.objects.all()

    if sync_from_datetime:
        task_members = task_members.filter(updated__gte=sync_from_datetime)

    logger.info("Syncing {0} TaskMember objects.".format(task_members.count()))

    for task_member in task_members:
        logger.debug("Syncing TaskMember: {0}".format(task_member.id))

        # Find the corresponding SF task members.
        try:
            sftaskmember = SalesforceTaskMembers.objects.get(external_id=task_member.id)
        except SalesforceTaskMembers.DoesNotExist:
            sftaskmember = SalesforceTaskMembers()

        # SF Layout: Information section.
        try:
            sftaskmember.contacts = SalesforceContact.objects.get(external_id=task_member.member.id)
        except SalesforceContact.DoesNotExist:
            logger.error("Unable to find contact id {0} in Salesforce for task member id {1}".format(
                task_member.member.id, task_member.id))
        try:
            sftaskmember.x1_club_task = SalesforceTask.objects.get(external_id=task_member.task.id)
        except SalesforceTask.DoesNotExist:
            logger.error("Unable to find task id {0} in Salesforce for task member id {1}".format(task_member.member.id,
                                                                                                  task_member.id))

        sftaskmember.external_id = task_member.id

        # Save the object to Salesforce
        if not dry_run:
            try:
                sftaskmember.save()
                success_count += 1
            except Exception as e:
                error_count += 1
                logger.error("Error while saving task id {0}: ".format(task_member.id) + str(e))

    return success_count, error_count
