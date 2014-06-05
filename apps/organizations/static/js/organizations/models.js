App.MyOrganization.reopen({
    // Override BB here as the website is not required.
    requiredOrganizationFields: ['name', 'email', 'phone_number'],
    valid: Em.computed.and('validOrganization', 'validBank'),

    validProfile: function () {
        if (this.get('name') &&  this.get('description') && this.get('email')) {
            return true;
        }
        return false;
    }.property('name', 'description', 'email'),

    validLegalStatus: function () {
        if (this.get('documents.length') > 0){
            return true;
        }
        return false;
    }.property('documents.length'),

    friendlyFieldNames: {
        'name': 'Name',
        'email' : 'Email',
        'phone_number' : 'Phone number' 
    }
});
