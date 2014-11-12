App.MonthlyDonationProjectView = App.ProjectPreviewView.extend({
    tagName: 'li',
    classNames: ['project-list-item'],

    actions: {
        deleteProject: function(project){
            var controller = this.get('controller');
            this.$().fadeOut(500, function(){
                controller.send('deleteProject', project);
            });
        }
    }
});
