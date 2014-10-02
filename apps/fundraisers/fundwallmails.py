from django.utils.translation import ugettext_lazy as _
from apps.fundraisers.models import FundRaiser

from bluebottle.wallposts.notifiers import WallPostObserver, ReactionObserver, ObserversContainer
from bluebottle.mail import send_mail



#TODO: fixed should work (fix text email)
class FundraiserWallObserver(WallPostObserver):

    model = FundRaiser

    def __init__(self, instance):
        WallPostObserver.__init__(self, instance)

    def notify(self):
        print 'FundraiserWallNotificator'
        fundraiser = self.post
        fundraiser_owner = fundraiser.author

        # Implement 1a: send email to Object owner, if Wallpost author is not the Object owner.
        if self.author != fundraiser_owner:
            send_mail(
                template_name='fundraiser_wallpost_new.mail',
                subject=_('%(author)s has left a message on your fundraiser page.') % {'author': self.author.get_short_name()},
                to=fundraiser_owner,

                project=fundraiser,
                link='/go/projects/{0}'.format(fundraiser.slug),
                author=self.author,
                receiver=fundraiser_owner
            )

#TODO: Just copied from others fix this
class FundraiserReactionObserver(ReactionObserver):

    model = FundRaiser

    def __init__(self, instance):
        ReactionObserver.__init__(self, instance)

    def notify(self):
        print 'FundraiserReactionWallNotificator'
        project = self.post.content_object
        project_owner = project.owner

        # Make sure users only get mailed once!
        mailed_users = set()

        # Implement 2c: send email to other Reaction authors that are not the Object owner or the post author.
        reactions = self.post.reactions.exclude(Q(author=self.post_author) |
                                                Q(author=project_owner) |
                                                Q(author=self.reaction_author))
        for r in reactions:
            if r.author not in mailed_users:
                send_mail(
                    template_name='project_wallpost_reaction_same_wallpost.mail',
                    subject=_('%(author)s commented on a post you reacted on.') % {'author': self.reaction_author.get_short_name()},
                    to=r.author,

                    project=project,
                    link='/go/projects/{0}'.format(project.slug),
                    author=self.reaction_author,
                    receiver=r.author
                )
                mailed_users.add(r.author)

        # Implement 2b: send email to post author, if Reaction author is not the post author.
        if self.reaction_author != self.post_author:
            if self.reaction_author not in mailed_users and self.post_author:
                send_mail(
                    template_name='project_wallpost_reaction_new.mail',
                    subject=_('%(author)s commented on your post.') % {'author': self.reaction_author.get_short_name()},
                    to=self.post_author,

                    project=project, #doesn't look like we need this
                    link='/go/projects/{0}'.format(project.slug),
                    site=self.site,
                    author=self.reaction_author,
                    receiver=self.post_author
                )
                mailed_users.add(self.post_author)

        # Implement 2a: send email to Object owner, if Reaction author is not the Object owner.
        if self.reaction_author != project_owner:
            if project_owner not in mailed_users:
                send_mail(
                    template_name='project_wallpost_reaction_project.mail',
                    subject=_('%(author)s commented on your project page.') % {'author': self.reaction_author.get_short_name()},
                    to=project_owner,

                    site=self.site,
                    link='/go/projects/{0}'.format(project.slug),
                    author=self.reaction_author,
                    receiver=project_owner
                )


ObserversContainer().register(FundraiserWallObserver)
ObserversContainer().register(FundraiserReactionObserver)