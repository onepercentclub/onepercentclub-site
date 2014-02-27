ALTER TABLE projects_projectpitch
	DROP CONSTRAINT theme_id_refs_id_8d479809;

ALTER TABLE projects_projectplan
	DROP CONSTRAINT theme_id_refs_id_e9f7d0d1;

DROP TABLE projects_projecttheme;

DROP TABLE tasks_taskmember;

CREATE SEQUENCE bb_tasks_skill_id_seq
	START WITH 1
	INCREMENT BY 1
	NO MAXVALUE
	NO MINVALUE
	CACHE 1;

CREATE SEQUENCE bb_tasks_taskfile_id_seq
	START WITH 1
	INCREMENT BY 1
	NO MAXVALUE
	NO MINVALUE
	CACHE 1;

CREATE SEQUENCE members_member_groups_id_seq
	START WITH 1
	INCREMENT BY 1
	NO MAXVALUE
	NO MINVALUE
	CACHE 1;

CREATE SEQUENCE members_member_id_seq
	START WITH 1
	INCREMENT BY 1
	NO MAXVALUE
	NO MINVALUE
	CACHE 1;

CREATE SEQUENCE members_member_user_permissions_id_seq
	START WITH 1
	INCREMENT BY 1
	NO MAXVALUE
	NO MINVALUE
	CACHE 1;

CREATE SEQUENCE payouts_organizationpayoutlog_id_seq
	START WITH 1
	INCREMENT BY 1
	NO MAXVALUE
	NO MINVALUE
	CACHE 1;

CREATE SEQUENCE payouts_payoutlog_id_seq
	START WITH 1
	INCREMENT BY 1
	NO MAXVALUE
	NO MINVALUE
	CACHE 1;

CREATE SEQUENCE projects_projectphase_id_seq
	START WITH 1
	INCREMENT BY 1
	NO MAXVALUE
	NO MINVALUE
	CACHE 1;

CREATE SEQUENCE tasks_task_files_id_seq
	START WITH 1
	INCREMENT BY 1
	NO MAXVALUE
	NO MINVALUE
	CACHE 1;

CREATE SEQUENCE tasks_task_members_id_seq
	START WITH 1
	INCREMENT BY 1
	NO MAXVALUE
	NO MINVALUE
	CACHE 1;

ALTER SEQUENCE projects_projecttheme_id_seq
	OWNED BY bb_projects_projecttheme.id;

ALTER SEQUENCE tasks_taskmember_id_seq
	OWNED BY bb_tasks_taskmember.id;

CREATE TABLE bb_projects_projectphase (
	id integer DEFAULT nextval('projects_projectphase_id_seq'::regclass) NOT NULL,
	name character varying(100) NOT NULL,
	description character varying(400) NOT NULL,
	"sequence" integer NOT NULL,
	active boolean NOT NULL,
	editable boolean NOT NULL,
	viewable boolean NOT NULL
);

CREATE TABLE bb_projects_projecttheme (
	id integer DEFAULT nextval('projects_projecttheme_id_seq'::regclass) NOT NULL,
	name character varying(100) NOT NULL,
	slug character varying(100) NOT NULL,
	description text NOT NULL,
	name_nl character varying(100) NOT NULL
);

CREATE TABLE bb_tasks_skill (
	id integer DEFAULT nextval('bb_tasks_skill_id_seq'::regclass) NOT NULL,
	name character varying(100) NOT NULL,
	name_nl character varying(100) NOT NULL,
	description text NOT NULL
);

CREATE TABLE bb_tasks_taskfile (
	id integer DEFAULT nextval('bb_tasks_taskfile_id_seq'::regclass) NOT NULL,
	author_id integer NOT NULL,
	title character varying(255) NOT NULL,
	file character varying(100) NOT NULL,
	created timestamp with time zone NOT NULL,
	updated timestamp with time zone NOT NULL
);

CREATE TABLE bb_tasks_taskmember (
	id integer DEFAULT nextval('tasks_taskmember_id_seq'::regclass) NOT NULL,
	task_id integer NOT NULL,
	member_id integer NOT NULL,
	status character varying(20) NOT NULL,
	created timestamp with time zone NOT NULL,
	updated timestamp with time zone NOT NULL,
	motivation text NOT NULL,
	comment text NOT NULL,
	time_spent double precision
);

CREATE TABLE members_member (
	id integer DEFAULT nextval('members_member_id_seq'::regclass) NOT NULL,
	password character varying(128) NOT NULL,
	last_login timestamp with time zone NOT NULL,
	is_superuser boolean NOT NULL,
	email character varying(254) NOT NULL,
	username character varying(50) NOT NULL,
	is_staff boolean NOT NULL,
	is_active boolean NOT NULL,
	date_joined timestamp with time zone NOT NULL,
	updated timestamp with time zone NOT NULL,
	deleted timestamp with time zone,
	user_type character varying(25) NOT NULL,
	first_name character varying(30) NOT NULL,
	last_name character varying(30) NOT NULL,
	location character varying(100) NOT NULL,
	website character varying(200) NOT NULL,
	picture character varying(100) NOT NULL,
	about text NOT NULL,
	why text NOT NULL,
	availability character varying(25) NOT NULL,
	skypename character varying(32) NOT NULL,
	primary_language character varying(5) NOT NULL,
	share_time_knowledge boolean NOT NULL,
	share_money boolean NOT NULL,
	newsletter boolean NOT NULL,
	phone_number character varying(50) NOT NULL,
	gender character varying(6) NOT NULL,
	birthdate date,
	facebook character varying(200) NOT NULL,
	twitter character varying(200) NOT NULL,
	contribution text NOT NULL,
	available_time text
);

CREATE TABLE members_member_groups (
	id integer DEFAULT nextval('members_member_groups_id_seq'::regclass) NOT NULL,
	member_id integer NOT NULL,
	group_id integer NOT NULL
);

CREATE TABLE members_member_user_permissions (
	id integer DEFAULT nextval('members_member_user_permissions_id_seq'::regclass) NOT NULL,
	member_id integer NOT NULL,
	permission_id integer NOT NULL
);

CREATE TABLE payouts_organizationpayoutlog (
	id integer DEFAULT nextval('payouts_organizationpayoutlog_id_seq'::regclass) NOT NULL,
	"date" timestamp with time zone NOT NULL,
	old_status character varying(20),
	new_status character varying(20) NOT NULL,
	payout_id integer NOT NULL
);

CREATE TABLE payouts_payoutlog (
	id integer DEFAULT nextval('payouts_payoutlog_id_seq'::regclass) NOT NULL,
	"date" timestamp with time zone NOT NULL,
	old_status character varying(20),
	new_status character varying(20) NOT NULL,
	payout_id integer NOT NULL
);

CREATE TABLE tasks_task_files (
	id integer DEFAULT nextval('tasks_task_files_id_seq'::regclass) NOT NULL,
	task_id integer NOT NULL,
	taskfile_id integer NOT NULL
);

CREATE TABLE tasks_task_members (
	id integer DEFAULT nextval('tasks_task_members_id_seq'::regclass) NOT NULL,
	task_id integer NOT NULL,
	taskmember_id integer NOT NULL
);

ALTER TABLE accounts_bluebottleuser
	ADD COLUMN skypename character varying(32) DEFAULT '' NOT NULL,
	ADD COLUMN facebook character varying(50) DEFAULT '' NOT NULL,
	ADD COLUMN twitter character varying(15) DEFAULT '' NOT NULL;

ALTER TABLE accounts_bluebottleuser
	ALTER COLUMN skypename DROP DEFAULT,
	ALTER COLUMN facebook DROP DEFAULT,
	ALTER COLUMN twitter DROP DEFAULT;

ALTER TABLE geo_country
	ALTER COLUMN numeric_code DROP NOT NULL;

ALTER TABLE geo_region
	ALTER COLUMN numeric_code DROP NOT NULL;

ALTER TABLE geo_subregion
	ALTER COLUMN numeric_code DROP NOT NULL;

ALTER TABLE projects_project
	ADD COLUMN status_id integer DEFAULT 0 NOT NULL,
	ADD COLUMN pitch text DEFAULT '' NOT NULL,
	ADD COLUMN favorite boolean DEFAULT false NOT NULL,
	ADD COLUMN description text DEFAULT '' NOT NULL,
	ADD COLUMN image character varying(255) DEFAULT '' NOT NULL,
	ADD COLUMN organization_id integer,
	ADD COLUMN country_id integer,
	ADD COLUMN theme_id integer DEFAULT 0 NOT NULL,
	ADD COLUMN latitude numeric(21,18),
	ADD COLUMN longitude numeric(21,18),
	ADD COLUMN reach integer,
	ADD COLUMN video_url character varying(100),
	ADD COLUMN deadline timestamp with time zone;

ALTER TABLE projects_project
	ALTER COLUMN status_id DROP DEFAULT,
	ALTER COLUMN pitch DROP DEFAULT,
	ALTER COLUMN favorite DROP DEFAULT,
	ALTER COLUMN description DROP DEFAULT,
	ALTER COLUMN image DROP DEFAULT,
	ALTER COLUMN theme_id DROP DEFAULT;

ALTER SEQUENCE bb_tasks_skill_id_seq
	OWNED BY bb_tasks_skill.id;

ALTER SEQUENCE bb_tasks_taskfile_id_seq
	OWNED BY bb_tasks_taskfile.id;

ALTER SEQUENCE members_member_groups_id_seq
	OWNED BY members_member_groups.id;

ALTER SEQUENCE members_member_id_seq
	OWNED BY members_member.id;

ALTER SEQUENCE members_member_user_permissions_id_seq
	OWNED BY members_member_user_permissions.id;

ALTER SEQUENCE payouts_organizationpayoutlog_id_seq
	OWNED BY payouts_organizationpayoutlog.id;

ALTER SEQUENCE payouts_payoutlog_id_seq
	OWNED BY payouts_payoutlog.id;

ALTER SEQUENCE projects_projectphase_id_seq
	OWNED BY bb_projects_projectphase.id;

ALTER SEQUENCE tasks_task_files_id_seq
	OWNED BY tasks_task_files.id;

ALTER SEQUENCE tasks_task_members_id_seq
	OWNED BY tasks_task_members.id;

ALTER TABLE bb_projects_projectphase
	ADD CONSTRAINT projects_projectphase_pkey PRIMARY KEY (id);

ALTER TABLE bb_projects_projecttheme
	ADD CONSTRAINT projects_projecttheme_pkey PRIMARY KEY (id);

ALTER TABLE bb_tasks_skill
	ADD CONSTRAINT bb_tasks_skill_pkey PRIMARY KEY (id);

ALTER TABLE bb_tasks_taskfile
	ADD CONSTRAINT bb_tasks_taskfile_pkey PRIMARY KEY (id);

ALTER TABLE bb_tasks_taskmember
	ADD CONSTRAINT tasks_taskmember_pkey PRIMARY KEY (id);

ALTER TABLE members_member
	ADD CONSTRAINT members_member_pkey PRIMARY KEY (id);

ALTER TABLE members_member_groups
	ADD CONSTRAINT members_member_groups_pkey PRIMARY KEY (id);

ALTER TABLE members_member_user_permissions
	ADD CONSTRAINT members_member_user_permissions_pkey PRIMARY KEY (id);

ALTER TABLE payouts_organizationpayoutlog
	ADD CONSTRAINT payouts_organizationpayoutlog_pkey PRIMARY KEY (id);

ALTER TABLE payouts_payoutlog
	ADD CONSTRAINT payouts_payoutlog_pkey PRIMARY KEY (id);

ALTER TABLE tasks_task_files
	ADD CONSTRAINT tasks_task_files_pkey PRIMARY KEY (id);

ALTER TABLE tasks_task_members
	ADD CONSTRAINT tasks_task_members_pkey PRIMARY KEY (id);

ALTER TABLE bb_projects_projectphase
	ADD CONSTRAINT projects_projectphase_name_key UNIQUE (name);

ALTER TABLE bb_projects_projectphase
	ADD CONSTRAINT projects_projectphase_sequence_key UNIQUE (sequence);

ALTER TABLE bb_projects_projecttheme
	ADD CONSTRAINT projects_projecttheme_name_key UNIQUE (name);

ALTER TABLE bb_projects_projecttheme
	ADD CONSTRAINT projects_projecttheme_slug_key UNIQUE (slug);

ALTER TABLE bb_tasks_skill
	ADD CONSTRAINT bb_tasks_skill_name_key UNIQUE (name);

ALTER TABLE bb_tasks_skill
	ADD CONSTRAINT bb_tasks_skill_name_nl_key UNIQUE (name_nl);

ALTER TABLE bb_tasks_taskfile
	ADD CONSTRAINT bb_tasks_taskfile_author_id_fkey FOREIGN KEY (author_id) REFERENCES members_member(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE bb_tasks_taskmember
	ADD CONSTRAINT member_id_refs_id_861b83e0 FOREIGN KEY (member_id) REFERENCES accounts_bluebottleuser(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE bb_tasks_taskmember
	ADD CONSTRAINT task_id_refs_id_e6a84bbf FOREIGN KEY (task_id) REFERENCES tasks_task(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE members_member
	ADD CONSTRAINT members_member_email_key UNIQUE (email);

ALTER TABLE members_member
	ADD CONSTRAINT members_member_username_key UNIQUE (username);

ALTER TABLE members_member_groups
	ADD CONSTRAINT members_member_groups_member_id_group_id_key UNIQUE (member_id, group_id);

ALTER TABLE members_member_groups
	ADD CONSTRAINT member_id_refs_id_6f23d3dd FOREIGN KEY (member_id) REFERENCES members_member(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE members_member_groups
	ADD CONSTRAINT members_member_groups_group_id_fkey FOREIGN KEY (group_id) REFERENCES auth_group(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE members_member_user_permissions
	ADD CONSTRAINT members_member_user_permissions_member_id_permission_id_key UNIQUE (member_id, permission_id);

ALTER TABLE members_member_user_permissions
	ADD CONSTRAINT member_id_refs_id_f7e99d7b FOREIGN KEY (member_id) REFERENCES members_member(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE members_member_user_permissions
	ADD CONSTRAINT members_member_user_permissions_permission_id_fkey FOREIGN KEY (permission_id) REFERENCES auth_permission(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE payouts_organizationpayoutlog
	ADD CONSTRAINT payouts_organizationpayoutlog_payout_id_fkey FOREIGN KEY (payout_id) REFERENCES payouts_organizationpayout(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE payouts_payoutlog
	ADD CONSTRAINT payouts_payoutlog_payout_id_fkey FOREIGN KEY (payout_id) REFERENCES payouts_payout(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE projects_project
	ADD CONSTRAINT ck_reach_pstv_2632592547ec141a CHECK ((reach >= 0));

ALTER TABLE projects_project
	ADD CONSTRAINT projects_project_reach_check CHECK ((reach >= 0));

ALTER TABLE projects_project
	ADD CONSTRAINT country_id_refs_id_3a57922e FOREIGN KEY (country_id) REFERENCES geo_country(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE projects_project
	ADD CONSTRAINT organization_id_refs_id_e42a8fc9 FOREIGN KEY (organization_id) REFERENCES organizations_organization(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE projects_project
	ADD CONSTRAINT status_id_refs_id_7b0c43f9 FOREIGN KEY (status_id) REFERENCES bb_projects_projectphase(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE projects_project
	ADD CONSTRAINT theme_id_refs_id_2a01adf5 FOREIGN KEY (theme_id) REFERENCES bb_projects_projecttheme(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE projects_projectpitch
	ADD CONSTRAINT theme_id_refs_id_8d479809 FOREIGN KEY (theme_id) REFERENCES bb_projects_projecttheme(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE projects_projectplan
	ADD CONSTRAINT theme_id_refs_id_e9f7d0d1 FOREIGN KEY (theme_id) REFERENCES bb_projects_projecttheme(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE tasks_task_files
	ADD CONSTRAINT tasks_task_files_task_id_78ceab895d23dc42_uniq UNIQUE (task_id, taskfile_id);

ALTER TABLE tasks_task_files
	ADD CONSTRAINT task_id_refs_id_68a7e47c FOREIGN KEY (task_id) REFERENCES tasks_task(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE tasks_task_files
	ADD CONSTRAINT taskfile_id_refs_id_8915c958 FOREIGN KEY (taskfile_id) REFERENCES bb_tasks_taskfile(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE tasks_task_members
	ADD CONSTRAINT tasks_task_members_task_id_ebfef1d4a7ceede_uniq UNIQUE (task_id, taskmember_id);

ALTER TABLE tasks_task_members
	ADD CONSTRAINT task_id_refs_id_d6afa2e6 FOREIGN KEY (task_id) REFERENCES tasks_task(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE tasks_task_members
	ADD CONSTRAINT taskmember_id_refs_id_964503d2 FOREIGN KEY (taskmember_id) REFERENCES bb_tasks_taskmember(id) DEFERRABLE INITIALLY DEFERRED;

CREATE INDEX projects_projectphase_name_like ON bb_projects_projectphase USING btree (name varchar_pattern_ops);

CREATE INDEX projects_projecttheme_name_like ON bb_projects_projecttheme USING btree (name varchar_pattern_ops);

CREATE INDEX projects_projecttheme_slug_like ON bb_projects_projecttheme USING btree (slug varchar_pattern_ops);

CREATE INDEX bb_tasks_skill_name_like ON bb_tasks_skill USING btree (name varchar_pattern_ops);

CREATE INDEX bb_tasks_skill_name_nl_like ON bb_tasks_skill USING btree (name_nl varchar_pattern_ops);

CREATE INDEX bb_tasks_taskfile_author_id ON bb_tasks_taskfile USING btree (author_id);

CREATE INDEX tasks_taskmember_member_id ON bb_tasks_taskmember USING btree (member_id);

CREATE INDEX tasks_taskmember_task_id ON bb_tasks_taskmember USING btree (task_id);

CREATE INDEX members_member_email_like ON members_member USING btree (email varchar_pattern_ops);

CREATE INDEX members_member_username_like ON members_member USING btree (username varchar_pattern_ops);

CREATE INDEX members_member_groups_group_id ON members_member_groups USING btree (group_id);

CREATE INDEX members_member_groups_member_id ON members_member_groups USING btree (member_id);

CREATE INDEX members_member_user_permissions_member_id ON members_member_user_permissions USING btree (member_id);

CREATE INDEX members_member_user_permissions_permission_id ON members_member_user_permissions USING btree (permission_id);

CREATE INDEX payouts_organizationpayoutlog_payout_id ON payouts_organizationpayoutlog USING btree (payout_id);

CREATE INDEX payouts_payoutlog_payout_id ON payouts_payoutlog USING btree (payout_id);

CREATE INDEX projects_project_country_id ON projects_project USING btree (country_id);

CREATE INDEX projects_project_organization_id ON projects_project USING btree (organization_id);

CREATE INDEX projects_project_status_id ON projects_project USING btree (status_id);

CREATE INDEX projects_project_theme_id ON projects_project USING btree (theme_id);

CREATE INDEX tasks_task_files_task_id ON tasks_task_files USING btree (task_id);

CREATE INDEX tasks_task_files_taskfile_id ON tasks_task_files USING btree (taskfile_id);

CREATE INDEX tasks_task_members_task_id ON tasks_task_members USING btree (task_id);

CREATE INDEX tasks_task_members_taskmember_id ON tasks_task_members USING btree (taskmember_id);

/* Original database ignored statements

SET statement_timeout = 0;

SET client_encoding = 'UTF8';

SET standard_conforming_strings = on;

SET check_function_bodies = false;

SET client_min_messages = warning;

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';

SET default_tablespace = '';

SET default_with_oids = false;

REVOKE ALL ON SCHEMA public FROM PUBLIC;

REVOKE ALL ON SCHEMA public FROM postgres;

GRANT ALL ON SCHEMA public TO postgres;

GRANT ALL ON SCHEMA public TO PUBLIC;
*/

/* New database ignored statements

SET statement_timeout = 0;

SET client_encoding = 'UTF8';

SET standard_conforming_strings = on;

SET check_function_bodies = false;

SET client_min_messages = warning;

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';

SET default_tablespace = '';

SET default_with_oids = false;

REVOKE ALL ON SCHEMA public FROM PUBLIC;

REVOKE ALL ON SCHEMA public FROM postgres;

GRANT ALL ON SCHEMA public TO postgres;

GRANT ALL ON SCHEMA public TO PUBLIC;
*/
