--
-- PostgreSQL database dump
--

\restrict RKHRWhK2o3ohA5emlU0bIzbqLQjk4ll20uJ9PMhHiGaje25drEJS28HccuUdpfc

-- Dumped from database version 18.4
-- Dumped by pg_dump version 18.4

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: pgcrypto; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;


--
-- Name: EXTENSION pgcrypto; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION pgcrypto IS 'cryptographic functions';


--
-- Name: add_risk_assessment(integer, numeric, character varying, character varying, text, integer); Type: PROCEDURE; Schema: public; Owner: -
--

CREATE PROCEDURE public.add_risk_assessment(IN p_company_id integer, IN p_risk_score numeric, IN p_risk_level character varying, IN p_model_version character varying, IN p_explanation text, IN p_assessed_by integer)
    LANGUAGE plpgsql
    AS $$
BEGIN

    INSERT INTO risk_assessment
    (
        company_id,
        risk_score,
        risk_level,
        model_version,
        explanation,
        assessed_by
    )
    VALUES
    (
        p_company_id,
        p_risk_score,
        p_risk_level,
        p_model_version,
        p_explanation,
        p_assessed_by
    );

END;
$$;


--
-- Name: compute_risk_delta(integer, integer); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.compute_risk_delta(p_company_id integer, p_days integer) RETURNS numeric
    LANGUAGE plpgsql
    AS $$
DECLARE
    latest NUMERIC;
    past NUMERIC;
BEGIN
    SELECT risk_score INTO latest FROM risk_assessment
    WHERE company_id = p_company_id ORDER BY assessed_at DESC LIMIT 1;

    SELECT risk_score INTO past FROM risk_assessment
    WHERE company_id = p_company_id
      AND assessed_at <= now() - (p_days || ' days')::interval
    ORDER BY assessed_at DESC LIMIT 1;

    RETURN COALESCE(latest, 0) - COALESCE(past, 0);
END;
$$;


--
-- Name: get_company_risk_level(integer); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.get_company_risk_level(p_company_id integer) RETURNS character varying
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_risk_level VARCHAR(20);
BEGIN
    SELECT risk_level
    INTO v_risk_level
    FROM risk_assessment
    WHERE company_id = p_company_id
    ORDER BY assessed_at DESC
    LIMIT 1;

    RETURN v_risk_level;
END;
$$;


--
-- Name: log_risk_assessment(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.log_risk_assessment() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    INSERT INTO public.risk_assessment_audit
        (
            risk_assessment_id,
            company_id,
            risk_score,
            action_type,
            risk_level,
            model_version,
            explanation,
            assessed_by
        )
    VALUES
        (
            NEW.risk_assessment_id,
            NEW.company_id,
            NEW.risk_score,
            'INSERT',
            NEW.risk_level,
            NEW.model_version,
            NEW.explanation,
            NEW.assessed_by
        );

    RETURN NEW;
END;
$$;


--
-- Name: prevent_risk_assessment_modification(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.prevent_risk_assessment_modification() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    RAISE EXCEPTION
        'Risk assessments are append-only. UPDATE and DELETE operations are not allowed. Create a new assessment instead.';
END;
$$;


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: companies; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.companies (
    company_id integer NOT NULL,
    company_name character varying(200) NOT NULL,
    registration_number character varying(100),
    industry character varying(100),
    country character varying(100),
    annual_revenue numeric(18,2),
    employee_count integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT chk_company_revenue CHECK (((annual_revenue IS NULL) OR (annual_revenue >= (0)::numeric))),
    CONSTRAINT chk_employee_count CHECK (((employee_count IS NULL) OR (employee_count >= 0)))
);


--
-- Name: companies_company_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.companies_company_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: companies_company_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.companies_company_id_seq OWNED BY public.companies.company_id;


--
-- Name: risk_assessment; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.risk_assessment (
    risk_assessment_id integer NOT NULL,
    company_id integer NOT NULL,
    risk_score numeric(5,2) NOT NULL,
    risk_level character varying(20) NOT NULL,
    assessed_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    model_version character varying(50),
    explanation text,
    assessed_by integer,
    CONSTRAINT chk_risk_level CHECK (((risk_level)::text = ANY ((ARRAY['LOW'::character varying, 'MEDIUM'::character varying, 'HIGH'::character varying, 'CRITICAL'::character varying])::text[]))),
    CONSTRAINT chk_risk_score CHECK (((risk_score >= (0)::numeric) AND (risk_score <= (100)::numeric)))
);


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    user_id integer NOT NULL,
    role_id integer NOT NULL,
    full_name character varying(100) NOT NULL,
    email character varying(255) NOT NULL,
    password_hash text NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    failed_login_attempts integer DEFAULT 0 NOT NULL,
    locked_until timestamp without time zone,
    last_login_at timestamp without time zone,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT chk_failed_login_attempts CHECK ((failed_login_attempts >= 0))
);


--
-- Name: company_risk_view; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.company_risk_view AS
 SELECT ra.risk_assessment_id,
    c.company_id,
    c.company_name,
    c.industry,
    c.country,
    c.annual_revenue,
    c.employee_count,
    ra.risk_score,
    ra.risk_level,
    ra.model_version,
    u.email AS assessed_by,
    ra.assessed_at
   FROM ((public.risk_assessment ra
     JOIN public.companies c ON ((ra.company_id = c.company_id)))
     LEFT JOIN public.users u ON ((ra.assessed_by = u.user_id)));


--
-- Name: financial_records; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.financial_records (
    financial_record_id integer NOT NULL,
    company_id integer NOT NULL,
    fiscal_year integer NOT NULL,
    revenue numeric(18,2),
    net_profit numeric(18,2),
    total_assets numeric(18,2),
    total_liabilities numeric(18,2),
    total_debt numeric(18,2),
    shareholders_equity numeric(18,2),
    operating_cash_flow numeric(18,2),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT chk_assets CHECK (((total_assets IS NULL) OR (total_assets >= (0)::numeric))),
    CONSTRAINT chk_debt CHECK (((total_debt IS NULL) OR (total_debt >= (0)::numeric))),
    CONSTRAINT chk_fiscal_year CHECK ((fiscal_year >= 1900)),
    CONSTRAINT chk_liabilities CHECK (((total_liabilities IS NULL) OR (total_liabilities >= (0)::numeric))),
    CONSTRAINT chk_revenue CHECK (((revenue IS NULL) OR (revenue >= (0)::numeric)))
);


--
-- Name: financial_records_financial_record_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.financial_records_financial_record_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: financial_records_financial_record_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.financial_records_financial_record_id_seq OWNED BY public.financial_records.financial_record_id;


--
-- Name: password_reset_tokens; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.password_reset_tokens (
    token_id integer NOT NULL,
    user_id integer NOT NULL,
    token_hash text NOT NULL,
    expires_at timestamp without time zone NOT NULL,
    used_at timestamp without time zone,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: password_reset_tokens_token_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.password_reset_tokens_token_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: password_reset_tokens_token_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.password_reset_tokens_token_id_seq OWNED BY public.password_reset_tokens.token_id;


--
-- Name: risk_assessment_audit; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.risk_assessment_audit (
    audit_id integer NOT NULL,
    risk_assessment_id integer NOT NULL,
    company_id integer NOT NULL,
    risk_score numeric NOT NULL,
    logged_at timestamp without time zone DEFAULT now() NOT NULL,
    action_type character varying(20) NOT NULL,
    risk_level character varying(20) NOT NULL,
    model_version character varying(50),
    explanation text,
    assessed_by integer,
    CONSTRAINT chk_audit_action_type CHECK (((action_type)::text = 'INSERT'::text)),
    CONSTRAINT chk_audit_risk_level CHECK (((risk_level)::text = ANY ((ARRAY['LOW'::character varying, 'MEDIUM'::character varying, 'HIGH'::character varying, 'CRITICAL'::character varying])::text[]))),
    CONSTRAINT chk_audit_risk_score CHECK (((risk_score >= (0)::numeric) AND (risk_score <= (100)::numeric)))
);


--
-- Name: risk_assessment_audit_audit_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.risk_assessment_audit_audit_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: risk_assessment_audit_audit_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.risk_assessment_audit_audit_id_seq OWNED BY public.risk_assessment_audit.audit_id;


--
-- Name: risk_assessment_risk_assessment_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.risk_assessment_risk_assessment_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: risk_assessment_risk_assessment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.risk_assessment_risk_assessment_id_seq OWNED BY public.risk_assessment.risk_assessment_id;


--
-- Name: roles; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.roles (
    role_id integer NOT NULL,
    role_name character varying(50) NOT NULL,
    description text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: roles_role_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.roles_role_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: roles_role_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.roles_role_id_seq OWNED BY public.roles.role_id;


--
-- Name: user_sessions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_sessions (
    session_id integer NOT NULL,
    user_id integer NOT NULL,
    token_hash text NOT NULL,
    expires_at timestamp without time zone NOT NULL,
    revoked_at timestamp without time zone,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: user_sessions_session_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.user_sessions_session_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: user_sessions_session_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.user_sessions_session_id_seq OWNED BY public.user_sessions.session_id;


--
-- Name: users_user_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.users_user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: users_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.users_user_id_seq OWNED BY public.users.user_id;


--
-- Name: companies company_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.companies ALTER COLUMN company_id SET DEFAULT nextval('public.companies_company_id_seq'::regclass);


--
-- Name: financial_records financial_record_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.financial_records ALTER COLUMN financial_record_id SET DEFAULT nextval('public.financial_records_financial_record_id_seq'::regclass);


--
-- Name: password_reset_tokens token_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.password_reset_tokens ALTER COLUMN token_id SET DEFAULT nextval('public.password_reset_tokens_token_id_seq'::regclass);


--
-- Name: risk_assessment risk_assessment_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.risk_assessment ALTER COLUMN risk_assessment_id SET DEFAULT nextval('public.risk_assessment_risk_assessment_id_seq'::regclass);


--
-- Name: risk_assessment_audit audit_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.risk_assessment_audit ALTER COLUMN audit_id SET DEFAULT nextval('public.risk_assessment_audit_audit_id_seq'::regclass);


--
-- Name: roles role_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.roles ALTER COLUMN role_id SET DEFAULT nextval('public.roles_role_id_seq'::regclass);


--
-- Name: user_sessions session_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_sessions ALTER COLUMN session_id SET DEFAULT nextval('public.user_sessions_session_id_seq'::regclass);


--
-- Name: users user_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users ALTER COLUMN user_id SET DEFAULT nextval('public.users_user_id_seq'::regclass);


--
-- Name: companies companies_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.companies
    ADD CONSTRAINT companies_pkey PRIMARY KEY (company_id);


--
-- Name: companies companies_registration_number_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.companies
    ADD CONSTRAINT companies_registration_number_key UNIQUE (registration_number);


--
-- Name: financial_records financial_records_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.financial_records
    ADD CONSTRAINT financial_records_pkey PRIMARY KEY (financial_record_id);


--
-- Name: password_reset_tokens password_reset_tokens_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.password_reset_tokens
    ADD CONSTRAINT password_reset_tokens_pkey PRIMARY KEY (token_id);


--
-- Name: password_reset_tokens password_reset_tokens_token_hash_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.password_reset_tokens
    ADD CONSTRAINT password_reset_tokens_token_hash_key UNIQUE (token_hash);


--
-- Name: risk_assessment_audit risk_assessment_audit_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.risk_assessment_audit
    ADD CONSTRAINT risk_assessment_audit_pkey PRIMARY KEY (audit_id);


--
-- Name: risk_assessment risk_assessment_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.risk_assessment
    ADD CONSTRAINT risk_assessment_pkey PRIMARY KEY (risk_assessment_id);


--
-- Name: roles roles_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (role_id);


--
-- Name: roles roles_role_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_role_name_key UNIQUE (role_name);


--
-- Name: financial_records uq_company_fiscal_year; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.financial_records
    ADD CONSTRAINT uq_company_fiscal_year UNIQUE (company_id, fiscal_year);


--
-- Name: user_sessions user_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_sessions
    ADD CONSTRAINT user_sessions_pkey PRIMARY KEY (session_id);


--
-- Name: user_sessions user_sessions_token_hash_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_sessions
    ADD CONSTRAINT user_sessions_token_hash_key UNIQUE (token_hash);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (user_id);


--
-- Name: idx_risk_assessment_company_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_risk_assessment_company_date ON public.risk_assessment USING btree (company_id, assessed_at DESC);


--
-- Name: risk_assessment trg_log_risk_assessment; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_log_risk_assessment AFTER INSERT ON public.risk_assessment FOR EACH ROW EXECUTE FUNCTION public.log_risk_assessment();


--
-- Name: risk_assessment trg_prevent_risk_assessment_modification; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_prevent_risk_assessment_modification BEFORE DELETE OR UPDATE ON public.risk_assessment FOR EACH ROW EXECUTE FUNCTION public.prevent_risk_assessment_modification();


--
-- Name: financial_records fk_financial_company; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.financial_records
    ADD CONSTRAINT fk_financial_company FOREIGN KEY (company_id) REFERENCES public.companies(company_id) ON DELETE CASCADE;


--
-- Name: password_reset_tokens fk_reset_user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.password_reset_tokens
    ADD CONSTRAINT fk_reset_user FOREIGN KEY (user_id) REFERENCES public.users(user_id) ON DELETE CASCADE;


--
-- Name: risk_assessment fk_risk_company; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.risk_assessment
    ADD CONSTRAINT fk_risk_company FOREIGN KEY (company_id) REFERENCES public.companies(company_id) ON DELETE CASCADE;


--
-- Name: risk_assessment fk_risk_user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.risk_assessment
    ADD CONSTRAINT fk_risk_user FOREIGN KEY (assessed_by) REFERENCES public.users(user_id) ON DELETE SET NULL;


--
-- Name: user_sessions fk_session_user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_sessions
    ADD CONSTRAINT fk_session_user FOREIGN KEY (user_id) REFERENCES public.users(user_id) ON DELETE CASCADE;


--
-- Name: users fk_users_role; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT fk_users_role FOREIGN KEY (role_id) REFERENCES public.roles(role_id);


--
-- PostgreSQL database dump complete
--

\unrestrict RKHRWhK2o3ohA5emlU0bIzbqLQjk4ll20uJ9PMhHiGaje25drEJS28HccuUdpfc
