-- Local development grants for the AEGIS market/evidence pipeline.
-- Run as a database administrator AFTER 02_market_evidence.sql.
-- Idempotent. No table data, ownership, or passwords are changed.
-- This intentionally grants only the market/evidence pipeline permissions.
-- Core application tables may require additional grants based on backend roles.
BEGIN;
GRANT USAGE ON SCHEMA public TO aegis_user;
GRANT SELECT ON TABLE public.companies, public.securities TO aegis_user;
GRANT SELECT, INSERT, UPDATE ON TABLE
    public.market_observations,
    public.financial_events,
    public.news_articles,
    public.model_predictions
TO aegis_user;
GRANT USAGE, SELECT ON SEQUENCE
    public.market_observations_observation_id_seq,
    public.financial_events_event_id_seq,
    public.news_articles_article_id_seq,
    public.model_predictions_prediction_id_seq
TO aegis_user;
COMMIT;
