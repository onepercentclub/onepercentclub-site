App.MyOrganization.reopen({
    requiredFields: ['name', 'email', 'phone_number'],

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
