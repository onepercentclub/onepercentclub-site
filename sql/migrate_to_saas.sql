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


-- More changes by apgdiff


COMMENT ON SCHEMA onepercent IS NULL;

SET search_path = onepercent, pg_catalog;

ALTER TABLE bb_payouts_organizationpayoutlog
	DROP CONSTRAINT payouts_organizationpayoutlog_pkey;

ALTER TABLE bb_payouts_projectpayoutlog
	DROP CONSTRAINT payouts_payoutlog_pkey;

ALTER TABLE members_useraddress
	DROP CONSTRAINT accounts_useraddress_pkey;

ALTER TABLE payouts_projectpayout
	DROP CONSTRAINT payouts_payout_pkey;

ALTER TABLE admin_tools_dashboard_preferences
	DROP CONSTRAINT admin_tools_dashboard_prefer_dashboard_id_374bce90a8a4eefc_uniq;

ALTER TABLE admin_tools_dashboard_preferences
	DROP CONSTRAINT user_id_refs_id_8731bda9;

ALTER TABLE admin_tools_menu_bookmark
	DROP CONSTRAINT user_id_refs_id_a2e64058;

ALTER TABLE auth_group_permissions
	DROP CONSTRAINT auth_group_permissions_group_id_key;

ALTER TABLE auth_permission
	DROP CONSTRAINT auth_permission_content_type_id_key;

ALTER TABLE bb_payouts_organizationpayoutlog
	DROP CONSTRAINT payout_id_refs_id_d601d93e;

ALTER TABLE bb_payouts_projectpayoutlog
	DROP CONSTRAINT payout_id_refs_id_3585d806;

ALTER TABLE bb_projects_projectphase
	DROP CONSTRAINT bb_projects_projectphase_id_key;

ALTER TABLE contact_contactmessage
	DROP CONSTRAINT author_id_refs_id_4e71209f;

ALTER TABLE contentitem_oembeditem_oembeditem
	DROP CONSTRAINT contentitem_ptr_id_refs_id_5c779195;

ALTER TABLE contentitem_rawhtml_rawhtmlitem
	DROP CONSTRAINT contentitem_ptr_id_refs_id_750f6db7;

ALTER TABLE contentitem_text_textitem
	DROP CONSTRAINT contentitem_ptr_id_refs_id_c1ae5a62;

ALTER TABLE django_admin_log
	DROP CONSTRAINT django_admin_log_content_type_id_fkey;

ALTER TABLE django_content_type
	DROP CONSTRAINT django_content_type_app_label_key;

ALTER TABLE donations_donation
	DROP CONSTRAINT fundraiser_id_refs_id_f98754a0;

ALTER TABLE donations_donation
	DROP CONSTRAINT project_id_refs_id_44b53000;

ALTER TABLE fluent_contents_contentitem
	DROP CONSTRAINT parent_type_id_refs_id_b2e67e62;

ALTER TABLE fluent_contents_contentitem
	DROP CONSTRAINT placeholder_id_refs_id_8e1f1b78;

ALTER TABLE fluent_contents_contentitem
	DROP CONSTRAINT polymorphic_ctype_id_refs_id_b2e67e62;

ALTER TABLE fluent_contents_placeholder
	DROP CONSTRAINT fluent_contents_placeholde_parent_type_id_451c85966d08dedf_uniq;

ALTER TABLE fluent_contents_placeholder
	DROP CONSTRAINT parent_type_id_refs_id_a0f06b12;

ALTER TABLE fundraisers_fundraiser
	DROP CONSTRAINT owner_id_refs_id_be2e6d23;

ALTER TABLE fundraisers_fundraiser
	DROP CONSTRAINT project_id_refs_id_01907c29;

ALTER TABLE geo_country
	DROP CONSTRAINT subregion_id_refs_id_8ed0be82;

ALTER TABLE geo_subregion
	DROP CONSTRAINT region_id_refs_id_2135f371;

ALTER TABLE members_member_groups
	DROP CONSTRAINT members_member_groups_member_id_1d988989311d97dc_uniq;

ALTER TABLE members_member_groups
	DROP CONSTRAINT group_id_refs_id_98a483ff;

ALTER TABLE members_member_groups
	DROP CONSTRAINT member_id_refs_id_87beb27c;

ALTER TABLE members_member_user_permissions
	DROP CONSTRAINT members_member_user_id_147f9109b2c6aedf_uniq;

ALTER TABLE members_member_user_permissions
	DROP CONSTRAINT member_id_refs_id_00516181;

ALTER TABLE members_member_user_permissions
	DROP CONSTRAINT permission_id_refs_id_b705fa48;

ALTER TABLE members_useraddress
	DROP CONSTRAINT country_id_refs_id_4f1cad9c;

ALTER TABLE members_useraddress
	DROP CONSTRAINT user_id_refs_id_d63735d0;

ALTER TABLE news_newsitem
	DROP CONSTRAINT author_id_refs_id_b9b4b013;

ALTER TABLE orders_order
	DROP CONSTRAINT user_id_refs_id_1d2647b6;

ALTER TABLE organizations_organizationdocument
	DROP CONSTRAINT author_id_refs_id_f32a2173;

ALTER TABLE organizations_organizationdocument
	DROP CONSTRAINT organization_id_refs_id_bbf94826;

ALTER TABLE organizations_organizationmember
	DROP CONSTRAINT organization_id_refs_id_1c91eaaf;

ALTER TABLE organizations_organizationmember
	DROP CONSTRAINT user_id_refs_id_495b3c89;

ALTER TABLE pages_page
	DROP CONSTRAINT pages_page_language_7415b110df64f20b_uniq;

ALTER TABLE pages_page
	DROP CONSTRAINT author_id_refs_id_423e462e;

ALTER TABLE payments_docdata_docdatadirectdebitpayment
	DROP CONSTRAINT payment_ptr_id_refs_id_e5a99559;

ALTER TABLE payments_docdata_docdatapayment
	DROP CONSTRAINT payment_ptr_id_refs_id_ea8901b0;

ALTER TABLE payments_docdata_docdatatransaction
	DROP CONSTRAINT transaction_ptr_id_refs_id_4e92d97e;

ALTER TABLE payments_logger_paymentlogentry
	DROP CONSTRAINT payment_id_refs_id_82bc8d67;

ALTER TABLE payments_orderpayment
	DROP CONSTRAINT authorization_action_id_refs_id_c10b7e5e;

ALTER TABLE payments_orderpayment
	DROP CONSTRAINT user_id_refs_id_aa6ebd4b;

ALTER TABLE payments_payment
	DROP CONSTRAINT polymorphic_ctype_id_refs_id_18b24db0;

ALTER TABLE payments_transaction
	DROP CONSTRAINT payment_id_refs_id_6e68e47b;

ALTER TABLE payments_transaction
	DROP CONSTRAINT polymorphic_ctype_id_refs_id_f715c75a;

ALTER TABLE payments_voucher_voucher
	DROP CONSTRAINT receiver_id_refs_id_df71862b;

ALTER TABLE payments_voucher_voucher
	DROP CONSTRAINT sender_id_refs_id_df71862b;

ALTER TABLE payments_voucher_voucherpayment
	DROP CONSTRAINT payment_ptr_id_refs_id_3f1e6734;

ALTER TABLE payouts_projectpayout
	DROP CONSTRAINT project_id_refs_id_604abf8b;

ALTER TABLE projects_project
	DROP CONSTRAINT owner_id_refs_id_00849aea;

ALTER TABLE projects_project
	DROP CONSTRAINT project_projects_language_id_refs_language_id;

ALTER TABLE quotes_quote
	DROP CONSTRAINT author_id_refs_id_5685a250;

ALTER TABLE quotes_quote
	DROP CONSTRAINT user_id_refs_id_5685a250;

ALTER TABLE recurring_donations_monthlydonation
	DROP CONSTRAINT order_id_refs_id_032890ef;

ALTER TABLE recurring_donations_monthlydonation
	DROP CONSTRAINT project_id_refs_id_5e867261;

ALTER TABLE recurring_donations_monthlydonation
	DROP CONSTRAINT user_id_refs_id_b1f89cf8;

ALTER TABLE recurring_donations_monthlydonor
	DROP CONSTRAINT user_id_refs_id_75810bb6;

ALTER TABLE recurring_donations_monthlydonorproject
	DROP CONSTRAINT donor_id_refs_id_04176065;

ALTER TABLE recurring_donations_monthlydonorproject
	DROP CONSTRAINT project_id_refs_id_99b9491f;

ALTER TABLE recurring_donations_monthlyorder
	DROP CONSTRAINT batch_id_refs_id_7518ff59;

ALTER TABLE recurring_donations_monthlyorder
	DROP CONSTRAINT user_id_refs_id_2bda443a;

ALTER TABLE recurring_donations_monthlyproject
	DROP CONSTRAINT batch_id_refs_id_c793b42a;

ALTER TABLE recurring_donations_monthlyproject
	DROP CONSTRAINT project_id_refs_id_0db1bf76;

ALTER TABLE slides_slide
	DROP CONSTRAINT author_id_refs_id_1fd1e6c5;

ALTER TABLE social_auth_association
	DROP CONSTRAINT social_auth_association_handle_693a924207fa6ae_uniq;

ALTER TABLE social_auth_nonce
	DROP CONSTRAINT social_auth_nonce_timestamp_3833ba21ef52524a_uniq;

ALTER TABLE social_auth_usersocialauth
	DROP CONSTRAINT social_auth_usersocialauth_provider_2f763109e2c4a1fb_uniq;

ALTER TABLE social_auth_usersocialauth
	DROP CONSTRAINT user_id_refs_id_3ee0ca96;

ALTER TABLE taggit_tag
	DROP CONSTRAINT taggit_tag_name_uniq;

ALTER TABLE taggit_taggeditem
	DROP CONSTRAINT content_type_id_refs_id_01d42cdf;

ALTER TABLE taggit_taggeditem
	DROP CONSTRAINT tag_id_refs_id_c23fda9d;

ALTER TABLE tasks_task
	DROP CONSTRAINT author_id_refs_id_4b876806;

ALTER TABLE tasks_task
	DROP CONSTRAINT project_id_refs_id_4ef2746e;

ALTER TABLE tasks_taskfile
	DROP CONSTRAINT author_id_refs_id_6979ba50;

ALTER TABLE tasks_taskfile
	DROP CONSTRAINT task_id_refs_id_0f9ed58e;

ALTER TABLE tasks_taskmember
	DROP CONSTRAINT member_id_refs_id_861b83e0;

ALTER TABLE tasks_taskmember
	DROP CONSTRAINT task_id_refs_id_e6a84bbf;

ALTER TABLE wallposts_mediawallpost
	DROP CONSTRAINT wallpost_ptr_id_refs_id_25930a7b;

ALTER TABLE wallposts_mediawallpostphoto
	DROP CONSTRAINT author_id_refs_id_ab104ed2;

ALTER TABLE wallposts_mediawallpostphoto
	DROP CONSTRAINT editor_id_refs_id_ab104ed2;

ALTER TABLE wallposts_mediawallpostphoto
	DROP CONSTRAINT mediawallpost_id_refs_wallpost_ptr_id_92d4ab8e;

ALTER TABLE wallposts_reaction
	DROP CONSTRAINT author_id_refs_id_19f2c26a;

ALTER TABLE wallposts_reaction
	DROP CONSTRAINT editor_id_refs_id_19f2c26a;

ALTER TABLE wallposts_reaction
	DROP CONSTRAINT wallpost_id_refs_id_bad3e69d;

ALTER TABLE wallposts_systemwallpost
	DROP CONSTRAINT related_type_id_refs_id_d37c45d3;

ALTER TABLE wallposts_systemwallpost
	DROP CONSTRAINT wallpost_ptr_id_refs_id_07f15c19;

ALTER TABLE wallposts_textwallpost
	DROP CONSTRAINT wallpost_ptr_id_refs_id_67d61a0a;

ALTER TABLE wallposts_wallpost
	DROP CONSTRAINT author_id_refs_id_245000e6;

ALTER TABLE wallposts_wallpost
	DROP CONSTRAINT content_type_id_refs_id_858aa98c;

ALTER TABLE wallposts_wallpost
	DROP CONSTRAINT editor_id_refs_id_245000e6;

ALTER TABLE wallposts_wallpost
	DROP CONSTRAINT polymorphic_ctype_id_refs_id_858aa98c;

DROP INDEX members_member_user_permissions_bluebottleuser_id;

DROP SEQUENCE accounts_timeavailable_id_seq;

DROP SEQUENCE accounts_useraddress_id_seq;

DROP SEQUENCE banners_slide_id_seq;

DROP SEQUENCE projects_projectphase_id_seq;

CREATE SEQUENCE bb_projects_projectphase_id_seq
	START WITH 1
	INCREMENT BY 1
	NO MAXVALUE
	NO MINVALUE
	CACHE 1;

CREATE SEQUENCE members_useraddress_id_seq
	START WITH 1
	INCREMENT BY 1
	NO MAXVALUE
	NO MINVALUE
	CACHE 1;

CREATE SEQUENCE slides_slide_id_seq
	START WITH 1
	INCREMENT BY 1
	NO MAXVALUE
	NO MINVALUE
	CACHE 1;

ALTER TABLE bb_projects_projectphase
	ALTER COLUMN id SET DEFAULT nextval('bb_projects_projectphase_id_seq'::regclass);

ALTER TABLE fluent_contents_contentitem
	ALTER COLUMN language_code DROP DEFAULT;

ALTER TABLE geo_location
	ALTER COLUMN id SET DEFAULT nextval('geo_location_id_seq'::regclass);

ALTER TABLE members_member
	ALTER COLUMN first_name TYPE character varying(100) /* TYPE change - table: members_member original: character varying(30) new: character varying(100) */,
	ALTER COLUMN last_name TYPE character varying(100) /* TYPE change - table: members_member original: character varying(30) new: character varying(100) */,
	ALTER COLUMN facebook DROP DEFAULT,
	ALTER COLUMN twitter DROP DEFAULT,
	ALTER COLUMN skypename DROP DEFAULT,
	ALTER COLUMN campaign_notifications DROP DEFAULT;

ALTER TABLE members_useraddress
	ALTER COLUMN id SET DEFAULT nextval('members_useraddress_id_seq'::regclass);

ALTER TABLE news_newsitem
	ALTER COLUMN author_id DROP NOT NULL;

ALTER TABLE orders_order
	ALTER COLUMN order_type SET NOT NULL;

ALTER TABLE organizations_organization
	ALTER COLUMN account_holder_name DROP DEFAULT,
	ALTER COLUMN account_holder_name SET NOT NULL,
	ALTER COLUMN account_holder_address DROP DEFAULT,
	ALTER COLUMN account_holder_address SET NOT NULL,
	ALTER COLUMN account_holder_postal_code DROP DEFAULT,
	ALTER COLUMN account_holder_postal_code SET NOT NULL,
	ALTER COLUMN account_holder_city DROP DEFAULT,
	ALTER COLUMN account_holder_city SET NOT NULL,
	ALTER COLUMN account_bank_postal_code DROP DEFAULT,
	ALTER COLUMN account_bank_postal_code SET NOT NULL,
	ALTER COLUMN account_bank_city DROP DEFAULT,
	ALTER COLUMN account_bank_city SET NOT NULL;

ALTER TABLE pages_page
	ALTER COLUMN full_page DROP DEFAULT,
	ALTER COLUMN full_page SET NOT NULL,
	ALTER COLUMN author_id DROP NOT NULL;

ALTER TABLE payouts_projectpayout
	ALTER COLUMN amount_payable DROP DEFAULT;

ALTER TABLE projects_project
	ALTER COLUMN pitch DROP DEFAULT,
	ALTER COLUMN status_id DROP DEFAULT,
	ALTER COLUMN favorite DROP DEFAULT,
	ALTER COLUMN description DROP DEFAULT,
	ALTER COLUMN image DROP DEFAULT,
	ALTER COLUMN amount_asked DROP DEFAULT,
	ALTER COLUMN amount_donated DROP DEFAULT,
	ALTER COLUMN amount_needed DROP DEFAULT,
	ALTER COLUMN popularity SET NOT NULL,
	ALTER COLUMN effects DROP DEFAULT,
	ALTER COLUMN for_who DROP DEFAULT,
	ALTER COLUMN future DROP DEFAULT;

ALTER TABLE projects_projectbudgetline
	ALTER COLUMN project_id SET NOT NULL;

ALTER TABLE quotes_quote
	ALTER COLUMN author_id DROP NOT NULL;

ALTER TABLE slides_slide
	ALTER COLUMN id SET DEFAULT nextval('slides_slide_id_seq'::regclass),
	ALTER COLUMN author_id DROP NOT NULL;

ALTER TABLE social_auth_nonce
	ALTER COLUMN salt TYPE character varying(65) /* TYPE change - table: social_auth_nonce original: character varying(40) new: character varying(65) */;

ALTER TABLE tasks_taskmember
	ALTER COLUMN time_spent TYPE smallint /* TYPE change - table: tasks_taskmember original: integer new: smallint */,
	ALTER COLUMN time_spent DROP DEFAULT;

ALTER TABLE utils_metadatamodel
	ALTER COLUMN id SET DEFAULT nextval('utils_metadatamodel_id_seq'::regclass);

ALTER TABLE wallposts_wallpost
	ALTER COLUMN email_followers DROP DEFAULT;

ALTER SEQUENCE bb_projects_projectphase_id_seq
	OWNED BY bb_projects_projectphase.id;

ALTER SEQUENCE members_useraddress_id_seq
	OWNED BY members_useraddress.id;

ALTER SEQUENCE slides_slide_id_seq
	OWNED BY slides_slide.id;

ALTER TABLE bb_payouts_organizationpayoutlog
	ADD CONSTRAINT bb_payouts_organizationpayoutlog_pkey PRIMARY KEY (id);

ALTER TABLE bb_payouts_projectpayoutlog
	ADD CONSTRAINT bb_payouts_projectpayoutlog_pkey PRIMARY KEY (id);

ALTER TABLE members_useraddress
	ADD CONSTRAINT members_useraddress_pkey PRIMARY KEY (id);

ALTER TABLE payouts_projectpayout
	ADD CONSTRAINT payouts_projectpayout_pkey PRIMARY KEY (id);

ALTER TABLE utils_metadatamodel
	ADD CONSTRAINT utils_metadatamodel_pkey PRIMARY KEY (id);

ALTER TABLE admin_tools_dashboard_preferences
	ADD CONSTRAINT admin_tools_dashboard_preferences_user_id_dashboard_id_key UNIQUE (user_id, dashboard_id);

ALTER TABLE admin_tools_dashboard_preferences
	ADD CONSTRAINT user_id_refs_id_c40e2350 FOREIGN KEY (user_id) REFERENCES members_member(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE admin_tools_menu_bookmark
	ADD CONSTRAINT user_id_refs_id_0305724a FOREIGN KEY (user_id) REFERENCES members_member(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE auth_group_permissions
	ADD CONSTRAINT auth_group_permissions_group_id_permission_id_key UNIQUE (group_id, permission_id);

ALTER TABLE auth_permission
	ADD CONSTRAINT auth_permission_content_type_id_codename_key UNIQUE (content_type_id, codename);

ALTER TABLE bb_payouts_organizationpayoutlog
	ADD CONSTRAINT payout_id_refs_id_58cbb149 FOREIGN KEY (payout_id) REFERENCES payouts_organizationpayout(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE bb_payouts_projectpayoutlog
	ADD CONSTRAINT payout_id_refs_id_620ec1e4 FOREIGN KEY (payout_id) REFERENCES payouts_projectpayout(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE bb_projects_projecttheme
	ADD CONSTRAINT bb_projects_projecttheme_name_nl_key UNIQUE (name_nl);

ALTER TABLE contentitem_oembeditem_oembeditem
	ADD CONSTRAINT contentitem_oembeditem_oembeditem_contentitem_ptr_id_fkey FOREIGN KEY (contentitem_ptr_id) REFERENCES fluent_contents_contentitem(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE contentitem_rawhtml_rawhtmlitem
	ADD CONSTRAINT contentitem_rawhtml_rawhtmlitem_contentitem_ptr_id_fkey FOREIGN KEY (contentitem_ptr_id) REFERENCES fluent_contents_contentitem(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE contentitem_text_textitem
	ADD CONSTRAINT contentitem_text_textitem_contentitem_ptr_id_fkey FOREIGN KEY (contentitem_ptr_id) REFERENCES fluent_contents_contentitem(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE django_admin_log
	ADD CONSTRAINT content_type_id_refs_id_93d2d1f8 FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE django_admin_log
	ADD CONSTRAINT user_id_refs_id_42a14991 FOREIGN KEY (user_id) REFERENCES members_member(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE django_content_type
	ADD CONSTRAINT django_content_type_app_label_model_key UNIQUE (app_label, model);

ALTER TABLE donations_donation
	ADD CONSTRAINT donations_donation_fundraiser_id_fkey FOREIGN KEY (fundraiser_id) REFERENCES fundraisers_fundraiser(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE donations_donation
	ADD CONSTRAINT donations_donation_project_id_fkey FOREIGN KEY (project_id) REFERENCES projects_project(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE fluent_contents_contentitem
	ADD CONSTRAINT fluent_contents_contentitem_parent_type_id_fkey FOREIGN KEY (parent_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE fluent_contents_contentitem
	ADD CONSTRAINT fluent_contents_contentitem_placeholder_id_fkey FOREIGN KEY (placeholder_id) REFERENCES fluent_contents_placeholder(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE fluent_contents_contentitem
	ADD CONSTRAINT fluent_contents_contentitem_polymorphic_ctype_id_fkey FOREIGN KEY (polymorphic_ctype_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE fluent_contents_placeholder
	ADD CONSTRAINT fluent_contents_placeholder_parent_type_id_parent_id_slot_key UNIQUE (parent_type_id, parent_id, slot);

ALTER TABLE fluent_contents_placeholder
	ADD CONSTRAINT fluent_contents_placeholder_parent_type_id_fkey FOREIGN KEY (parent_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE fundraisers_fundraiser
	ADD CONSTRAINT fundraisers_fundraiser_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES members_member(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE fundraisers_fundraiser
	ADD CONSTRAINT fundraisers_fundraiser_project_id_fkey FOREIGN KEY (project_id) REFERENCES projects_project(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE geo_country
	ADD CONSTRAINT geo_country_subregion_id_fkey FOREIGN KEY (subregion_id) REFERENCES geo_subregion(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE geo_subregion
	ADD CONSTRAINT geo_subregion_region_id_fkey FOREIGN KEY (region_id) REFERENCES geo_region(id) DEFERRABLE INITIALLY DEFERRED;

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

ALTER TABLE members_useraddress
	ADD CONSTRAINT members_useraddress_country_id_fkey FOREIGN KEY (country_id) REFERENCES geo_country(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE members_useraddress
	ADD CONSTRAINT members_useraddress_user_id_fkey FOREIGN KEY (user_id) REFERENCES members_member(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE news_newsitem
	ADD CONSTRAINT news_newsitem_author_id_fkey FOREIGN KEY (author_id) REFERENCES members_member(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE orders_order
	ADD CONSTRAINT orders_order_user_id_fkey FOREIGN KEY (user_id) REFERENCES members_member(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE organizations_organizationdocument
	ADD CONSTRAINT organizations_organizationdocument_author_id_fkey FOREIGN KEY (author_id) REFERENCES members_member(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE organizations_organizationdocument
	ADD CONSTRAINT organizations_organizationdocument_organization_id_fkey FOREIGN KEY (organization_id) REFERENCES organizations_organization(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE organizations_organizationmember
	ADD CONSTRAINT organizations_organizationmember_organization_id_fkey FOREIGN KEY (organization_id) REFERENCES organizations_organization(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE organizations_organizationmember
	ADD CONSTRAINT organizations_organizationmember_user_id_fkey FOREIGN KEY (user_id) REFERENCES members_member(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE pages_page
	ADD CONSTRAINT pages_page_language_slug_key UNIQUE (language, slug);

ALTER TABLE pages_page
	ADD CONSTRAINT pages_page_author_id_fkey FOREIGN KEY (author_id) REFERENCES members_member(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE payments_docdata_docdatadirectdebitpayment
	ADD CONSTRAINT payments_docdata_docdatadirectdebitpayment_payment_ptr_id_fkey FOREIGN KEY (payment_ptr_id) REFERENCES payments_payment(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE payments_docdata_docdatapayment
	ADD CONSTRAINT payments_docdata_docdatapayment_payment_ptr_id_fkey FOREIGN KEY (payment_ptr_id) REFERENCES payments_payment(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE payments_docdata_docdatatransaction
	ADD CONSTRAINT payments_docdata_docdatatransaction_transaction_ptr_id_fkey FOREIGN KEY (transaction_ptr_id) REFERENCES payments_transaction(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE payments_logger_paymentlogentry
	ADD CONSTRAINT payments_logger_paymentlogentry_payment_id_fkey FOREIGN KEY (payment_id) REFERENCES payments_payment(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE payments_mock_mockpayment
	ADD CONSTRAINT payment_ptr_id_refs_id_2b26da6b FOREIGN KEY (payment_ptr_id) REFERENCES payments_payment(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE payments_orderpayment
	ADD CONSTRAINT payments_orderpayment_authorization_action_id_fkey FOREIGN KEY (authorization_action_id) REFERENCES payments_orderpaymentaction(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE payments_orderpayment
	ADD CONSTRAINT payments_orderpayment_user_id_fkey FOREIGN KEY (user_id) REFERENCES members_member(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE payments_payment
	ADD CONSTRAINT payments_payment_polymorphic_ctype_id_fkey FOREIGN KEY (polymorphic_ctype_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE payments_transaction
	ADD CONSTRAINT payments_transaction_payment_id_fkey FOREIGN KEY (payment_id) REFERENCES payments_payment(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE payments_transaction
	ADD CONSTRAINT payments_transaction_polymorphic_ctype_id_fkey FOREIGN KEY (polymorphic_ctype_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE payments_voucher_voucher
	ADD CONSTRAINT payments_voucher_voucher_order_id_fkey FOREIGN KEY (order_id) REFERENCES orders_order(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE payments_voucher_voucher
	ADD CONSTRAINT payments_voucher_voucher_receiver_id_fkey FOREIGN KEY (receiver_id) REFERENCES members_member(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE payments_voucher_voucher
	ADD CONSTRAINT payments_voucher_voucher_sender_id_fkey FOREIGN KEY (sender_id) REFERENCES members_member(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE payments_voucher_voucherpayment
	ADD CONSTRAINT payments_voucher_voucherpayment_payment_ptr_id_fkey FOREIGN KEY (payment_ptr_id) REFERENCES payments_payment(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE payouts_projectpayout
	ADD CONSTRAINT payouts_projectpayout_project_id_fkey FOREIGN KEY (project_id) REFERENCES projects_project(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE projects_project
	ADD CONSTRAINT projects_project_reach_check CHECK ((reach >= 0));

ALTER TABLE projects_project
	ADD CONSTRAINT projects_project_title_key UNIQUE (title);

ALTER TABLE projects_project
	ADD CONSTRAINT country_id_refs_id_3a57922e FOREIGN KEY (country_id) REFERENCES geo_country(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE projects_project
	ADD CONSTRAINT language_id_refs_id_084485b0 FOREIGN KEY (language_id) REFERENCES utils_language(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE projects_project
	ADD CONSTRAINT organization_id_refs_id_e42a8fc9 FOREIGN KEY (organization_id) REFERENCES organizations_organization(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE projects_project
	ADD CONSTRAINT projects_project_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES members_member(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE projects_project
	ADD CONSTRAINT status_id_refs_id_a99ffd5e FOREIGN KEY (status_id) REFERENCES bb_projects_projectphase(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE projects_project
	ADD CONSTRAINT theme_id_refs_id_232bb1be FOREIGN KEY (theme_id) REFERENCES bb_projects_projecttheme(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE projects_projectbudgetline
	ADD CONSTRAINT projects_projectbudgetline_project_id_fkey FOREIGN KEY (project_id) REFERENCES projects_project(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE quotes_quote
	ADD CONSTRAINT quotes_quote_author_id_fkey FOREIGN KEY (author_id) REFERENCES members_member(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE quotes_quote
	ADD CONSTRAINT quotes_quote_user_id_fkey FOREIGN KEY (user_id) REFERENCES members_member(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE recurring_donations_monthlydonation
	ADD CONSTRAINT recurring_donations_monthlydonation_order_id_fkey FOREIGN KEY (order_id) REFERENCES recurring_donations_monthlyorder(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE recurring_donations_monthlydonation
	ADD CONSTRAINT recurring_donations_monthlydonation_project_id_fkey FOREIGN KEY (project_id) REFERENCES projects_project(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE recurring_donations_monthlydonation
	ADD CONSTRAINT recurring_donations_monthlydonation_user_id_fkey FOREIGN KEY (user_id) REFERENCES members_member(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE recurring_donations_monthlydonor
	ADD CONSTRAINT recurring_donations_monthlydonor_user_id_fkey FOREIGN KEY (user_id) REFERENCES members_member(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE recurring_donations_monthlydonorproject
	ADD CONSTRAINT recurring_donations_monthlydonorproject_donor_id_fkey FOREIGN KEY (donor_id) REFERENCES recurring_donations_monthlydonor(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE recurring_donations_monthlydonorproject
	ADD CONSTRAINT recurring_donations_monthlydonorproject_project_id_fkey FOREIGN KEY (project_id) REFERENCES projects_project(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE recurring_donations_monthlyorder
	ADD CONSTRAINT recurring_donations_monthlyorder_batch_id_fkey FOREIGN KEY (batch_id) REFERENCES recurring_donations_monthlybatch(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE recurring_donations_monthlyorder
	ADD CONSTRAINT recurring_donations_monthlyorder_user_id_fkey FOREIGN KEY (user_id) REFERENCES members_member(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE recurring_donations_monthlyproject
	ADD CONSTRAINT recurring_donations_monthlyproject_batch_id_fkey FOREIGN KEY (batch_id) REFERENCES recurring_donations_monthlybatch(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE recurring_donations_monthlyproject
	ADD CONSTRAINT recurring_donations_monthlyproject_project_id_fkey FOREIGN KEY (project_id) REFERENCES projects_project(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE slides_slide
	ADD CONSTRAINT slides_slide_author_id_fkey FOREIGN KEY (author_id) REFERENCES members_member(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE social_auth_usersocialauth
	ADD CONSTRAINT social_auth_usersocialauth_provider_uid_key UNIQUE (provider, uid);

ALTER TABLE social_auth_usersocialauth
	ADD CONSTRAINT user_id_refs_id_b7aa3a38 FOREIGN KEY (user_id) REFERENCES members_member(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE taggit_tag
	ADD CONSTRAINT taggit_tag_name_key UNIQUE (name);

ALTER TABLE taggit_taggeditem
	ADD CONSTRAINT taggit_taggeditem_content_type_id_fkey FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE taggit_taggeditem
	ADD CONSTRAINT taggit_taggeditem_tag_id_fkey FOREIGN KEY (tag_id) REFERENCES taggit_tag(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE tasks_task
	ADD CONSTRAINT tasks_task_author_id_fkey FOREIGN KEY (author_id) REFERENCES members_member(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE tasks_task
	ADD CONSTRAINT tasks_task_project_id_fkey FOREIGN KEY (project_id) REFERENCES projects_project(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE tasks_taskfile
	ADD CONSTRAINT tasks_taskfile_author_id_fkey FOREIGN KEY (author_id) REFERENCES members_member(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE tasks_taskfile
	ADD CONSTRAINT tasks_taskfile_task_id_fkey FOREIGN KEY (task_id) REFERENCES tasks_task(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE tasks_taskmember
	ADD CONSTRAINT tasks_taskmember_member_id_fkey FOREIGN KEY (member_id) REFERENCES members_member(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE tasks_taskmember
	ADD CONSTRAINT tasks_taskmember_task_id_fkey FOREIGN KEY (task_id) REFERENCES tasks_task(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE wallposts_mediawallpost
	ADD CONSTRAINT wallposts_mediawallpost_wallpost_ptr_id_fkey FOREIGN KEY (wallpost_ptr_id) REFERENCES wallposts_wallpost(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE wallposts_mediawallpostphoto
	ADD CONSTRAINT wallposts_mediawallpostphoto_author_id_fkey FOREIGN KEY (author_id) REFERENCES members_member(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE wallposts_mediawallpostphoto
	ADD CONSTRAINT wallposts_mediawallpostphoto_editor_id_fkey FOREIGN KEY (editor_id) REFERENCES members_member(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE wallposts_mediawallpostphoto
	ADD CONSTRAINT wallposts_mediawallpostphoto_mediawallpost_id_fkey FOREIGN KEY (mediawallpost_id) REFERENCES wallposts_mediawallpost(wallpost_ptr_id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE wallposts_reaction
	ADD CONSTRAINT wallposts_reaction_author_id_fkey FOREIGN KEY (author_id) REFERENCES members_member(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE wallposts_reaction
	ADD CONSTRAINT wallposts_reaction_editor_id_fkey FOREIGN KEY (editor_id) REFERENCES members_member(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE wallposts_reaction
	ADD CONSTRAINT wallposts_reaction_wallpost_id_fkey FOREIGN KEY (wallpost_id) REFERENCES wallposts_wallpost(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE wallposts_systemwallpost
	ADD CONSTRAINT wallposts_systemwallpost_related_type_id_fkey FOREIGN KEY (related_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE wallposts_systemwallpost
	ADD CONSTRAINT wallposts_systemwallpost_wallpost_ptr_id_fkey FOREIGN KEY (wallpost_ptr_id) REFERENCES wallposts_wallpost(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE wallposts_textwallpost
	ADD CONSTRAINT wallposts_textwallpost_wallpost_ptr_id_fkey FOREIGN KEY (wallpost_ptr_id) REFERENCES wallposts_wallpost(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE wallposts_wallpost
	ADD CONSTRAINT wallposts_wallpost_author_id_fkey FOREIGN KEY (author_id) REFERENCES members_member(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE wallposts_wallpost
	ADD CONSTRAINT wallposts_wallpost_content_type_id_fkey FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE wallposts_wallpost
	ADD CONSTRAINT wallposts_wallpost_editor_id_fkey FOREIGN KEY (editor_id) REFERENCES members_member(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE wallposts_wallpost
	ADD CONSTRAINT wallposts_wallpost_polymorphic_ctype_id_fkey FOREIGN KEY (polymorphic_ctype_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;

CREATE INDEX members_member_user_permissions_member_id ON members_member_user_permissions USING btree (member_id);

--  NOW RENAME THE SCHEMA
ALTER SCHEMA public RENAME TO onepercent;



