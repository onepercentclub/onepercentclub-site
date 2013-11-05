Factory.define('wallPost', {
  	// id: 'projectfactory',
  	// created: Date.now(),
  	title: 'Kick start on the road to clean drinking water',
  	text: 'Community Water Enterprise’s recent marketing efforts',
    type: 'media',
    author: function() {
    	return attr('userPreview');
  	},
    reactions: [],
    video_html: '',
    video_url: '',
    photos: ''
});