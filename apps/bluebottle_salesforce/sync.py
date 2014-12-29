import logging
from apps.recurring_donations.models import MonthlyDonor
from bluebottle.payments.models import OrderPayment
import re
from django.utils import timezone
from registration.models import RegistrationProfile
from apps.cowry_docdata.models import payment_method_mapping
from bluebottle.projects.models import ProjectBudgetLine
from apps.organizations.models import Organization, OrganizationMember
from bluebottle.tasks.models import Task, TaskMember
from bluebottle.donations.models import Donation
from apps.vouchers.models import Voucher, VoucherStatuses
from bluebottle.fundraisers.models import Fundraiser
from bluebottle.projects.models import Project
from bluebottle.members.models import Member

from apps.bluebottle_salesforce.models import SalesforceOrganization, SalesforceContact, SalesforceProject, \
    SalesforceDonation, SalesforceProjectBudget, SalesforceTask, SalesforceTaskMembers, SalesforceVoucher, \
    SalesforceLogItem, SalesforceFundraiser, SalesforceOrganizationMember

logger = logging.getLogger('bluebottle.salesforce')
re_email = re.compile("^[A-Z0-9._%+-/!#$%&'*=?^_`{|}~]+@[A-Z0-9.-]+\\.[A-Z]{2,4}$")


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

        # Find the corresponding SF organization
        try:
            sforganization = SalesforceOrganization.objects.get(external_id=organization.id)
        except SalesforceOrganization.DoesNotExist:
            sforganization = SalesforceOrganization()
        except Exception as e:
            logger.error("Error while loading sforganization id {0} - stopping: ".format(organization.id) + str(e))
            return success_count, error_count+1

        # Populate the data from the source
        sforganization.name = organization.name

        sforganization.billing_city = organization.city[:40]
        sforganization.billing_street = organization.address_line1 + " " + organization.address_line2
        sforganization.billing_postal_code = organization.postal_code
        sforganization.billing_state = organization.state[:20]

        if organization.country:
            sforganization.billing_country = organization.country.name
        else:
            sforganization.billing_country = ''

        if organization.email and re_email.match(organization.email.upper()):
            sforganization.email_address = organization.email
        elif organization.email:
            logger.error("Organization has invalid e-mail address '{0}', org id {1}. "
                         "Ignoring e-mail address field.".format(organization.email, organization.id))

        sforganization.phone = organization.phone_number
        sforganization.website = organization.website
        sforganization.twitter = organization.twitter
        sforganization.facebook = organization.facebook
        sforganization.skype = organization.skype

        sforganization.tags = ""
        for tag in organization.tags.all():
            sforganization.tags = str(tag) + ", " + sforganization.tags

        sforganization.bank_account_name = organization.account_holder_name
        sforganization.bank_account_address = organization.account_holder_address
        sforganization.bank_account_postalcode = organization.account_holder_postal_code
        sforganization.bank_account_city = organization.account_holder_city
        if organization.account_holder_country:
            sforganization.bank_account_country = organization.account_holder_country.name
        else:
            sforganization.bank_account_country = ''

        sforganization.bank_name = organization.account_bank_name
        sforganization.bank_address = organization.account_bank_address
        sforganization.bank_postalcode = organization.account_bank_postal_code
        sforganization.bank_city = organization.account_bank_city
        if organization.account_bank_country:
            sforganization.bank_country = organization.account_bank_country.name
        else:
            sforganization.bank_country = ''

        sforganization.bank_account_number = organization.account_number
        sforganization.bank_bic_swift = organization.account_bic
        sforganization.bank_account_iban = organization.account_iban

        sforganization.external_id = organization.id
        sforganization.created_date = organization.created
        sforganization.deleted_date = organization.deleted

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

    users = Member.objects.all()
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
        except Exception as e:
            logger.error("Error while loading sfcontact id {0} - stopping: ".format(user.id) + str(e))
            return success_count, error_count+1

        # Populate the data from the source
        contact.external_id = user.id
        contact.user_name = user.username

        if re_email.match(user.email.upper()):
            contact.email = user.email
        else:
            logger.error("User has invalid e-mail address '{0}', member id {1}. "
                         "Ignoring e-mail address field.".format(user.email, user.id))

        contact.is_active = user.is_active
        contact.member_since = user.date_joined
        contact.date_joined = user.date_joined
        contact.deleted = user.deleted

        contact.category1 = Member.UserType.values[user.user_type].title()

        contact.first_name = user.first_name
        if user.last_name.strip():
            contact.last_name = user.last_name
        else:
            contact.last_name = "1%MEMBER"

        contact.location = user.location
        contact.website = user.website

        contact.picture_location = ""
        if user.picture:
            contact.picture_location = str(user.picture)

        contact.about_me_us = user.about
        contact.why_one_percent_member = user.why

        contact.availability = user.available_time

        contact.facebook = user.facebook
        contact.twitter = user.twitter
        contact.skype = user.skypename

        contact.primary_language = user.primary_language
        contact.receive_newsletter = user.newsletter
        contact.phone = user.phone_number
        contact.birth_date = user.birthdate

        if user.gender == "male":
            contact.gender = Member.Gender.values['male'].title()
        elif user.gender == "female":
            contact.gender = Member.Gender.values['female'].title()
        else:
            contact.gender = ""

        contact.tags = ""
        for tag in user.tags.all():
            contact.tags = str(tag) + ", " + contact.tags

        if user.address:
            contact.mailing_city = user.address.city
            contact.mailing_street = user.address.line1 + ' ' + user.address.line2
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

        contact.last_login = user.last_login

        # Bank details of recurring payments
        try:
            monthly_donor = MonthlyDonor.objects.get(user=user)
            contact.bank_account_city = monthly_donor.city
            contact.bank_account_holder = monthly_donor.name
            contact.bank_account_number = ''
            contact.bank_account_iban = monthly_donor.iban
            contact.bank_account_active_recurring_debit = monthly_donor.active
        except MonthlyDonor.DoesNotExist:
            contact.bank_account_city = ''
            contact.bank_account_holder = ''
            contact.bank_account_number = ''
            contact.bank_account_iban = ''
            contact.bank_account_active_recurring_debit = False

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

    projects = Project.objects.all()

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
        except Exception as e:
            logger.error("Error while loading sfproject id {0} - stopping: ".format(project.id) + str(e))
            return success_count, error_count+1

        # Populate the data
        sfproject.external_id = project.id
        sfproject.project_name = project.title
        sfproject.describe_the_project_in_one_sentence = project.pitch[:5000]

        sfproject.video_url = project.video_url

        sfproject.date_project_deadline = project.deadline or None
        sfproject.is_campaign = project.is_campaign
        sfproject.amount_at_the_moment = "%01.2f" % (project.amount_donated or 0)
        sfproject.amount_requested = "%01.2f" % (project.amount_asked or 0)
        sfproject.amount_still_needed = "%01.2f" % (project.amount_needed or 0)
        sfproject.allow_overfunding = project.allow_overfunding
        sfproject.story = project.story

        sfproject.date_plan_submitted = project.date_submitted
        sfproject.date_started = project.campaign_started
        sfproject.date_ended = project.campaign_ended
        sfproject.date_funded = project.campaign_funded

        sfproject.picture_location = ""
        if project.image:
            sfproject.picture_location = str(project.image)

        try:
            sfproject.project_owner = SalesforceContact.objects.get(external_id=project.owner.id)
        except SalesforceContact.DoesNotExist:
            logger.error("Unable to find contact id {0} in Salesforce for project id {1}".format(project.owner.id,
                                                                                                 project.id))
        if project.organization:
            try:
                sfproject.organization_account = SalesforceOrganization.objects.get(
                    external_id=project.organization_id)
            except SalesforceOrganization.DoesNotExist:
                logger.error("Unable to find organization id {0} in Salesforce for project id {1}".format(
                    project.organization.id, project.id))

        if project.country:
            sfproject.country_in_which_the_project_is_located = project.country.name.encode("utf-8")
            sfproject.sub_region = project.country.subregion.name.encode("utf-8")
            sfproject.region = project.country.subregion.region.name.encode("utf-8")

        sfproject.theme = ""
        if project.theme:
            sfproject.theme = project.theme.name

        if project.status:
            sfproject.status_project = project.status.name.encode("utf-8")

        sfproject.project_created_date = project.created
        sfproject.project_updated_date = project.updated

        sfproject.tags = ""
        for tag in project.tags.all():
            sfproject.tags = str(tag) + ", " + sfproject.tags
        sfproject.tags = sfproject.tags[:255]

        sfproject.partner_organization = ""
        if project.partner_organization:
            sfproject.partner_organization = project.partner_organization.name

        sfproject.slug = project.slug

        sfproject.donation_total = "%01.2f" % (project.get_money_total(['paid', 'pending']))
        sfproject.donation_oo_total = "%01.2f" % (project.get_money_total(['paid', 'pending']))
        sfproject.supporter_count = project.supporters_count()
        sfproject.supporter_oo_count = project.supporters_count(True)

        # Save the object to Salesforce
        if not dry_run:
            try:
                sfproject.save()
                success_count += 1
            except Exception as e:
                error_count += 1
                logger.error("Error while saving project id {0}: ".format(project.id) + str(e))

    return success_count, error_count


def sync_fundraisers(dry_run, sync_from_datetime, loglevel):
    logger.setLevel(loglevel)
    error_count = 0
    success_count = 0

    fundraisers = Fundraiser.objects.all()

    if sync_from_datetime:
        fundraisers = fundraisers.filter(updated__gte=sync_from_datetime)

    logger.info("Syncing {0} Fundraiser objects.".format(fundraisers.count()))

    for fundraiser in fundraisers:
        logger.debug("Syncing Fundraiser: {0}".format(fundraiser.id))

        # Find the corresponding SF Fundraiser.
        try:
            sffundraiser = SalesforceFundraiser.objects.get(external_id=fundraiser.id)
        except SalesforceFundraiser.DoesNotExist:
            sffundraiser = SalesforceFundraiser()
        except Exception as e:
            logger.error("Error while loading sffundraiser id {0} - stopping: ".format(fundraiser.id) + str(e))
            return success_count, error_count+1

        # Populate the data
        sffundraiser.external_id = fundraiser.id

        try:
            sffundraiser.owner = SalesforceContact.objects.get(external_id=fundraiser.owner.id)
        except SalesforceContact.DoesNotExist:
            logger.error("Unable to find contact id {0} in Salesforce for fundraiser id {1}".format(fundraiser.owner.id,
                                                                                                    fundraiser.id))
        try:
            sffundraiser.project = SalesforceProject.objects.get(external_id=fundraiser.project.id)
        except SalesforceProject.DoesNotExist:
            logger.error("Unable to find project id {0} in Salesforce for fundraiser id {1}".format(
                fundraiser.project.id, fundraiser.id))

        sffundraiser.picture_location = ""
        if fundraiser.image:
            sffundraiser.picture_location = str(fundraiser.image)

        sffundraiser.name = fundraiser.title[:80]
        sffundraiser.description = fundraiser.description
        sffundraiser.video_url = fundraiser.video_url
        sffundraiser.amount = '%01.2f' % (float(fundraiser.amount) / 100)
        sffundraiser.amount_at_the_moment = '%01.2f' % (float(fundraiser.amount_donated) / 100)

        sffundraiser.deadline = fundraiser.deadline.date()
        sffundraiser.created = fundraiser.created

        # Save the object to Salesforce
        if not dry_run:
            try:
                sffundraiser.save()
                success_count += 1
            except Exception as e:
                error_count += 1
                logger.error("Error while saving fundraiser id {0}: ".format(fundraiser.id) + str(e))

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
        except Exception as e:
            logger.error("Error while loading sfbudget_line id {0} - stopping: ".format(budget_line.id) + str(e))
            return success_count, error_count+1

        # Populate the data
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
        except Exception as e:
            logger.error("Error while loading sfdonation id {0} - stopping: ".format(donation.id) + str(e))
            return success_count, error_count+1

        # Poplate the data
        sfdonation.external_id_donation = donation.id
        sfdonation.amount = "%01.2f" % donation.amount

        if donation.user:
            try:
                sfdonation.donor = SalesforceContact.objects.get(external_id=donation.order.user.id)
            except SalesforceContact.DoesNotExist:
                logger.error("Unable to find contact id {0} in Salesforce for donation id {1}".format(
                    donation.order.user.id, donation.id))
        if donation.project:
            try:
                sfdonation.project = SalesforceProject.objects.get(external_id=donation.project.id)
            except SalesforceProject.DoesNotExist:
                logger.error("Unable to find project id {0} in Salesforce for donation id {1}".format(
                    donation.project.id, donation.id))
        if donation.fundraiser:
            try:
                sfdonation.fundraiser = SalesforceFundraiser.objects.get(external_id=donation.fundraiser.id)
            except SalesforceFundraiser.DoesNotExist:
                logger.error("Unable to find fundraiser id {0} in Salesforce for donation id {1}".format(
                    donation.fundraiser.id, donation.id))

        sfdonation.stage_name = donation.order.get_status_display()
        sfdonation.close_date = donation.created
        sfdonation.donation_created_date = donation.created
        sfdonation.donation_updated_date = donation.updated
        sfdonation.donation_ready_date = donation.completed or None

        sfdonation.type = donation.order.order_type

        if donation.user and donation.order.user.get_full_name() != '':
            sfdonation.name = donation.order.user.get_full_name()
        else:
            sfdonation.name = "Anonymous"

        sfdonation.record_type = "012A0000000ZK6FIAW"

        # Get the payment method from the associated order / payment
        sfdonation.payment_method = payment_method_mapping['']  # Maps to Unknown for DocData.
        if donation.order:
            lp = OrderPayment.get_latest_by_order(donation.order)
            if lp and lp.payment_method in payment_method_mapping:
                sfdonation.payment_method = payment_method_mapping[lp.payment_method]

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
        except Exception as e:
            logger.error("Error while loading sftask id {0} - stopping: ".format(task.id) + str(e))
            return success_count, error_count+1

        # Populate the data
        sftask.external_id = task.id

        try:
            sftask.project = SalesforceProject.objects.get(external_id=task.project.id)
        except SalesforceProject.DoesNotExist:
            logger.error("Unable to find project id {0} in Salesforce for task id {1}".format(task.project.id, task.id))

        try:
            sftask.author = SalesforceContact.objects.get(external_id=task.author.id)
        except SalesforceContact.DoesNotExist:
            logger.error("Unable to find contact id {0} in Salesforce for task id {1}".format(task.author.id, task.id))

        sftask.deadline = task.deadline or None

        sftask.effort = task.time_needed
        sftask.extended_task_description = task.description
        sftask.location_of_the_task = task.location
        sftask.people_needed = task.people_needed
        sftask.end_goal = task.end_goal

        if task.skill:
            sftask.task_expertise = task.skill.name.encode("utf-8")

        sftask.task_status = task.status
        sftask.title = task.title
        sftask.task_created_date = task.created or None

        sftask.tags = ""
        for tag in task.tags.all():
            sftask.tags = str(tag) + ", " + sftask.tags

        sftask.date_realized = None
        if task.status == 'realized' and task.date_status_change:
            sftask.date_realized = task.date_status_change

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
        except Exception as e:
            logger.error("Error while loading sftaskmember id {0} - stopping: ".format(task_member.id) + str(e))
            return success_count, error_count+1

        # Populate the data
        sftaskmember.external_id = task_member.id

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
        sftaskmember.motivation = task_member.motivation
        sftaskmember.status = TaskMember.TaskMemberStatuses.values[task_member.status].title()
        sftaskmember.taskmember_created_date = task_member.created

        # Save the object to Salesforce
        if not dry_run:
            try:
                sftaskmember.save()
                success_count += 1
            except Exception as e:
                error_count += 1
                logger.error("Error while saving task member id {0}: ".format(task_member.id) + str(e))

    return success_count, error_count


def sync_organizationmembers(dry_run, sync_from_datetime, loglevel):
    logger.setLevel(loglevel)
    error_count = 0
    success_count = 0

    org_members = OrganizationMember.objects.all()

    if sync_from_datetime:
        org_members = org_members.filter(updated__gte=sync_from_datetime)

    logger.info("Syncing {0} OrganizationMember objects.".format(org_members.count()))

    for org_member in org_members:
        logger.debug("Syncing OrganizationMember: {0}".format(org_member.id))

        # Find the corresponding SF organization members.
        try:
            sf_org_member = SalesforceOrganizationMember.objects.get(external_id=org_member.id)
        except SalesforceOrganizationMember.DoesNotExist:
            sf_org_member = SalesforceOrganizationMember()
            logger.debug("Creating new SalesforceOrganizationMember")
        except Exception as e:
            logger.error("Error while loading sf_org_member id {0} - stopping: ".format(org_member.id) + str(e))
            return success_count, error_count+1

        # Populate the data
        sf_org_member.external_id = org_member.id

        try:
            sf_org_member.contact = SalesforceContact.objects.get(external_id=org_member.user.id)
            # logger.debug("Connecting contact id {0} in Salesforce".format(org_member.user.id))
        except SalesforceContact.DoesNotExist:
            logger.error("Unable to find contact id {0} in Salesforce for organization member id {1}".format(
                org_member.user.id, org_member.id))

        try:
            sf_org_member.organization = SalesforceOrganization.objects.get(external_id=org_member.organization.id)
            # logger.debug("Connecting organization id {0} in Salesforce".format(org_member.organization.id))
        except SalesforceOrganization.DoesNotExist:
            logger.error("Unable to find organization id {0} in Salesforce for organization member id {1}".format(
                org_member.organization.id, org_member.id))

        sf_org_member.role = org_member.function

        # Save the object to Salesforce
        if not dry_run:
            try:
                sf_org_member.save()
                success_count += 1
            except Exception as e:
                error_count += 1
                logger.error("Error while saving organization member id {0}: {1}".format(org_member.id, e))

    return success_count, error_count


def send_log(filename, err, succ, command, command_ext, dry_run, loglevel):
    logger.setLevel(loglevel)

    sflog = SalesforceLogItem()

    logger.info("Sending log to Salesforce...")

    sflog.entered = timezone.localtime(timezone.now())
    sflog.source = str(command)
    sflog.source_extended = str(command_ext)
    sflog.errors = err
    sflog.successes = succ

    with open(filename, "r") as logfile:
        for line in logfile:
            if len(line) > 1300:
                sflog.message += line[:1300]
            else:
                sflog.message += line

    # Save the object to Salesforce
    if not dry_run:
        try:
            sflog.save()
        except Exception as e:
            logger.error("Error while saving log: " + str(e))