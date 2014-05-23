--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: accounting_banktransaction; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE accounting_banktransaction (
    id integer NOT NULL,
    sender_account character varying(35) NOT NULL,
    currency character varying(3) NOT NULL,
    interest_date date NOT NULL,
    credit_debit character varying(1) NOT NULL,
    amount numeric(14,2) NOT NULL,
    counter_account character varying(35) NOT NULL,
    counter_name character varying(70) NOT NULL,
    book_date date NOT NULL,
    book_code character varying(2) NOT NULL,
    filler character varying(6) NOT NULL,
    description1 character varying(35) NOT NULL,
    description2 character varying(35) NOT NULL,
    description3 character varying(35) NOT NULL,
    description4 character varying(35) NOT NULL,
    description5 character varying(35) NOT NULL,
    description6 character varying(35) NOT NULL,
    end_to_end_id character varying(35) NOT NULL,
    id_recipient character varying(35) NOT NULL,
    mandate_id character varying(35) NOT NULL
);


--
-- Name: accounting_banktransaction_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE accounting_banktransaction_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: accounting_banktransaction_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE accounting_banktransaction_id_seq OWNED BY accounting_banktransaction.id;


--
-- Name: accounting_docdatapayment; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE accounting_docdatapayment (
    id integer NOT NULL,
    merchant_reference character varying(35) NOT NULL,
    triple_deal_reference integer NOT NULL,
    payment_type character varying(15) NOT NULL,
    amount_registered numeric(14,2) NOT NULL,
    currency_amount_registered character varying(3) NOT NULL,
    amount_collected numeric(14,2) NOT NULL,
    currency_amount_collected character varying(3) NOT NULL,
    tpcd numeric(14,2),
    currency_tpcd character varying(3) NOT NULL,
    tpci numeric(14,2),
    currency_tpci character varying(3) NOT NULL,
    docdata_fee numeric(14,2) NOT NULL,
    currency_docdata_fee character varying(3) NOT NULL,
    CONSTRAINT accounting_docdatapayment_triple_deal_reference_check CHECK ((triple_deal_reference >= 0))
);


--
-- Name: accounting_docdatapayment_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE accounting_docdatapayment_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: accounting_docdatapayment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE accounting_docdatapayment_id_seq OWNED BY accounting_docdatapayment.id;


--
-- Name: accounting_docdatapayout; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE accounting_docdatapayout (
    id integer NOT NULL,
    period_id integer NOT NULL,
    start_date date NOT NULL,
    end_date date NOT NULL,
    total numeric(14,2),
    CONSTRAINT accounting_docdatapayout_period_id_check CHECK ((period_id >= 0))
);


--
-- Name: accounting_docdatapayout_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE accounting_docdatapayout_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: accounting_docdatapayout_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE accounting_docdatapayout_id_seq OWNED BY accounting_docdatapayout.id;


--
-- Name: accounts_bluebottleuser; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE accounts_bluebottleuser (
    id integer NOT NULL,
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
    primary_language character varying(5) NOT NULL,
    share_time_knowledge boolean NOT NULL,
    share_money boolean NOT NULL,
    newsletter boolean NOT NULL,
    phone_number character varying(50) NOT NULL,
    gender character varying(6) NOT NULL,
    birthdate date,
    available_time text NOT NULL,
    contribution text NOT NULL
);


--
-- Name: accounts_bluebottleuser_groups; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE accounts_bluebottleuser_groups (
    id integer NOT NULL,
    bluebottleuser_id integer NOT NULL,
    group_id integer NOT NULL
);


--
-- Name: accounts_bluebottleuser_groups_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE accounts_bluebottleuser_groups_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: accounts_bluebottleuser_groups_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE accounts_bluebottleuser_groups_id_seq OWNED BY accounts_bluebottleuser_groups.id;


--
-- Name: accounts_bluebottleuser_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE accounts_bluebottleuser_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: accounts_bluebottleuser_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE accounts_bluebottleuser_id_seq OWNED BY accounts_bluebottleuser.id;


--
-- Name: accounts_bluebottleuser_user_permissions; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE accounts_bluebottleuser_user_permissions (
    id integer NOT NULL,
    bluebottleuser_id integer NOT NULL,
    permission_id integer NOT NULL
);


--
-- Name: accounts_bluebottleuser_user_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE accounts_bluebottleuser_user_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: accounts_bluebottleuser_user_permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE accounts_bluebottleuser_user_permissions_id_seq OWNED BY accounts_bluebottleuser_user_permissions.id;


--
-- Name: accounts_useraddress; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE accounts_useraddress (
    id integer NOT NULL,
    line1 character varying(100) NOT NULL,
    line2 character varying(100) NOT NULL,
    city character varying(100) NOT NULL,
    state character varying(100) NOT NULL,
    country_id integer,
    postal_code character varying(20) NOT NULL,
    address_type character varying(10) NOT NULL,
    user_id integer NOT NULL
);


--
-- Name: accounts_useraddress_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE accounts_useraddress_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: accounts_useraddress_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE accounts_useraddress_id_seq OWNED BY accounts_useraddress.id;


--
-- Name: admin_tools_dashboard_preferences; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE admin_tools_dashboard_preferences (
    id integer NOT NULL,
    user_id integer NOT NULL,
    data text NOT NULL,
    dashboard_id character varying(100) NOT NULL
);


--
-- Name: admin_tools_dashboard_preferences_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE admin_tools_dashboard_preferences_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: admin_tools_dashboard_preferences_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE admin_tools_dashboard_preferences_id_seq OWNED BY admin_tools_dashboard_preferences.id;


--
-- Name: admin_tools_menu_bookmark; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE admin_tools_menu_bookmark (
    id integer NOT NULL,
    user_id integer NOT NULL,
    url character varying(255) NOT NULL,
    title character varying(255) NOT NULL
);


--
-- Name: admin_tools_menu_bookmark_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE admin_tools_menu_bookmark_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: admin_tools_menu_bookmark_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE admin_tools_menu_bookmark_id_seq OWNED BY admin_tools_menu_bookmark.id;


--
-- Name: auth_group; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE auth_group (
    id integer NOT NULL,
    name character varying(80) NOT NULL
);


--
-- Name: auth_group_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE auth_group_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: auth_group_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE auth_group_id_seq OWNED BY auth_group.id;


--
-- Name: auth_group_permissions; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE auth_group_permissions (
    id integer NOT NULL,
    group_id integer NOT NULL,
    permission_id integer NOT NULL
);


--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE auth_group_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE auth_group_permissions_id_seq OWNED BY auth_group_permissions.id;


--
-- Name: auth_permission; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE auth_permission (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    content_type_id integer NOT NULL,
    codename character varying(100) NOT NULL
);


--
-- Name: auth_permission_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE auth_permission_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: auth_permission_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE auth_permission_id_seq OWNED BY auth_permission.id;


--
-- Name: banners_slide; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE banners_slide (
    id integer NOT NULL,
    title character varying(100) NOT NULL,
    slug character varying(50) NOT NULL,
    language character varying(5) NOT NULL,
    status character varying(20) NOT NULL,
    publication_date timestamp with time zone,
    publication_end_date timestamp with time zone,
    sequence integer NOT NULL,
    author_id integer NOT NULL,
    creation_date timestamp with time zone NOT NULL,
    modification_date timestamp with time zone NOT NULL,
    tab_text character varying(100) NOT NULL,
    body text NOT NULL,
    image character varying(255),
    background_image character varying(255),
    link_text character varying(400) NOT NULL,
    link_url character varying(400) NOT NULL,
    style character varying(40) NOT NULL,
    video_url character varying(100) NOT NULL
);


--
-- Name: banners_slide_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE banners_slide_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: banners_slide_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE banners_slide_id_seq OWNED BY banners_slide.id;


--
-- Name: blogs_blogcategory; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE blogs_blogcategory (
    id integer NOT NULL,
    title character varying(200) NOT NULL
);


--
-- Name: blogs_blogcategory_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE blogs_blogcategory_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: blogs_blogcategory_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE blogs_blogcategory_id_seq OWNED BY blogs_blogcategory.id;


--
-- Name: blogs_blogpost; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE blogs_blogpost (
    id integer NOT NULL,
    post_type character varying(20) NOT NULL,
    title character varying(200) NOT NULL,
    slug character varying(50) NOT NULL,
    main_image character varying(100) NOT NULL,
    language character varying(5) NOT NULL,
    status character varying(20) NOT NULL,
    publication_date timestamp with time zone,
    publication_end_date timestamp with time zone,
    allow_comments boolean NOT NULL,
    author_id integer NOT NULL,
    creation_date timestamp with time zone NOT NULL,
    modification_date timestamp with time zone NOT NULL
);


--
-- Name: blogs_blogpost_categories; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE blogs_blogpost_categories (
    id integer NOT NULL,
    blogpost_id integer NOT NULL,
    blogcategory_id integer NOT NULL
);


--
-- Name: blogs_blogpost_categories_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE blogs_blogpost_categories_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: blogs_blogpost_categories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE blogs_blogpost_categories_id_seq OWNED BY blogs_blogpost_categories.id;


--
-- Name: blogs_blogpost_countries; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE blogs_blogpost_countries (
    id integer NOT NULL,
    blogpost_id integer NOT NULL,
    country_id integer NOT NULL
);


--
-- Name: blogs_blogpost_countries_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE blogs_blogpost_countries_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: blogs_blogpost_countries_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE blogs_blogpost_countries_id_seq OWNED BY blogs_blogpost_countries.id;


--
-- Name: blogs_blogpost_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE blogs_blogpost_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: blogs_blogpost_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE blogs_blogpost_id_seq OWNED BY blogs_blogpost.id;


--
-- Name: campaigns_campaign; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE campaigns_campaign (
    id integer NOT NULL,
    title character varying(255) NOT NULL,
    start timestamp with time zone NOT NULL,
    "end" timestamp with time zone NOT NULL,
    target integer NOT NULL,
    currency character varying(10) NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    deleted timestamp with time zone,
    homepage character varying(255) NOT NULL,
    CONSTRAINT campaigns_campaign_target_check CHECK ((target >= 0))
);


--
-- Name: campaigns_campaign_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE campaigns_campaign_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: campaigns_campaign_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE campaigns_campaign_id_seq OWNED BY campaigns_campaign.id;


--
-- Name: celery_taskmeta; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE celery_taskmeta (
    id integer NOT NULL,
    task_id character varying(255) NOT NULL,
    status character varying(50) NOT NULL,
    result text,
    date_done timestamp with time zone NOT NULL,
    traceback text,
    hidden boolean NOT NULL,
    meta text
);


--
-- Name: celery_taskmeta_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE celery_taskmeta_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: celery_taskmeta_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE celery_taskmeta_id_seq OWNED BY celery_taskmeta.id;


--
-- Name: celery_tasksetmeta; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE celery_tasksetmeta (
    id integer NOT NULL,
    taskset_id character varying(255) NOT NULL,
    result text NOT NULL,
    date_done timestamp with time zone NOT NULL,
    hidden boolean NOT NULL
);


--
-- Name: celery_tasksetmeta_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE celery_tasksetmeta_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: celery_tasksetmeta_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE celery_tasksetmeta_id_seq OWNED BY celery_tasksetmeta.id;


--
-- Name: contentitem_contentplugins_pictureitem; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE contentitem_contentplugins_pictureitem (
    contentitem_ptr_id integer NOT NULL,
    image character varying(100) NOT NULL,
    align character varying(50) NOT NULL
);


--
-- Name: contentitem_oembeditem_oembeditem; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE contentitem_oembeditem_oembeditem (
    contentitem_ptr_id integer NOT NULL,
    embed_url character varying(200) NOT NULL,
    embed_max_width integer,
    embed_max_height integer,
    type character varying(20),
    url character varying(200),
    title character varying(512),
    description text,
    author_name character varying(255),
    author_url character varying(200),
    provider_name character varying(255),
    provider_url character varying(200),
    thumbnail_url character varying(200),
    thumbnail_height integer,
    thumbnail_width integer,
    height integer,
    width integer,
    html text,
    CONSTRAINT contentitem_oembeditem_oembeditem_embed_max_height_check CHECK ((embed_max_height >= 0)),
    CONSTRAINT contentitem_oembeditem_oembeditem_embed_max_width_check CHECK ((embed_max_width >= 0))
);


--
-- Name: contentitem_rawhtml_rawhtmlitem; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE contentitem_rawhtml_rawhtmlitem (
    contentitem_ptr_id integer NOT NULL,
    html text NOT NULL
);


--
-- Name: contentitem_text_textitem; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE contentitem_text_textitem (
    contentitem_ptr_id integer NOT NULL,
    text text NOT NULL
);


--
-- Name: cowry_docdata_docdatapayment; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE cowry_docdata_docdatapayment (
    id integer NOT NULL,
    polymorphic_ctype_id integer,
    status character varying(30) NOT NULL,
    docdata_payment_order_id integer NOT NULL,
    payment_id character varying(100) NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    payment_method character varying(60) NOT NULL
);


--
-- Name: cowry_docdata_docdatapayment_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE cowry_docdata_docdatapayment_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: cowry_docdata_docdatapayment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE cowry_docdata_docdatapayment_id_seq OWNED BY cowry_docdata_docdatapayment.id;


--
-- Name: cowry_docdata_docdatapaymentlogentry; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE cowry_docdata_docdatapaymentlogentry (
    id integer NOT NULL,
    message character varying(200) NOT NULL,
    level character varying(15) NOT NULL,
    "timestamp" timestamp with time zone NOT NULL,
    docdata_payment_order_id integer NOT NULL
);


--
-- Name: cowry_docdata_docdatapaymentlogentry_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE cowry_docdata_docdatapaymentlogentry_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: cowry_docdata_docdatapaymentlogentry_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE cowry_docdata_docdatapaymentlogentry_id_seq OWNED BY cowry_docdata_docdatapaymentlogentry.id;


--
-- Name: cowry_docdata_docdatapaymentorder; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE cowry_docdata_docdatapaymentorder (
    payment_ptr_id integer NOT NULL,
    merchant_order_reference character varying(100) NOT NULL,
    customer_id integer NOT NULL,
    email character varying(254) NOT NULL,
    first_name character varying(200) NOT NULL,
    last_name character varying(200) NOT NULL,
    address character varying(200) NOT NULL,
    postal_code character varying(20) NOT NULL,
    city character varying(200) NOT NULL,
    country character varying(2) NOT NULL,
    language character varying(2) NOT NULL,
    payment_order_id character varying(200) NOT NULL,
    CONSTRAINT ck_customer_id_pstv_2bd95f391a5c70fc CHECK ((customer_id >= 0))
);


--
-- Name: cowry_docdata_docdatawebdirectdirectdebit; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE cowry_docdata_docdatawebdirectdirectdebit (
    docdatapayment_ptr_id integer NOT NULL,
    account_name character varying(35) NOT NULL,
    account_city character varying(35) NOT NULL,
    iban character varying(34) NOT NULL,
    bic character varying(11) NOT NULL
);


--
-- Name: cowry_payment; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE cowry_payment (
    id integer NOT NULL,
    polymorphic_ctype_id integer,
    amount integer NOT NULL,
    currency character varying(3) NOT NULL,
    fee integer NOT NULL,
    payment_method_id character varying(20) NOT NULL,
    payment_submethod_id character varying(20) NOT NULL,
    status character varying(15) NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    order_id integer NOT NULL,
    CONSTRAINT cowry_payment_amount_check CHECK ((amount >= 0)),
    CONSTRAINT cowry_payment_fee_check CHECK ((fee >= 0))
);


--
-- Name: cowry_payment_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE cowry_payment_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: cowry_payment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE cowry_payment_id_seq OWNED BY cowry_payment.id;


--
-- Name: django_admin_log; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE django_admin_log (
    id integer NOT NULL,
    action_time timestamp with time zone NOT NULL,
    user_id integer NOT NULL,
    content_type_id integer,
    object_id text,
    object_repr character varying(200) NOT NULL,
    action_flag smallint NOT NULL,
    change_message text NOT NULL,
    CONSTRAINT django_admin_log_action_flag_check CHECK ((action_flag >= 0))
);


--
-- Name: django_admin_log_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE django_admin_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: django_admin_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE django_admin_log_id_seq OWNED BY django_admin_log.id;


--
-- Name: django_content_type; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE django_content_type (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    app_label character varying(100) NOT NULL,
    model character varying(100) NOT NULL
);


--
-- Name: django_content_type_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE django_content_type_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: django_content_type_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE django_content_type_id_seq OWNED BY django_content_type.id;


--
-- Name: django_redirect; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE django_redirect (
    id integer NOT NULL,
    old_path character varying(200) NOT NULL,
    new_path character varying(200) NOT NULL,
    regular_expression boolean NOT NULL,
    fallback_redirect boolean NOT NULL,
    nr_times_visited integer NOT NULL
);


--
-- Name: django_redirect_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE django_redirect_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: django_redirect_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE django_redirect_id_seq OWNED BY django_redirect.id;


--
-- Name: django_session; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE django_session (
    session_key character varying(40) NOT NULL,
    session_data text NOT NULL,
    expire_date timestamp with time zone NOT NULL
);


--
-- Name: django_site; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE django_site (
    id integer NOT NULL,
    domain character varying(100) NOT NULL,
    name character varying(50) NOT NULL
);


--
-- Name: django_site_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE django_site_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: django_site_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE django_site_id_seq OWNED BY django_site.id;


--
-- Name: djcelery_crontabschedule; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE djcelery_crontabschedule (
    id integer NOT NULL,
    minute character varying(64) NOT NULL,
    hour character varying(64) NOT NULL,
    day_of_week character varying(64) NOT NULL,
    day_of_month character varying(64) NOT NULL,
    month_of_year character varying(64) NOT NULL
);


--
-- Name: djcelery_crontabschedule_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE djcelery_crontabschedule_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: djcelery_crontabschedule_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE djcelery_crontabschedule_id_seq OWNED BY djcelery_crontabschedule.id;


--
-- Name: djcelery_intervalschedule; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE djcelery_intervalschedule (
    id integer NOT NULL,
    every integer NOT NULL,
    period character varying(24) NOT NULL
);


--
-- Name: djcelery_intervalschedule_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE djcelery_intervalschedule_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: djcelery_intervalschedule_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE djcelery_intervalschedule_id_seq OWNED BY djcelery_intervalschedule.id;


--
-- Name: djcelery_periodictask; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE djcelery_periodictask (
    id integer NOT NULL,
    name character varying(200) NOT NULL,
    task character varying(200) NOT NULL,
    interval_id integer,
    crontab_id integer,
    args text NOT NULL,
    kwargs text NOT NULL,
    queue character varying(200),
    exchange character varying(200),
    routing_key character varying(200),
    expires timestamp with time zone,
    enabled boolean NOT NULL,
    last_run_at timestamp with time zone,
    total_run_count integer NOT NULL,
    date_changed timestamp with time zone NOT NULL,
    description text NOT NULL,
    CONSTRAINT djcelery_periodictask_total_run_count_check CHECK ((total_run_count >= 0))
);


--
-- Name: djcelery_periodictask_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE djcelery_periodictask_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: djcelery_periodictask_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE djcelery_periodictask_id_seq OWNED BY djcelery_periodictask.id;


--
-- Name: djcelery_periodictasks; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE djcelery_periodictasks (
    ident smallint NOT NULL,
    last_update timestamp with time zone NOT NULL
);


--
-- Name: djcelery_taskstate; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE djcelery_taskstate (
    id integer NOT NULL,
    state character varying(64) NOT NULL,
    task_id character varying(36) NOT NULL,
    name character varying(200),
    tstamp timestamp with time zone NOT NULL,
    args text,
    kwargs text,
    eta timestamp with time zone,
    expires timestamp with time zone,
    result text,
    traceback text,
    runtime double precision,
    retries integer NOT NULL,
    worker_id integer,
    hidden boolean NOT NULL
);


--
-- Name: djcelery_taskstate_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE djcelery_taskstate_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: djcelery_taskstate_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE djcelery_taskstate_id_seq OWNED BY djcelery_taskstate.id;


--
-- Name: djcelery_workerstate; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE djcelery_workerstate (
    id integer NOT NULL,
    hostname character varying(255) NOT NULL,
    last_heartbeat timestamp with time zone
);


--
-- Name: djcelery_workerstate_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE djcelery_workerstate_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: djcelery_workerstate_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE djcelery_workerstate_id_seq OWNED BY djcelery_workerstate.id;


--
-- Name: fluent_contents_contentitem; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE fluent_contents_contentitem (
    id integer NOT NULL,
    polymorphic_ctype_id integer,
    parent_type_id integer NOT NULL,
    parent_id integer,
    placeholder_id integer,
    sort_order integer NOT NULL
);


--
-- Name: fluent_contents_contentitem_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE fluent_contents_contentitem_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: fluent_contents_contentitem_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE fluent_contents_contentitem_id_seq OWNED BY fluent_contents_contentitem.id;


--
-- Name: fluent_contents_placeholder; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE fluent_contents_placeholder (
    id integer NOT NULL,
    slot character varying(50) NOT NULL,
    role character varying(1) NOT NULL,
    parent_type_id integer,
    parent_id integer,
    title character varying(255) NOT NULL
);


--
-- Name: fluent_contents_placeholder_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE fluent_contents_placeholder_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: fluent_contents_placeholder_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE fluent_contents_placeholder_id_seq OWNED BY fluent_contents_placeholder.id;


--
-- Name: fund_donation; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE fund_donation (
    id integer NOT NULL,
    amount integer NOT NULL,
    currency character varying(3) NOT NULL,
    user_id integer,
    project_id integer NOT NULL,
    status character varying(20) NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    donation_type character varying(20) NOT NULL,
    order_id integer,
    ready timestamp with time zone,
    fundraiser_id integer,
    voucher_id integer,
    CONSTRAINT fund_donation_amount_check CHECK ((amount >= 0))
);


--
-- Name: fund_donation_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE fund_donation_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: fund_donation_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE fund_donation_id_seq OWNED BY fund_donation.id;


--
-- Name: fund_order; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE fund_order (
    id integer NOT NULL,
    user_id integer,
    status character varying(20) NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    recurring boolean NOT NULL,
    order_number character varying(30) NOT NULL,
    closed timestamp with time zone
);


--
-- Name: fund_order_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE fund_order_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: fund_order_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE fund_order_id_seq OWNED BY fund_order.id;


--
-- Name: fund_recurringdirectdebitpayment; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE fund_recurringdirectdebitpayment (
    id integer NOT NULL,
    user_id integer NOT NULL,
    active boolean NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    name character varying(35) NOT NULL,
    city character varying(35) NOT NULL,
    account character varying(10) NOT NULL,
    amount integer NOT NULL,
    currency character varying(3) NOT NULL,
    iban character varying(34) NOT NULL,
    bic character varying(11) NOT NULL,
    manually_process boolean NOT NULL,
    CONSTRAINT ck_amount_pstv_4b157c3c84570908 CHECK ((amount >= 0)),
    CONSTRAINT fund_recurringdirectdebitpayment_amount_check CHECK ((amount >= 0))
);


--
-- Name: fund_recurringdirectdebitpayment_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE fund_recurringdirectdebitpayment_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: fund_recurringdirectdebitpayment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE fund_recurringdirectdebitpayment_id_seq OWNED BY fund_recurringdirectdebitpayment.id;


--
-- Name: fundraisers_fundraiser; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE fundraisers_fundraiser (
    id integer NOT NULL,
    owner_id integer NOT NULL,
    project_id integer NOT NULL,
    title character varying(255) NOT NULL,
    description text NOT NULL,
    image character varying(255),
    video_url character varying(100) NOT NULL,
    amount integer NOT NULL,
    deadline timestamp with time zone,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    currency character varying(10) NOT NULL,
    deleted timestamp with time zone,
    CONSTRAINT fundraisers_fundraiser_amount_check CHECK ((amount >= 0))
);


--
-- Name: fundraisers_fundraiser_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE fundraisers_fundraiser_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: fundraisers_fundraiser_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE fundraisers_fundraiser_id_seq OWNED BY fundraisers_fundraiser.id;


--
-- Name: geo_country; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE geo_country (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    numeric_code character varying(3) NOT NULL,
    subregion_id integer NOT NULL,
    alpha2_code character varying(2) NOT NULL,
    alpha3_code character varying(3) NOT NULL,
    oda_recipient boolean NOT NULL
);


--
-- Name: geo_country_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE geo_country_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: geo_country_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE geo_country_id_seq OWNED BY geo_country.id;


--
-- Name: geo_region; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE geo_region (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    numeric_code character varying(3) NOT NULL
);


--
-- Name: geo_region_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE geo_region_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: geo_region_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE geo_region_id_seq OWNED BY geo_region.id;


--
-- Name: geo_subregion; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE geo_subregion (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    numeric_code character varying(3) NOT NULL,
    region_id integer NOT NULL
);


--
-- Name: geo_subregion_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE geo_subregion_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: geo_subregion_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE geo_subregion_id_seq OWNED BY geo_subregion.id;


--
-- Name: love_lovedeclaration; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE love_lovedeclaration (
    id integer NOT NULL,
    content_type_id integer NOT NULL,
    object_id integer NOT NULL,
    creation_date timestamp with time zone NOT NULL,
    user_id integer NOT NULL,
    CONSTRAINT love_lovedeclaration_object_id_check CHECK ((object_id >= 0))
);


--
-- Name: love_lovedeclaration_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE love_lovedeclaration_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: love_lovedeclaration_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE love_lovedeclaration_id_seq OWNED BY love_lovedeclaration.id;


--
-- Name: organizations_organization; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE organizations_organization (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    slug character varying(100) NOT NULL,
    description text NOT NULL,
    phone_number character varying(40) NOT NULL,
    website character varying(200) NOT NULL,
    email character varying(75) NOT NULL,
    twitter character varying(255) NOT NULL,
    facebook character varying(255) NOT NULL,
    skype character varying(255) NOT NULL,
    legal_status character varying(255) NOT NULL,
    registration character varying(100),
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    deleted timestamp with time zone,
    partner_organizations text NOT NULL,
    account_bank_name character varying(255) NOT NULL,
    account_bank_address character varying(255) NOT NULL,
    account_bank_country_id integer,
    account_iban character varying(34) NOT NULL,
    account_bic character varying(11) NOT NULL,
    account_number character varying(255) NOT NULL,
    account_name character varying(255) NOT NULL,
    account_city character varying(255) NOT NULL,
    account_other character varying(255) NOT NULL,
    address_line1 character varying(100) NOT NULL,
    address_line2 character varying(100) NOT NULL,
    city character varying(100) NOT NULL,
    state character varying(100) NOT NULL,
    country_id integer,
    postal_code character varying(20) NOT NULL
);


--
-- Name: organizations_organization_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE organizations_organization_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: organizations_organization_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE organizations_organization_id_seq OWNED BY organizations_organization.id;


--
-- Name: organizations_organizationdocument; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE organizations_organizationdocument (
    id integer NOT NULL,
    organization_id integer NOT NULL,
    file character varying(100) NOT NULL,
    author_id integer
);


--
-- Name: organizations_organizationdocument_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE organizations_organizationdocument_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: organizations_organizationdocument_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE organizations_organizationdocument_id_seq OWNED BY organizations_organizationdocument.id;


--
-- Name: organizations_organizationmember; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE organizations_organizationmember (
    id integer NOT NULL,
    organization_id integer NOT NULL,
    user_id integer NOT NULL,
    function character varying(20) NOT NULL
);


--
-- Name: organizations_organizationmember_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE organizations_organizationmember_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: organizations_organizationmember_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE organizations_organizationmember_id_seq OWNED BY organizations_organizationmember.id;


--
-- Name: pages_contactmessage; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE pages_contactmessage (
    id integer NOT NULL,
    status character varying(20) NOT NULL,
    author_id integer,
    name character varying(200) NOT NULL,
    email character varying(200) NOT NULL,
    message text NOT NULL,
    creation_date timestamp with time zone NOT NULL,
    modification_date timestamp with time zone NOT NULL
);


--
-- Name: pages_contactmessage_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE pages_contactmessage_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: pages_contactmessage_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE pages_contactmessage_id_seq OWNED BY pages_contactmessage.id;


--
-- Name: pages_page; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE pages_page (
    id integer NOT NULL,
    title character varying(200) NOT NULL,
    slug character varying(50) NOT NULL,
    language character varying(5) NOT NULL,
    status character varying(20) NOT NULL,
    publication_date timestamp with time zone,
    publication_end_date timestamp with time zone,
    author_id integer NOT NULL,
    creation_date timestamp with time zone NOT NULL,
    modification_date timestamp with time zone NOT NULL
);


--
-- Name: pages_page_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE pages_page_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: pages_page_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE pages_page_id_seq OWNED BY pages_page.id;


--
-- Name: payouts_bankmutation; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE payouts_bankmutation (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    mut_file character varying(100),
    mutations text NOT NULL
);


--
-- Name: payouts_bankmutation_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE payouts_bankmutation_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: payouts_bankmutation_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE payouts_bankmutation_id_seq OWNED BY payouts_bankmutation.id;


--
-- Name: payouts_bankmutationline; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE payouts_bankmutationline (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    bank_mutation_id integer NOT NULL,
    issuer_account_number character varying(100) NOT NULL,
    currency character varying(3) NOT NULL,
    start_date date NOT NULL,
    dc character varying(1) NOT NULL,
    amount numeric(15,2) NOT NULL,
    account_number character varying(100) NOT NULL,
    account_name character varying(100) NOT NULL,
    transaction_type character varying(10) NOT NULL,
    invoice_reference character varying(100) NOT NULL,
    description_line1 character varying(100) NOT NULL,
    description_line2 character varying(100) NOT NULL,
    description_line3 character varying(100) NOT NULL,
    description_line4 character varying(100) NOT NULL,
    payout_id integer
);


--
-- Name: payouts_bankmutationline_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE payouts_bankmutationline_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: payouts_bankmutationline_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE payouts_bankmutationline_id_seq OWNED BY payouts_bankmutationline.id;


--
-- Name: payouts_organizationpayout; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE payouts_organizationpayout (
    id integer NOT NULL,
    invoice_reference character varying(100) NOT NULL,
    completed date,
    planned date NOT NULL,
    status character varying(20) NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    start_date date NOT NULL,
    end_date date NOT NULL,
    organization_fee_excl numeric(12,2) NOT NULL,
    organization_fee_vat numeric(12,2) NOT NULL,
    organization_fee_incl numeric(12,2) NOT NULL,
    psp_fee_excl numeric(12,2) NOT NULL,
    psp_fee_vat numeric(12,2) NOT NULL,
    psp_fee_incl numeric(12,2) NOT NULL,
    other_costs_excl numeric(12,2) NOT NULL,
    other_costs_vat numeric(12,2) NOT NULL,
    other_costs_incl numeric(12,2) NOT NULL,
    payable_amount_excl numeric(12,2) NOT NULL,
    payable_amount_vat numeric(12,2) NOT NULL,
    payable_amount_incl numeric(12,2) NOT NULL
);


--
-- Name: payouts_organizationpayout_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE payouts_organizationpayout_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: payouts_organizationpayout_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE payouts_organizationpayout_id_seq OWNED BY payouts_organizationpayout.id;


--
-- Name: payouts_payout; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE payouts_payout (
    id integer NOT NULL,
    planned date NOT NULL,
    project_id integer NOT NULL,
    status character varying(20) NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    amount_payable numeric(12,2) DEFAULT 0.00 NOT NULL,
    sender_account_number character varying(100) NOT NULL,
    receiver_account_number character varying(100) NOT NULL,
    receiver_account_iban character varying(100) NOT NULL,
    receiver_account_bic character varying(100) NOT NULL,
    receiver_account_name character varying(100) NOT NULL,
    receiver_account_city character varying(100) NOT NULL,
    receiver_account_country character varying(100),
    invoice_reference character varying(100) NOT NULL,
    description_line1 character varying(100) NOT NULL,
    description_line2 character varying(100) NOT NULL,
    description_line3 character varying(100) NOT NULL,
    description_line4 character varying(100) NOT NULL,
    payout_rule character varying(20) NOT NULL,
    amount_raised numeric(12,2) NOT NULL,
    organization_fee numeric(12,2) NOT NULL,
    completed date
);


--
-- Name: payouts_payout_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE payouts_payout_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: payouts_payout_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE payouts_payout_id_seq OWNED BY payouts_payout.id;


--
-- Name: projects_partnerorganization; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE projects_partnerorganization (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    slug character varying(100) NOT NULL,
    description text NOT NULL,
    image character varying(255)
);


--
-- Name: projects_partnerorganization_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE projects_partnerorganization_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: projects_partnerorganization_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE projects_partnerorganization_id_seq OWNED BY projects_partnerorganization.id;


--
-- Name: projects_project; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE projects_project (
    id integer NOT NULL,
    owner_id integer NOT NULL,
    coach_id integer,
    title character varying(255) NOT NULL,
    slug character varying(100) NOT NULL,
    phase character varying(20) NOT NULL,
    partner_organization_id integer,
    created timestamp with time zone NOT NULL,
    popularity double precision,
    updated timestamp with time zone NOT NULL,
    is_campaign boolean NOT NULL
);


--
-- Name: projects_project_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE projects_project_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: projects_project_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE projects_project_id_seq OWNED BY projects_project.id;


--
-- Name: projects_projectambassador; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE projects_projectambassador (
    id integer NOT NULL,
    project_plan_id integer NOT NULL,
    name character varying(255) NOT NULL,
    email character varying(75) NOT NULL,
    description text NOT NULL
);


--
-- Name: projects_projectambassador_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE projects_projectambassador_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: projects_projectambassador_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE projects_projectambassador_id_seq OWNED BY projects_projectambassador.id;


--
-- Name: projects_projectbudgetline; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE projects_projectbudgetline (
    id integer NOT NULL,
    project_plan_id integer NOT NULL,
    description character varying(255) NOT NULL,
    currency character varying(3) NOT NULL,
    amount integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    CONSTRAINT projects_projectbudgetline_amount_check CHECK ((amount >= 0))
);


--
-- Name: projects_projectbudgetline_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE projects_projectbudgetline_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: projects_projectbudgetline_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE projects_projectbudgetline_id_seq OWNED BY projects_projectbudgetline.id;


--
-- Name: projects_projectcampaign; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE projects_projectcampaign (
    id integer NOT NULL,
    project_id integer NOT NULL,
    status character varying(20) NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    currency character varying(10) NOT NULL,
    money_asked integer NOT NULL,
    deadline timestamp with time zone,
    money_donated integer NOT NULL,
    money_needed integer NOT NULL,
    payout_date timestamp with time zone,
    CONSTRAINT ck_money_donated_pstv_24a9c1460d185ff9 CHECK ((money_donated >= 0)),
    CONSTRAINT ck_money_needed_pstv_482443bfe589ecba CHECK ((money_needed >= 0)),
    CONSTRAINT projects_projectcampaign_money_asked_check CHECK ((money_asked >= 0)),
    CONSTRAINT projects_projectcampaign_money_donated_check CHECK ((money_donated >= 0)),
    CONSTRAINT projects_projectcampaign_money_needed_check CHECK ((money_needed >= 0))
);


--
-- Name: projects_projectcampaign_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE projects_projectcampaign_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: projects_projectcampaign_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE projects_projectcampaign_id_seq OWNED BY projects_projectcampaign.id;


--
-- Name: projects_projectphaselog; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE projects_projectphaselog (
    id integer NOT NULL,
    project_id integer NOT NULL,
    phase character varying(20) NOT NULL,
    created timestamp with time zone NOT NULL
);


--
-- Name: projects_projectphaselog_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE projects_projectphaselog_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: projects_projectphaselog_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE projects_projectphaselog_id_seq OWNED BY projects_projectphaselog.id;


--
-- Name: projects_projectpitch; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE projects_projectpitch (
    id integer NOT NULL,
    project_id integer NOT NULL,
    status character varying(20) NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    title character varying(100) NOT NULL,
    pitch text NOT NULL,
    description text NOT NULL,
    need character varying(20),
    theme_id integer,
    latitude numeric(21,18),
    longitude numeric(21,18),
    country_id integer,
    image character varying(255),
    video_url character varying(100) NOT NULL
);


--
-- Name: projects_projectpitch_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE projects_projectpitch_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: projects_projectpitch_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE projects_projectpitch_id_seq OWNED BY projects_projectpitch.id;


--
-- Name: projects_projectplan; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE projects_projectplan (
    id integer NOT NULL,
    project_id integer NOT NULL,
    status character varying(20) NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    title character varying(100) NOT NULL,
    pitch text NOT NULL,
    need character varying(20),
    theme_id integer,
    description text NOT NULL,
    effects text NOT NULL,
    for_who text NOT NULL,
    future text NOT NULL,
    reach integer,
    latitude numeric(21,18),
    longitude numeric(21,18),
    country_id integer,
    image character varying(255) NOT NULL,
    video_url character varying(100),
    organization_id integer,
    money_needed text NOT NULL,
    campaign text NOT NULL,
    CONSTRAINT projects_projectplan_reach_check CHECK ((reach >= 0))
);


--
-- Name: projects_projectplan_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE projects_projectplan_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: projects_projectplan_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE projects_projectplan_id_seq OWNED BY projects_projectplan.id;


--
-- Name: projects_projectresult; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE projects_projectresult (
    id integer NOT NULL,
    project_id integer NOT NULL,
    status character varying(20) NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL
);


--
-- Name: projects_projectresult_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE projects_projectresult_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: projects_projectresult_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE projects_projectresult_id_seq OWNED BY projects_projectresult.id;


--
-- Name: projects_projecttheme; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE projects_projecttheme (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    slug character varying(100) NOT NULL,
    description text NOT NULL,
    name_nl character varying(100) NOT NULL
);


--
-- Name: projects_projecttheme_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE projects_projecttheme_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: projects_projecttheme_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE projects_projecttheme_id_seq OWNED BY projects_projecttheme.id;


--
-- Name: quotes_quote; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE quotes_quote (
    id integer NOT NULL,
    language character varying(5) NOT NULL,
    quote text NOT NULL,
    segment character varying(20) NOT NULL,
    status character varying(20) NOT NULL,
    publication_date timestamp with time zone,
    publication_end_date timestamp with time zone,
    author_id integer NOT NULL,
    user_id integer NOT NULL,
    creation_date timestamp with time zone NOT NULL,
    modification_date timestamp with time zone NOT NULL
);


--
-- Name: quotes_quote_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE quotes_quote_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: quotes_quote_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE quotes_quote_id_seq OWNED BY quotes_quote.id;


--
-- Name: registration_registrationprofile; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE registration_registrationprofile (
    id integer NOT NULL,
    user_id integer NOT NULL,
    activation_key character varying(40) NOT NULL
);


--
-- Name: registration_registrationprofile_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE registration_registrationprofile_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: registration_registrationprofile_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE registration_registrationprofile_id_seq OWNED BY registration_registrationprofile.id;


--
-- Name: social_auth_association; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE social_auth_association (
    id integer NOT NULL,
    server_url character varying(255) NOT NULL,
    handle character varying(255) NOT NULL,
    secret character varying(255) NOT NULL,
    issued integer NOT NULL,
    lifetime integer NOT NULL,
    assoc_type character varying(64) NOT NULL
);


--
-- Name: social_auth_association_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE social_auth_association_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: social_auth_association_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE social_auth_association_id_seq OWNED BY social_auth_association.id;


--
-- Name: social_auth_nonce; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE social_auth_nonce (
    id integer NOT NULL,
    server_url character varying(255) NOT NULL,
    "timestamp" integer NOT NULL,
    salt character varying(40) NOT NULL
);


--
-- Name: social_auth_nonce_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE social_auth_nonce_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: social_auth_nonce_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE social_auth_nonce_id_seq OWNED BY social_auth_nonce.id;


--
-- Name: social_auth_usersocialauth; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE social_auth_usersocialauth (
    id integer NOT NULL,
    user_id integer NOT NULL,
    provider character varying(32) NOT NULL,
    uid character varying(255) NOT NULL,
    extra_data text NOT NULL
);


--
-- Name: social_auth_usersocialauth_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE social_auth_usersocialauth_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: social_auth_usersocialauth_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE social_auth_usersocialauth_id_seq OWNED BY social_auth_usersocialauth.id;


--
-- Name: south_migrationhistory; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE south_migrationhistory (
    id integer NOT NULL,
    app_name character varying(255) NOT NULL,
    migration character varying(255) NOT NULL,
    applied timestamp with time zone NOT NULL
);


--
-- Name: south_migrationhistory_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE south_migrationhistory_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: south_migrationhistory_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE south_migrationhistory_id_seq OWNED BY south_migrationhistory.id;


--
-- Name: statistics_statistic; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE statistics_statistic (
    id integer NOT NULL,
    lives_changed integer NOT NULL,
    projects integer NOT NULL,
    countries integer NOT NULL,
    hours_spent integer NOT NULL,
    creation_date timestamp with time zone NOT NULL
);


--
-- Name: statistics_statistic_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE statistics_statistic_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: statistics_statistic_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE statistics_statistic_id_seq OWNED BY statistics_statistic.id;


--
-- Name: taggit_tag; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE taggit_tag (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    slug character varying(100) NOT NULL
);


--
-- Name: taggit_tag_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE taggit_tag_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: taggit_tag_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE taggit_tag_id_seq OWNED BY taggit_tag.id;


--
-- Name: taggit_taggeditem; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE taggit_taggeditem (
    id integer NOT NULL,
    tag_id integer NOT NULL,
    object_id integer NOT NULL,
    content_type_id integer NOT NULL
);


--
-- Name: taggit_taggeditem_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE taggit_taggeditem_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: taggit_taggeditem_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE taggit_taggeditem_id_seq OWNED BY taggit_taggeditem.id;


--
-- Name: tasks_skill; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE tasks_skill (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    name_nl character varying(100) NOT NULL,
    description text NOT NULL
);


--
-- Name: tasks_skill_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE tasks_skill_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: tasks_skill_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE tasks_skill_id_seq OWNED BY tasks_skill.id;


--
-- Name: tasks_task; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE tasks_task (
    id integer NOT NULL,
    title character varying(100) NOT NULL,
    description text NOT NULL,
    end_goal text NOT NULL,
    location character varying(200) NOT NULL,
    expertise character varying(200) NOT NULL,
    time_needed character varying(200) NOT NULL,
    status character varying(20) NOT NULL,
    people_needed integer NOT NULL,
    project_id integer NOT NULL,
    author_id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    deadline timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    skill_id integer,
    date_status_change timestamp with time zone,
    CONSTRAINT tasks_task_people_needed_check CHECK ((people_needed >= 0))
);


--
-- Name: tasks_task_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE tasks_task_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: tasks_task_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE tasks_task_id_seq OWNED BY tasks_task.id;


--
-- Name: tasks_taskfile; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE tasks_taskfile (
    id integer NOT NULL,
    task_id integer NOT NULL,
    author_id integer NOT NULL,
    title character varying(255) NOT NULL,
    file character varying(100) NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL
);


--
-- Name: tasks_taskfile_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE tasks_taskfile_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: tasks_taskfile_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE tasks_taskfile_id_seq OWNED BY tasks_taskfile.id;


--
-- Name: tasks_taskmember; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE tasks_taskmember (
    id integer NOT NULL,
    task_id integer NOT NULL,
    member_id integer NOT NULL,
    status character varying(20) NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    motivation text NOT NULL,
    comment text NOT NULL
);


--
-- Name: tasks_taskmember_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE tasks_taskmember_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: tasks_taskmember_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE tasks_taskmember_id_seq OWNED BY tasks_taskmember.id;


--
-- Name: tests_childsluggedtestmodel; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE tests_childsluggedtestmodel (
    sluggedtestmodel_ptr_id integer NOT NULL
);


--
-- Name: tests_name; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE tests_name (
    id integer NOT NULL,
    name character varying(50) NOT NULL
);


--
-- Name: tests_name_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE tests_name_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: tests_name_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE tests_name_id_seq OWNED BY tests_name.id;


--
-- Name: tests_note; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE tests_note (
    id integer NOT NULL,
    note text NOT NULL
);


--
-- Name: tests_note_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE tests_note_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: tests_note_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE tests_note_id_seq OWNED BY tests_note.id;


--
-- Name: tests_person; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE tests_person (
    id integer NOT NULL,
    name_id integer NOT NULL,
    age integer NOT NULL,
    CONSTRAINT tests_person_age_check CHECK ((age >= 0))
);


--
-- Name: tests_person_children; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE tests_person_children (
    id integer NOT NULL,
    from_person_id integer NOT NULL,
    to_person_id integer NOT NULL
);


--
-- Name: tests_person_children_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE tests_person_children_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: tests_person_children_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE tests_person_children_id_seq OWNED BY tests_person_children.id;


--
-- Name: tests_person_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE tests_person_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: tests_person_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE tests_person_id_seq OWNED BY tests_person.id;


--
-- Name: tests_person_notes; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE tests_person_notes (
    id integer NOT NULL,
    person_id integer NOT NULL,
    note_id integer NOT NULL
);


--
-- Name: tests_person_notes_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE tests_person_notes_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: tests_person_notes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE tests_person_notes_id_seq OWNED BY tests_person_notes.id;


--
-- Name: tests_secret; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE tests_secret (
    id integer NOT NULL
);


--
-- Name: tests_secret_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE tests_secret_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: tests_secret_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE tests_secret_id_seq OWNED BY tests_secret.id;


--
-- Name: tests_sluggedtestmodel; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE tests_sluggedtestmodel (
    id integer NOT NULL,
    title character varying(42) NOT NULL,
    slug character varying(50) NOT NULL
);


--
-- Name: tests_sluggedtestmodel_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE tests_sluggedtestmodel_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: tests_sluggedtestmodel_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE tests_sluggedtestmodel_id_seq OWNED BY tests_sluggedtestmodel.id;


--
-- Name: tests_testagregatemodel; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE tests_testagregatemodel (
    testmodel_pk_ptr_id character varying(36) NOT NULL,
    a integer NOT NULL
);


--
-- Name: tests_testmanytomanymodel; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE tests_testmanytomanymodel (
    testmodel_pk_ptr_id character varying(36) NOT NULL
);


--
-- Name: tests_testmanytomanymodel_many; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE tests_testmanytomanymodel_many (
    id integer NOT NULL,
    testmanytomanymodel_id character varying(36) NOT NULL,
    testmodel_field_id integer NOT NULL
);


--
-- Name: tests_testmanytomanymodel_many_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE tests_testmanytomanymodel_many_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: tests_testmanytomanymodel_many_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE tests_testmanytomanymodel_many_id_seq OWNED BY tests_testmanytomanymodel_many.id;


--
-- Name: tests_testmodel; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE tests_testmodel (
    id integer NOT NULL,
    a integer NOT NULL,
    j_field text NOT NULL
);


--
-- Name: tests_testmodel_field; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE tests_testmodel_field (
    id integer NOT NULL,
    a integer NOT NULL,
    uuid_field character varying(36) NOT NULL
);


--
-- Name: tests_testmodel_field_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE tests_testmodel_field_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: tests_testmodel_field_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE tests_testmodel_field_id_seq OWNED BY tests_testmodel_field.id;


--
-- Name: tests_testmodel_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE tests_testmodel_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: tests_testmodel_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE tests_testmodel_id_seq OWNED BY tests_testmodel.id;


--
-- Name: tests_testmodel_pk; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE tests_testmodel_pk (
    uuid_field character varying(36) NOT NULL
);


--
-- Name: thumbnail_kvstore; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE thumbnail_kvstore (
    key character varying(200) NOT NULL,
    value text NOT NULL
);


--
-- Name: vouchers_customvoucherrequest; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE vouchers_customvoucherrequest (
    id integer NOT NULL,
    value character varying(100) NOT NULL,
    number integer NOT NULL,
    contact_id integer,
    contact_name character varying(100) NOT NULL,
    contact_email character varying(75) NOT NULL,
    contact_phone character varying(100) NOT NULL,
    organization character varying(200) NOT NULL,
    message text NOT NULL,
    type character varying(20) NOT NULL,
    status character varying(20) NOT NULL,
    created timestamp with time zone NOT NULL,
    CONSTRAINT fund_customvoucherrequest_number_check CHECK ((number >= 0))
);


--
-- Name: vouchers_customvoucherrequest_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE vouchers_customvoucherrequest_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: vouchers_customvoucherrequest_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE vouchers_customvoucherrequest_id_seq OWNED BY vouchers_customvoucherrequest.id;


--
-- Name: vouchers_voucher; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE vouchers_voucher (
    id integer NOT NULL,
    amount integer NOT NULL,
    currency character varying(3) NOT NULL,
    language character varying(2) NOT NULL,
    message text NOT NULL,
    code character varying(100) NOT NULL,
    status character varying(20) NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    sender_id integer,
    sender_email character varying(75) NOT NULL,
    sender_name character varying(100) NOT NULL,
    receiver_id integer,
    receiver_email character varying(75) NOT NULL,
    receiver_name character varying(100) NOT NULL,
    order_id integer,
    CONSTRAINT fund_voucher_amount_check CHECK ((amount >= 0))
);


--
-- Name: vouchers_voucher_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE vouchers_voucher_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: vouchers_voucher_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE vouchers_voucher_id_seq OWNED BY vouchers_voucher.id;


--
-- Name: wallposts_mediawallpost; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE wallposts_mediawallpost (
    wallpost_ptr_id integer NOT NULL,
    title character varying(60) NOT NULL,
    text text NOT NULL,
    video_url character varying(100) NOT NULL
);


--
-- Name: wallposts_mediawallpostphoto; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE wallposts_mediawallpostphoto (
    id integer NOT NULL,
    mediawallpost_id integer,
    photo character varying(100) NOT NULL,
    deleted timestamp with time zone,
    ip_address inet,
    author_id integer,
    editor_id integer
);


--
-- Name: wallposts_mediawallpostphoto_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE wallposts_mediawallpostphoto_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: wallposts_mediawallpostphoto_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE wallposts_mediawallpostphoto_id_seq OWNED BY wallposts_mediawallpostphoto.id;


--
-- Name: wallposts_reaction; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE wallposts_reaction (
    id integer NOT NULL,
    author_id integer NOT NULL,
    editor_id integer,
    text text NOT NULL,
    wallpost_id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    deleted timestamp with time zone,
    ip_address inet
);


--
-- Name: wallposts_reaction_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE wallposts_reaction_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: wallposts_reaction_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE wallposts_reaction_id_seq OWNED BY wallposts_reaction.id;


--
-- Name: wallposts_systemwallpost; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE wallposts_systemwallpost (
    wallpost_ptr_id integer NOT NULL,
    text text NOT NULL,
    related_type_id integer NOT NULL,
    related_id integer NOT NULL,
    CONSTRAINT wallposts_systemwallpost_related_id_check CHECK ((related_id >= 0))
);


--
-- Name: wallposts_textwallpost; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE wallposts_textwallpost (
    wallpost_ptr_id integer NOT NULL,
    text text NOT NULL
);


--
-- Name: wallposts_wallpost; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE wallposts_wallpost (
    id integer NOT NULL,
    polymorphic_ctype_id integer,
    author_id integer,
    editor_id integer,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    deleted timestamp with time zone,
    ip_address inet,
    content_type_id integer NOT NULL,
    object_id integer NOT NULL,
    CONSTRAINT wallposts_wallpost_object_id_check CHECK ((object_id >= 0))
);


--
-- Name: wallposts_wallpost_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE wallposts_wallpost_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: wallposts_wallpost_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE wallposts_wallpost_id_seq OWNED BY wallposts_wallpost.id;


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY accounting_banktransaction ALTER COLUMN id SET DEFAULT nextval('accounting_banktransaction_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY accounting_docdatapayment ALTER COLUMN id SET DEFAULT nextval('accounting_docdatapayment_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY accounting_docdatapayout ALTER COLUMN id SET DEFAULT nextval('accounting_docdatapayout_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY accounts_bluebottleuser ALTER COLUMN id SET DEFAULT nextval('accounts_bluebottleuser_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY accounts_bluebottleuser_groups ALTER COLUMN id SET DEFAULT nextval('accounts_bluebottleuser_groups_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY accounts_bluebottleuser_user_permissions ALTER COLUMN id SET DEFAULT nextval('accounts_bluebottleuser_user_permissions_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY accounts_useraddress ALTER COLUMN id SET DEFAULT nextval('accounts_useraddress_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY admin_tools_dashboard_preferences ALTER COLUMN id SET DEFAULT nextval('admin_tools_dashboard_preferences_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY admin_tools_menu_bookmark ALTER COLUMN id SET DEFAULT nextval('admin_tools_menu_bookmark_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY auth_group ALTER COLUMN id SET DEFAULT nextval('auth_group_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY auth_group_permissions ALTER COLUMN id SET DEFAULT nextval('auth_group_permissions_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY auth_permission ALTER COLUMN id SET DEFAULT nextval('auth_permission_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY banners_slide ALTER COLUMN id SET DEFAULT nextval('banners_slide_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY blogs_blogcategory ALTER COLUMN id SET DEFAULT nextval('blogs_blogcategory_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY blogs_blogpost ALTER COLUMN id SET DEFAULT nextval('blogs_blogpost_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY blogs_blogpost_categories ALTER COLUMN id SET DEFAULT nextval('blogs_blogpost_categories_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY blogs_blogpost_countries ALTER COLUMN id SET DEFAULT nextval('blogs_blogpost_countries_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY campaigns_campaign ALTER COLUMN id SET DEFAULT nextval('campaigns_campaign_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY celery_taskmeta ALTER COLUMN id SET DEFAULT nextval('celery_taskmeta_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY celery_tasksetmeta ALTER COLUMN id SET DEFAULT nextval('celery_tasksetmeta_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY cowry_docdata_docdatapayment ALTER COLUMN id SET DEFAULT nextval('cowry_docdata_docdatapayment_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY cowry_docdata_docdatapaymentlogentry ALTER COLUMN id SET DEFAULT nextval('cowry_docdata_docdatapaymentlogentry_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY cowry_payment ALTER COLUMN id SET DEFAULT nextval('cowry_payment_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY django_admin_log ALTER COLUMN id SET DEFAULT nextval('django_admin_log_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY django_content_type ALTER COLUMN id SET DEFAULT nextval('django_content_type_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY django_redirect ALTER COLUMN id SET DEFAULT nextval('django_redirect_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY django_site ALTER COLUMN id SET DEFAULT nextval('django_site_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY djcelery_crontabschedule ALTER COLUMN id SET DEFAULT nextval('djcelery_crontabschedule_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY djcelery_intervalschedule ALTER COLUMN id SET DEFAULT nextval('djcelery_intervalschedule_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY djcelery_periodictask ALTER COLUMN id SET DEFAULT nextval('djcelery_periodictask_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY djcelery_taskstate ALTER COLUMN id SET DEFAULT nextval('djcelery_taskstate_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY djcelery_workerstate ALTER COLUMN id SET DEFAULT nextval('djcelery_workerstate_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY fluent_contents_contentitem ALTER COLUMN id SET DEFAULT nextval('fluent_contents_contentitem_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY fluent_contents_placeholder ALTER COLUMN id SET DEFAULT nextval('fluent_contents_placeholder_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY fund_donation ALTER COLUMN id SET DEFAULT nextval('fund_donation_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY fund_order ALTER COLUMN id SET DEFAULT nextval('fund_order_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY fund_recurringdirectdebitpayment ALTER COLUMN id SET DEFAULT nextval('fund_recurringdirectdebitpayment_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY fundraisers_fundraiser ALTER COLUMN id SET DEFAULT nextval('fundraisers_fundraiser_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY geo_country ALTER COLUMN id SET DEFAULT nextval('geo_country_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY geo_region ALTER COLUMN id SET DEFAULT nextval('geo_region_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY geo_subregion ALTER COLUMN id SET DEFAULT nextval('geo_subregion_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY love_lovedeclaration ALTER COLUMN id SET DEFAULT nextval('love_lovedeclaration_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY organizations_organization ALTER COLUMN id SET DEFAULT nextval('organizations_organization_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY organizations_organizationdocument ALTER COLUMN id SET DEFAULT nextval('organizations_organizationdocument_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY organizations_organizationmember ALTER COLUMN id SET DEFAULT nextval('organizations_organizationmember_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY pages_contactmessage ALTER COLUMN id SET DEFAULT nextval('pages_contactmessage_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY pages_page ALTER COLUMN id SET DEFAULT nextval('pages_page_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY payouts_bankmutation ALTER COLUMN id SET DEFAULT nextval('payouts_bankmutation_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY payouts_bankmutationline ALTER COLUMN id SET DEFAULT nextval('payouts_bankmutationline_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY payouts_organizationpayout ALTER COLUMN id SET DEFAULT nextval('payouts_organizationpayout_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY payouts_payout ALTER COLUMN id SET DEFAULT nextval('payouts_payout_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY projects_partnerorganization ALTER COLUMN id SET DEFAULT nextval('projects_partnerorganization_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY projects_project ALTER COLUMN id SET DEFAULT nextval('projects_project_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY projects_projectambassador ALTER COLUMN id SET DEFAULT nextval('projects_projectambassador_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY projects_projectbudgetline ALTER COLUMN id SET DEFAULT nextval('projects_projectbudgetline_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY projects_projectcampaign ALTER COLUMN id SET DEFAULT nextval('projects_projectcampaign_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY projects_projectphaselog ALTER COLUMN id SET DEFAULT nextval('projects_projectphaselog_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY projects_projectpitch ALTER COLUMN id SET DEFAULT nextval('projects_projectpitch_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY projects_projectplan ALTER COLUMN id SET DEFAULT nextval('projects_projectplan_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY projects_projectresult ALTER COLUMN id SET DEFAULT nextval('projects_projectresult_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY projects_projecttheme ALTER COLUMN id SET DEFAULT nextval('projects_projecttheme_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY quotes_quote ALTER COLUMN id SET DEFAULT nextval('quotes_quote_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY registration_registrationprofile ALTER COLUMN id SET DEFAULT nextval('registration_registrationprofile_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY social_auth_association ALTER COLUMN id SET DEFAULT nextval('social_auth_association_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY social_auth_nonce ALTER COLUMN id SET DEFAULT nextval('social_auth_nonce_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY social_auth_usersocialauth ALTER COLUMN id SET DEFAULT nextval('social_auth_usersocialauth_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY south_migrationhistory ALTER COLUMN id SET DEFAULT nextval('south_migrationhistory_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY statistics_statistic ALTER COLUMN id SET DEFAULT nextval('statistics_statistic_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY taggit_tag ALTER COLUMN id SET DEFAULT nextval('taggit_tag_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY taggit_taggeditem ALTER COLUMN id SET DEFAULT nextval('taggit_taggeditem_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY tasks_skill ALTER COLUMN id SET DEFAULT nextval('tasks_skill_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY tasks_task ALTER COLUMN id SET DEFAULT nextval('tasks_task_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY tasks_taskfile ALTER COLUMN id SET DEFAULT nextval('tasks_taskfile_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY tasks_taskmember ALTER COLUMN id SET DEFAULT nextval('tasks_taskmember_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY tests_name ALTER COLUMN id SET DEFAULT nextval('tests_name_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY tests_note ALTER COLUMN id SET DEFAULT nextval('tests_note_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY tests_person ALTER COLUMN id SET DEFAULT nextval('tests_person_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY tests_person_children ALTER COLUMN id SET DEFAULT nextval('tests_person_children_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY tests_person_notes ALTER COLUMN id SET DEFAULT nextval('tests_person_notes_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY tests_secret ALTER COLUMN id SET DEFAULT nextval('tests_secret_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY tests_sluggedtestmodel ALTER COLUMN id SET DEFAULT nextval('tests_sluggedtestmodel_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY tests_testmanytomanymodel_many ALTER COLUMN id SET DEFAULT nextval('tests_testmanytomanymodel_many_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY tests_testmodel ALTER COLUMN id SET DEFAULT nextval('tests_testmodel_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY tests_testmodel_field ALTER COLUMN id SET DEFAULT nextval('tests_testmodel_field_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY vouchers_customvoucherrequest ALTER COLUMN id SET DEFAULT nextval('vouchers_customvoucherrequest_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY vouchers_voucher ALTER COLUMN id SET DEFAULT nextval('vouchers_voucher_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY wallposts_mediawallpostphoto ALTER COLUMN id SET DEFAULT nextval('wallposts_mediawallpostphoto_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY wallposts_reaction ALTER COLUMN id SET DEFAULT nextval('wallposts_reaction_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY wallposts_wallpost ALTER COLUMN id SET DEFAULT nextval('wallposts_wallpost_id_seq'::regclass);


--
-- Name: accounting_banktransaction_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY accounting_banktransaction
    ADD CONSTRAINT accounting_banktransaction_pkey PRIMARY KEY (id);


--
-- Name: accounting_docdatap_triple_deal_reference_684590fbb06cb125_uniq; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY accounting_docdatapayment
    ADD CONSTRAINT accounting_docdatap_triple_deal_reference_684590fbb06cb125_uniq UNIQUE (triple_deal_reference, merchant_reference, payment_type);


--
-- Name: accounting_docdatapayment_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY accounting_docdatapayment
    ADD CONSTRAINT accounting_docdatapayment_pkey PRIMARY KEY (id);


--
-- Name: accounting_docdatapayout_period_id_key; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY accounting_docdatapayout
    ADD CONSTRAINT accounting_docdatapayout_period_id_key UNIQUE (period_id);


--
-- Name: accounting_docdatapayout_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY accounting_docdatapayout
    ADD CONSTRAINT accounting_docdatapayout_pkey PRIMARY KEY (id);


--
-- Name: accounts_bluebottleuser_bluebottleuser_id_147f9109b2c6aedf_uniq; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY accounts_bluebottleuser_user_permissions
    ADD CONSTRAINT accounts_bluebottleuser_bluebottleuser_id_147f9109b2c6aedf_uniq UNIQUE (bluebottleuser_id, permission_id);


--
-- Name: accounts_bluebottleuser_bluebottleuser_id_1d988989311d97dc_uniq; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY accounts_bluebottleuser_groups
    ADD CONSTRAINT accounts_bluebottleuser_bluebottleuser_id_1d988989311d97dc_uniq UNIQUE (bluebottleuser_id, group_id);


--
-- Name: accounts_bluebottleuser_email_key; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY accounts_bluebottleuser
    ADD CONSTRAINT accounts_bluebottleuser_email_key UNIQUE (email);


--
-- Name: accounts_bluebottleuser_groups_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY accounts_bluebottleuser_groups
    ADD CONSTRAINT accounts_bluebottleuser_groups_pkey PRIMARY KEY (id);


--
-- Name: accounts_bluebottleuser_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY accounts_bluebottleuser
    ADD CONSTRAINT accounts_bluebottleuser_pkey PRIMARY KEY (id);


--
-- Name: accounts_bluebottleuser_user_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY accounts_bluebottleuser_user_permissions
    ADD CONSTRAINT accounts_bluebottleuser_user_permissions_pkey PRIMARY KEY (id);


--
-- Name: accounts_bluebottleuser_username_key; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY accounts_bluebottleuser
    ADD CONSTRAINT accounts_bluebottleuser_username_key UNIQUE (username);


--
-- Name: accounts_useraddress_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY accounts_useraddress
    ADD CONSTRAINT accounts_useraddress_pkey PRIMARY KEY (id);


--
-- Name: admin_tools_dashboard_prefer_dashboard_id_374bce90a8a4eefc_uniq; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY admin_tools_dashboard_preferences
    ADD CONSTRAINT admin_tools_dashboard_prefer_dashboard_id_374bce90a8a4eefc_uniq UNIQUE (dashboard_id, user_id);


--
-- Name: admin_tools_dashboard_preferences_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY admin_tools_dashboard_preferences
    ADD CONSTRAINT admin_tools_dashboard_preferences_pkey PRIMARY KEY (id);


--
-- Name: admin_tools_menu_bookmark_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY admin_tools_menu_bookmark
    ADD CONSTRAINT admin_tools_menu_bookmark_pkey PRIMARY KEY (id);


--
-- Name: auth_group_name_key; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY auth_group
    ADD CONSTRAINT auth_group_name_key UNIQUE (name);


--
-- Name: auth_group_permissions_group_id_key; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_key UNIQUE (group_id, permission_id);


--
-- Name: auth_group_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_pkey PRIMARY KEY (id);


--
-- Name: auth_group_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY auth_group
    ADD CONSTRAINT auth_group_pkey PRIMARY KEY (id);


--
-- Name: auth_permission_content_type_id_key; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_key UNIQUE (content_type_id, codename);


--
-- Name: auth_permission_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY auth_permission
    ADD CONSTRAINT auth_permission_pkey PRIMARY KEY (id);


--
-- Name: banners_slide_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY banners_slide
    ADD CONSTRAINT banners_slide_pkey PRIMARY KEY (id);


--
-- Name: blogs_blogcategory_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY blogs_blogcategory
    ADD CONSTRAINT blogs_blogcategory_pkey PRIMARY KEY (id);


--
-- Name: blogs_blogpost_categories_blogpost_id_1ae874162b0a2862_uniq; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY blogs_blogpost_categories
    ADD CONSTRAINT blogs_blogpost_categories_blogpost_id_1ae874162b0a2862_uniq UNIQUE (blogpost_id, blogcategory_id);


--
-- Name: blogs_blogpost_categories_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY blogs_blogpost_categories
    ADD CONSTRAINT blogs_blogpost_categories_pkey PRIMARY KEY (id);


--
-- Name: blogs_blogpost_countries_blogpost_id_6d0b1ceb642aa356_uniq; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY blogs_blogpost_countries
    ADD CONSTRAINT blogs_blogpost_countries_blogpost_id_6d0b1ceb642aa356_uniq UNIQUE (blogpost_id, country_id);


--
-- Name: blogs_blogpost_countries_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY blogs_blogpost_countries
    ADD CONSTRAINT blogs_blogpost_countries_pkey PRIMARY KEY (id);


--
-- Name: blogs_blogpost_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY blogs_blogpost
    ADD CONSTRAINT blogs_blogpost_pkey PRIMARY KEY (id);


--
-- Name: blogs_blogpost_slug_6b3bc696cce4c377_uniq; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY blogs_blogpost
    ADD CONSTRAINT blogs_blogpost_slug_6b3bc696cce4c377_uniq UNIQUE (slug, language);


--
-- Name: campaigns_campaign_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY campaigns_campaign
    ADD CONSTRAINT campaigns_campaign_pkey PRIMARY KEY (id);


--
-- Name: celery_taskmeta_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY celery_taskmeta
    ADD CONSTRAINT celery_taskmeta_pkey PRIMARY KEY (id);


--
-- Name: celery_taskmeta_task_id_key; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY celery_taskmeta
    ADD CONSTRAINT celery_taskmeta_task_id_key UNIQUE (task_id);


--
-- Name: celery_tasksetmeta_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY celery_tasksetmeta
    ADD CONSTRAINT celery_tasksetmeta_pkey PRIMARY KEY (id);


--
-- Name: celery_tasksetmeta_taskset_id_key; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY celery_tasksetmeta
    ADD CONSTRAINT celery_tasksetmeta_taskset_id_key UNIQUE (taskset_id);


--
-- Name: contentitem_contentplugins_pictureitem_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY contentitem_contentplugins_pictureitem
    ADD CONSTRAINT contentitem_contentplugins_pictureitem_pkey PRIMARY KEY (contentitem_ptr_id);


--
-- Name: contentitem_oembeditem_oembeditem_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY contentitem_oembeditem_oembeditem
    ADD CONSTRAINT contentitem_oembeditem_oembeditem_pkey PRIMARY KEY (contentitem_ptr_id);


--
-- Name: contentitem_rawhtml_rawhtmlitem_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY contentitem_rawhtml_rawhtmlitem
    ADD CONSTRAINT contentitem_rawhtml_rawhtmlitem_pkey PRIMARY KEY (contentitem_ptr_id);


--
-- Name: contentitem_text_textitem_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY contentitem_text_textitem
    ADD CONSTRAINT contentitem_text_textitem_pkey PRIMARY KEY (contentitem_ptr_id);


--
-- Name: cowry_docdata_docdatapayment_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY cowry_docdata_docdatapayment
    ADD CONSTRAINT cowry_docdata_docdatapayment_pkey PRIMARY KEY (id);


--
-- Name: cowry_docdata_docdatapaymentlogentry_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY cowry_docdata_docdatapaymentlogentry
    ADD CONSTRAINT cowry_docdata_docdatapaymentlogentry_pkey PRIMARY KEY (id);


--
-- Name: cowry_docdata_docdatapaymentorder_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY cowry_docdata_docdatapaymentorder
    ADD CONSTRAINT cowry_docdata_docdatapaymentorder_pkey PRIMARY KEY (payment_ptr_id);


--
-- Name: cowry_docdata_docdatawebdirectdirectdebit_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY cowry_docdata_docdatawebdirectdirectdebit
    ADD CONSTRAINT cowry_docdata_docdatawebdirectdirectdebit_pkey PRIMARY KEY (docdatapayment_ptr_id);


--
-- Name: cowry_payment_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY cowry_payment
    ADD CONSTRAINT cowry_payment_pkey PRIMARY KEY (id);


--
-- Name: django_admin_log_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY django_admin_log
    ADD CONSTRAINT django_admin_log_pkey PRIMARY KEY (id);


--
-- Name: django_content_type_app_label_key; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY django_content_type
    ADD CONSTRAINT django_content_type_app_label_key UNIQUE (app_label, model);


--
-- Name: django_content_type_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY django_content_type
    ADD CONSTRAINT django_content_type_pkey PRIMARY KEY (id);


--
-- Name: django_redirect_old_path_key; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY django_redirect
    ADD CONSTRAINT django_redirect_old_path_key UNIQUE (old_path);


--
-- Name: django_redirect_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY django_redirect
    ADD CONSTRAINT django_redirect_pkey PRIMARY KEY (id);


--
-- Name: django_session_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY django_session
    ADD CONSTRAINT django_session_pkey PRIMARY KEY (session_key);


--
-- Name: django_site_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY django_site
    ADD CONSTRAINT django_site_pkey PRIMARY KEY (id);


--
-- Name: djcelery_crontabschedule_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY djcelery_crontabschedule
    ADD CONSTRAINT djcelery_crontabschedule_pkey PRIMARY KEY (id);


--
-- Name: djcelery_intervalschedule_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY djcelery_intervalschedule
    ADD CONSTRAINT djcelery_intervalschedule_pkey PRIMARY KEY (id);


--
-- Name: djcelery_periodictask_name_key; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY djcelery_periodictask
    ADD CONSTRAINT djcelery_periodictask_name_key UNIQUE (name);


--
-- Name: djcelery_periodictask_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY djcelery_periodictask
    ADD CONSTRAINT djcelery_periodictask_pkey PRIMARY KEY (id);


--
-- Name: djcelery_periodictasks_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY djcelery_periodictasks
    ADD CONSTRAINT djcelery_periodictasks_pkey PRIMARY KEY (ident);


--
-- Name: djcelery_taskstate_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY djcelery_taskstate
    ADD CONSTRAINT djcelery_taskstate_pkey PRIMARY KEY (id);


--
-- Name: djcelery_taskstate_task_id_key; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY djcelery_taskstate
    ADD CONSTRAINT djcelery_taskstate_task_id_key UNIQUE (task_id);


--
-- Name: djcelery_workerstate_hostname_key; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY djcelery_workerstate
    ADD CONSTRAINT djcelery_workerstate_hostname_key UNIQUE (hostname);


--
-- Name: djcelery_workerstate_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY djcelery_workerstate
    ADD CONSTRAINT djcelery_workerstate_pkey PRIMARY KEY (id);


--
-- Name: fluent_contents_contentitem_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY fluent_contents_contentitem
    ADD CONSTRAINT fluent_contents_contentitem_pkey PRIMARY KEY (id);


--
-- Name: fluent_contents_placeholde_parent_type_id_451c85966d08dedf_uniq; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY fluent_contents_placeholder
    ADD CONSTRAINT fluent_contents_placeholde_parent_type_id_451c85966d08dedf_uniq UNIQUE (parent_type_id, parent_id, slot);


--
-- Name: fluent_contents_placeholder_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY fluent_contents_placeholder
    ADD CONSTRAINT fluent_contents_placeholder_pkey PRIMARY KEY (id);


--
-- Name: fund_customvoucherrequest_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY vouchers_customvoucherrequest
    ADD CONSTRAINT fund_customvoucherrequest_pkey PRIMARY KEY (id);


--
-- Name: fund_donation_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY fund_donation
    ADD CONSTRAINT fund_donation_pkey PRIMARY KEY (id);


--
-- Name: fund_order_order_number_key; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY fund_order
    ADD CONSTRAINT fund_order_order_number_key UNIQUE (order_number);


--
-- Name: fund_order_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY fund_order
    ADD CONSTRAINT fund_order_pkey PRIMARY KEY (id);


--
-- Name: fund_recurringdirectdebitpayment_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY fund_recurringdirectdebitpayment
    ADD CONSTRAINT fund_recurringdirectdebitpayment_pkey PRIMARY KEY (id);


--
-- Name: fund_recurringdirectdebitpayment_user_id_key; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY fund_recurringdirectdebitpayment
    ADD CONSTRAINT fund_recurringdirectdebitpayment_user_id_key UNIQUE (user_id);


--
-- Name: fund_voucher_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY vouchers_voucher
    ADD CONSTRAINT fund_voucher_pkey PRIMARY KEY (id);


--
-- Name: fundraisers_fundraiser_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY fundraisers_fundraiser
    ADD CONSTRAINT fundraisers_fundraiser_pkey PRIMARY KEY (id);


--
-- Name: geo_country_numeric_code_key; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY geo_country
    ADD CONSTRAINT geo_country_numeric_code_key UNIQUE (numeric_code);


--
-- Name: geo_country_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY geo_country
    ADD CONSTRAINT geo_country_pkey PRIMARY KEY (id);


--
-- Name: geo_region_numeric_code_key; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY geo_region
    ADD CONSTRAINT geo_region_numeric_code_key UNIQUE (numeric_code);


--
-- Name: geo_region_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY geo_region
    ADD CONSTRAINT geo_region_pkey PRIMARY KEY (id);


--
-- Name: geo_subregion_numeric_code_key; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY geo_subregion
    ADD CONSTRAINT geo_subregion_numeric_code_key UNIQUE (numeric_code);


--
-- Name: geo_subregion_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY geo_subregion
    ADD CONSTRAINT geo_subregion_pkey PRIMARY KEY (id);


--
-- Name: love_lovedeclaration_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY love_lovedeclaration
    ADD CONSTRAINT love_lovedeclaration_pkey PRIMARY KEY (id);


--
-- Name: love_lovedeclaration_user_id_55a8ddf7d6820d97_uniq; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY love_lovedeclaration
    ADD CONSTRAINT love_lovedeclaration_user_id_55a8ddf7d6820d97_uniq UNIQUE (user_id, content_type_id, object_id);


--
-- Name: organizations_organization_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY organizations_organization
    ADD CONSTRAINT organizations_organization_pkey PRIMARY KEY (id);


--
-- Name: organizations_organization_slug_key; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY organizations_organization
    ADD CONSTRAINT organizations_organization_slug_key UNIQUE (slug);


--
-- Name: organizations_organizationdocument_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY organizations_organizationdocument
    ADD CONSTRAINT organizations_organizationdocument_pkey PRIMARY KEY (id);


--
-- Name: organizations_organizationmember_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY organizations_organizationmember
    ADD CONSTRAINT organizations_organizationmember_pkey PRIMARY KEY (id);


--
-- Name: pages_contactmessage_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY pages_contactmessage
    ADD CONSTRAINT pages_contactmessage_pkey PRIMARY KEY (id);


--
-- Name: pages_page_language_7415b110df64f20b_uniq; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY pages_page
    ADD CONSTRAINT pages_page_language_7415b110df64f20b_uniq UNIQUE (language, slug);


--
-- Name: pages_page_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY pages_page
    ADD CONSTRAINT pages_page_pkey PRIMARY KEY (id);


--
-- Name: payouts_bankmutation_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY payouts_bankmutation
    ADD CONSTRAINT payouts_bankmutation_pkey PRIMARY KEY (id);


--
-- Name: payouts_bankmutationline_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY payouts_bankmutationline
    ADD CONSTRAINT payouts_bankmutationline_pkey PRIMARY KEY (id);


--
-- Name: payouts_organizationpayout_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY payouts_organizationpayout
    ADD CONSTRAINT payouts_organizationpayout_pkey PRIMARY KEY (id);


--
-- Name: payouts_organizationpayout_start_date_73b3545711f6730e_uniq; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY payouts_organizationpayout
    ADD CONSTRAINT payouts_organizationpayout_start_date_73b3545711f6730e_uniq UNIQUE (start_date, end_date);


--
-- Name: payouts_payout_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY payouts_payout
    ADD CONSTRAINT payouts_payout_pkey PRIMARY KEY (id);


--
-- Name: projects_partnerorganization_name_key; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY projects_partnerorganization
    ADD CONSTRAINT projects_partnerorganization_name_key UNIQUE (name);


--
-- Name: projects_partnerorganization_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY projects_partnerorganization
    ADD CONSTRAINT projects_partnerorganization_pkey PRIMARY KEY (id);


--
-- Name: projects_partnerorganization_slug_key; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY projects_partnerorganization
    ADD CONSTRAINT projects_partnerorganization_slug_key UNIQUE (slug);


--
-- Name: projects_project_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY projects_project
    ADD CONSTRAINT projects_project_pkey PRIMARY KEY (id);


--
-- Name: projects_project_slug_key; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY projects_project
    ADD CONSTRAINT projects_project_slug_key UNIQUE (slug);


--
-- Name: projects_projectambassador_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY projects_projectambassador
    ADD CONSTRAINT projects_projectambassador_pkey PRIMARY KEY (id);


--
-- Name: projects_projectbudgetline_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY projects_projectbudgetline
    ADD CONSTRAINT projects_projectbudgetline_pkey PRIMARY KEY (id);


--
-- Name: projects_projectcampaign_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY projects_projectcampaign
    ADD CONSTRAINT projects_projectcampaign_pkey PRIMARY KEY (id);


--
-- Name: projects_projectcampaign_project_id_key; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY projects_projectcampaign
    ADD CONSTRAINT projects_projectcampaign_project_id_key UNIQUE (project_id);


--
-- Name: projects_projectphaselog_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY projects_projectphaselog
    ADD CONSTRAINT projects_projectphaselog_pkey PRIMARY KEY (id);


--
-- Name: projects_projectphaselog_project_id_6ffb33f12e77a8da_uniq; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY projects_projectphaselog
    ADD CONSTRAINT projects_projectphaselog_project_id_6ffb33f12e77a8da_uniq UNIQUE (project_id, phase);


--
-- Name: projects_projectpitch_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY projects_projectpitch
    ADD CONSTRAINT projects_projectpitch_pkey PRIMARY KEY (id);


--
-- Name: projects_projectpitch_project_id_key; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY projects_projectpitch
    ADD CONSTRAINT projects_projectpitch_project_id_key UNIQUE (project_id);


--
-- Name: projects_projectplan_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY projects_projectplan
    ADD CONSTRAINT projects_projectplan_pkey PRIMARY KEY (id);


--
-- Name: projects_projectplan_project_id_key; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY projects_projectplan
    ADD CONSTRAINT projects_projectplan_project_id_key UNIQUE (project_id);


--
-- Name: projects_projectresult_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY projects_projectresult
    ADD CONSTRAINT projects_projectresult_pkey PRIMARY KEY (id);


--
-- Name: projects_projectresult_project_id_key; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY projects_projectresult
    ADD CONSTRAINT projects_projectresult_project_id_key UNIQUE (project_id);


--
-- Name: projects_projecttheme_name_key; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY projects_projecttheme
    ADD CONSTRAINT projects_projecttheme_name_key UNIQUE (name);


--
-- Name: projects_projecttheme_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY projects_projecttheme
    ADD CONSTRAINT projects_projecttheme_pkey PRIMARY KEY (id);


--
-- Name: projects_projecttheme_slug_key; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY projects_projecttheme
    ADD CONSTRAINT projects_projecttheme_slug_key UNIQUE (slug);


--
-- Name: quotes_quote_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY quotes_quote
    ADD CONSTRAINT quotes_quote_pkey PRIMARY KEY (id);


--
-- Name: registration_registrationprofile_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY registration_registrationprofile
    ADD CONSTRAINT registration_registrationprofile_pkey PRIMARY KEY (id);


--
-- Name: registration_registrationprofile_user_id_key; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY registration_registrationprofile
    ADD CONSTRAINT registration_registrationprofile_user_id_key UNIQUE (user_id);


--
-- Name: social_auth_association_handle_693a924207fa6ae_uniq; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY social_auth_association
    ADD CONSTRAINT social_auth_association_handle_693a924207fa6ae_uniq UNIQUE (handle, server_url);


--
-- Name: social_auth_association_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY social_auth_association
    ADD CONSTRAINT social_auth_association_pkey PRIMARY KEY (id);


--
-- Name: social_auth_nonce_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY social_auth_nonce
    ADD CONSTRAINT social_auth_nonce_pkey PRIMARY KEY (id);


--
-- Name: social_auth_nonce_timestamp_3833ba21ef52524a_uniq; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY social_auth_nonce
    ADD CONSTRAINT social_auth_nonce_timestamp_3833ba21ef52524a_uniq UNIQUE ("timestamp", salt, server_url);


--
-- Name: social_auth_usersocialauth_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY social_auth_usersocialauth
    ADD CONSTRAINT social_auth_usersocialauth_pkey PRIMARY KEY (id);


--
-- Name: social_auth_usersocialauth_provider_2f763109e2c4a1fb_uniq; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY social_auth_usersocialauth
    ADD CONSTRAINT social_auth_usersocialauth_provider_2f763109e2c4a1fb_uniq UNIQUE (provider, uid);


--
-- Name: south_migrationhistory_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY south_migrationhistory
    ADD CONSTRAINT south_migrationhistory_pkey PRIMARY KEY (id);


--
-- Name: statistics_statistic_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY statistics_statistic
    ADD CONSTRAINT statistics_statistic_pkey PRIMARY KEY (id);


--
-- Name: taggit_tag_name_uniq; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY taggit_tag
    ADD CONSTRAINT taggit_tag_name_uniq UNIQUE (name);


--
-- Name: taggit_tag_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY taggit_tag
    ADD CONSTRAINT taggit_tag_pkey PRIMARY KEY (id);


--
-- Name: taggit_tag_slug_key; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY taggit_tag
    ADD CONSTRAINT taggit_tag_slug_key UNIQUE (slug);


--
-- Name: taggit_taggeditem_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY taggit_taggeditem
    ADD CONSTRAINT taggit_taggeditem_pkey PRIMARY KEY (id);


--
-- Name: tasks_skill_name_key; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY tasks_skill
    ADD CONSTRAINT tasks_skill_name_key UNIQUE (name);


--
-- Name: tasks_skill_name_nl_key; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY tasks_skill
    ADD CONSTRAINT tasks_skill_name_nl_key UNIQUE (name_nl);


--
-- Name: tasks_skill_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY tasks_skill
    ADD CONSTRAINT tasks_skill_pkey PRIMARY KEY (id);


--
-- Name: tasks_task_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY tasks_task
    ADD CONSTRAINT tasks_task_pkey PRIMARY KEY (id);


--
-- Name: tasks_taskfile_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY tasks_taskfile
    ADD CONSTRAINT tasks_taskfile_pkey PRIMARY KEY (id);


--
-- Name: tasks_taskmember_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY tasks_taskmember
    ADD CONSTRAINT tasks_taskmember_pkey PRIMARY KEY (id);


--
-- Name: tests_childsluggedtestmodel_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY tests_childsluggedtestmodel
    ADD CONSTRAINT tests_childsluggedtestmodel_pkey PRIMARY KEY (sluggedtestmodel_ptr_id);


--
-- Name: tests_name_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY tests_name
    ADD CONSTRAINT tests_name_pkey PRIMARY KEY (id);


--
-- Name: tests_note_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY tests_note
    ADD CONSTRAINT tests_note_pkey PRIMARY KEY (id);


--
-- Name: tests_person_children_from_person_id_key; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY tests_person_children
    ADD CONSTRAINT tests_person_children_from_person_id_key UNIQUE (from_person_id, to_person_id);


--
-- Name: tests_person_children_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY tests_person_children
    ADD CONSTRAINT tests_person_children_pkey PRIMARY KEY (id);


--
-- Name: tests_person_notes_person_id_key; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY tests_person_notes
    ADD CONSTRAINT tests_person_notes_person_id_key UNIQUE (person_id, note_id);


--
-- Name: tests_person_notes_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY tests_person_notes
    ADD CONSTRAINT tests_person_notes_pkey PRIMARY KEY (id);


--
-- Name: tests_person_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY tests_person
    ADD CONSTRAINT tests_person_pkey PRIMARY KEY (id);


--
-- Name: tests_secret_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY tests_secret
    ADD CONSTRAINT tests_secret_pkey PRIMARY KEY (id);


--
-- Name: tests_sluggedtestmodel_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY tests_sluggedtestmodel
    ADD CONSTRAINT tests_sluggedtestmodel_pkey PRIMARY KEY (id);


--
-- Name: tests_testagregatemodel_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY tests_testagregatemodel
    ADD CONSTRAINT tests_testagregatemodel_pkey PRIMARY KEY (testmodel_pk_ptr_id);


--
-- Name: tests_testmanytomanymodel_many_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY tests_testmanytomanymodel_many
    ADD CONSTRAINT tests_testmanytomanymodel_many_pkey PRIMARY KEY (id);


--
-- Name: tests_testmanytomanymodel_many_testmanytomanymodel_id_key; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY tests_testmanytomanymodel_many
    ADD CONSTRAINT tests_testmanytomanymodel_many_testmanytomanymodel_id_key UNIQUE (testmanytomanymodel_id, testmodel_field_id);


--
-- Name: tests_testmanytomanymodel_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY tests_testmanytomanymodel
    ADD CONSTRAINT tests_testmanytomanymodel_pkey PRIMARY KEY (testmodel_pk_ptr_id);


--
-- Name: tests_testmodel_field_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY tests_testmodel_field
    ADD CONSTRAINT tests_testmodel_field_pkey PRIMARY KEY (id);


--
-- Name: tests_testmodel_pk_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY tests_testmodel_pk
    ADD CONSTRAINT tests_testmodel_pk_pkey PRIMARY KEY (uuid_field);


--
-- Name: tests_testmodel_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY tests_testmodel
    ADD CONSTRAINT tests_testmodel_pkey PRIMARY KEY (id);


--
-- Name: thumbnail_kvstore_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY thumbnail_kvstore
    ADD CONSTRAINT thumbnail_kvstore_pkey PRIMARY KEY (key);


--
-- Name: wallposts_mediawallpost_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY wallposts_mediawallpost
    ADD CONSTRAINT wallposts_mediawallpost_pkey PRIMARY KEY (wallpost_ptr_id);


--
-- Name: wallposts_mediawallpostphoto_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY wallposts_mediawallpostphoto
    ADD CONSTRAINT wallposts_mediawallpostphoto_pkey PRIMARY KEY (id);


--
-- Name: wallposts_reaction_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY wallposts_reaction
    ADD CONSTRAINT wallposts_reaction_pkey PRIMARY KEY (id);


--
-- Name: wallposts_systemwallpost_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY wallposts_systemwallpost
    ADD CONSTRAINT wallposts_systemwallpost_pkey PRIMARY KEY (wallpost_ptr_id);


--
-- Name: wallposts_textwallpost_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY wallposts_textwallpost
    ADD CONSTRAINT wallposts_textwallpost_pkey PRIMARY KEY (wallpost_ptr_id);


--
-- Name: wallposts_wallpost_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY wallposts_wallpost
    ADD CONSTRAINT wallposts_wallpost_pkey PRIMARY KEY (id);


--
-- Name: accounting_banktransaction_book_date; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX accounting_banktransaction_book_date ON accounting_banktransaction USING btree (book_date);


--
-- Name: accounting_banktransaction_credit_debit; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX accounting_banktransaction_credit_debit ON accounting_banktransaction USING btree (credit_debit);


--
-- Name: accounting_banktransaction_credit_debit_like; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX accounting_banktransaction_credit_debit_like ON accounting_banktransaction USING btree (credit_debit varchar_pattern_ops);


--
-- Name: accounting_docdatapayment_merchant_reference; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX accounting_docdatapayment_merchant_reference ON accounting_docdatapayment USING btree (merchant_reference);


--
-- Name: accounting_docdatapayment_merchant_reference_like; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX accounting_docdatapayment_merchant_reference_like ON accounting_docdatapayment USING btree (merchant_reference varchar_pattern_ops);


--
-- Name: accounting_docdatapayment_payment_type; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX accounting_docdatapayment_payment_type ON accounting_docdatapayment USING btree (payment_type);


--
-- Name: accounting_docdatapayment_triple_deal_reference; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX accounting_docdatapayment_triple_deal_reference ON accounting_docdatapayment USING btree (triple_deal_reference);


--
-- Name: accounting_docdatapayout_end_date; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX accounting_docdatapayout_end_date ON accounting_docdatapayout USING btree (end_date);


--
-- Name: accounting_docdatapayout_start_date; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX accounting_docdatapayout_start_date ON accounting_docdatapayout USING btree (start_date);


--
-- Name: accounts_bluebottleuser_email_like; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX accounts_bluebottleuser_email_like ON accounts_bluebottleuser USING btree (email varchar_pattern_ops);


--
-- Name: accounts_bluebottleuser_groups_bluebottleuser_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX accounts_bluebottleuser_groups_bluebottleuser_id ON accounts_bluebottleuser_groups USING btree (bluebottleuser_id);


--
-- Name: accounts_bluebottleuser_groups_group_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX accounts_bluebottleuser_groups_group_id ON accounts_bluebottleuser_groups USING btree (group_id);


--
-- Name: accounts_bluebottleuser_user_permissions_bluebottleuser_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX accounts_bluebottleuser_user_permissions_bluebottleuser_id ON accounts_bluebottleuser_user_permissions USING btree (bluebottleuser_id);


--
-- Name: accounts_bluebottleuser_user_permissions_permission_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX accounts_bluebottleuser_user_permissions_permission_id ON accounts_bluebottleuser_user_permissions USING btree (permission_id);


--
-- Name: accounts_bluebottleuser_username_like; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX accounts_bluebottleuser_username_like ON accounts_bluebottleuser USING btree (username varchar_pattern_ops);


--
-- Name: accounts_useraddress_country_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX accounts_useraddress_country_id ON accounts_useraddress USING btree (country_id);


--
-- Name: accounts_useraddress_user_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX accounts_useraddress_user_id ON accounts_useraddress USING btree (user_id);


--
-- Name: admin_tools_dashboard_preferences_user_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX admin_tools_dashboard_preferences_user_id ON admin_tools_dashboard_preferences USING btree (user_id);


--
-- Name: admin_tools_menu_bookmark_user_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX admin_tools_menu_bookmark_user_id ON admin_tools_menu_bookmark USING btree (user_id);


--
-- Name: auth_group_name_like; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX auth_group_name_like ON auth_group USING btree (name varchar_pattern_ops);


--
-- Name: auth_group_permissions_group_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX auth_group_permissions_group_id ON auth_group_permissions USING btree (group_id);


--
-- Name: auth_group_permissions_permission_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX auth_group_permissions_permission_id ON auth_group_permissions USING btree (permission_id);


--
-- Name: auth_permission_content_type_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX auth_permission_content_type_id ON auth_permission USING btree (content_type_id);


--
-- Name: banners_slide_author_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX banners_slide_author_id ON banners_slide USING btree (author_id);


--
-- Name: banners_slide_publication_date; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX banners_slide_publication_date ON banners_slide USING btree (publication_date);


--
-- Name: banners_slide_publication_end_date; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX banners_slide_publication_end_date ON banners_slide USING btree (publication_end_date);


--
-- Name: banners_slide_slug; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX banners_slide_slug ON banners_slide USING btree (slug);


--
-- Name: banners_slide_slug_like; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX banners_slide_slug_like ON banners_slide USING btree (slug varchar_pattern_ops);


--
-- Name: banners_slide_status; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX banners_slide_status ON banners_slide USING btree (status);


--
-- Name: banners_slide_status_like; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX banners_slide_status_like ON banners_slide USING btree (status varchar_pattern_ops);


--
-- Name: blogs_blogpost_author_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX blogs_blogpost_author_id ON blogs_blogpost USING btree (author_id);


--
-- Name: blogs_blogpost_categories_blogcategory_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX blogs_blogpost_categories_blogcategory_id ON blogs_blogpost_categories USING btree (blogcategory_id);


--
-- Name: blogs_blogpost_categories_blogpost_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX blogs_blogpost_categories_blogpost_id ON blogs_blogpost_categories USING btree (blogpost_id);


--
-- Name: blogs_blogpost_countries_blogpost_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX blogs_blogpost_countries_blogpost_id ON blogs_blogpost_countries USING btree (blogpost_id);


--
-- Name: blogs_blogpost_countries_country_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX blogs_blogpost_countries_country_id ON blogs_blogpost_countries USING btree (country_id);


--
-- Name: blogs_blogpost_post_type; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX blogs_blogpost_post_type ON blogs_blogpost USING btree (post_type);


--
-- Name: blogs_blogpost_post_type_like; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX blogs_blogpost_post_type_like ON blogs_blogpost USING btree (post_type varchar_pattern_ops);


--
-- Name: blogs_blogpost_publication_date; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX blogs_blogpost_publication_date ON blogs_blogpost USING btree (publication_date);


--
-- Name: blogs_blogpost_publication_end_date; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX blogs_blogpost_publication_end_date ON blogs_blogpost USING btree (publication_end_date);


--
-- Name: blogs_blogpost_slug; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX blogs_blogpost_slug ON blogs_blogpost USING btree (slug);


--
-- Name: blogs_blogpost_slug_like; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX blogs_blogpost_slug_like ON blogs_blogpost USING btree (slug varchar_pattern_ops);


--
-- Name: blogs_blogpost_status; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX blogs_blogpost_status ON blogs_blogpost USING btree (status);


--
-- Name: blogs_blogpost_status_like; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX blogs_blogpost_status_like ON blogs_blogpost USING btree (status varchar_pattern_ops);


--
-- Name: celery_taskmeta_hidden; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX celery_taskmeta_hidden ON celery_taskmeta USING btree (hidden);


--
-- Name: celery_taskmeta_task_id_like; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX celery_taskmeta_task_id_like ON celery_taskmeta USING btree (task_id varchar_pattern_ops);


--
-- Name: celery_tasksetmeta_hidden; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX celery_tasksetmeta_hidden ON celery_tasksetmeta USING btree (hidden);


--
-- Name: celery_tasksetmeta_taskset_id_like; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX celery_tasksetmeta_taskset_id_like ON celery_tasksetmeta USING btree (taskset_id varchar_pattern_ops);


--
-- Name: cowry_docdata_docdatapayment_docdata_payment_order_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX cowry_docdata_docdatapayment_docdata_payment_order_id ON cowry_docdata_docdatapayment USING btree (docdata_payment_order_id);


--
-- Name: cowry_docdata_docdatapayment_polymorphic_ctype_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX cowry_docdata_docdatapayment_polymorphic_ctype_id ON cowry_docdata_docdatapayment USING btree (polymorphic_ctype_id);


--
-- Name: cowry_docdata_docdatapaymentlogentry_docdata_payment_order_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX cowry_docdata_docdatapaymentlogentry_docdata_payment_order_id ON cowry_docdata_docdatapaymentlogentry USING btree (docdata_payment_order_id);


--
-- Name: cowry_payment_order_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX cowry_payment_order_id ON cowry_payment USING btree (order_id);


--
-- Name: cowry_payment_polymorphic_ctype_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX cowry_payment_polymorphic_ctype_id ON cowry_payment USING btree (polymorphic_ctype_id);


--
-- Name: cowry_payment_status; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX cowry_payment_status ON cowry_payment USING btree (status);


--
-- Name: cowry_payment_status_like; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX cowry_payment_status_like ON cowry_payment USING btree (status varchar_pattern_ops);


--
-- Name: django_admin_log_content_type_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX django_admin_log_content_type_id ON django_admin_log USING btree (content_type_id);


--
-- Name: django_admin_log_user_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX django_admin_log_user_id ON django_admin_log USING btree (user_id);


--
-- Name: django_redirect_old_path_like; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX django_redirect_old_path_like ON django_redirect USING btree (old_path varchar_pattern_ops);


--
-- Name: django_session_expire_date; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX django_session_expire_date ON django_session USING btree (expire_date);


--
-- Name: django_session_session_key_like; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX django_session_session_key_like ON django_session USING btree (session_key varchar_pattern_ops);


--
-- Name: djcelery_periodictask_crontab_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX djcelery_periodictask_crontab_id ON djcelery_periodictask USING btree (crontab_id);


--
-- Name: djcelery_periodictask_interval_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX djcelery_periodictask_interval_id ON djcelery_periodictask USING btree (interval_id);


--
-- Name: djcelery_periodictask_name_like; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX djcelery_periodictask_name_like ON djcelery_periodictask USING btree (name varchar_pattern_ops);


--
-- Name: djcelery_taskstate_hidden; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX djcelery_taskstate_hidden ON djcelery_taskstate USING btree (hidden);


--
-- Name: djcelery_taskstate_name; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX djcelery_taskstate_name ON djcelery_taskstate USING btree (name);


--
-- Name: djcelery_taskstate_name_like; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX djcelery_taskstate_name_like ON djcelery_taskstate USING btree (name varchar_pattern_ops);


--
-- Name: djcelery_taskstate_state; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX djcelery_taskstate_state ON djcelery_taskstate USING btree (state);


--
-- Name: djcelery_taskstate_state_like; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX djcelery_taskstate_state_like ON djcelery_taskstate USING btree (state varchar_pattern_ops);


--
-- Name: djcelery_taskstate_task_id_like; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX djcelery_taskstate_task_id_like ON djcelery_taskstate USING btree (task_id varchar_pattern_ops);


--
-- Name: djcelery_taskstate_tstamp; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX djcelery_taskstate_tstamp ON djcelery_taskstate USING btree (tstamp);


--
-- Name: djcelery_taskstate_worker_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX djcelery_taskstate_worker_id ON djcelery_taskstate USING btree (worker_id);


--
-- Name: djcelery_workerstate_hostname_like; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX djcelery_workerstate_hostname_like ON djcelery_workerstate USING btree (hostname varchar_pattern_ops);


--
-- Name: djcelery_workerstate_last_heartbeat; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX djcelery_workerstate_last_heartbeat ON djcelery_workerstate USING btree (last_heartbeat);


--
-- Name: fluent_contents_contentitem_parent_type_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX fluent_contents_contentitem_parent_type_id ON fluent_contents_contentitem USING btree (parent_type_id);


--
-- Name: fluent_contents_contentitem_placeholder_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX fluent_contents_contentitem_placeholder_id ON fluent_contents_contentitem USING btree (placeholder_id);


--
-- Name: fluent_contents_contentitem_polymorphic_ctype_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX fluent_contents_contentitem_polymorphic_ctype_id ON fluent_contents_contentitem USING btree (polymorphic_ctype_id);


--
-- Name: fluent_contents_contentitem_sort_order; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX fluent_contents_contentitem_sort_order ON fluent_contents_contentitem USING btree (sort_order);


--
-- Name: fluent_contents_placeholder_parent_type_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX fluent_contents_placeholder_parent_type_id ON fluent_contents_placeholder USING btree (parent_type_id);


--
-- Name: fluent_contents_placeholder_slot; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX fluent_contents_placeholder_slot ON fluent_contents_placeholder USING btree (slot);


--
-- Name: fluent_contents_placeholder_slot_like; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX fluent_contents_placeholder_slot_like ON fluent_contents_placeholder USING btree (slot varchar_pattern_ops);


--
-- Name: fund_customvoucherrequest_contact_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX fund_customvoucherrequest_contact_id ON vouchers_customvoucherrequest USING btree (contact_id);


--
-- Name: fund_customvoucherrequest_status; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX fund_customvoucherrequest_status ON vouchers_customvoucherrequest USING btree (status);


--
-- Name: fund_customvoucherrequest_status_like; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX fund_customvoucherrequest_status_like ON vouchers_customvoucherrequest USING btree (status varchar_pattern_ops);


--
-- Name: fund_donation_donation_type; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX fund_donation_donation_type ON fund_donation USING btree (donation_type);


--
-- Name: fund_donation_donation_type_like; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX fund_donation_donation_type_like ON fund_donation USING btree (donation_type varchar_pattern_ops);


--
-- Name: fund_donation_fundraiser_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX fund_donation_fundraiser_id ON fund_donation USING btree (fundraiser_id);


--
-- Name: fund_donation_order_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX fund_donation_order_id ON fund_donation USING btree (order_id);


--
-- Name: fund_donation_project_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX fund_donation_project_id ON fund_donation USING btree (project_id);


--
-- Name: fund_donation_status; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX fund_donation_status ON fund_donation USING btree (status);


--
-- Name: fund_donation_status_like; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX fund_donation_status_like ON fund_donation USING btree (status varchar_pattern_ops);


--
-- Name: fund_donation_user_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX fund_donation_user_id ON fund_donation USING btree (user_id);


--
-- Name: fund_donation_voucher_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX fund_donation_voucher_id ON fund_donation USING btree (voucher_id);


--
-- Name: fund_order_order_number_like; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX fund_order_order_number_like ON fund_order USING btree (order_number varchar_pattern_ops);


--
-- Name: fund_order_status; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX fund_order_status ON fund_order USING btree (status);


--
-- Name: fund_order_status_like; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX fund_order_status_like ON fund_order USING btree (status varchar_pattern_ops);


--
-- Name: fund_order_user_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX fund_order_user_id ON fund_order USING btree (user_id);


--
-- Name: fund_voucher_order_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX fund_voucher_order_id ON vouchers_voucher USING btree (order_id);


--
-- Name: fund_voucher_receiver_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX fund_voucher_receiver_id ON vouchers_voucher USING btree (receiver_id);


--
-- Name: fund_voucher_sender_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX fund_voucher_sender_id ON vouchers_voucher USING btree (sender_id);


--
-- Name: fund_voucher_status; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX fund_voucher_status ON vouchers_voucher USING btree (status);


--
-- Name: fund_voucher_status_like; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX fund_voucher_status_like ON vouchers_voucher USING btree (status varchar_pattern_ops);


--
-- Name: fundraisers_fundraiser_owner_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX fundraisers_fundraiser_owner_id ON fundraisers_fundraiser USING btree (owner_id);


--
-- Name: fundraisers_fundraiser_project_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX fundraisers_fundraiser_project_id ON fundraisers_fundraiser USING btree (project_id);


--
-- Name: geo_country_numeric_code_like; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX geo_country_numeric_code_like ON geo_country USING btree (numeric_code varchar_pattern_ops);


--
-- Name: geo_country_subregion_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX geo_country_subregion_id ON geo_country USING btree (subregion_id);


--
-- Name: geo_region_numeric_code_like; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX geo_region_numeric_code_like ON geo_region USING btree (numeric_code varchar_pattern_ops);


--
-- Name: geo_subregion_numeric_code_like; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX geo_subregion_numeric_code_like ON geo_subregion USING btree (numeric_code varchar_pattern_ops);


--
-- Name: geo_subregion_region_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX geo_subregion_region_id ON geo_subregion USING btree (region_id);


--
-- Name: love_lovedeclaration_content_type_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX love_lovedeclaration_content_type_id ON love_lovedeclaration USING btree (content_type_id);


--
-- Name: love_lovedeclaration_user_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX love_lovedeclaration_user_id ON love_lovedeclaration USING btree (user_id);


--
-- Name: organizations_organization_account_bank_country_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX organizations_organization_account_bank_country_id ON organizations_organization USING btree (account_bank_country_id);


--
-- Name: organizations_organization_country_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX organizations_organization_country_id ON organizations_organization USING btree (country_id);


--
-- Name: organizations_organization_slug_like; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX organizations_organization_slug_like ON organizations_organization USING btree (slug varchar_pattern_ops);


--
-- Name: organizations_organizationdocument_author_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX organizations_organizationdocument_author_id ON organizations_organizationdocument USING btree (author_id);


--
-- Name: organizations_organizationdocument_organization_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX organizations_organizationdocument_organization_id ON organizations_organizationdocument USING btree (organization_id);


--
-- Name: organizations_organizationmember_organization_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX organizations_organizationmember_organization_id ON organizations_organizationmember USING btree (organization_id);


--
-- Name: organizations_organizationmember_user_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX organizations_organizationmember_user_id ON organizations_organizationmember USING btree (user_id);


--
-- Name: pages_contactmessage_author_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX pages_contactmessage_author_id ON pages_contactmessage USING btree (author_id);


--
-- Name: pages_page_author_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX pages_page_author_id ON pages_page USING btree (author_id);


--
-- Name: pages_page_publication_date; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX pages_page_publication_date ON pages_page USING btree (publication_date);


--
-- Name: pages_page_publication_end_date; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX pages_page_publication_end_date ON pages_page USING btree (publication_end_date);


--
-- Name: pages_page_slug; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX pages_page_slug ON pages_page USING btree (slug);


--
-- Name: pages_page_slug_like; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX pages_page_slug_like ON pages_page USING btree (slug varchar_pattern_ops);


--
-- Name: pages_page_status; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX pages_page_status ON pages_page USING btree (status);


--
-- Name: pages_page_status_like; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX pages_page_status_like ON pages_page USING btree (status varchar_pattern_ops);


--
-- Name: payouts_bankmutationline_bank_mutation_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX payouts_bankmutationline_bank_mutation_id ON payouts_bankmutationline USING btree (bank_mutation_id);


--
-- Name: payouts_bankmutationline_payout_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX payouts_bankmutationline_payout_id ON payouts_bankmutationline USING btree (payout_id);


--
-- Name: payouts_payout_project_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX payouts_payout_project_id ON payouts_payout USING btree (project_id);


--
-- Name: projects_partnerorganization_name_like; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX projects_partnerorganization_name_like ON projects_partnerorganization USING btree (name varchar_pattern_ops);


--
-- Name: projects_partnerorganization_slug_like; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX projects_partnerorganization_slug_like ON projects_partnerorganization USING btree (slug varchar_pattern_ops);


--
-- Name: projects_project_coach_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX projects_project_coach_id ON projects_project USING btree (coach_id);


--
-- Name: projects_project_owner_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX projects_project_owner_id ON projects_project USING btree (owner_id);


--
-- Name: projects_project_partner_organization_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX projects_project_partner_organization_id ON projects_project USING btree (partner_organization_id);


--
-- Name: projects_project_slug_like; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX projects_project_slug_like ON projects_project USING btree (slug varchar_pattern_ops);


--
-- Name: projects_projectambassador_project_plan_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX projects_projectambassador_project_plan_id ON projects_projectambassador USING btree (project_plan_id);


--
-- Name: projects_projectbudgetline_project_plan_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX projects_projectbudgetline_project_plan_id ON projects_projectbudgetline USING btree (project_plan_id);


--
-- Name: projects_projectphaselog_project_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX projects_projectphaselog_project_id ON projects_projectphaselog USING btree (project_id);


--
-- Name: projects_projectpitch_country_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX projects_projectpitch_country_id ON projects_projectpitch USING btree (country_id);


--
-- Name: projects_projectpitch_theme_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX projects_projectpitch_theme_id ON projects_projectpitch USING btree (theme_id);


--
-- Name: projects_projectplan_country_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX projects_projectplan_country_id ON projects_projectplan USING btree (country_id);


--
-- Name: projects_projectplan_organization_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX projects_projectplan_organization_id ON projects_projectplan USING btree (organization_id);


--
-- Name: projects_projectplan_theme_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX projects_projectplan_theme_id ON projects_projectplan USING btree (theme_id);


--
-- Name: projects_projecttheme_name_like; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX projects_projecttheme_name_like ON projects_projecttheme USING btree (name varchar_pattern_ops);


--
-- Name: projects_projecttheme_slug_like; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX projects_projecttheme_slug_like ON projects_projecttheme USING btree (slug varchar_pattern_ops);


--
-- Name: quotes_quote_author_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX quotes_quote_author_id ON quotes_quote USING btree (author_id);


--
-- Name: quotes_quote_publication_date; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX quotes_quote_publication_date ON quotes_quote USING btree (publication_date);


--
-- Name: quotes_quote_publication_end_date; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX quotes_quote_publication_end_date ON quotes_quote USING btree (publication_end_date);


--
-- Name: quotes_quote_segment; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX quotes_quote_segment ON quotes_quote USING btree (segment);


--
-- Name: quotes_quote_segment_like; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX quotes_quote_segment_like ON quotes_quote USING btree (segment varchar_pattern_ops);


--
-- Name: quotes_quote_status; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX quotes_quote_status ON quotes_quote USING btree (status);


--
-- Name: quotes_quote_status_like; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX quotes_quote_status_like ON quotes_quote USING btree (status varchar_pattern_ops);


--
-- Name: quotes_quote_user_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX quotes_quote_user_id ON quotes_quote USING btree (user_id);


--
-- Name: social_auth_association_issued; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX social_auth_association_issued ON social_auth_association USING btree (issued);


--
-- Name: social_auth_nonce_timestamp; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX social_auth_nonce_timestamp ON social_auth_nonce USING btree ("timestamp");


--
-- Name: social_auth_usersocialauth_user_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX social_auth_usersocialauth_user_id ON social_auth_usersocialauth USING btree (user_id);


--
-- Name: taggit_tag_slug_like; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX taggit_tag_slug_like ON taggit_tag USING btree (slug varchar_pattern_ops);


--
-- Name: taggit_taggeditem_content_type_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX taggit_taggeditem_content_type_id ON taggit_taggeditem USING btree (content_type_id);


--
-- Name: taggit_taggeditem_object_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX taggit_taggeditem_object_id ON taggit_taggeditem USING btree (object_id);


--
-- Name: taggit_taggeditem_tag_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX taggit_taggeditem_tag_id ON taggit_taggeditem USING btree (tag_id);


--
-- Name: tasks_skill_name_like; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX tasks_skill_name_like ON tasks_skill USING btree (name varchar_pattern_ops);


--
-- Name: tasks_skill_name_nl_like; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX tasks_skill_name_nl_like ON tasks_skill USING btree (name_nl varchar_pattern_ops);


--
-- Name: tasks_task_author_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX tasks_task_author_id ON tasks_task USING btree (author_id);


--
-- Name: tasks_task_project_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX tasks_task_project_id ON tasks_task USING btree (project_id);


--
-- Name: tasks_task_skill_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX tasks_task_skill_id ON tasks_task USING btree (skill_id);


--
-- Name: tasks_taskfile_author_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX tasks_taskfile_author_id ON tasks_taskfile USING btree (author_id);


--
-- Name: tasks_taskfile_task_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX tasks_taskfile_task_id ON tasks_taskfile USING btree (task_id);


--
-- Name: tasks_taskmember_member_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX tasks_taskmember_member_id ON tasks_taskmember USING btree (member_id);


--
-- Name: tasks_taskmember_task_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX tasks_taskmember_task_id ON tasks_taskmember USING btree (task_id);


--
-- Name: tests_person_children_from_person_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX tests_person_children_from_person_id ON tests_person_children USING btree (from_person_id);


--
-- Name: tests_person_children_to_person_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX tests_person_children_to_person_id ON tests_person_children USING btree (to_person_id);


--
-- Name: tests_person_name_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX tests_person_name_id ON tests_person USING btree (name_id);


--
-- Name: tests_person_notes_note_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX tests_person_notes_note_id ON tests_person_notes USING btree (note_id);


--
-- Name: tests_person_notes_person_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX tests_person_notes_person_id ON tests_person_notes USING btree (person_id);


--
-- Name: tests_sluggedtestmodel_slug; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX tests_sluggedtestmodel_slug ON tests_sluggedtestmodel USING btree (slug);


--
-- Name: tests_sluggedtestmodel_slug_like; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX tests_sluggedtestmodel_slug_like ON tests_sluggedtestmodel USING btree (slug varchar_pattern_ops);


--
-- Name: tests_testagregatemodel_testmodel_pk_ptr_id_like; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX tests_testagregatemodel_testmodel_pk_ptr_id_like ON tests_testagregatemodel USING btree (testmodel_pk_ptr_id varchar_pattern_ops);


--
-- Name: tests_testmanytomanymodel_many_testmanytomanymodel_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX tests_testmanytomanymodel_many_testmanytomanymodel_id ON tests_testmanytomanymodel_many USING btree (testmanytomanymodel_id);


--
-- Name: tests_testmanytomanymodel_many_testmanytomanymodel_id_like; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX tests_testmanytomanymodel_many_testmanytomanymodel_id_like ON tests_testmanytomanymodel_many USING btree (testmanytomanymodel_id varchar_pattern_ops);


--
-- Name: tests_testmanytomanymodel_many_testmodel_field_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX tests_testmanytomanymodel_many_testmodel_field_id ON tests_testmanytomanymodel_many USING btree (testmodel_field_id);


--
-- Name: tests_testmanytomanymodel_testmodel_pk_ptr_id_like; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX tests_testmanytomanymodel_testmodel_pk_ptr_id_like ON tests_testmanytomanymodel USING btree (testmodel_pk_ptr_id varchar_pattern_ops);


--
-- Name: tests_testmodel_pk_uuid_field_like; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX tests_testmodel_pk_uuid_field_like ON tests_testmodel_pk USING btree (uuid_field varchar_pattern_ops);


--
-- Name: thumbnail_kvstore_key_like; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX thumbnail_kvstore_key_like ON thumbnail_kvstore USING btree (key varchar_pattern_ops);


--
-- Name: wallposts_mediawallpostphoto_author_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX wallposts_mediawallpostphoto_author_id ON wallposts_mediawallpostphoto USING btree (author_id);


--
-- Name: wallposts_mediawallpostphoto_editor_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX wallposts_mediawallpostphoto_editor_id ON wallposts_mediawallpostphoto USING btree (editor_id);


--
-- Name: wallposts_mediawallpostphoto_mediawallpost_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX wallposts_mediawallpostphoto_mediawallpost_id ON wallposts_mediawallpostphoto USING btree (mediawallpost_id);


--
-- Name: wallposts_reaction_author_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX wallposts_reaction_author_id ON wallposts_reaction USING btree (author_id);


--
-- Name: wallposts_reaction_editor_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX wallposts_reaction_editor_id ON wallposts_reaction USING btree (editor_id);


--
-- Name: wallposts_reaction_wallpost_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX wallposts_reaction_wallpost_id ON wallposts_reaction USING btree (wallpost_id);


--
-- Name: wallposts_systemwallpost_related_type_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX wallposts_systemwallpost_related_type_id ON wallposts_systemwallpost USING btree (related_type_id);


--
-- Name: wallposts_wallpost_author_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX wallposts_wallpost_author_id ON wallposts_wallpost USING btree (author_id);


--
-- Name: wallposts_wallpost_content_type_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX wallposts_wallpost_content_type_id ON wallposts_wallpost USING btree (content_type_id);


--
-- Name: wallposts_wallpost_editor_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX wallposts_wallpost_editor_id ON wallposts_wallpost USING btree (editor_id);


--
-- Name: wallposts_wallpost_polymorphic_ctype_id; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX wallposts_wallpost_polymorphic_ctype_id ON wallposts_wallpost USING btree (polymorphic_ctype_id);


--
-- Name: account_bank_country_id_refs_id_64796f4e; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY organizations_organization
    ADD CONSTRAINT account_bank_country_id_refs_id_64796f4e FOREIGN KEY (account_bank_country_id) REFERENCES geo_country(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_group_permissions_permission_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_permission_id_fkey FOREIGN KEY (permission_id) REFERENCES auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: author_id_refs_id_19f2c26a; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY wallposts_reaction
    ADD CONSTRAINT author_id_refs_id_19f2c26a FOREIGN KEY (author_id) REFERENCES accounts_bluebottleuser(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: author_id_refs_id_1fd1e6c5; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY banners_slide
    ADD CONSTRAINT author_id_refs_id_1fd1e6c5 FOREIGN KEY (author_id) REFERENCES accounts_bluebottleuser(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: author_id_refs_id_245000e6; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY wallposts_wallpost
    ADD CONSTRAINT author_id_refs_id_245000e6 FOREIGN KEY (author_id) REFERENCES accounts_bluebottleuser(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: author_id_refs_id_423e462e; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY pages_page
    ADD CONSTRAINT author_id_refs_id_423e462e FOREIGN KEY (author_id) REFERENCES accounts_bluebottleuser(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: author_id_refs_id_4b876806; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY tasks_task
    ADD CONSTRAINT author_id_refs_id_4b876806 FOREIGN KEY (author_id) REFERENCES accounts_bluebottleuser(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: author_id_refs_id_4e71209f; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY pages_contactmessage
    ADD CONSTRAINT author_id_refs_id_4e71209f FOREIGN KEY (author_id) REFERENCES accounts_bluebottleuser(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: author_id_refs_id_5685a250; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY quotes_quote
    ADD CONSTRAINT author_id_refs_id_5685a250 FOREIGN KEY (author_id) REFERENCES accounts_bluebottleuser(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: author_id_refs_id_6979ba50; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY tasks_taskfile
    ADD CONSTRAINT author_id_refs_id_6979ba50 FOREIGN KEY (author_id) REFERENCES accounts_bluebottleuser(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: author_id_refs_id_ab104ed2; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY wallposts_mediawallpostphoto
    ADD CONSTRAINT author_id_refs_id_ab104ed2 FOREIGN KEY (author_id) REFERENCES accounts_bluebottleuser(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: author_id_refs_id_b9b4b013; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY blogs_blogpost
    ADD CONSTRAINT author_id_refs_id_b9b4b013 FOREIGN KEY (author_id) REFERENCES accounts_bluebottleuser(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: author_id_refs_id_f32a2173; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY organizations_organizationdocument
    ADD CONSTRAINT author_id_refs_id_f32a2173 FOREIGN KEY (author_id) REFERENCES accounts_bluebottleuser(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: bank_mutation_id_refs_id_4f3c9268; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY payouts_bankmutationline
    ADD CONSTRAINT bank_mutation_id_refs_id_4f3c9268 FOREIGN KEY (bank_mutation_id) REFERENCES payouts_bankmutation(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: blogcategory_id_refs_id_33f0ae10; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY blogs_blogpost_categories
    ADD CONSTRAINT blogcategory_id_refs_id_33f0ae10 FOREIGN KEY (blogcategory_id) REFERENCES blogs_blogcategory(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: blogpost_id_refs_id_a343ee7c; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY blogs_blogpost_categories
    ADD CONSTRAINT blogpost_id_refs_id_a343ee7c FOREIGN KEY (blogpost_id) REFERENCES blogs_blogpost(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: blogpost_id_refs_id_b68d6a64; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY blogs_blogpost_countries
    ADD CONSTRAINT blogpost_id_refs_id_b68d6a64 FOREIGN KEY (blogpost_id) REFERENCES blogs_blogpost(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: bluebottleuser_id_refs_id_00516181; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY accounts_bluebottleuser_user_permissions
    ADD CONSTRAINT bluebottleuser_id_refs_id_00516181 FOREIGN KEY (bluebottleuser_id) REFERENCES accounts_bluebottleuser(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: bluebottleuser_id_refs_id_87beb27c; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY accounts_bluebottleuser_groups
    ADD CONSTRAINT bluebottleuser_id_refs_id_87beb27c FOREIGN KEY (bluebottleuser_id) REFERENCES accounts_bluebottleuser(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: coach_id_refs_id_00849aea; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY projects_project
    ADD CONSTRAINT coach_id_refs_id_00849aea FOREIGN KEY (coach_id) REFERENCES accounts_bluebottleuser(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: contact_id_refs_id_9cbc4372; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY vouchers_customvoucherrequest
    ADD CONSTRAINT contact_id_refs_id_9cbc4372 FOREIGN KEY (contact_id) REFERENCES accounts_bluebottleuser(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: content_type_id_refs_id_01d42cdf; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY taggit_taggeditem
    ADD CONSTRAINT content_type_id_refs_id_01d42cdf FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: content_type_id_refs_id_858aa98c; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY wallposts_wallpost
    ADD CONSTRAINT content_type_id_refs_id_858aa98c FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: content_type_id_refs_id_d043b34a; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY auth_permission
    ADD CONSTRAINT content_type_id_refs_id_d043b34a FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: content_type_id_refs_id_ffafe769; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY love_lovedeclaration
    ADD CONSTRAINT content_type_id_refs_id_ffafe769 FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: contentitem_ptr_id_refs_id_5c779195; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY contentitem_oembeditem_oembeditem
    ADD CONSTRAINT contentitem_ptr_id_refs_id_5c779195 FOREIGN KEY (contentitem_ptr_id) REFERENCES fluent_contents_contentitem(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: contentitem_ptr_id_refs_id_750f6db7; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY contentitem_rawhtml_rawhtmlitem
    ADD CONSTRAINT contentitem_ptr_id_refs_id_750f6db7 FOREIGN KEY (contentitem_ptr_id) REFERENCES fluent_contents_contentitem(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: contentitem_ptr_id_refs_id_c1ae5a62; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY contentitem_text_textitem
    ADD CONSTRAINT contentitem_ptr_id_refs_id_c1ae5a62 FOREIGN KEY (contentitem_ptr_id) REFERENCES fluent_contents_contentitem(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: contentitem_ptr_id_refs_id_e2f9bb30; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY contentitem_contentplugins_pictureitem
    ADD CONSTRAINT contentitem_ptr_id_refs_id_e2f9bb30 FOREIGN KEY (contentitem_ptr_id) REFERENCES fluent_contents_contentitem(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: country_id_refs_id_4f1cad9c; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY accounts_useraddress
    ADD CONSTRAINT country_id_refs_id_4f1cad9c FOREIGN KEY (country_id) REFERENCES geo_country(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: country_id_refs_id_6021296c; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY projects_projectpitch
    ADD CONSTRAINT country_id_refs_id_6021296c FOREIGN KEY (country_id) REFERENCES geo_country(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: country_id_refs_id_64796f4e; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY organizations_organization
    ADD CONSTRAINT country_id_refs_id_64796f4e FOREIGN KEY (country_id) REFERENCES geo_country(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: country_id_refs_id_bb9fc248; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY blogs_blogpost_countries
    ADD CONSTRAINT country_id_refs_id_bb9fc248 FOREIGN KEY (country_id) REFERENCES geo_country(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: country_id_refs_id_ce2db457; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY projects_projectplan
    ADD CONSTRAINT country_id_refs_id_ce2db457 FOREIGN KEY (country_id) REFERENCES geo_country(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: crontab_id_refs_id_286da0d1; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY djcelery_periodictask
    ADD CONSTRAINT crontab_id_refs_id_286da0d1 FOREIGN KEY (crontab_id) REFERENCES djcelery_crontabschedule(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_admin_log_content_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY django_admin_log
    ADD CONSTRAINT django_admin_log_content_type_id_fkey FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: docdata_payment_order_id_refs_payment_ptr_id_0d2ea97d; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY cowry_docdata_docdatapaymentlogentry
    ADD CONSTRAINT docdata_payment_order_id_refs_payment_ptr_id_0d2ea97d FOREIGN KEY (docdata_payment_order_id) REFERENCES cowry_docdata_docdatapaymentorder(payment_ptr_id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: docdata_payment_order_id_refs_payment_ptr_id_1fd01801; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY cowry_docdata_docdatapayment
    ADD CONSTRAINT docdata_payment_order_id_refs_payment_ptr_id_1fd01801 FOREIGN KEY (docdata_payment_order_id) REFERENCES cowry_docdata_docdatapaymentorder(payment_ptr_id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: docdatapayment_ptr_id_refs_id_3fb140d6; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY cowry_docdata_docdatawebdirectdirectdebit
    ADD CONSTRAINT docdatapayment_ptr_id_refs_id_3fb140d6 FOREIGN KEY (docdatapayment_ptr_id) REFERENCES cowry_docdata_docdatapayment(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: editor_id_refs_id_19f2c26a; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY wallposts_reaction
    ADD CONSTRAINT editor_id_refs_id_19f2c26a FOREIGN KEY (editor_id) REFERENCES accounts_bluebottleuser(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: editor_id_refs_id_245000e6; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY wallposts_wallpost
    ADD CONSTRAINT editor_id_refs_id_245000e6 FOREIGN KEY (editor_id) REFERENCES accounts_bluebottleuser(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: editor_id_refs_id_ab104ed2; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY wallposts_mediawallpostphoto
    ADD CONSTRAINT editor_id_refs_id_ab104ed2 FOREIGN KEY (editor_id) REFERENCES accounts_bluebottleuser(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: from_person_id_refs_id_43c8c30c; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY tests_person_children
    ADD CONSTRAINT from_person_id_refs_id_43c8c30c FOREIGN KEY (from_person_id) REFERENCES tests_person(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: fundraiser_id_refs_id_48b2a41b; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY fund_donation
    ADD CONSTRAINT fundraiser_id_refs_id_48b2a41b FOREIGN KEY (fundraiser_id) REFERENCES fundraisers_fundraiser(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: group_id_refs_id_98a483ff; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY accounts_bluebottleuser_groups
    ADD CONSTRAINT group_id_refs_id_98a483ff FOREIGN KEY (group_id) REFERENCES auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: group_id_refs_id_f4b32aac; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT group_id_refs_id_f4b32aac FOREIGN KEY (group_id) REFERENCES auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: interval_id_refs_id_1829f358; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY djcelery_periodictask
    ADD CONSTRAINT interval_id_refs_id_1829f358 FOREIGN KEY (interval_id) REFERENCES djcelery_intervalschedule(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: mediawallpost_id_refs_wallpost_ptr_id_92d4ab8e; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY wallposts_mediawallpostphoto
    ADD CONSTRAINT mediawallpost_id_refs_wallpost_ptr_id_92d4ab8e FOREIGN KEY (mediawallpost_id) REFERENCES wallposts_mediawallpost(wallpost_ptr_id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: member_id_refs_id_861b83e0; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY tasks_taskmember
    ADD CONSTRAINT member_id_refs_id_861b83e0 FOREIGN KEY (member_id) REFERENCES accounts_bluebottleuser(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: order_id_refs_id_0e0f062d; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY vouchers_voucher
    ADD CONSTRAINT order_id_refs_id_0e0f062d FOREIGN KEY (order_id) REFERENCES fund_order(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: order_id_refs_id_784844c3; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY fund_donation
    ADD CONSTRAINT order_id_refs_id_784844c3 FOREIGN KEY (order_id) REFERENCES fund_order(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: order_id_refs_id_bea6af0c; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY cowry_payment
    ADD CONSTRAINT order_id_refs_id_bea6af0c FOREIGN KEY (order_id) REFERENCES fund_order(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: organization_id_refs_id_1c91eaaf; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY organizations_organizationmember
    ADD CONSTRAINT organization_id_refs_id_1c91eaaf FOREIGN KEY (organization_id) REFERENCES organizations_organization(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: organization_id_refs_id_bbf94826; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY organizations_organizationdocument
    ADD CONSTRAINT organization_id_refs_id_bbf94826 FOREIGN KEY (organization_id) REFERENCES organizations_organization(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: organization_id_refs_id_e6b32650; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY projects_projectplan
    ADD CONSTRAINT organization_id_refs_id_e6b32650 FOREIGN KEY (organization_id) REFERENCES organizations_organization(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: owner_id_refs_id_00849aea; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY projects_project
    ADD CONSTRAINT owner_id_refs_id_00849aea FOREIGN KEY (owner_id) REFERENCES accounts_bluebottleuser(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: owner_id_refs_id_be2e6d23; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY fundraisers_fundraiser
    ADD CONSTRAINT owner_id_refs_id_be2e6d23 FOREIGN KEY (owner_id) REFERENCES accounts_bluebottleuser(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: parent_type_id_refs_id_a0f06b12; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY fluent_contents_placeholder
    ADD CONSTRAINT parent_type_id_refs_id_a0f06b12 FOREIGN KEY (parent_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: parent_type_id_refs_id_b2e67e62; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY fluent_contents_contentitem
    ADD CONSTRAINT parent_type_id_refs_id_b2e67e62 FOREIGN KEY (parent_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: partner_organization_id_refs_id_2bcec5fc; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY projects_project
    ADD CONSTRAINT partner_organization_id_refs_id_2bcec5fc FOREIGN KEY (partner_organization_id) REFERENCES projects_partnerorganization(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: payment_ptr_id_refs_id_e656046e; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY cowry_docdata_docdatapaymentorder
    ADD CONSTRAINT payment_ptr_id_refs_id_e656046e FOREIGN KEY (payment_ptr_id) REFERENCES cowry_payment(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: payout_id_refs_id_97adf095; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY payouts_bankmutationline
    ADD CONSTRAINT payout_id_refs_id_97adf095 FOREIGN KEY (payout_id) REFERENCES payouts_payout(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: permission_id_refs_id_b705fa48; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY accounts_bluebottleuser_user_permissions
    ADD CONSTRAINT permission_id_refs_id_b705fa48 FOREIGN KEY (permission_id) REFERENCES auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: person_id_refs_id_0c4ebe52; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY tests_person_notes
    ADD CONSTRAINT person_id_refs_id_0c4ebe52 FOREIGN KEY (person_id) REFERENCES tests_person(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: placeholder_id_refs_id_8e1f1b78; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY fluent_contents_contentitem
    ADD CONSTRAINT placeholder_id_refs_id_8e1f1b78 FOREIGN KEY (placeholder_id) REFERENCES fluent_contents_placeholder(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: polymorphic_ctype_id_refs_id_858aa98c; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY wallposts_wallpost
    ADD CONSTRAINT polymorphic_ctype_id_refs_id_858aa98c FOREIGN KEY (polymorphic_ctype_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: polymorphic_ctype_id_refs_id_a290b957; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY cowry_payment
    ADD CONSTRAINT polymorphic_ctype_id_refs_id_a290b957 FOREIGN KEY (polymorphic_ctype_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: polymorphic_ctype_id_refs_id_ae3116c2; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY cowry_docdata_docdatapayment
    ADD CONSTRAINT polymorphic_ctype_id_refs_id_ae3116c2 FOREIGN KEY (polymorphic_ctype_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: polymorphic_ctype_id_refs_id_b2e67e62; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY fluent_contents_contentitem
    ADD CONSTRAINT polymorphic_ctype_id_refs_id_b2e67e62 FOREIGN KEY (polymorphic_ctype_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: project_id_refs_id_01907c29; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY fundraisers_fundraiser
    ADD CONSTRAINT project_id_refs_id_01907c29 FOREIGN KEY (project_id) REFERENCES projects_project(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: project_id_refs_id_1b9cfb33; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY fund_donation
    ADD CONSTRAINT project_id_refs_id_1b9cfb33 FOREIGN KEY (project_id) REFERENCES projects_project(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: project_id_refs_id_21e8e674; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY projects_projectresult
    ADD CONSTRAINT project_id_refs_id_21e8e674 FOREIGN KEY (project_id) REFERENCES projects_project(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: project_id_refs_id_36f7716c; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY projects_projectcampaign
    ADD CONSTRAINT project_id_refs_id_36f7716c FOREIGN KEY (project_id) REFERENCES projects_project(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: project_id_refs_id_4ef2746e; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY tasks_task
    ADD CONSTRAINT project_id_refs_id_4ef2746e FOREIGN KEY (project_id) REFERENCES projects_project(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: project_id_refs_id_604abf8b; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY payouts_payout
    ADD CONSTRAINT project_id_refs_id_604abf8b FOREIGN KEY (project_id) REFERENCES projects_project(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: project_id_refs_id_a2cbb1b9; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY projects_projectphaselog
    ADD CONSTRAINT project_id_refs_id_a2cbb1b9 FOREIGN KEY (project_id) REFERENCES projects_project(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: project_id_refs_id_d3b01567; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY projects_projectplan
    ADD CONSTRAINT project_id_refs_id_d3b01567 FOREIGN KEY (project_id) REFERENCES projects_project(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: project_id_refs_id_f43ba9a4; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY projects_projectpitch
    ADD CONSTRAINT project_id_refs_id_f43ba9a4 FOREIGN KEY (project_id) REFERENCES projects_project(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: project_plan_id_refs_id_62897bfc; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY projects_projectbudgetline
    ADD CONSTRAINT project_plan_id_refs_id_62897bfc FOREIGN KEY (project_plan_id) REFERENCES projects_projectplan(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: project_plan_id_refs_id_908deb4b; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY projects_projectambassador
    ADD CONSTRAINT project_plan_id_refs_id_908deb4b FOREIGN KEY (project_plan_id) REFERENCES projects_projectplan(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: receiver_id_refs_id_872b16f5; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY vouchers_voucher
    ADD CONSTRAINT receiver_id_refs_id_872b16f5 FOREIGN KEY (receiver_id) REFERENCES accounts_bluebottleuser(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: region_id_refs_id_2135f371; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY geo_subregion
    ADD CONSTRAINT region_id_refs_id_2135f371 FOREIGN KEY (region_id) REFERENCES geo_region(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: related_type_id_refs_id_d37c45d3; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY wallposts_systemwallpost
    ADD CONSTRAINT related_type_id_refs_id_d37c45d3 FOREIGN KEY (related_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: sender_id_refs_id_872b16f5; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY vouchers_voucher
    ADD CONSTRAINT sender_id_refs_id_872b16f5 FOREIGN KEY (sender_id) REFERENCES accounts_bluebottleuser(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: skill_id_refs_id_82830aff; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY tasks_task
    ADD CONSTRAINT skill_id_refs_id_82830aff FOREIGN KEY (skill_id) REFERENCES tasks_skill(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: subregion_id_refs_id_8ed0be82; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY geo_country
    ADD CONSTRAINT subregion_id_refs_id_8ed0be82 FOREIGN KEY (subregion_id) REFERENCES geo_subregion(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: tag_id_refs_id_c23fda9d; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY taggit_taggeditem
    ADD CONSTRAINT tag_id_refs_id_c23fda9d FOREIGN KEY (tag_id) REFERENCES taggit_tag(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: task_id_refs_id_0f9ed58e; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY tasks_taskfile
    ADD CONSTRAINT task_id_refs_id_0f9ed58e FOREIGN KEY (task_id) REFERENCES tasks_task(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: task_id_refs_id_e6a84bbf; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY tasks_taskmember
    ADD CONSTRAINT task_id_refs_id_e6a84bbf FOREIGN KEY (task_id) REFERENCES tasks_task(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: testmanytomanymodel_id_refs_testmodel_pk_ptr_id_6315ca71; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY tests_testmanytomanymodel_many
    ADD CONSTRAINT testmanytomanymodel_id_refs_testmodel_pk_ptr_id_6315ca71 FOREIGN KEY (testmanytomanymodel_id) REFERENCES tests_testmanytomanymodel(testmodel_pk_ptr_id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: tests_childsluggedtestmodel_sluggedtestmodel_ptr_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY tests_childsluggedtestmodel
    ADD CONSTRAINT tests_childsluggedtestmodel_sluggedtestmodel_ptr_id_fkey FOREIGN KEY (sluggedtestmodel_ptr_id) REFERENCES tests_sluggedtestmodel(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: tests_person_name_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY tests_person
    ADD CONSTRAINT tests_person_name_id_fkey FOREIGN KEY (name_id) REFERENCES tests_name(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: tests_person_notes_note_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY tests_person_notes
    ADD CONSTRAINT tests_person_notes_note_id_fkey FOREIGN KEY (note_id) REFERENCES tests_note(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: tests_testagregatemodel_testmodel_pk_ptr_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY tests_testagregatemodel
    ADD CONSTRAINT tests_testagregatemodel_testmodel_pk_ptr_id_fkey FOREIGN KEY (testmodel_pk_ptr_id) REFERENCES tests_testmodel_pk(uuid_field) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: tests_testmanytomanymodel_many_testmodel_field_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY tests_testmanytomanymodel_many
    ADD CONSTRAINT tests_testmanytomanymodel_many_testmodel_field_id_fkey FOREIGN KEY (testmodel_field_id) REFERENCES tests_testmodel_field(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: tests_testmanytomanymodel_testmodel_pk_ptr_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY tests_testmanytomanymodel
    ADD CONSTRAINT tests_testmanytomanymodel_testmodel_pk_ptr_id_fkey FOREIGN KEY (testmodel_pk_ptr_id) REFERENCES tests_testmodel_pk(uuid_field) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: theme_id_refs_id_8d479809; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY projects_projectpitch
    ADD CONSTRAINT theme_id_refs_id_8d479809 FOREIGN KEY (theme_id) REFERENCES projects_projecttheme(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: theme_id_refs_id_e9f7d0d1; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY projects_projectplan
    ADD CONSTRAINT theme_id_refs_id_e9f7d0d1 FOREIGN KEY (theme_id) REFERENCES projects_projecttheme(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: to_person_id_refs_id_43c8c30c; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY tests_person_children
    ADD CONSTRAINT to_person_id_refs_id_43c8c30c FOREIGN KEY (to_person_id) REFERENCES tests_person(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: user_id_refs_id_0fae8b4a; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY fund_order
    ADD CONSTRAINT user_id_refs_id_0fae8b4a FOREIGN KEY (user_id) REFERENCES accounts_bluebottleuser(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: user_id_refs_id_3ee0ca96; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY social_auth_usersocialauth
    ADD CONSTRAINT user_id_refs_id_3ee0ca96 FOREIGN KEY (user_id) REFERENCES accounts_bluebottleuser(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: user_id_refs_id_495b3c89; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY organizations_organizationmember
    ADD CONSTRAINT user_id_refs_id_495b3c89 FOREIGN KEY (user_id) REFERENCES accounts_bluebottleuser(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: user_id_refs_id_5685a250; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY quotes_quote
    ADD CONSTRAINT user_id_refs_id_5685a250 FOREIGN KEY (user_id) REFERENCES accounts_bluebottleuser(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: user_id_refs_id_79415003; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY love_lovedeclaration
    ADD CONSTRAINT user_id_refs_id_79415003 FOREIGN KEY (user_id) REFERENCES accounts_bluebottleuser(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: user_id_refs_id_84e63574; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY fund_donation
    ADD CONSTRAINT user_id_refs_id_84e63574 FOREIGN KEY (user_id) REFERENCES accounts_bluebottleuser(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: user_id_refs_id_8731bda9; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY admin_tools_dashboard_preferences
    ADD CONSTRAINT user_id_refs_id_8731bda9 FOREIGN KEY (user_id) REFERENCES accounts_bluebottleuser(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: user_id_refs_id_91141083; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY fund_recurringdirectdebitpayment
    ADD CONSTRAINT user_id_refs_id_91141083 FOREIGN KEY (user_id) REFERENCES accounts_bluebottleuser(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: user_id_refs_id_a2e64058; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY admin_tools_menu_bookmark
    ADD CONSTRAINT user_id_refs_id_a2e64058 FOREIGN KEY (user_id) REFERENCES accounts_bluebottleuser(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: user_id_refs_id_d63735d0; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY accounts_useraddress
    ADD CONSTRAINT user_id_refs_id_d63735d0 FOREIGN KEY (user_id) REFERENCES accounts_bluebottleuser(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: voucher_id_refs_id_ff7475d8; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY fund_donation
    ADD CONSTRAINT voucher_id_refs_id_ff7475d8 FOREIGN KEY (voucher_id) REFERENCES vouchers_voucher(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: wallpost_id_refs_id_bad3e69d; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY wallposts_reaction
    ADD CONSTRAINT wallpost_id_refs_id_bad3e69d FOREIGN KEY (wallpost_id) REFERENCES wallposts_wallpost(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: wallpost_ptr_id_refs_id_07f15c19; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY wallposts_systemwallpost
    ADD CONSTRAINT wallpost_ptr_id_refs_id_07f15c19 FOREIGN KEY (wallpost_ptr_id) REFERENCES wallposts_wallpost(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: wallpost_ptr_id_refs_id_25930a7b; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY wallposts_mediawallpost
    ADD CONSTRAINT wallpost_ptr_id_refs_id_25930a7b FOREIGN KEY (wallpost_ptr_id) REFERENCES wallposts_wallpost(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: wallpost_ptr_id_refs_id_67d61a0a; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY wallposts_textwallpost
    ADD CONSTRAINT wallpost_ptr_id_refs_id_67d61a0a FOREIGN KEY (wallpost_ptr_id) REFERENCES wallposts_wallpost(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: worker_id_refs_id_6fd8ce95; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY djcelery_taskstate
    ADD CONSTRAINT worker_id_refs_id_6fd8ce95 FOREIGN KEY (worker_id) REFERENCES djcelery_workerstate(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: public; Type: ACL; Schema: -; Owner: -
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

