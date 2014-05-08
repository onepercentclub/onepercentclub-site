--
-- MEMBERS
--

-- Time Available
-- Project Phase

CREATE SEQUENCE accounts_timeavailable_id_seq
	START WITH 1
	INCREMENT BY 1
	NO MAXVALUE
	NO MINVALUE
	CACHE 1;

  
CREATE TABLE bb_accounts_timeavailable (
	id integer DEFAULT nextval('accounts_timeavailable_id_seq'::regclass) UNIQUE NOT NULL,
	type character varying(100) NOT NULL,
	description character varying(400) NOT NULL
);

-- Set Default times available
INSERT INTO bb_accounts_timeavailable (id, type, description) VALUES
  (1, '1-4_hours_week', '1-4 hours per week'),
  (2, '5-8_hours_week', '5-8 hours per week'),
  (3, '9-16_hours_week', '9-16 hours week'),
  (4, '1-4_hours_month', '1-4 hours month'),
  (6, '5-8_hours_month', '5-8 hours month'),
  (7, '9-16_hours_month', '9-16 hours month'),
  (8, 'lots_of_time', 'I have all the time in the world. Bring it on :D'),
  (9, 'depends', 'It depends on the content of the tasks. Challenge me!');


-- Members
ALTER TABLE accounts_bluebottleuser RENAME TO members_member;

ALTER TABLE members_member
	ADD COLUMN skypename character varying(32) DEFAULT '' NOT NULL,
	ADD COLUMN facebook character varying(50) DEFAULT '' NOT NULL,
	ADD COLUMN twitter character varying(15) DEFAULT '' NOT NULL,
	DROP COLUMN available_time,
	ALTER COLUMN contribution DROP NOT NULL,
	ADD COLUMN time_available_id integer,
	ADD CONSTRAINT time_available_id FOREIGN KEY (time_available_id)
	  REFERENCES bb_accounts_timeavailable (id) MATCH SIMPLE
    ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;

-- move info of availability to time_available

UPDATE members_member SET time_available_id =
  (SELECT ta.id FROM bb_accounts_timeavailable as ta WHERE ta.type = '1-4_hours_week')
  WHERE availability = '1-4_hours_week';

UPDATE members_member SET time_available_id =
  (SELECT ta.id FROM bb_accounts_timeavailable as ta WHERE ta.type = '5-8_hours_week')
  WHERE availability = '5-8_hours_week';

UPDATE members_member SET time_available_id =
  (SELECT ta.id FROM bb_accounts_timeavailable as ta WHERE ta.type = '9-16_hours_week')
  WHERE availability = '9-16_hours_week';

UPDATE members_member SET time_available_id =
  (SELECT ta.id FROM bb_accounts_timeavailable as ta WHERE ta.type = '1-4_hours_month')
  WHERE availability = '1-4_hours_month';

UPDATE members_member SET time_available_id =
  (SELECT ta.id FROM bb_accounts_timeavailable as ta WHERE ta.type = '5-8_hours_month')
  WHERE availability = '5-8_hours_month';

UPDATE members_member SET time_available_id =
  (SELECT ta.id FROM bb_accounts_timeavailable as ta WHERE ta.type = '9-16_hours_month')
  WHERE availability = '9-16_hours_month';

UPDATE members_member SET time_available_id =
  (SELECT ta.id FROM bb_accounts_timeavailable as ta WHERE ta.type = 'lots_of_time')
  WHERE availability = 'lots_of_time';

UPDATE members_member SET time_available_id =
  (SELECT ta.id FROM bb_accounts_timeavailable as ta WHERE ta.type = 'depends')
  WHERE availability = 'depends';

-- delete old availability field
ALTER TABLE members_member DROP COLUMN availability;


-- Renaming indexes & sequences
ALTER INDEX accounts_bluebottleuser_pkey RENAME TO members_member_pkey;
ALTER INDEX accounts_bluebottleuser_email_key RENAME TO members_member_email_key;
ALTER INDEX accounts_bluebottleuser_username_key RENAME TO members_member_username_key;

ALTER INDEX accounts_bluebottleuser_email_like RENAME TO members_member_email_like;
ALTER INDEX accounts_bluebottleuser_username_like RENAME TO members_member_username_like;
ALTER INDEX accounts_bluebottleuser_user_permissions_pkey RENAME TO members_member_user_permissions_pkey;
ALTER INDEX accounts_bluebottleuser_user_permissions_bluebottleuser_id RENAME TO members_member_user_permissions_bluebottleuser_id;
ALTER INDEX accounts_bluebottleuser_user_permissions_permission_id RENAME TO members_member_user_permissions_permission_id;

ALTER SEQUENCE accounts_bluebottleuser_id_seq RENAME TO members_member_id_seq;

-- Change permission table
ALTER TABLE accounts_bluebottleuser_user_permissions RENAME TO members_member_user_permissions;
ALTER SEQUENCE accounts_bluebottleuser_user_permissions_id_seq RENAME TO members_member_user_permissions_id_seq;
ALTER INDEX accounts_bluebottleuser_user_permissions_pkey RENAME TO members_member_user_permissions_pkey;

ALTER TABLE members_member_user_permissions RENAME bluebottleuser_id TO member_id;
ALTER INDEX accounts_bluebottleuser_user_permissions_bluebottleuser_id RENAME TO members_member_user_permissions_user_id;
ALTER INDEX accounts_bluebottleuser_user_permissions_id RENAME TO members_member_user_permissions_permission_id;

ALTER TABLE members_member_user_permissions DROP CONSTRAINT accounts_bluebottleuser_bluebottleuser_id_147f9109b2c6aedf_uniq;
ALTER TABLE members_member_user_permissions
  ADD CONSTRAINT members_member_user_id_147f9109b2c6aedf_uniq UNIQUE(member_id, permission_id);

ALTER TABLE members_member_user_permissions DROP CONSTRAINT bluebottleuser_id_refs_id_00516181;
ALTER TABLE members_member_user_permissions
  ADD CONSTRAINT member_id_refs_id_00516181 FOREIGN KEY (member_id)
      REFERENCES members_member (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;

-- Change group table
ALTER TABLE accounts_bluebottleuser_groups RENAME TO members_member_groups;
ALTER SEQUENCE accounts_bluebottleuser_groups_id_seq RENAME TO members_member_groups_id_seq;
ALTER INDEX accounts_bluebottleuser_groups_pkey RENAME TO members_member_groups_pkey;

ALTER TABLE members_member_groups RENAME bluebottleuser_id TO member_id;
ALTER INDEX accounts_bluebottleuser_groups_bluebottleuser_id RENAME TO members_member_groups_member_id;
ALTER INDEX accounts_bluebottleuser_groups_group_id RENAME TO members_member_groups_group_id;

ALTER TABLE members_member_groups DROP CONSTRAINT accounts_bluebottleuser_bluebottleuser_id_1d988989311d97dc_uniq;
ALTER TABLE members_member_groups
  ADD CONSTRAINT members_member_groups_member_id_1d988989311d97dc_uniq UNIQUE(member_id, group_id);

ALTER TABLE members_member_groups DROP CONSTRAINT bluebottleuser_id_refs_id_87beb27c;
ALTER TABLE members_member_groups
  ADD CONSTRAINT member_id_refs_id_87beb27c FOREIGN KEY (member_id)
      REFERENCES members_member (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;


--
-- PROJECTS
--

-- Project Phase

CREATE SEQUENCE projects_projectphase_id_seq
	START WITH 1
	INCREMENT BY 1
	NO MAXVALUE
	NO MINVALUE
	CACHE 1;

CREATE TABLE bb_projects_projectphase (
	id integer DEFAULT nextval('projects_projectphase_id_seq'::regclass) NOT NULL,
	name character varying(100) NOT NULL,
	description character varying(400) NOT NULL,
	"sequence" integer NOT NULL,
	active boolean NOT NULL,
	editable boolean NOT NULL,
	viewable boolean NOT NULL,
  slug character varying(200) NOT NULL
);

-- Set default phases

INSERT INTO bb_projects_projectphase (id, name, description, sequence, active, editable, viewable, slug) VALUES
  (1, 'Plan - New', '', 1, true, true, false, 'plan-new'),
  (2, 'Plan - Submitted', '', 2, true, false, false, 'plan-submitted'),
  (3, 'Plan - Needs Work', '', 3, true, true, false, 'plan-needs-work'),
  (4, 'Plan - Rejected', '', 4, true, false, false, 'plan-rejected'),
  (5, 'Campaign', '', 5, true, true, true, 'campaign'),
  (6, 'Stopped', '', 6, true, false, false, 'stopped'),
  (7, 'Done - Complete', '', 7, true, true, true, 'done-complete'),
  (8, 'Done - Incomplete', '', 8, true, false, true, 'done-incomplete'),
  (9, 'Done - Stopped', '', 9, true, false, false, 'done-stopped');

-- Project Theme

ALTER TABLE projects_projecttheme RENAME TO bb_projects_projecttheme;
-- change sequence
ALTER SEQUENCE projects_projecttheme_id_seq RENAME TO bb_projects_projecttheme_id_seq;
ALTER SEQUENCE bb_projects_projecttheme_id_seq	OWNED BY bb_projects_projecttheme.id;
--change index


-- Project

ALTER TABLE projects_project
	ADD COLUMN status_id integer DEFAULT 0 NOT NULL,
	ADD COLUMN pitch text DEFAULT '' NOT NULL,
	ADD COLUMN favorite boolean DEFAULT false NOT NULL,
	ADD COLUMN description text DEFAULT '' NOT NULL,
	ADD COLUMN image character varying(255) DEFAULT '' NOT NULL,
	ADD COLUMN organization_id integer,
	ADD COLUMN country_id integer,
	ADD COLUMN theme_id integer,
	ADD COLUMN latitude numeric(21,18),
	ADD COLUMN longitude numeric(21,18),
	ADD COLUMN reach integer,
	ADD COLUMN video_url character varying(100),
	ADD COLUMN deadline timestamp with time zone,
  ADD COLUMN amount_asked numeric(12,2) DEFAULT 0.00 NOT NULL,
  ADD COLUMN amount_donated numeric(12,2) DEFAULT 0.00 NOT NULL,
  ADD COLUMN amount_needed numeric(12,2) DEFAULT 0.00 NOT NULL,
  ADD COLUMN effects text DEFAULT '',
  ADD COLUMN for_who text DEFAULT '',
  ADD COLUMN future text DEFAULT '',
  ADD COLUMN language_id integer,
  ADD COLUMN date_submitted timestamp with time zone,
  ADD COLUMN campaign_started timestamp with time zone,
  ADD COLUMN campaign_ended timestamp with time zone,
  ADD COLUMN campaign_funded timestamp with time zone;

-- Language

CREATE TABLE utils_language (
    id serial NOT NULL PRIMARY KEY,
    code varchar(2) NOT NULL,
    language_name varchar(100) NOT NULL,
    native_name varchar(100) NOT NULL
);

INSERT INTO utils_language (id, code, language_name, native_name) VALUES
  (1, 'en', 'English', 'English'),
  (2, 'nl', 'Dutch', 'Nederlands');

ALTER TABLE projects_project ADD CONSTRAINT "project_projects_language_id_refs_language_id" 
  FOREIGN KEY ("language_id") 
  REFERENCES "utils_language" ("id") DEFERRABLE INITIALLY DEFERRED;

-- Organization

ALTER TABLE organizations_organization
  ALTER COLUMN description SET DEFAULT '',
  ALTER COLUMN legal_status SET DEFAULT '',
  ADD COLUMN account_holder_name character varying(255) DEFAULT '',
  ADD COLUMN account_holder_address character varying(255) DEFAULT '',
  ADD COLUMN account_holder_postal_code character varying(20) DEFAULT '',
  ADD COLUMN account_holder_city character varying(255) DEFAULT '',
  ADD COLUMN account_holder_country_id integer,
  ADD COLUMN account_bank_postal_code character varying(20) DEFAULT '',
  ADD COLUMN account_bank_city character varying(255) DEFAULT '';

-- Migrate old fields into new ones:
-- account_name                              -> account_holder_name
UPDATE organizations_organization SET account_holder_name = account_name;
-- account_city                              -> account_holder_city
UPDATE organizations_organization SET account_holder_city = account_city;


-- DROP old column after migration
ALTER TABLE organizations_organization DROP COLUMN account_name;
ALTER TABLE organizations_organization DROP COLUMN account_city;


-- Migrate phases to status

UPDATE projects_project SET status_id = 1 WHERE phase IN ('pitch', 'plan');
UPDATE projects_project SET status_id = 2 WHERE id in (SELECT project_id FROM projects_projectpitch WHERE status = 'submitted');
UPDATE projects_project SET status_id = 5 WHERE phase = 'campaign';
UPDATE projects_project SET status_id = 7 WHERE phase IN ('acts', 'results', 'realized');
UPDATE projects_project SET status_id = 10 WHERE phase = 'failed';


-- Migrate info from pitch or plan

UPDATE projects_project p
  SET pitch = pp.pitch,
      description = pp.description,
      image = pp.image,
      country_id = pp.country_id
  FROM projects_projectpitch AS pp
  WHERE pp.project_id = p.id
  AND p.phase = 'pitch';

UPDATE projects_project p
  SET theme_id = pp.theme_id
  FROM projects_projectpitch AS pp
  WHERE pp.project_id = p.id
  AND p.phase = 'pitch' AND pp.theme_id IS NOT NULL;


UPDATE projects_project p
  SET pitch = pp.pitch,
      description = pp.description,
      image = pp.image,
      country_id = pp.country_id,
      latitude = pp.latitude,
      longitude = pp.longitude
  FROM projects_projectplan AS pp
  WHERE pp.project_id = p.id
  AND p.phase <> 'pitch';

UPDATE projects_project p
  SET theme_id = pp.theme_id
  FROM projects_projectplan AS pp
  WHERE pp.project_id = p.id
  AND p.phase <> 'pitch' AND pp.theme_id IS NOT NULL;


-- Migrate ProjectCampaign

UPDATE projects_project p
  SET amount_asked = (pc.money_asked / 100),
      amount_donated = (pc.money_donated / 100),
      amount_needed = (pc.money_needed / 100),
      deadline = (pc.deadline)
  FROM projects_projectcampaign AS pc
  WHERE pc.project_id = p.id;

-- Migrate ProjectPlan

UPDATE projects_project p
  SET effects = pp.effects,
      for_who = pp.for_who,
      future = pp.future,
      reach = pp.reach
  FROM projects_projectplan as pp
  WHERE pp.project_id = p.id;

-- Now drop phase

ALTER TABLE projects_project DROP COLUMN phase;

-- Add 'story' column to projects
ALTER TABLE projects_project ADD COLUMN story text;

-- Move the Why What How, Effects and Future fields to Story field

UPDATE projects_project p
  SET story = '<h2>Why, What and How</h2>' || project.description || '</br></br><h2>Effects</h2>' || project.effects || '</br></br><h2>Future</h2>' || project.future
  FROM projects_project as project
  WHERE project.id = p.id;

-- Migrate Budget Lines

-- Reference project instead of project plan
ALTER TABLE projects_projectbudgetline
  ADD COLUMN project_id INTEGER NULL;

UPDATE projects_projectbudgetline pbl
  SET project_id = (
    SELECT project_id FROM projects_projectplan pp
    WHERE pp.id = pbl.project_plan_id);

-- Remove now obsolete project_plan_id

ALTER TABLE projects_projectbudgetline
  DROP COLUMN project_plan_id;

-- At foreign key constraint



--
-- TASKS
--

ALTER TABLE tasks_task DROP COLUMN expertise;

ALTER TABLE tasks_taskmember
  ADD COLUMN time_spent INTEGER DEFAULT 0 NOT NULL;



--
-- SLIDES
--

ALTER TABLE banners_slide RENAME TO slides_slide;
ALTER INDEX banners_slide_pkey RENAME TO slides_slide_pkey;
ALTER INDEX banners_slide_author_id RENAME TO slides_slide_author_id;
ALTER INDEX banners_slide_publication_date RENAME TO slides_slide_publication_date;
ALTER INDEX banners_slide_publication_end_date RENAME TO slides_slide_publication_end_date;
ALTER INDEX banners_slide_slug RENAME TO slides_slide_slug;
ALTER INDEX banners_slide_slug_like RENAME TO slides_slide_slug_like;
ALTER INDEX banners_slide_status RENAME TO slides_slide_status;
ALTER INDEX banners_slide_status_like RENAME TO slides_slide_status_like;


--
-- GEO
--

ALTER TABLE geo_country ALTER COLUMN numeric_code DROP NOT NULL;

ALTER TABLE geo_region ALTER COLUMN numeric_code DROP NOT NULL;

ALTER TABLE geo_subregion ALTER COLUMN numeric_code DROP NOT NULL;


-- Pages
ALTER TABLE pages_page
	ADD COLUMN full_page boolean DEFAULT FALSE;

UPDATE pages_page set full_page = TRUE WHERE slug IN ('about', 'get-involved');

-- Rename old User Address model
ALTER TABLE accounts_useraddress RENAME TO members_useraddress;


--
-- BLOG
--

-- Clean BlogPost table

ALTER TABLE blogs_blogpost DROP COLUMN post_type;
ALTER TABLE blogs_blogpost RENAME TO news_newsitem;


-- Deleting old tables

DROP TABLE blogs_blogpost_categories;
DROP TABLE blogs_blogcategory;
DROP TABLE blogs_blogpost_countries;

-- Cleaning Permissions

DELETE FROM auth_group_permissions WHERE permission_id = 457;
DELETE FROM auth_group_permissions WHERE permission_id = 458;
DELETE FROM auth_group_permissions WHERE permission_id = 459;
DELETE FROM members_member_user_permissions WHERE permission_id = 457;
DELETE FROM members_member_user_permissions WHERE permission_id = 458;
DELETE FROM members_member_user_permissions WHERE permission_id = 459;
DELETE FROM auth_permission WHERE content_type_id = 153;
DELETE FROM django_content_type WHERE id = 153;
DELETE FROM django_content_type WHERE id = 155;
DELETE FROM django_content_type WHERE id = 156;


-- Changing django_content_type to match the new 'newsitem' table

UPDATE django_content_type
  SET name = 'News',
      app_label = 'news',
      model = 'newsitem'
  WHERE id = 154;



-- Rename Contact table. It's in it's own app now.
ALTER TABLE pages_contactmessage RENAME TO contact_contactmessage;


------------
-- TODO: See if we need these DB changes


-- ALTER TABLE payouts_organizationpayoutlog
-- 	DROP CONSTRAINT payout_id_refs_id_d601d93e;
--
-- ALTER TABLE payouts_payoutlog
-- 	DROP CONSTRAINT payout_id_refs_id_3585d806;
--
-- ALTER TABLE projects_projectpitch
-- 	DROP CONSTRAINT theme_id_refs_id_8d479809;
--
-- ALTER TABLE projects_projectplan
-- 	DROP CONSTRAINT theme_id_refs_id_e9f7d0d1;


-- ALTER SEQUENCE members_member_groups_id_seq
-- 	OWNED BY members_member_groups.id;
--
-- ALTER SEQUENCE members_member_id_seq
-- 	OWNED BY members_member.id;
--
-- ALTER SEQUENCE members_member_user_permissions_id_seq
-- 	OWNED BY members_member_user_permissions.id;
--
-- ALTER SEQUENCE tasks_task_files_id_seq
-- 	OWNED BY tasks_task_files.id;
--
-- ALTER SEQUENCE tasks_task_members_id_seq
-- 	OWNED BY tasks_task_members.id;
--
-- ALTER TABLE members_member
-- 	ADD CONSTRAINT members_member_pkey PRIMARY KEY (id);
--
-- ALTER TABLE members_member_groups
-- 	ADD CONSTRAINT members_member_groups_pkey PRIMARY KEY (id);
--
-- ALTER TABLE members_member_user_permissions
-- 	ADD CONSTRAINT members_member_user_permissions_pkey PRIMARY KEY (id);
--
-- ALTER TABLE tasks_task_files
-- 	ADD CONSTRAINT tasks_task_files_pkey PRIMARY KEY (id);
--
-- ALTER TABLE tasks_task_members
-- 	ADD CONSTRAINT tasks_task_members_pkey PRIMARY KEY (id);
--
-- ALTER TABLE bb_projects_projectphase
-- 	ADD CONSTRAINT projects_projectphase_name_key UNIQUE (name);
--
-- ALTER TABLE bb_projects_projectphase
-- 	ADD CONSTRAINT projects_projectphase_sequence_key UNIQUE (sequence);
--
-- ALTER TABLE bb_projects_projecttheme
-- 	ADD CONSTRAINT projects_projecttheme_name_key UNIQUE (name);
--
-- ALTER TABLE bb_projects_projecttheme
-- 	ADD CONSTRAINT projects_projecttheme_slug_key UNIQUE (slug);
--
-- ALTER TABLE bb_tasks_skill
-- 	ADD CONSTRAINT bb_tasks_skill_name_key UNIQUE (name);
--
-- ALTER TABLE bb_tasks_skill
-- 	ADD CONSTRAINT bb_tasks_skill_name_nl_key UNIQUE (name_nl);
--
-- ALTER TABLE bb_tasks_taskfile
-- 	ADD CONSTRAINT bb_tasks_taskfile_author_id_fkey FOREIGN KEY (author_id) REFERENCES members_member(id) DEFERRABLE INITIALLY DEFERRED;
--
-- ALTER TABLE bb_tasks_taskmember
-- 	ADD CONSTRAINT member_id_refs_id_861b83e0 FOREIGN KEY (member_id) REFERENCES accounts_bluebottleuser(id) DEFERRABLE INITIALLY DEFERRED;
--
-- ALTER TABLE bb_tasks_taskmember
-- 	ADD CONSTRAINT task_id_refs_id_e6a84bbf FOREIGN KEY (task_id) REFERENCES tasks_task(id) DEFERRABLE INITIALLY DEFERRED;
--
-- ALTER TABLE members_member
-- 	ADD CONSTRAINT members_member_email_key UNIQUE (email);
--
-- ALTER TABLE members_member
-- 	ADD CONSTRAINT members_member_username_key UNIQUE (username);
--
-- ALTER TABLE members_member_groups
-- 	ADD CONSTRAINT members_member_groups_member_id_group_id_key UNIQUE (member_id, group_id);
--
-- ALTER TABLE members_member_groups
-- 	ADD CONSTRAINT member_id_refs_id_6f23d3dd FOREIGN KEY (member_id) REFERENCES members_member(id) DEFERRABLE INITIALLY DEFERRED;
--
-- ALTER TABLE members_member_groups
-- 	ADD CONSTRAINT members_member_groups_group_id_fkey FOREIGN KEY (group_id) REFERENCES auth_group(id) DEFERRABLE INITIALLY DEFERRED;
--
-- ALTER TABLE members_member_user_permissions
-- 	ADD CONSTRAINT members_member_user_permissions_member_id_permission_id_key UNIQUE (member_id, permission_id);
--
-- ALTER TABLE members_member_user_permissions
-- 	ADD CONSTRAINT member_id_refs_id_f7e99d7b FOREIGN KEY (member_id) REFERENCES members_member(id) DEFERRABLE INITIALLY DEFERRED;
--
-- ALTER TABLE members_member_user_permissions
-- 	ADD CONSTRAINT members_member_user_permissions_permission_id_fkey FOREIGN KEY (permission_id) REFERENCES auth_permission(id) DEFERRABLE INITIALLY DEFERRED;
--
-- ALTER TABLE payouts_organizationpayoutlog
-- 	ADD CONSTRAINT payouts_organizationpayoutlog_payout_id_fkey FOREIGN KEY (payout_id) REFERENCES payouts_organizationpayout(id) DEFERRABLE INITIALLY DEFERRED;
--
-- ALTER TABLE payouts_payoutlog
-- 	ADD CONSTRAINT payouts_payoutlog_payout_id_fkey FOREIGN KEY (payout_id) REFERENCES payouts_payout(id) DEFERRABLE INITIALLY DEFERRED;
--
-- ALTER TABLE projects_project
-- 	ADD CONSTRAINT ck_reach_pstv_2632592547ec141a CHECK ((reach >= 0));
--
-- ALTER TABLE projects_project
-- 	ADD CONSTRAINT projects_project_reach_check CHECK ((reach >= 0));
--
-- ALTER TABLE projects_project
-- 	ADD CONSTRAINT country_id_refs_id_3a57922e FOREIGN KEY (country_id) REFERENCES geo_country(id) DEFERRABLE INITIALLY DEFERRED;
--
-- ALTER TABLE projects_project
-- 	ADD CONSTRAINT organization_id_refs_id_e42a8fc9 FOREIGN KEY (organization_id) REFERENCES organizations_organization(id) DEFERRABLE INITIALLY DEFERRED;
--
-- ALTER TABLE projects_project
-- 	ADD CONSTRAINT status_id_refs_id_7b0c43f9 FOREIGN KEY (status_id) REFERENCES bb_projects_projectphase(id) DEFERRABLE INITIALLY DEFERRED;
--
-- ALTER TABLE projects_project
-- 	ADD CONSTRAINT theme_id_refs_id_2a01adf5 FOREIGN KEY (theme_id) REFERENCES bb_projects_projecttheme(id) DEFERRABLE INITIALLY DEFERRED;
--
-- ALTER TABLE projects_projectpitch
-- 	ADD CONSTRAINT theme_id_refs_id_8d479809 FOREIGN KEY (theme_id) REFERENCES bb_projects_projecttheme(id) DEFERRABLE INITIALLY DEFERRED;
--
-- ALTER TABLE projects_projectplan
-- 	ADD CONSTRAINT theme_id_refs_id_e9f7d0d1 FOREIGN KEY (theme_id) REFERENCES bb_projects_projecttheme(id) DEFERRABLE INITIALLY DEFERRED;
--
-- ALTER TABLE tasks_task_files
-- 	ADD CONSTRAINT tasks_task_files_task_id_78ceab895d23dc42_uniq UNIQUE (task_id, taskfile_id);
--
-- ALTER TABLE tasks_task_files
-- 	ADD CONSTRAINT task_id_refs_id_68a7e47c FOREIGN KEY (task_id) REFERENCES tasks_task(id) DEFERRABLE INITIALLY DEFERRED;
--
-- ALTER TABLE tasks_task_files
-- 	ADD CONSTRAINT taskfile_id_refs_id_8915c958 FOREIGN KEY (taskfile_id) REFERENCES bb_tasks_taskfile(id) DEFERRABLE INITIALLY DEFERRED;
--
-- ALTER TABLE tasks_task_members
-- 	ADD CONSTRAINT tasks_task_members_task_id_ebfef1d4a7ceede_uniq UNIQUE (task_id, taskmember_id);
--
-- ALTER TABLE tasks_task_members
-- 	ADD CONSTRAINT task_id_refs_id_d6afa2e6 FOREIGN KEY (task_id) REFERENCES tasks_task(id) DEFERRABLE INITIALLY DEFERRED;
--
-- ALTER TABLE tasks_task_members
-- 	ADD CONSTRAINT taskmember_id_refs_id_964503d2 FOREIGN KEY (taskmember_id) REFERENCES bb_tasks_taskmember(id) DEFERRABLE INITIALLY DEFERRED;
--
-- CREATE INDEX projects_projectphase_name_like ON bb_projects_projectphase USING btree (name varchar_pattern_ops);
--
-- CREATE INDEX projects_projecttheme_name_like ON bb_projects_projecttheme USING btree (name varchar_pattern_ops);
--
-- CREATE INDEX projects_projecttheme_slug_like ON bb_projects_projecttheme USING btree (slug varchar_pattern_ops);
--
-- CREATE INDEX bb_tasks_skill_name_like ON bb_tasks_skill USING btree (name varchar_pattern_ops);
--
-- CREATE INDEX bb_tasks_skill_name_nl_like ON bb_tasks_skill USING btree (name_nl varchar_pattern_ops);
--
-- CREATE INDEX bb_tasks_taskfile_author_id ON bb_tasks_taskfile USING btree (author_id);
--
-- CREATE INDEX tasks_taskmember_member_id ON bb_tasks_taskmember USING btree (member_id);
--
-- CREATE INDEX tasks_taskmember_task_id ON bb_tasks_taskmember USING btree (task_id);
--
-- CREATE INDEX members_member_email_like ON members_member USING btree (email varchar_pattern_ops);
--
-- CREATE INDEX members_member_username_like ON members_member USING btree (username varchar_pattern_ops);
--
-- CREATE INDEX members_member_groups_group_id ON members_member_groups USING btree (group_id);
--
-- CREATE INDEX members_member_groups_member_id ON members_member_groups USING btree (member_id);
--
-- CREATE INDEX members_member_user_permissions_member_id ON members_member_user_permissions USING btree (member_id);
--
-- CREATE INDEX members_member_user_permissions_permission_id ON members_member_user_permissions USING btree (permission_id);
--
-- CREATE INDEX projects_project_country_id ON projects_project USING btree (country_id);
--
-- CREATE INDEX projects_project_organization_id ON projects_project USING btree (organization_id);
--
-- CREATE INDEX projects_project_status_id ON projects_project USING btree (status_id);
--
-- CREATE INDEX projects_project_theme_id ON projects_project USING btree (theme_id);
--
-- CREATE INDEX tasks_task_files_task_id ON tasks_task_files USING btree (task_id);
--
-- CREATE INDEX tasks_task_files_taskfile_id ON tasks_task_files USING btree (taskfile_id);
--
-- CREATE INDEX tasks_task_members_task_id ON tasks_task_members USING btree (task_id);
--
-- CREATE INDEX tasks_task_members_taskmember_id ON tasks_task_members USING btree (taskmember_id);
--
