
// This is union of all different wallposts.
App.Order = DS.Model.extend({
    url: 'projects/wallposts',

    // Model fields
    project_slug: DS.attr('string'),
    author: DS.belongsTo('App.Member'),
    title: DS.attr('string'),
    text: DS.attr('string'),
    created: DS.attr('string'),
    timesince: DS.attr('string'),
    video_url: DS.attr('string'),
    video_html: DS.attr('string'),
    photo: DS.attr('string'),
    photos: DS.hasMany('App.MediaWallPostPhoto'),
    reactions: DS.hasMany('App.WallPostReaction')
});