$(document).ready(function(){
    //initProgress();
    //initLightbox();
    //initJiraFeedback();
    
    // added by Frans
    // initFileUpload();
    initToggleText();
    $("label.inline").inFieldLabels(); 
    $("textarea").autogrow();
})

function initToggleText(){
    
    $('.toggle-reactions').live('click', function(e) {
        $('.reactions', $(this).closest('.reaction-box')).toggle();
    });

    // toggles content and classnames on click, mouseenter & mouseleave
    $('.toggle-reactions, .toggle-love')
        .live('click', function(e) {
            $(this)
                .toggleClass('is-active')
                .addClass('is-activated')
                .trigger('mouseleave');
            e.preventDefault();
        })
        .live('mouseenter', function(e) {
            if ( $(this).hasClass('is-active') ) {
                $(this).html( $(this).data('content-toggled-hover') );
            } else {
                $(this).html( $(this).data('content-hover') );
            }
            $(this).removeClass('is-activated');
        })
        .live('mouseleave', function(e) {
            if ( $(this).hasClass('is-active') ) {
                $(this).html( $(this).data('content-toggled') );
            } else {
                $(this).html( $(this).data('content') );
            }
        });
    
    $('.share')
        .live('mouseenter', function(e) {
            $('.share-actions', $(this)).show();
        })
        .live('mouseleave', function(e) {
            $('.share-actions', $(this)).hide();
        });
};

function initFileUpload(){

    // replace with multiple file uploader
    $('.fileupload').fileupload({

    });
}

function initLightbox(){
  
    // open external data in lightbox on specific links
    $('a.open-in-lightbox').live('click',function(e){
    
      e.preventDefault();
      
      $.colorbox({
        href: this.href,
        fixed: true,
        overlayClose: false,
        escKey: true,
        opacity: '0.7',
        scrolling: true,
        transition: 'none',
        width: 880,
        maxHeight: '90%',
        top: '40px',
        onComplete: function(){
            initInputCountdown('#colorbox');
        }
      });
      
      return false;
      
    });
    
    // custom lightbox close actions
    $("#lightbox-cancel, #lightbox-save").live("click", function(e){
        $.colorbox.close();
    });

    $(".loginbox").colorbox({
        fixed: true,
        overlayClose: false,
        escKey: true,
        opacity: '0.7',
        scrolling: false,
        transition: 'none',
        width: 400,
        height: 300,
        iframe: true
    });

}

function initProgress(){
    $('.donate-static').each(function(){
        var donated = Math.round($('.donated', this).html()); 
        var asked = Math.round($('.asked', this).html());
        if (donated > asked) {
            perc = 100;
        } else if (asked) {
            perc = 100 * donated / asked;
        } else {
            perc = 100;
        }
        perc = Math.round(perc);
        $('.donate-percentage', this).css({width: perc +'%'});
    });

    $('.donate-status').each(function(){
        var donated = Math.round($('.donated', this).html()); 
        var asked = Math.round($('.asked', this).html());
        if (donated > asked) {
            perc = 100;
        } else if (asked) {
            perc = 100 * donated / asked;
        } else {
            perc = 100;
        }
        perc = Math.round(perc);
        if (perc == 0) {
            $('.donate-percentage', this).addClass('is-empty');
        } else if(perc == 100) {
            $('.donate-percentage', this).addClass('is-full');
            
        } else {
            $('.donate-percentage', this).addClass('is-in-progress');
        }
        
        $('.donate-percentage', this).animate({width: perc +'%'}, 2000);
        
    });
}


function initJiraFeedback() {
    jQuery.ajax({
        url: "https://onepercentclub.atlassian.net/s/en_USfyzlz7-418945332/809/42/1.2.5/_/download/batch/com.atlassian.jira.collector.plugin.jira-issue-collector-plugin:issuecollector-embededjs/com.atlassian.jira.collector.plugin.jira-issue-collector-plugin:issuecollector-embededjs.js?collectorId=8a8cc0df",
        type: "get",
        cache: true,
        dataType: "script"
    });
}
