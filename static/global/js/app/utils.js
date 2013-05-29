// TODO: Combine this Country model with the one in projects and use API for loading this list.
App.Country = DS.Model.extend({
    url: "utils/countries",

    // Can't use 'id' because it doesn't work with 'optionValuePath' in Em.Select.
    pk: DS.attr('string'),
    code: DS.attr('string'),
    title: DS.attr('string')
});


App.CountryList = [
    {"value": "0", "title": "loading"}
];

App.CountrySelectView = Em.Select.extend({
    content: App.CountryList,
    optionValuePath: "content.pk",
    optionLabelPath: "content.title"
});


// TODO: get this list from the server
App.ExpertiseList = [
    {value: "unknown", title: "unknown"},
    {value: "research", title: "(online) Research"},
    {value: "agriculture", title: "Agriculture"},
    {value: "engineering", title: "Architecture/Engineering"},
    {value: "blogging", title: "Blogging"},
    {value: "brainstorming", title: "Brainstorming"},
    {value: "business_modelling", title: "Business Modelling"},
    {value: "community_engagement", title: "Community Engagement"},
    {value: "ict", title: "Computer/ICT"},
    {value: "copy_writing ", title: "Copy writing"},
    {value: "design", title: "Design"},
    {value: "education", title: "Education/Training"},
    {value: "finance", title: "Finance"},
    {value: "fund_raising", title: "Fund raising"},
    {value: "feedback", title: "Giving feedback"},
    {value: "health_care", title: "Health care"},
    {value: "hrm", title: "HRM"},
    {value: "law_and_politics", title: "Law enforcement & politics"},
    {value: "logistics", title: "Logistics"},
    {value: "pr", title: "Marketing/PR"},
    {value: "mobile_phones", title: "Mobile Phones"},
    {value: "presentations", title: "Presentations"},
    {value: "project_management", title: "Project Management"},
    {value: "social_media", title: "Social Media"},
    {value: "sustainability ", title: "Sustainability"},
    {value: "tourism", title: "Tourism"},
    {value: "translations", title: "Translations"},
    {value: "web_development", title: "Web Development"},
    {value: "writing_proposals", title: "Writing proposals"}

];

App.ExpertiseSelectView = Em.Select.extend({
    content: App.ExpertiseList,
    optionValuePath: "content.value",
    optionLabelPath: "content.title"
});

App.TimeNeededList = [
    {value: 0.25, title: "up to 15 minutes"},
    {value: 0.5, title: "half an hour"},
    {value: 1, title: "up to one hour"},
    {value: 2, title: "two hours"},
    {value: 4, title: "half a day"},
    {value: 8, title: "one day"},
    {value: 16, title: "two days"},
    {value: 40, title: "one week"},
    {value: 80, title: "two weeks"},
    {value: 160, title: "one month"}

];

App.TimeNeededSelectView = Em.Select.extend({
    content: App.TimeNeededList,
    optionValuePath: "content.value",
    optionLabelPath: "content.title"
});

App.IsAuthorMixin = Em.Mixin.create({
    isAuthor: function () {
        var username = this.get('controllers.currentUser.username');
        var authorname = this.get('author.username');
        if (username) {
            return (username == authorname);
        }
        return false;
    }.property('author.username', 'controllers.currentUser.username')
});


App.DeleteModelMixin = Em.Mixin.create({
    deleteRecordOnServer: function () {
        var record = this.get('model');
        var transaction = this.get('store').transaction();
        transaction.add(record);
        record.deleteRecord();
        transaction.commit();
    }
});


/*
 Mixin that controllers with editable models can use. E.g. App.UserProfileController

 @see App.UserProfileRoute and App.UserProfileController to see it in action.
 */
App.Editable = Ember.Mixin.create({
    saved: false,

    startEditing: function() {
        var record = this.get('model');
        if (record.transaction.isDefault == true) {
            this.transaction = this.get('store').transaction();
            this.transaction.add(record);
        }
    },

    stopEditing: function() {
        var self = this;
        var record = this.get('model');
        var transaction = record.get('transaction');

        if (record.get('isDirty')) {
            Bootstrap.ModalPane.popup({
                classNames: ['modal'],
                heading: 'Save changed data?',
                message: 'You have some unsaved changes. Do you want to save before you leave?',
                primary: 'Save',
                secondary: 'Cancel',
                callback: function(opts, e) {
                    e.preventDefault();

                    if (opts.primary) {
                        self.save(record);
                    }

                    if (opts.secondary) {
                        transaction.rollback();
                    }
                }
            });
        }
    },

    save: function(record) {
        var self = this;

        if (record.get('isDirty')) {
            this.set('saving', true);
            this.set('saved', false);
        }

        record.one('didUpdate', function() {
            // record was saved
            self.set('saving', false);
            self.set('saved', true);
        });

        record.get('transaction').commit();
    },

    saveButtonText: (function() {
        if (this.get('saving')) {
            return 'Saving';
        }

        return 'Save';
    }).property('saving')
});

App.UploadFile = Ember.TextField.extend({
    type: 'file',
    attributeBindings: ['name'],
    change: function (evt) {
        var self = this;
        var input = evt.target;
        var self = this;
        var input = evt.target;
        if (input.files && input.files[0]) {
            var reader = new FileReader();
            var that = this;
            reader.onload = function (e) {
                var fileToUpload = e.srcElement.result;
                self.get('controller').set(self.get('name'), fileToUpload);
            }
            reader.readAsDataURL(input.files[0]);
        }
    }
});


// See/Use App.DatePicker
App.DatePickerValue = Ember.TextField.extend({
    type: 'hidden',
    valueBinding: "parentView.value"
});

// See/Use App.DatePicker
App.DatePickerWidget = Ember.TextField.extend({

    dateBinding: "parentView.value",

    didInsertElement: function(){
        this.$().datepicker();
        this.$().datepicker('setDate', this.get('date'));
    },

    change: function(){
        this.set('date', this.$().datepicker('getDate'));
    }
});

// This renders a TextField with the localized date.
// On click it will use jQuery UI date picker dialog so the user can select a date.
// valueBinding should bind to a  DS.attr('date') property of an Ember model.
App.DatePicker = Ember.ContainerView.extend({
    childViews: [App.DatePickerValue, App.DatePickerWidget]
});


// The id will be the tag string.
App.Tag = DS.Model.extend({
    url: 'utils/tags',
    // Hack to make sure that newly added tags won't conflict when the are saved embedded.
    loadedData: function() {
        if (this.get('isDirty') === false) {
            this._super.apply(this, arguments);
        }
    }
});


App.TagField = Em.TextField.extend({
    keyUp: function(e){
        if (e.keyCode == 188) {
            e.preventDefault();
            var val = this.get('value');
            val = val.replace(',','');
            this.set('parentView.new_tag', val);
            this.get('parentView').addTag();
        }
    }
});

App.TagWidget = Em.View.extend({
    templateName: 'tag_widget',
    addTag: function(){
        if (this.get('new_tag')) {
            var new_tag = this.get('new_tag').toLowerCase();
            var tags = this.get('tags');
            var tag = App.Tag.createRecord({'id': new_tag});
            tags.pushObject(tag);
            this.set('new_tag', '');
        }
    },
    removeTag: function(tag) {
        var tags = this.get('tags');
        tags.removeObject(tag);
    }
});


/*
  Mixin for (Array)Controllers to limit the items viewed.

  'model' should hold the complete list.
  'items' holds de items to show and is the property to use in henadlebars template.
  'canLoadMore' is a boolean to determine if there are still more items to show.
  'showMore' is the event to trigger to add more items.
  'perPage' is the initial and incremental number of items to show.
  'page' tracks the current page.
 */
App.ShowMoreItemsMixin = Em.Mixin.create({
    perPage: 5,
    page: 0,
    items: Em.A(),

    remainingItemCount: function(){
        return this.get('model.length') - (this.get('page')  * this.get('perPage'));
    }.property('page', 'model', 'perPage'),

    canLoadMore: function(){
        var totalPages = Math.ceil(this.get('model.length') / this.get('perPage'));
        return totalPages > this.get('page');
    }.property('perPage', 'page'),

    loadInitial: function(){
        this.showMore();
    }.observes('model.isLoaded'),

    showMore: function() {
        var start = this.get('page') * this.get('perPage');
        this.incrementProperty('page');
        var end = this.get('page') * this.get('perPage');
        this.get('items').pushObjects(this.get('model').slice(start, end));
    }

});

App.PopOverMixin = Em.Mixin.create({
   didInsertElement: function(){
        this.$('.has-popover').popover({trigger: 'hover', placement: 'right'});
        this.$('.has-tooltip').tooltip({trigger: 'hover', placement: 'right'});
   }
});


App.Theme = DS.Model.extend({
    url:'utils/themes',

    value: DS.attr('string'),
    title: DS.attr('string')
});


App.ThemeList = [
    {value: "loading", title: "--loading--"},
];

App.ThemeSelectView = Em.Select.extend({
    content: App.ThemeList,
    optionValuePath: "content.value",
    optionLabelPath: "content.title"
});


App.MapPicker = Em.View.extend({

    templateName: 'map_picker',
    submit: function(e){
        e.preventDefault();
        this.lookUpLocation();
    },

    lookUpLocation: function() {
        var address = this.get('lookup');
        var view = this;
        view.geocoder.geocode( {'address': address}, function(results, status) {
            if (status == google.maps.GeocoderStatus.OK) {
                view.map.setCenter(results[0].geometry.location);
                var marker = new google.maps.Marker({
                    map: view.map,
                    position: results[0].geometry.location
                });
                view.set('latitude',  results[0].geometry.location.lat());
                view.set('longitude',  results[0].geometry.location.lng());

            } else {
                alert('Geocode was not successful for the following reason: ' + status);
            }
        });
    },

    didInsertElement: function(){
        var view = this;
        this.geocoder = new google.maps.Geocoder();
        var view = this;
        var mapOptions = {
            zoom: 6,
            center: new google.maps.LatLng(view.get('latitude'), view.get('longitude')),
            mapTypeId: google.maps.MapTypeId.ROADMAP
          };
        view.map = new google.maps.Map(this.$('.map-picker').get(0), mapOptions);


        function placeMarker(position, map) {
            var marker = new google.maps.Marker({
                position: position,
                map: map
            });
            map.panTo(position);
        }
        google.maps.event.addListener(view.map, 'click', function(e) {
            var loc = {};
            view.set('latitude',  e.latLng.lat());
            view.set('longitude',  e.latLng.lng());
            placeMarker(e.latLng, view.map);
        });
    }

});


App.MapPickerValue = Ember.TextField.extend({
    type: 'hidden',
    valueBinding: "parentView.value"

});


App.MapPicker = Ember.ContainerView.extend({
    childViews: [App.MapPickerValue, App.MapPickerWidget]

});

å
