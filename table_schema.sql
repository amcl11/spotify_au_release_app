--
-- PostgreSQL database dump
--

-- Dumped from database version 15.6 (Ubuntu 15.6-1.pgdg20.04+1)
-- Dumped by pg_dump version 15.3

-- Started on 2024-03-09 01:10:30 AEDT

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 218 (class 1259 OID 1403689)
-- Name: nmf_spotify_coverage; Type: TABLE; Schema: public; Owner: ucmiyvvhfaztau
--

CREATE TABLE public.nmf_spotify_coverage (
    "Date" text NOT NULL,
    "Artist" text NOT NULL,
    "Title" text NOT NULL,
    "Playlist" text NOT NULL,
    "Position" integer NOT NULL,
    "Followers" integer NOT NULL,
    "Image_URL" text,
    "Cover_Artist" text
);


ALTER TABLE public.nmf_spotify_coverage OWNER TO ucmiyvvhfaztau;

--
-- TOC entry 4318 (class 0 OID 0)
-- Dependencies: 850
-- Name: LANGUAGE plpgsql; Type: ACL; Schema: -; Owner: postgres
--

GRANT ALL ON LANGUAGE plpgsql TO ucmiyvvhfaztau;


-- Completed on 2024-03-09 01:10:49 AEDT

--
-- PostgreSQL database dump complete
--

