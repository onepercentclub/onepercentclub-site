/**
 * Embedded mapping
 */

App.Adapter.map('App.WallPost', {
    author: {embedded: 'load'},
    photos: {embedded: 'load'},
    reactions: {embedded: 'load'}
});
App.Adapter.map('App.TextWallPost', {
    author: {embedded: 'load'},
    reactions: {embedded: 'load'}
});
App.Adapter.map('App.MediaWallPost', {
    author: {embedded: 'load'},
    photos: {embedded: 'load'},
    reactions: {embedded: 'load'}
});
App.Adapter.map('App.WallPostReaction', {
    author: {embedded: 'load'}
});


/*
 Models
 */


App.WallPostPhoto = DS.Model.extend({
    url: 'wallposts/photos',
    photo: DS.attr('image'),
    mediawallpost: DS.belongsTo('App.MediaWallPost')
});

// This is union of all different wallposts.
App.WallPost = DS.Model.extend({
    url: 'wallposts',

    // Model fields
    author: DS.belongsTo('App.UserPreview'),
    title: DS.attr('string', {defaultValue: ''}),
    text: DS.attr('string', {defaultValue: ''}),
    type: DS.attr('string'),
    created: DS.attr('date'),
    reactions: DS.hasMany('App.WallPostReaction'),

    video_url: DS.attr('string', {defaultValue: ''}),
    video_html: DS.attr('string'),
    photos: DS.hasMany('App.WallPostPhoto'),

    parent_id: DS.attr('string'),
    parent_type: DS.attr('string'),

    related_type: DS.attr('string'),
    related_object: DS.attr('object'), // keep it generic

    isSystemWallPost: function(){
        return (this.get('type') == 'system');
    }.property('type'),

    // determine if this wallpost is related to a fundraiser
    fundraiser: function() {
        if (this.get('related_object')){
            var fundraiser = this.get('related_object').fundraiser;
            if(this.get('isSystemWallPost') && this.get('related_type') == 'donation' && fundraiser !== undefined){
                return fundraiser;
            }
        }
        return false;
    }.property('related_type', 'isSystemWallPost', 'related_object')
});


App.TextWallPost = App.WallPost.extend({
    url: 'wallposts/textwallposts'
});


App.MediaWallPost = App.WallPost.extend({
    url: 'wallposts/mediawallposts'
});


/* Reactions */


App.WallPostReaction = DS.Model.extend({
    url: 'wallposts/reactions',

    text: DS.attr('string'),
    author: DS.belongsTo('App.UserPreview'),
    created: DS.attr('date'),
    wallpost: DS.belongsTo('App.WallPost')
});

