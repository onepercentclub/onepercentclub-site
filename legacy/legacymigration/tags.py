

def copy_tags(from_instance, to_instance):
    # Ignore the tags on this project because it has a tag that is > 100 chars.
    if from_instance.title == u'Fair Trade and Safe Workplace for Waste Pickers Sustainable Livelihoods':
        return

    for project_tag in from_instance.projecttag_set.all():
        from_tag = project_tag.tag.name

        # Some of the source tags have multiple tags so they need to be split.
        for tag in from_tag.split(','):
            stripped_tag = tag.strip('-"\' ;')

            if stripped_tag.isupper():
                # Note: This incorrectly sets all-caps country names to lower
                # case. Since we're not automatically fixing the
                # capitalization of countries, this should ok.
                stripped_tag = stripped_tag.lower()

            if stripped_tag:
                # Strip out some garbage characters when adding the tag.
                to_instance.tags.add(stripped_tag)
