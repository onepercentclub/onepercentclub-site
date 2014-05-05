from django.utils.translation import ugettext as _

# Custom dashboard configuration
# ADMIN_TOOLS_INDEX_DASHBOARD = 'fluent_dashboard.dashboard.FluentIndexDashboard'
ADMIN_TOOLS_INDEX_DASHBOARD = 'dashboard.CustomIndexDashboard'
ADMIN_TOOLS_APP_INDEX_DASHBOARD = 'fluent_dashboard.dashboard.FluentAppIndexDashboard'
ADMIN_TOOLS_MENU = 'fluent_dashboard.menu.FluentMenu'


# Further customize the dashboard
FLUENT_DASHBOARD_DEFAULT_MODULE = 'admin_tools.dashboard.modules.AppList'
FLUENT_DASHBOARD_APP_GROUPS = (
    (_('Site content'), {
        'models': [
            'apps.pages.*',
            'apps.blogs.*',
            'apps.media.*',
            'apps.banners.*',
            'apps.quotes.*',
            'apps.statistics.*',
            'apps.campaigns.*',
        ],
        'module': 'fluent_dashboard.modules.AppIconList',
        'collapsible': False,
    }),
    (_('Projects'), {
        'models': (
            'apps.projects.models.*',
            'apps.fundraisers.*',
            'apps.organizations.*',
        ),
        'module': 'fluent_dashboard.modules.AppIconList',
        'collapsible': False,
    }),
    (_('Donations'), {
        'models': (
            'apps.fund.*',
            'apps.vouchers.*',
        ),
        'module': 'fluent_dashboard.modules.AppIconList',
        'collapsible': False,
    }),
    (_('Finances'), {
        'models': (
            'apps.payouts.*',
            'apps.cowry_docdata.*',
            'apps.cowry.*',
        ),
        'module': 'fluent_dashboard.modules.AppIconList',
        'collapsible': False,
    }),
    (_('Tasks'), {
        'models': (
            'apps.tasks.*',
        ),
        'module': 'fluent_dashboard.modules.AppIconList',
        'collapsible': False,
    }),
    (_('Members'), {
        'models': (
            'django.contrib.auth.*',
            'registration.*',
            'bluebottle.accounts.*',
        ),
        'module': 'fluent_dashboard.modules.AppIconList',
        'collapsible': False,
    }),
    (_('Site settings'), {
        'models': (
            'django.contrib.sites.*',
            'apps.redirects.*'
        ),
        'module': 'fluent_dashboard.modules.AppIconList',
        'collapsible': False,
    }),
    (_('Wall Posts'), {
        'models': (
            'apps.wallposts.*',
        ),
        'module': 'fluent_dashboard.modules.AppIconList',
        'collapsible': False,
    }),
    # The '*' selector acts like a fallback for all other apps. This section mainly displays models
    # with tabular data that is rarely touched. The important models have an icon.
    (_('Applications'), {
        'models': ('*',),
        'module': FLUENT_DASHBOARD_DEFAULT_MODULE,
        'collapsible': False,
    }),
)

ADMIN_TOOLS_THEMING_CSS = 'css/admin/dashboard.css'

# Icon filenames can either be relative to the theme directory (if no path separators are used),
# or be a relative to the STATIC_URL (if path separators are used in the icon name)
# The dictionary key is appname/modelname, identical to the slugs used in the admin page URLs
# django-fluent-dashboard ships with a set of commonly useful icons. To get the whole Oxygen set,
# download http://download.kde.org/stable/4.9.0/src/oxygen-icons-4.9.0.tar.xz It's LGPL3 licensed.
FLUENT_DASHBOARD_APP_ICONS = {
    # Members
    'accounts/bluebottleuser': 'icons/flaticons_stroke/SVGs/user-1.svg',
    'auth/group': 'icons/flaticons_stroke/SVGs/group-1.svg',
    'registration/registrationprofile': 'icons/flaticons_stroke/SVGs/add-user-1.svg',


    # Projects
    'projects/project': 'icons/flaticons_stroke/SVGs/notebook-1.svg',
    'projects/projectpitch': 'icons/flaticons_stroke/SVGs/lightbulb-3.svg',
    'projects/projectplan': 'icons/flaticons_stroke/SVGs/notebook-3.svg',
    'projects/projecttheme': 'icons/flaticons_stroke/SVGs/leaf-1.svg',
    'projects/projectcampaign': 'icons/flaticons_stroke/SVGs/megaphone-1.svg',
    'projects/projectresult': 'icons/flaticons_stroke/SVGs/trophy-1.svg',
    'organizations/organization': 'icons/flaticons_stroke/SVGs/suitcase-1.svg',
    'organizations/organizationmember': 'icons/flaticons_stroke/SVGs/group-1.svg',
    'projects/partnerorganization': 'icons/flaticons_stroke/SVGs/compose-3.svg',

    # Fundraisers
    'fundraisers/fundraiser': 'icons/flaticons_solid/SVGs/bike-1.svg',

    # Campaigns
    'campaigns/campaign': 'icons/flaticons_solid/SVGs/rocket-1.svg',

    # Wall Posts
    'wallposts/wallpost': 'icons/flaticons_stroke/SVGs/paragraph-text-1.svg',
    'wallposts/systemwallpost': 'icons/flaticons_stroke/SVGs/paragraph-text-1.svg',
    'wallposts/textwallpost': 'icons/flaticons_stroke/SVGs/paragraph-text-1.svg',
    'wallposts/mediawallpost': 'icons/flaticons_stroke/SVGs/photo-gallery-1.svg',
    'wallposts/reaction': 'icons/flaticons_stroke/SVGs/comment-2.svg',

    # Donations
    'fund/donation': 'icons/flaticons_stroke/SVGs/money-2.svg',
    'fund/order': 'icons/flaticons_stroke/SVGs/cart-1.svg',
    'fund/recurringdirectdebitpayment': 'icons/flaticons_stroke/SVGs/repeat-2.svg',
    'vouchers/voucher': 'icons/flaticons_stroke/SVGs/gift-2.svg',
    'vouchers/customvoucherrequest': 'icons/flaticons_stroke/SVGs/mail-2.svg',

    # Tasks
    'tasks/task': 'icons/flaticons_stroke/SVGs/work-1.svg',
    'tasks/skill': 'icons/flaticons_stroke/SVGs/toolbox-1.svg',

    # Finances
    'payouts/payout': 'icons/flaticons_stroke/SVGs/bag-1.svg',
    'payouts/organizationpayout': 'icons/flaticons_stroke/SVGs/money-2.svg',
    'payouts/bankmutation': 'icons/flaticons_stroke/SVGs/menu-2.svg',
    'payouts/bankmutationline': 'icons/flaticons_stroke/SVGs/menu-2.svg',
    'cowry_docdata/docdatapaymentorder': 'icons/flaticons_stroke/SVGs/wallet-1.svg',
    'cowry_docdata/docdatapaymentlogentry': 'icons/flaticons_stroke/SVGs/menu-list-3.svg',

    # Site Content
    'banners/slide': 'icons/flaticons_stroke/SVGs/id-1.svg',
    'blogs/blogpostproxy': 'icons/flaticons_stroke/SVGs/newspaper-2.svg',
    'blogs/newspostproxy': 'icons/flaticons_stroke/SVGs/newspaper-2.svg',
    'pages/page': 'icons/flaticons_stroke/SVGs/paragraph-text-1.svg',
    'pages/contactmessage': 'icons/flaticons_stroke/SVGs/mail-2.svg',
    'quotes/quote': 'icons/flaticons_stroke/SVGs/post-comment-2.svg',
    'statistics/statistic': 'icons/flaticons_stroke/SVGs/graph-1.svg',

    # Site Settings
    'sites/site': 'icons/flaticons_stroke/SVGs/browser-2.svg',
    'redirects/redirect': 'icons/flaticons_stroke/SVGs/next-3.svg',
}
