from django.db import models


""" 
This code is preliminary and will not validate when enabled.

Some of the related models are missing.
"""
# class Event(models.Model):
#     """ Event. Even for Project/Member update wall
#         Events can refer to various modeltypes.
#         Most refer on 'the old way' by a special foreignkey field.
#         Some use 'the new way' using a generic reference with item_id/item_type
#     """
#     id = models.IntegerField(primary_key=True)
#     member = models.ForeignKey('members.Member')
#     project = models.ForeignKey('projects.Project', null=True, blank=True)
#     meta_info = models.CharField(max_length=255, blank=True)
#     created = models.DateTimeField()
#     deleted = models.DateTimeField(null=True, blank=True)
#     add_friend = models.ForeignKey('members.Member', null=True, blank=True)
#     mem_message = models.ForeignKey(MemberMessage, null=True, blank=True)
#     member_joined = models.ForeignKey('members.Member', null=True, blank=True)
#     prj_testimonials = models.ForeignKey(Testimonial, null=True, blank=True)
#     prj_messages = models.ForeignKey(ProjectMessage, null=True, blank=True)
#     web_weblog_message = models.ForeignKey(WeblogMessage, null=True, blank=True)
#     alb_albums = models.ForeignKey(Album, null=True, blank=True)
#     alb_fotos = models.ForeignKey(Picture, null=True, blank=True)
#     prj_project_videos = models.ForeignKey(Video, null=True, blank=True)
#     prj_project_links = models.ForeignKey(Link, null=True, blank=True)
#     prj_project_rating_id = models.SmallIntegerField(null=True, blank=True)
#     evt_reaction_on_alb_fotos = models.ForeignKey(Reaction, null=True, blank=True)
#     evt_reaction_on_prj_project_videos = models.ForeignKey(Reaction, null=True, blank=True)
#     new_project = models.ForeignKey(Project, null=True, blank=True)
#     status_change_project = models.ForeignKey(Project, null=True, blank=True)
#     rendered_content = models.TextField(blank=True)
#     cache_rendering = models.SmallIntegerField()
#     cou_coupons = models.ForeignKey(Voucher, null=True, blank=True)
#     task_id = models.IntegerField(null=True, blank=True)
#     task_message = models.ForeignKey(TaskMessage, null=True, blank=True)
#     item_id = models.IntegerField(null=True, blank=True)
#     item_type = models.CharField(max_length=255, blank=True)
#     class Meta:
#         db_table = u'evt_event'
# 
# 
# class Reaction(models.Model):
#     id = models.IntegerField(primary_key=True)
#     event = models.ForeignKey(Event)
#     from_member = models.ForeignKey(Member)
#     text = models.TextField()
#     created = models.DateTimeField()
#     deleted = models.DateTimeField(null=True, blank=True)
#     class Meta:
#         db_table = u'evt_reaction'