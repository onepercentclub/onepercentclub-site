App.CheetahProgressbarComponent = Ember.Component.extend({
    didInsertElement: function(){
        this.$('.slider-progress, .funded-cheetah-progress').css('width', '0px');
        var width = 0,
            // Target is 30% not 100%
            target =  30/100 * this.targetValue;

        if (target > 0) {
            if(this.currentValue >= target){
                width = 100;
            } else {
                width = 100 * this.currentValue / target;
            }
            width += '%';
        }
        this.$('.slider-progress, .funded-cheetah-progress').animate({'width': width}, 1000);
    }
});


