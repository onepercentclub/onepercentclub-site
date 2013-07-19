import logging
from apps.accounts.models import BlueBottleUser
from apps.projects.models import Project, ProjectBudgetLine, ProjectCampaign, ProjectPitch, ProjectPlan
from apps.organizations.models import Organization, OrganizationAddress
from apps.tasks.models import Task, TaskMember
from apps.fund.models import Donation, Voucher, VoucherStatuses, DonationStatuses
from apps.bluebottle_salesforce.models import SalesforceOrganization, SalesforceContact, SalesforceProject, \
    SalesforceDonation, SalesforceProjectBudget, SalesforceTask, SalesforceTaskMembers, SalesforceVoucher

logger = logging.getLogger(__name__)


def sync_organizations(dry_run, sync_from_datetime, loglevel):
    logger.setLevel(loglevel)
    error_count = 0
    success_count = 0

    organizations = Organization.objects.all()
    if sync_from_datetime:
        organizations = organizations.filter(updated__gte=sync_from_datetime)

    logger.info("Syncing {0} Organization objects.".format(organizations.count()))

    for organization in organizations:
        logger.info("Syncing Organization: {0}".format(organization.id))

        # Find the corresponding SF organization.
        try:
            sforganization = SalesforceOrganization.objects.get(external_id=organization.id)
        except SalesforceOrganization.DoesNotExist:
            sforganization = SalesforceOrganization()

        # SF Layout: Account details section.
        sforganization.name = organization.name
        sforganization.legal_status = organization.legal_status
        sforganization.description = organization.description

        # TODO: Determine if and how organization type should be entered
        # sforganization.organization_type =

        # SF Layout: Contact Information section. Intentionally ignore the address type as it is not used.
        try:
            organizationaddress = OrganizationAddress.objects.get(organization=organization)
        except OrganizationAddress.DoesNotExist:
            sforganization.billing_city = ''
            sforganization.billing_street = ''
            sforganization.billing_postal_code = ''
            sforganization.billing_country = ''
        except OrganizationAddress.MultipleObjectsReturned:
            logger.warn("Organization id {0} has multiple addresses, this is not supported by the integration.".format(
                organization.id))
        else:
            sforganization.billing_city = organizationaddress.city
            sforganization.billing_street = organizationaddress.line1 + " " + organizationaddress.line2
            sforganization.billing_postal_code = organizationaddress.postal_code
            if organizationaddress.country:
                sforganization.billing_country = organizationaddress.country.name
            else:
                sforganization.billing_country = ''
        # E-mail addresses for organizations are currently left out because source data is not validated
        # sforganization.email_address = organization.email
        sforganization.phone = organization.phone_number
        sforganization.website = organization.website

        # SF Layout: Bank Account section.
        sforganization.address_bank = organization.account_bank_address
        sforganization.bank_account_name = organization.account_bank_name
        sforganization.bank_account_number = organization.account_number
        sforganization.bank_name = organization.name
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

    users = BlueBottleUser.objects.all()

    if sync_from_datetime:
        users = users.filter(updated__gte=sync_from_datetime)

    logger.info("Syncing {0} User objects.".format(users.count()))

    for user in users:
        logger.info("Syncing User: {0}".format(user.id))

        # Find the corresponding SF user.
        try:
            contact = SalesforceContact.objects.get(external_id=user.id)
        except SalesforceContact.DoesNotExist:
            contact = SalesforceContact()

        # Determine and set user type (person, group, foundation, school, company, ... )
        contact.category1 = BlueBottleUser.UserType.values[user.user_type]

        # SF Layout: Profile section.
        contact.first_name = user.first_name
        if user.last_name:
            contact.last_name = user.last_name
        else:
            contact.last_name = "1%MEMBER"

        if user.gender == "male":
            contact.gender = BlueBottleUser.Gender.values['male']
        elif user.gender == "female":
            contact.gender = BlueBottleUser.Gender.values['female']
        else:
            contact.gender = ""

        contact.user_name = user.username
        contact.is_active = user.is_active
        contact.close_date = user.deleted
        contact.member_since = user.date_joined
        contact.why_one_percent_member = user.why
        contact.about_me_us = user.about
        contact.location = user.location
        contact.birth_date = user.birthdate
        # TODO: check field contact.available_time = user.available_time ?
        # contact.which_1_would_you_like_to_contribute =
        # TODO: contact.tags - should be copied? - 20130530 - discussed with Suzanne, check with Liane
        # contact.tags = user.tags.get()

        # SF Layout: Contact Information section.
        contact.email = user.email
        contact.website = user.website

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

        # Note: Fill with the number of activities of a member
        # contact.activity_number = user.

        # SF Layout: Contact Activity section.
        # -- back-end calculations with Ben
        #contact.amount_of_single_donations

        # -- 20130530 - Not used: discussed with Suzanne,Ben
        #contact.has_n_friends
        #contact.has_given_n_vouchers
        #contact.is_doing_n_tasks
        #contact.number_of_donations
        #contact.support_n_projects
        #contact.total_amount_of_donations

        # SF Layout: My Settings section.
        contact.receive_newsletter = user.newsletter
        contact.primary_language = user.primary_language

        # TODO: contact expertise on website by web-team (20130530)
        #contact.administration_finance =
        #contact.agriculture_environment
        #contact.architecture
        #contact.computer_ict
        #contact.design
        #contact.economy_business
        #contact.education
        #contact.fund_raising
        #contact.graphic_design
        #contact.health
        #contact.internet_research
        #contact.law_and_politics
        #contact.marketing_pr
        #contact.online_marketing
        #contact.photo_video
        #contact.physics_technique
        #contact.presentations
        #contact.project_management
        #contact.psychology
        #contact.social_work
        #contact.sport_and_development
        #contact.tourism
        #contact.trade_transport
        #contact.translating_writing
        #contact.web_development
        #contact.writing_proposals

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

    projects = Project.objects.all()

    # TODO: Projects is a little more complicated because of all of the related modules.
    # if sync_from_datetime:
    #     projects = projects.filter(updated__gte=sync_from_datetime)

    logger.info("Syncing {0} Project objects.".format(projects.count()))

    for project in projects:
        logger.info("Syncing Project: {0}".format(project.id))

        # Find the corresponding SF project.
        try:
            sfproject = SalesforceProject.objects.get(external_id=project.id)
        except SalesforceProject.DoesNotExist:
            sfproject = SalesforceProject()

        # SF Layout: 1%CLUB Project Detail section.
        try:
            project_campaign = ProjectCampaign.objects.get(project=project)
        except ProjectCampaign.DoesNotExist:
            pass
        else:
            sfproject.amount_at_the_moment = project_campaign.money_donated
            sfproject.amount_requested = project_campaign.money_asked
            sfproject.amount_still_needed = project_campaign.money_needed

        try:
            sfproject.project_owner = SalesforceContact.objects.get(external_id=project.owner.id)
        except SalesforceContact.DoesNotExist:
            logger.error("Unable to find contact id {0} in Salesforce for project id {1}".format(project.owner.id,
                                                                                                 project.id))

        sfproject.project_name = project.title

        # TODO: Confirm that this is the correct project status to take
        sfproject.status_project = project.phase

        # SF Layout: Summary Project Details section.
        try:
            project_pitch = ProjectPitch.objects.get(project=project)
        except ProjectPitch.DoesNotExist:
            pass
        else:
            if project_pitch.country:
                sfproject.country_in_which_the_project_is_located = project_pitch.country.name
            sfproject.describe_the_project_in_one_sentence = project_pitch.title

        try:
            project_plan = ProjectPlan.objects.get(project=project)
        except ProjectPlan.DoesNotExist:
            sfproject.organization_account = None
        else:
            # TODO: determine what should be in project target_group?
            # sfproject.target_group = project.fundphase.impact_group
            sfproject.number_of_people_reached_direct = project_plan.reach
            # TODO: determine what should be in project number_of_people_reached_indirect?
            # sfproject.number_of_people_reached_indirect = (project.fundphase.impact_indirect_male +
            #                                                project.fundphase.impact_indirect_female)
            try:
                sfproject.organization_account = SalesforceOrganization.objects.get(
                    external_id=project_plan.organization.id)
            except SalesforceOrganization.DoesNotExist:
                logger.error("Unable to find organization id {0} in Salesforce for project id {1}".format(
                    project_plan.organization.id, project.id))

        # SF Layout: Extensive project information section.
        # TODO: Determine extended project information details
        # Unknown error: sfproject.describe_where_the_money_is_needed_for =
        # Unknown error: sfproject.project_url = project.get_absolute_url
        # Unknown: sfproject.third_half_project =
        # Unknown: sfproject.comments =
        # Unknown: sfproject.contribution_project_in_reducing_poverty =
        # Unknown: sfproject.earth_charther_project =
        # Unknown: sfproject.extensive_project_description =
        # Unknown: sfproject.project_goals =
        # Unknown: sfproject.sustainability =
        # sfproject.starting_date_of_the_project = project.planned_start_date
        # Unknown - Multipicklist: ?? - sfproject.millennium_goals =
        # Note: Not used like contact?-  sfproject.tags =

        # SF Layout: Project planning and budget section.
        # TODO: Determine project budget details
        # Unknown: sfproject.additional_explanation_of_budget =
        # sfproject.end_date_of_the_project = project.planned_end_date
        # Unknown: sfproject.expected_funding_through_other_resources =
        # Unknown: sfproject.expected_project_results =
        # Unknown: sfproject.funding_received_through_other_resources =
        # Unknown: sfproject.need_for_volunteers =
        # Unknown: sfproject.other_way_people_can_contribute =
        # Unknown: sfproject.project_activities_and_timetable =

        # SF Layout: Referrals section.
        # TODO: Determine project referral section integration
        # Unknown: sfproject.name_referral_1 = project.referral.name
        # Unknown: sfproject.name_referral_2 =
        # Unknown: sfproject.name_referral_3 =
        # Unknown: sfproject.description_referral_1 = project.referral.description
        # Unknown: sfproject.description_referral_2 =
        # Unknown: sfproject.description_referral_3 =
        # Unknown: sfproject.email_address_referral_1 = project.referral.email
        # Unknown: sfproject.email_address_referral_2 =
        # Unknown: sfproject.email_address_referral_3 =
        # Unknown: sfproject.relation_referral_1_with_project_org =
        # Unknown: sfproject.relation_referral_2_with_project_org =
        # Unknown: sfproject.relation_referral_3_with_project_org =

        # SF Layout: Project Team Information section.
        sfproject.project_created_date = project.created

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
    # TODO: The ProjectBudgetLine model needs an updated field. Wait for a proper solution for projects.
    # if sync_from_datetime:
    #     budget_lines = budget_lines.filter(updated__gte=sync_from_datetime)

    logger.info("Syncing {0} BudgetLine objects.".format(budget_lines.count()))

    for budget_line in budget_lines:
        logger.info("Syncing BudgetLine: {0}".format(budget_line.id))

        # Find the corresponding SF budget lines.
        try:
            sfbudget_line = SalesforceProjectBudget.objects.get(external_id=budget_line.id)
        except SalesforceProjectBudget.DoesNotExist:
            sfbudget_line = SalesforceProjectBudget()

        # SF Layout: Information section
        # Unknown: Materialen, Tools, Transport, Training, etc.
        # sfbudget_line.category =

        sfbudget_line.costs = "%01.2f" % (budget_line.amount / 100)
        sfbudget_line.description = budget_line.description
        sfbudget_line.external_id = budget_line.id
        sfbudget_line.project = SalesforceProject.objects.get(external_id=budget_line.project_plan.id)

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
        logger.info("Syncing Donation: {0}".format(donation.id))

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

        # Unknown - sfdonation.payment_method =

        sfdonation.stage_name = DonationStatuses.values[donation.status]
        # TODO: Should we use "Recurring" instead of Monthly?
        sfdonation.opportunity_type = donation.DonationTypes.values[donation.donation_type]

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
        logger.info("Syncing Voucher: {0}".format(voucher.id))

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
        sfvoucher.stage_name = VoucherStatuses.values[voucher.status]

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
        logger.info("Syncing Task: {0}".format(task.id))

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

        sftask.deadline = task.deadline
        sftask.effort = task.time_needed
        sftask.extended_task_description = task.description
        sftask.location_of_the_task = task.location
        sftask.task_expertise = task.expertise
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
        logger.info("Syncing TaskMember: {0}".format(task_member.id))

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
