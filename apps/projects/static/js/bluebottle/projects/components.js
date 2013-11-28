/**
 * Adds an animated progressbar.
 *
 * Usage: {{#bb-progressbar totalValue=100 currentValue=50}}{{/bb-progressbar}}
 */
App.BbProgressbarComponent = Ember.Component.extend({
    didInsertElement: function(){
        this.$('.slider-progress').css('width', '0px');
        var width = 0;
        if (this.totalValue > 0) {
        	if(this.currentValue >= this.totalValue){
        		width = 100;
        	} else {
	            width = 100 * this.currentValue / this.totalValue;
        	}
            width += '%';
        }
        this.$('.slider-progress').animate({'width': width}, 1000);
    }
});
