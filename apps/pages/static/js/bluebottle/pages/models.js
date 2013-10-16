/* Models */


App.Page = DS.Model.extend({
    url: 'pages',
    title: DS.attr('string'),
    body: DS.attr('string')
});


App.ContactMessage = DS.Model.extend({
    url: 'pages/contact',

    name: DS.attr('string'),
    email: DS.attr('string'),
    message: DS.attr('string'),

    isComplete: function(){
        if (this.get('name') && this.get('email') && this.get('message')){
            return true;
        }
        return false;
    }.property('name', 'email', 'message'),

    isSent: function(){
        if (this.get('id')){
            return true;
        }
        return false;
    }.property('id')
});


App.PartnerOrganization = DS.Model.extend({
    url: 'partners',
    name: DS.attr('string'),
    projects: DS.hasMany('App.ProjectPreview'),
    description: DS.attr('string'),
    image: DS.attr('image')
});
