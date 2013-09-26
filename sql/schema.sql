--
-- PostgreSQL database dump
--

SET client_encoding = 'UTF8';
SET standard_conforming_strings = off;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET escape_string_warning = off;

--
-- Name: plpgsql; Type: PROCEDURAL LANGUAGE; Schema: -; Owner: OWNER-LOGIN
--

-- Uncomment if plpgsql is not installed
--CREATE PROCEDURAL LANGUAGE plpgsql;


ALTER PROCEDURAL LANGUAGE plpgsql OWNER TO OWNER-LOGIN;

SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: client; Type: TABLE; Schema: public; Owner: OWNER-LOGIN; Tablespace: 
--

CREATE TABLE client (
    id integer NOT NULL,
    login character varying,
    password character varying,
    project integer,
    level integer,
    allowed boolean,
    mail character varying,
    creationdate timestamp without time zone DEFAULT now(),
    lastlogin timestamp without time zone DEFAULT now(),
    subscription boolean DEFAULT false
);


ALTER TABLE public.client OWNER TO OWNER-LOGIN;

--
-- Name: comment; Type: TABLE; Schema: public; Owner: OWNER-LOGIN; Tablespace: 
--

CREATE TABLE comment (
    id integer NOT NULL,
    author integer,
    ticket integer,
    creationdate timestamp without time zone DEFAULT now(),
    content text
);


ALTER TABLE public.comment OWNER TO OWNER-LOGIN;

--
-- Name: ticket; Type: TABLE; Schema: public; Owner: OWNER-LOGIN; Tablespace: 
--

CREATE TABLE ticket (
    id integer NOT NULL,
    relativeid integer,
    project integer,
    category integer,
    name character varying,
    description text,
    status integer,
    severity integer,
    creator integer,
    maintainer integer,
    creationdate timestamp without time zone DEFAULT now(),
    lastmodification timestamp without time zone DEFAULT now(),
    lastmessageid character varying
);


ALTER TABLE public.ticket OWNER TO OWNER-LOGIN;

--
-- Name: file; Type: TABLE; Schema: public; Owner: OWNER-LOGIN; Tablespace: 
--

CREATE TABLE file (
    id integer NOT NULL,
    project integer,
    ticket integer,
    type character varying(10),
    name text,
    creationdate timestamp without time zone DEFAULT now()
);


ALTER TABLE public.file OWNER TO OWNER-LOGIN;

--
-- Name: project; Type: TABLE; Schema: public; Owner: OWNER-LOGIN; Tablespace: 
--

CREATE TABLE project (
    id integer NOT NULL,
    name character varying,
    webname character varying,
    owner integer,
    lang character varying(2) DEFAULT 'en'::character varying
);


ALTER TABLE public.project OWNER TO OWNER-LOGIN;

--
-- Name: concat_comments(integer); Type: FUNCTION; Schema: public; Owner: OWNER-LOGIN
--

CREATE FUNCTION concat_comments(id_comment integer) RETURNS text
    AS $$
DECLARE 
result text := 'coucou';
c text := '';
BEGIN
FOR c IN SELECT content FROM Comment WHERE Comment.ticket = id_comment ORDER BY Comment.id ASC
LOOP
result := result || ' ' || c;
END LOOP;
RETURN result;
END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.concat_comments(id_comment integer) OWNER TO OWNER-LOGIN;

--
-- Name: next_relative_id(); Type: FUNCTION; Schema: public; Owner: OWNER-LOGIN
--

CREATE FUNCTION next_relative_id() RETURNS trigger
    AS $$
DECLARE
    max_relative_id integer;
BEGIN
    SELECT max(relativeID) INTO max_relative_id FROM Ticket WHERE project = NEW.project AND category = NEW.category;
    IF max_relative_id IS NULL THEN
        max_relative_id := 0;
    END IF;
    max_relative_id := max_relative_id + 1;
    UPDATE Ticket SET relativeID = max_relative_id WHERE id=NEW.id;
    RETURN NEW;
END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.next_relative_id() OWNER TO OWNER-LOGIN;

--
-- Name: no_accents(text); Type: FUNCTION; Schema: public; Owner: OWNER-LOGIN
--

CREATE FUNCTION no_accents(str text) RETURNS text
    AS $$
DECLARE
    res text := str;
BEGIN
    -- vowels
    res := translate(res, 'áàäâåã', 'aaaaaa');
    res := translate(res, 'ÁÀÄÂÅÃ', 'AAAAAA');
    res := translate(res, 'éèëê', 'eeee');
    res := translate(res, 'ÉÈËÊ', 'ZEEE');
    res := translate(res, 'íìïî', 'iiii');
    res := translate(res, 'ÍÌÏÎ', 'IIII');
    res := translate(res, 'óòöôõ', 'ooooo');
    res := translate(res, 'ÓÒÖÔÕ', 'OOOOO');
    res := translate(res, 'úùüû', 'uuuu');
    res := translate(res, 'ÚÙÜÛ', 'UUUU');
    res := translate(res, 'ÿ', 'y');
    res := translate(res, 'Ÿ', 'Y');
    -- consonants
    res := translate(res, 'çÇ', 'cC');
    res := translate(res, 'ñÑ', 'nN');
    RETURN res;
END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.no_accents(str text) OWNER TO OWNER-LOGIN;

--
-- Name: update_last_modification_after_new_comment(); Type: FUNCTION; Schema: public; Owner: OWNER-LOGIN
--

CREATE FUNCTION update_last_modification_after_new_comment() RETURNS trigger
    AS $$
BEGIN
    UPDATE Ticket SET lastModification = current_timestamp WHERE id = NEW.ticket;
    RETURN NEW;
END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.update_last_modification_after_new_comment() OWNER TO OWNER-LOGIN;

--
-- Name: client_id_seq; Type: SEQUENCE; Schema: public; Owner: OWNER-LOGIN
--

CREATE SEQUENCE client_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.client_id_seq OWNER TO OWNER-LOGIN;

--
-- Name: client_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: OWNER-LOGIN
--

ALTER SEQUENCE client_id_seq OWNED BY client.id;


--
-- Name: comment_id_seq; Type: SEQUENCE; Schema: public; Owner: OWNER-LOGIN
--

CREATE SEQUENCE comment_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.comment_id_seq OWNER TO OWNER-LOGIN;

--
-- Name: comment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: OWNER-LOGIN
--

ALTER SEQUENCE comment_id_seq OWNED BY comment.id;


--
-- Name: ticket_id_seq; Type: SEQUENCE; Schema: public; Owner: OWNER-LOGIN
--

CREATE SEQUENCE ticket_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.ticket_id_seq OWNER TO OWNER-LOGIN;

--
-- Name: ticket_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: OWNER-LOGIN
--

ALTER SEQUENCE ticket_id_seq OWNED BY ticket.id;


--
-- Name: file_id_seq; Type: SEQUENCE; Schema: public; Owner: OWNER-LOGIN
--

CREATE SEQUENCE file_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.file_id_seq OWNER TO OWNER-LOGIN;

--
-- Name: file_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: OWNER-LOGIN
--

ALTER SEQUENCE file_id_seq OWNED BY file.id;


--
-- Name: project_id_seq; Type: SEQUENCE; Schema: public; Owner: OWNER-LOGIN
--

CREATE SEQUENCE project_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.project_id_seq OWNER TO OWNER-LOGIN;

--
-- Name: project_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: OWNER-LOGIN
--

ALTER SEQUENCE project_id_seq OWNED BY project.id;


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: OWNER-LOGIN
--

ALTER TABLE client ALTER COLUMN id SET DEFAULT nextval('client_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: OWNER-LOGIN
--

ALTER TABLE comment ALTER COLUMN id SET DEFAULT nextval('comment_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: OWNER-LOGIN
--

ALTER TABLE ticket ALTER COLUMN id SET DEFAULT nextval('ticket_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: OWNER-LOGIN
--

ALTER TABLE file ALTER COLUMN id SET DEFAULT nextval('file_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: OWNER-LOGIN
--

ALTER TABLE project ALTER COLUMN id SET DEFAULT nextval('project_id_seq'::regclass);


--
-- Name: client_pkey; Type: CONSTRAINT; Schema: public; Owner: OWNER-LOGIN; Tablespace: 
--

ALTER TABLE ONLY client
    ADD CONSTRAINT client_pkey PRIMARY KEY (id);


--
-- Name: comment_pkey; Type: CONSTRAINT; Schema: public; Owner: OWNER-LOGIN; Tablespace: 
--

ALTER TABLE ONLY comment
    ADD CONSTRAINT comment_pkey PRIMARY KEY (id);


--
-- Name: ticket_pkey; Type: CONSTRAINT; Schema: public; Owner: OWNER-LOGIN; Tablespace: 
--

ALTER TABLE ONLY ticket
    ADD CONSTRAINT ticket_pkey PRIMARY KEY (id);


--
-- Name: file_pkey; Type: CONSTRAINT; Schema: public; Owner: OWNER-LOGIN; Tablespace: 
--

ALTER TABLE ONLY file
    ADD CONSTRAINT file_pkey PRIMARY KEY (id);


--
-- Name: project_pkey; Type: CONSTRAINT; Schema: public; Owner: OWNER-LOGIN; Tablespace: 
--

ALTER TABLE ONLY project
    ADD CONSTRAINT project_pkey PRIMARY KEY (id);


--
-- Name: set_relative_id; Type: TRIGGER; Schema: public; Owner: OWNER-LOGIN
--

CREATE TRIGGER set_relative_id
    AFTER INSERT ON ticket
    FOR EACH ROW
    EXECUTE PROCEDURE next_relative_id();


--
-- Name: update_last_modification_after_new_comment; Type: TRIGGER; Schema: public; Owner: OWNER-LOGIN
--

CREATE TRIGGER update_last_modification_after_new_comment
    AFTER INSERT ON comment
    FOR EACH ROW
    EXECUTE PROCEDURE update_last_modification_after_new_comment();


--
-- Name: client_project_fkey; Type: FK CONSTRAINT; Schema: public; Owner: OWNER-LOGIN
--

ALTER TABLE ONLY client
    ADD CONSTRAINT client_project_fkey FOREIGN KEY (project) REFERENCES project(id);


--
-- Name: comment_author_fkey; Type: FK CONSTRAINT; Schema: public; Owner: OWNER-LOGIN
--

ALTER TABLE ONLY comment
    ADD CONSTRAINT comment_author_fkey FOREIGN KEY (author) REFERENCES client(id);


--
-- Name: comment_ticket_fkey; Type: FK CONSTRAINT; Schema: public; Owner: OWNER-LOGIN
--

ALTER TABLE ONLY comment
    ADD CONSTRAINT comment_ticket_fkey FOREIGN KEY (ticket) REFERENCES ticket(id);


--
-- Name: ticket_creator_fkey; Type: FK CONSTRAINT; Schema: public; Owner: OWNER-LOGIN
--

ALTER TABLE ONLY ticket
    ADD CONSTRAINT ticket_creator_fkey FOREIGN KEY (creator) REFERENCES client(id);


--
-- Name: ticket_project_fkey; Type: FK CONSTRAINT; Schema: public; Owner: OWNER-LOGIN
--

ALTER TABLE ONLY ticket
    ADD CONSTRAINT ticket_project_fkey FOREIGN KEY (project) REFERENCES project(id);


--
-- Name: file_project_fkey; Type: FK CONSTRAINT; Schema: public; Owner: OWNER-LOGIN
--

ALTER TABLE ONLY file
    ADD CONSTRAINT file_project_fkey FOREIGN KEY (project) REFERENCES project(id);


--
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

