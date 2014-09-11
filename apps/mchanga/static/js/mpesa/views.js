

App.ProjectMpesaListView = Em.View.extend({
    templateName: 'project_mpesa_list'
});


App.MpesaDonateView = Em.View.extend({
    templateName: 'mpesa_donate',

    mchanga_account: function(){
        return this.get('controller.mchanga_account');
    }.property('controller.mchanga_account'),

    mpesaTitle: function(){
        return "To donate through Safaricom"
    }.property('mchanga_account'),

    mpesaInstruction: function(){
        var html = '<table>'
            + '<tr><th>1. Go to MPESA Paybill</th><td>891300</td></tr>'
            + '<tr><th>2. Enter account</th><td>' + this.get('mchanga_account') + '</td></tr>'
            + '<tr><th>3. Choose amount (KES)</th><td>e.g. 1500</td></tr>'
            + '</table><hr />'
            + 'Secure transaction provided by <img src="/static/assets/images/mchanga/m-changa.png" />';
        return html;
    }.property('mchanga_account'),

    didInsertElement: function(){
        var model = this.get('controller.content');
        this.$('a').popover({
            trigger: 'hover',
            placement: 'top',
            html: true,
            title: this.get('mpesaTitle'),
            content: this.get('mpesaInstruction')
        });
    }

});
