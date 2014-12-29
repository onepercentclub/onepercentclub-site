App.MyOrganization.reopen({
    // Override BB here as the website is not required.
    requiredOrganizationFields: ['name', 'email', 'phone_number', 'hasDocument'],
    valid: Em.computed.and('validOrganization', 'validBank'),

    validProfile: function () {
        if (this.get('name') &&  this.get('description') && this.get('email')) {
            return true;
        }
        return false;
    }.property('name', 'description', 'email'),

    friendlyFieldNames: {
        'name': gettext('Name'),
        'email' : gettext('Email'),
        'phone_number' : gettext('Phone number'),
        'hasDocument' : gettext('Document'),
        'account_holder_name' : gettext('Account name'),
        'account_holder_address' : gettext('Account address'),
        'account_holder_postal_code': gettext("Account postal code"),
        'account_holder_city' : gettext('Account city'),
        'account_holder_country' : gettext('Account country'),
        'account_bic' : gettext('Account BIC code'),
        'account_iban': gettext('Account IBAN code'),
        'validIban': gettext('Account IBAN code'),
        'validBic': gettext('Account BIC code')
    }
});
