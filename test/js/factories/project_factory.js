Factory.define('project', {
    // created: Date.now(),
    owner: function() {
        return attr('userPreview');
    },
    slug: 'empire-strikes-back',
    title: 'Empire Strikes Back',
    phase: 'Episode Five'
});