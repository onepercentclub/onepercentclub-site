-- This migration is intended to migrate stand-alone 1%Club site to a schema
-- that could be imported into a mulii-tenant site.
--
-- Steps:
-- 1. Copy the db you want to migrate.
--    a. echo 'CREATE DATABASE opc_to_saas WITH TEMPLATE onepercentsite;' | psql onepercentsite
-- 2. Run these scripts on the new db:
--    a. psql opc_to_saas < migrate_to_saas.sql
-- 3. Dump the new schema:
--    a. pg_dump opc_to_saas -n onepercent > onepercent_saas.sql
-- 4. Load it in a saas db that already has a onepercent client.
--    a. echo 'DROP SCHEMA onepercent CASCADE;' | psql saas
--    b. psql saas < onepercent_saas.sql


DROP TABLE accounting_banktransaction;
DROP TABLE accounting_banktransactioncategory;
DROP TABLE accounting_docdatapayment;
DROP TABLE accounting_docdatapayout;

DROP TABLE campaigns_campaign;

DROP TABLE celery_taskmeta;
DROP TABLE celery_tasksetmeta;
DROP TABLE djcelery_crontabschedule CASCADE;
DROP TABLE djcelery_intervalschedule CASCADE;
DROP TABLE djcelery_periodictask;
DROP TABLE djcelery_periodictasks;
DROP TABLE djcelery_taskstate;
DROP TABLE djcelery_workerstate;

DROP TABLE cowry_docdata_docdatapayment CASCADE;
DROP TABLE cowry_docdata_docdatapaymentlogentry;
DROP TABLE cowry_docdata_docdatapaymentorder CASCADE;
DROP TABLE cowry_docdata_docdatawebdirectdirectdebit;
DROP TABLE cowry_payment CASCADE;

DROP TABLE django_session;

ALTER TABLE fluent_contents_contentitem ADD COLUMN language_code character varying(15) NOT NULL DEFAULT 'en';

DROP TABLE fund_donation;
DROP TABLE fund_order CASCADE;
DROP TABLE fund_recurringdirectdebitpayment;

CREATE TABLE geo_location (
   id integer NOT NULL,
   name character varying(100) NOT NULL,
   active boolean NOT NULL,
   latitude numeric(21,18),
   longitude numeric(21,18),
   country_id integer
);

CREATE SEQUENCE geo_location_id_seq
   START WITH 1
   INCREMENT BY 1
   NO MINVALUE
   NO MAXVALUE
   CACHE 1;

ALTER SEQUENCE geo_location_id_seq OWNED BY geo_location.id;

DROP TABLE love_lovedeclaration;

DROP TABLE mchanga_mpesafundraiser;
DROP TABLE mchanga_mpesapayment;

ALTER TABLE members_member RENAME COLUMN about to about_me;
ALTER TABLE members_member DROP COLUMN contribution;
ALTER TABLE members_member ADD COLUMN campaign_notifications boolean NOT NULL DEFAULT TRUE;

CREATE TABLE bb_follow_follow (
   id integer NOT NULL,
   user_id integer NOT NULL,
   content_type_id integer NOT NULL,
   object_id integer NOT NULL,
   CONSTRAINT bb_follow_follow_object_id_check CHECK ((object_id >= 0))
);

CREATE SEQUENCE bb_follow_follow_id_seq
   START WITH 1
   INCREMENT BY 1
   NO MINVALUE
   NO MAXVALUE
   CACHE 1;


ALTER SEQUENCE bb_follow_follow_id_seq OWNED BY bb_follow_follow.id;

ALTER TABLE organizations_organization DROP COLUMN description;
ALTER TABLE organizations_organization DROP COLUMN legal_status;

ALTER TABLE payments_docdata_docdatapayment DROP constraint ck_customer_id_pstv_45403734d00129e7;

CREATE TABLE payments_mock_mockpayment (
   payment_ptr_id integer NOT NULL
);

ALTER TABLE projects_project DROP COLUMN coach_id;
ALTER TABLE projects_project DROP COLUMN mchanga_account;

DROP TABLE projects_projectambassador;
DROP TABLE projects_projectcampaign;
DROP TABLE projects_projectpitch;
DROP TABLE projects_projectplan;
DROP TABLE projects_projectresult;

ALTER TABLE quotes_quote DROP COLUMN segment;

DROP TABLE registration_registrationprofile;

ALTER TABLE tasks_task DROP COLUMN end_goal;

ALTER TABLE tasks_taskmember ADD CONSTRAINT tasks_taskmember_time_spent_check CHECK ((time_spent >= 0));


DROP TABLE tests_childsluggedtestmodel;
DROP TABLE tests_name CASCADE;
DROP TABLE tests_note CASCADE;
DROP TABLE tests_person CASCADE;
DROP TABLE tests_person_children;
DROP TABLE tests_person_notes;
DROP TABLE tests_secret;
DROP TABLE tests_sluggedtestmodel;
DROP TABLE tests_testagregatemodel;
DROP TABLE tests_testmanytomanymodel CASCADE;
DROP TABLE tests_testmanytomanymodel_many;
DROP TABLE tests_testmodel;
DROP TABLE tests_testmodel_field;
DROP TABLE tests_testmodel_pk CASCADE;

DROP TABLE thumbnail_kvstore;

DROP TABLE vouchers_customvoucherrequest;
DROP TABLE vouchers_voucher;


CREATE TABLE utils_metadatamodel (
   id integer NOT NULL,
   title character varying(50) NOT NULL
);


ALTER TABLE utils_metadatamodel OWNER TO gannetson;
CREATE SEQUENCE utils_metadatamodel_id_seq
   START WITH 1
   INCREMENT BY 1
   NO MINVALUE
   NO MAXVALUE
   CACHE 1;

ALTER SEQUENCE utils_metadatamodel_id_seq OWNED BY utils_metadatamodel.id;

ALTER TABLE wallposts_wallpost ADD COLUMN email_followers boolean NOT NULL DEFAULT TRUE;


DELETE FROM south_migrationhistory WHERE app_name IN ('djcelery', 'django_extensions');


-- Part 2


ALTER SEQUENCE accounts_useraddress_id_seq RENAME TO members_useraddress_id_seq;

ALTER SEQUENCE banners_slide_id_seq RENAME TO slides_slide_id_seq;

ALTER SEQUENCE projects_projectphase_id_seq RENAME TO bb_projects_projectphase_id_seq;

ALTER SEQUENCE blogs_blogpost_id_seq RENAME TO news_newsitem_id_seq;

ALTER SEQUENCE pages_contactmessage_id_seq RENAME TO contact_contactmessage_id_seq;

ALTER TABLE ONLY bb_follow_follow ALTER COLUMN id SET DEFAULT nextval('bb_follow_follow_id_seq'::regclass);

ALTER TABLE ONLY bb_follow_follow ADD CONSTRAINT bb_follow_follow_pkey PRIMARY KEY (id);

-- ALTER INDEX payouts_organizationpayoutlog_pkey RENAME TO bb_payouts_organizationpayoutlog_pkey;
-- ALTER INDEX payouts_payoutlog_pkey RENAME TO bb_payouts_projectpayoutlog_pkey;

ALTER TABLE ONLY bb_projects_projectphase ADD CONSTRAINT bb_projects_projectphase_pkey PRIMARY KEY (id);

ALTER TABLE ONLY bb_projects_projectphase ADD CONSTRAINT bb_projects_projectphase_name_key UNIQUE (name);

ALTER TABLE ONLY bb_projects_projectphase ADD CONSTRAINT bb_projects_projectphase_slug_key UNIQUE (slug);

ALTER TABLE ONLY bb_projects_projectphase ADD CONSTRAINT bb_projects_projectphase_sequence_key UNIQUE (sequence);


ALTER TABLE bb_projects_projecttheme DROP CONSTRAINT projects_projecttheme_name_key;
ALTER TABLE bb_projects_projecttheme DROP CONSTRAINT projects_projecttheme_pkey;
ALTER TABLE bb_projects_projecttheme DROP CONSTRAINT projects_projecttheme_slug_key;
ALTER TABLE ONLY bb_projects_projecttheme
    ADD CONSTRAINT bb_projects_projecttheme_name_key UNIQUE (name);
ALTER TABLE ONLY bb_projects_projecttheme
    ADD CONSTRAINT bb_projects_projecttheme_name_nl_key UNIQUE (name_nl);
ALTER TABLE ONLY bb_projects_projecttheme
    ADD CONSTRAINT bb_projects_projecttheme_pkey PRIMARY KEY (id);
ALTER TABLE ONLY bb_projects_projecttheme
    ADD CONSTRAINT bb_projects_projecttheme_slug_key UNIQUE (slug);


ALTER TABLE payouts_organizationpayout
    DROP CONSTRAINT payouts_organizationpayout_start_date_73b3545711f6730e_uniq;
ALTER TABLE ONLY payouts_organizationpayout
    ADD CONSTRAINT payouts_organizationpayout_start_date_end_date_key UNIQUE (start_date, end_date);

ALTER TABLE payouts_projectpayout
    DROP CONSTRAINT payouts_payout_pkey;
ALTER TABLE ONLY payouts_projectpayout
    ADD CONSTRAINT payouts_projectpayout_pkey PRIMARY KEY (id);

ALTER TABLE contact_contactmessage
    DROP CONSTRAINT pages_contactmessage_pkey;
ALTER TABLE ONLY contact_contactmessage
    ADD CONSTRAINT contact_contactmessage_pkey PRIMARY KEY (id);


ALTER TABLE news_newsitem DROP CONSTRAINT blogs_blogpost_pkey;
ALTER TABLE news_newsitem DROP CONSTRAINT blogs_blogpost_slug_6b3bc696cce4c377_uniq;
ALTER TABLE ONLY news_newsitem
    ADD CONSTRAINT news_newsitem_pkey PRIMARY KEY (id);

ALTER TABLE ONLY geo_location
    ADD CONSTRAINT geo_location_name_key UNIQUE (name);
ALTER TABLE ONLY geo_location
    ADD CONSTRAINT geo_location_pkey PRIMARY KEY (id);


ALTER TABLE ONLY members_useraddress
    ADD CONSTRAINT members_useraddress_pkey PRIMARY KEY (id);
ALTER TABLE ONLY members_useraddress
    ADD CONSTRAINT members_useraddress_user_id_key UNIQUE (user_id);


ALTER TABLE ONLY payments_mock_mockpayment
    ADD CONSTRAINT payments_mock_mockpayment_pkey PRIMARY KEY (payment_ptr_id);

ALTER TABLE ONLY payments_voucher_voucherpayment
    ADD CONSTRAINT payments_voucher_voucherpayment_voucher_id_key UNIQUE (voucher_id);

ALTER TABLE ONLY projects_project
    ADD CONSTRAINT projects_project_title_key UNIQUE (title);

-- ALTER TABLE ONLY social_auth_code
--     DROP CONSTRAINT social_auth_code_email_code_key;
--
-- ALTER TABLE ONLY taggit_tag
--     DROP CONSTRAINT taggit_tag_pkey;
--
-- ALTER TABLE ONLY wallposts_textwallpost
--     DROP CONSTRAINT wallposts_textwallpost_pkey;

DROP INDEX accounts_useraddress_country_id;
DROP INDEX accounts_useraddress_user_id;
CREATE INDEX members_useraddress_country_id ON members_useraddress USING btree (country_id);



DROP INDEX blogs_blogpost_author_id;
DROP INDEX blogs_blogpost_publication_date;
DROP INDEX blogs_blogpost_publication_end_date;
DROP INDEX blogs_blogpost_slug;
DROP INDEX blogs_blogpost_slug_like;
DROP INDEX blogs_blogpost_status;
DROP INDEX blogs_blogpost_status_like;

CREATE INDEX news_newsitem_author_id ON news_newsitem USING btree (author_id);
CREATE INDEX news_newsitem_publication_date ON news_newsitem USING btree (publication_date);
CREATE INDEX news_newsitem_publication_end_date ON news_newsitem USING btree (publication_end_date);
CREATE INDEX news_newsitem_slug ON news_newsitem USING btree (slug);
CREATE INDEX news_newsitem_slug_like ON news_newsitem USING btree (slug varchar_pattern_ops);
CREATE INDEX news_newsitem_status ON news_newsitem USING btree (status);
CREATE INDEX news_newsitem_status_like ON news_newsitem USING btree (status varchar_pattern_ops);


CREATE INDEX bb_follow_follow_content_type_id ON bb_follow_follow USING btree (content_type_id);
CREATE INDEX bb_follow_follow_user_id ON bb_follow_follow USING btree (user_id);


DROP INDEX payouts_organizationpayoutlog_payout_id;
DROP INDEX payouts_payout_project_id;
DROP INDEX payouts_payoutlog_payout_id;

CREATE INDEX bb_payouts_organizationpayoutlog_payout_id ON bb_payouts_organizationpayoutlog USING btree (payout_id);
CREATE INDEX bb_payouts_projectpayoutlog_payout_id ON bb_payouts_projectpayoutlog USING btree (payout_id);
CREATE INDEX bb_projects_projectphase_name_like ON bb_projects_projectphase USING btree (name varchar_pattern_ops);
CREATE INDEX bb_projects_projectphase_slug_like ON bb_projects_projectphase USING btree (slug varchar_pattern_ops);
CREATE INDEX bb_projects_projecttheme_name_like ON bb_projects_projecttheme USING btree (name varchar_pattern_ops);
CREATE INDEX bb_projects_projecttheme_name_nl_like ON bb_projects_projecttheme USING btree (name_nl varchar_pattern_ops);
CREATE INDEX bb_projects_projecttheme_slug_like ON bb_projects_projecttheme USING btree (slug varchar_pattern_ops);
CREATE INDEX contact_contactmessage_author_id ON contact_contactmessage USING btree (author_id);


CREATE INDEX fluent_contents_contentitem_language_code ON fluent_contents_contentitem USING btree (language_code);
CREATE INDEX fluent_contents_contentitem_language_code_like ON fluent_contents_contentitem USING btree (language_code varchar_pattern_ops);

CREATE INDEX geo_location_country_id ON geo_location USING btree (country_id);
CREATE INDEX geo_location_name_like ON geo_location USING btree (name varchar_pattern_ops);

CREATE INDEX organizations_organization_account_holder_country_id ON organizations_organization USING btree (account_holder_country_id);

DROP INDEX pages_contactmessage_author_id;

DROP INDEX payments_docdata_docdatatransaction_docdata_id_like;

CREATE INDEX payouts_projectpayout_project_id ON payouts_projectpayout USING btree (project_id);
DROP INDEX payments_voucher_voucherpayment_voucher_id;

CREATE INDEX projects_project_country_id ON projects_project USING btree (country_id);
CREATE INDEX projects_project_language_id ON projects_project USING btree (language_id);
CREATE INDEX projects_project_organization_id ON projects_project USING btree (organization_id);

CREATE INDEX projects_project_status_id ON projects_project USING btree (status_id);
CREATE INDEX projects_project_theme_id ON projects_project USING btree (theme_id);
CREATE INDEX projects_project_title_like ON projects_project USING btree (title varchar_pattern_ops);
CREATE INDEX projects_projectbudgetline_project_id ON projects_projectbudgetline USING btree (project_id);

DROP INDEX projects_projecttheme_name_like;
DROP INDEX projects_projecttheme_slug_like;

DROP INDEX social_auth_association_issued;
DROP INDEX social_auth_nonce_timestamp;

CREATE INDEX taggit_tag_name_like ON taggit_tag USING btree (name varchar_pattern_ops);

ALTER TABLE ONLY organizations_organization
    ADD CONSTRAINT account_holder_country_id_refs_id_64796f4e FOREIGN KEY (account_holder_country_id) REFERENCES geo_country(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE ONLY bb_follow_follow
    ADD CONSTRAINT bb_follow_follow_content_type_id_fkey FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE ONLY bb_follow_follow
    ADD CONSTRAINT bb_follow_follow_user_id_fkey FOREIGN KEY (user_id) REFERENCES members_member(id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE ONLY contact_contactmessage
    ADD CONSTRAINT contact_contactmessage_author_id_fkey FOREIGN KEY (author_id) REFERENCES members_member(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE ONLY geo_location
    ADD CONSTRAINT country_id_refs_id_c339534a FOREIGN KEY (country_id) REFERENCES geo_country(id) DEFERRABLE INITIALLY DEFERRED;


-- ALTER TABLE ONLY members_useraddress
--     ADD CONSTRAINT members_useraddress_country_id_fkey FOREIGN KEY (country_id) REFERENCES geo_country(id) DEFERRABLE INITIALLY DEFERRED;
-- ALTER TABLE ONLY members_useraddress
--     ADD CONSTRAINT members_useraddress_user_id_fkey FOREIGN KEY (user_id) REFERENCES members_member(id) DEFERRABLE INITIALLY DEFERRED;
-- ALTER TABLE ONLY news_newsitem
--     ADD CONSTRAINT news_newsitem_author_id_fkey FOREIGN KEY (author_id) REFERENCES members_member(id) DEFERRABLE INITIALLY DEFERRED;

-- ALTER TABLE ONLY payments_mock_mockpayment
--     ADD CONSTRAINT payment_ptr_id_refs_id_2b26da6b FOREIGN KEY (payment_ptr_id) REFERENCES payments_payment(id) DEFERRABLE INITIALLY DEFERRED;

-- ALTER TABLE ONLY payouts_projectpayout
--     ADD CONSTRAINT payouts_projectpayout_project_id_fkey FOREIGN KEY (project_id) REFERENCES projects_project(id) DEFERRABLE INITIALLY DEFERRED;


--  NOW RENAME THE SCHEMA
ALTER SCHEMA public RENAME TO onepercent;



