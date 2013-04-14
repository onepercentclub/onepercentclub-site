
/*
 Models
 */

App.Country = DS.Model.extend({
    name: DS.attr('string'),
    subregion: DS.attr('string')
});


App.Project = DS.Model.extend({
    url: 'projects',

    // Model fields
    slug: DS.attr('string'),
    title: DS.attr('string'),
    image: DS.attr('string'),
    image_small: DS.attr('string'),
    image_square: DS.attr('string'),
    image_bg: DS.attr('string'),
    phase: DS.attr('string'),
    organization: DS.attr('string'),
    description: DS.attr('string'),
    money_asked: DS.attr('number'),
    money_donated: DS.attr('number'),
    created: DS.attr('date'),
    tags: DS.attr('array'),
    owner: DS.belongsTo('App.MemberPreview'),
    country: DS.belongsTo('App.Country'),

    // FIXME: For now we set some default values here because we don't have actual numbers
    supporter_count: DS.attr('number', {defaultValue: 123}),
    days_left: DS.attr('number', {defaultValue: 123}),

    money_needed: function(){
        var donated = this.get('money_asked') - this.get('money_donated');
        if (donated < 0) {
            return 0;
        }
        return Math.ceil(donated);
    }.property('money_asked', 'money_donated')

});


/*
 Controllers
 */


App.ProjectController = Em.ObjectController.extend({
    isFundable: function(){
        return this.get('phase') == 'Fund';
    }.property('phase')

});


/*
 Views
 */

App.ProjectSupportersView = Em.View.extend({
    templateName: 'project_supporters'
});


App.ProjectListView = Em.View.extend({
    templateName: 'project_list'
});


App.ProjectView = Em.View.extend({
    templateName: 'project',

    didInsertElement: function(){
        this.$('#detail').css('background', 'url("' + this.get('controller.image_bg') + '") 50% 50%');
        this.$('#detail').css('background-size', '100%');

        // TODO: The 50% dark background doesn't work this way. :-s
        this.$('#detail').css('backgroundColor', 'rgba(0,0,0,0.5)');

        var donated = this.get('controller.money_donated');
        var asked = this.get('controller.money_asked');
        this.$('.donate-progress').css('width', '0px');
        var width = 0;
        if (asked > 0) {
            width = 100 * donated / asked;
            width += '%';
        }
        this.$('.donate-progress').animate({'width': width}, 1000);
    }
});
