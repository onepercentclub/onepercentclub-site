/**
 * Init
 * 
 * Put everything here that can't be handled by a $().live() thingy
 * 
 * 
 * @param {Object} container
 */
jQuery.fn.exists = function(){return this.length>0;}

function initBehaviour(container) {
//    $("label.inline", container).inFieldLabels();

    // initFileUpload();
    toggleText( $('.toggle-reactions', container) );
    toggleText( $('.toggle-love', container) );
    toggleText( $('#subtitle'), $('#logo') );
}

// Initializing
$(document).ready(function(){
    // swap text in logo
    initPopup()
    //initLightbox();
    //initFileUpload();

    // show/hide sharing options
    $('.share')
        .live('mouseenter', function(e) {
            $('.share-actions', $(this)).show();
        })
        .live('mouseleave', function(e) {
            $('.share-actions', $(this)).hide();
        });
    
    // DEVELOPMENT: needed for static template
    initBehaviour('body');

    // expande reaction-box on focus
    $('.reaction-form textarea')
        .live('focus', function(e) {
            $(e.currentTarget).closest('.reaction-form').addClass('is-selected');
        })
        .live('blur', function(e) {
            $(e.currentTarget).closest('.reaction-form').removeClass('is-selected');
        });
        
    toggleText( $('.toggle-reactions') );
    toggleText( $('.toggle-love') );
    
});




// show popup on hover of element, styled and positioned by css. 
// Needed because we can't render elements outside parent with overview: hidden
function initPopup() {
    popupTimer = null;
    $('.member, .popup').live('mouseenter', function(e) {
        
        // if his has a .popup as child
        if( $('.popup', this).exists() ) {
            // hide & remove any previous popups
            $('.clone').fadeOut(40, function() {
                $(this).remove();
            });
            // clone to bottom of DOM & display
            $('.popup', this)
                .clone()
                .addClass('clone')
                .offset( $('.popup', this).offset() )
                .appendTo($('body'))
                .hide()
                .css('visibility', 'visible')
                .fadeIn(40);
        }
        // check if we have a pending execution and clear it if necessary
        if(popupTimer != null) {
            clearTimeout(popupTimer);
            popupTimer = null;
        }
    });
    // hide onmouseout of parent & popup iself. Needs timer for the later
    $('.member, .popup').live('mouseleave', function(e) {
        popupTimer = setTimeout(function() {
            $('.clone').fadeOut(40, function() {
                $(this).remove();
            });
        }, 200);
    });
};


// toggles content and classnames on click, mouseenter & mouseleave
function toggleText(el, parent){
    // if it doesn't have a parent, bind on itself
    this.parent = typeof parent !== 'undefined' ? parent : el;
    // swap text & classnames
    $(this.parent)
        .live('click',{el: el}, function(e) {
            $(el)
                .toggleClass('is-active')
                .addClass('is-activated')
                .trigger('mouseleave');
            e.preventDefault();
        })
        .live('mouseenter',{el: el}, function(e) {
            if ( $(el).hasClass('is-active') ) {
                $(el).html( $(el).data('content-toggled-hover') );
            } else {
                $(el).html( $(el).data('content-hover') );
            }
            $(el).removeClass('is-activated');
        })
        .live('mouseleave',{el: el}, function(e) {
            if ( $(el).hasClass('is-active') ) {
                $(el).html( $(el).data('content-toggled') );
            } else {
                $(el).html( $(el).data('content') );
            }
        });
};


// replace default file uploader with multiple file uploader
// TODO
function initFileUpload(){

    $('.fileupload').fileupload({

    });
}


// open external data in lightbox on specific links
// TODO: refactor
function initLightbox(){
 
    $('a.open-in-lightbox').live('click',function(e){

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
        e.preventDefault();
        
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


// animate donation-progress meter
// TODO: refactor
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
