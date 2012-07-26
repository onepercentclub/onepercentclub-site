

def copy_tags(from_instance, to_instance):
    """
    Utility method to copy the tags from a source instance to a destination
    instance. This method has not been included in a Migration class so that
    it can be used for both Projects and Tasks.
    """
    # Ignore the tags on this project because it has a tag that is > 100 chars.
    if from_instance.title == u'Fair Trade and Safe Workplace for Waste Pickers Sustainable Livelihoods':
        return

    # Remove the tags from the destination instance so that migration can be
    # run multiple times with the same result.
    to_instance.tags.clear()

    for project_tag in from_instance.projecttag_set.all():
        from_tag = project_tag.tag.name

        # Some of the source tags have multiple tags so they need to be split.
        for tag in from_tag.split(','):
            stripped_tag = tag.strip('-"\' ;')

            if stripped_tag.isupper():
                # Note: This incorrectly sets all-caps country names to lower
                # case. Since we're not automatically fixing the
                # capitalization of countries, this should be ok.
                stripped_tag = stripped_tag.lower()

            if stripped_tag:
                # Strip out some garbage characters when adding the tag.
                to_instance.tags.add(stripped_tag)


def test_tags(from_instance, to_instance, logger):
    """
    Utility method to test that the tags present in the destination instance
    can be found in the source instance. This method has not been included in
    a Migration class so that it can be used for both Projects and Tasks.
    """
    # Create a string with all the old tags.
    from_tags = ''
    for project_tag in from_instance.projecttag_set.all():
        from_tags += project_tag.tag.name + ' '

    # Check if the new tag is in the old tags string taking into account the
    # transformations that have been done in copy_tags().
    for to_tag in to_instance.tags.all():
        if to_tag.name not in from_tags and to_tag.name.upper() not in from_tags:
            logger.error('Destination tag %s is not in the source tag list.',
                         to_tag.name)
            return False

    return True
