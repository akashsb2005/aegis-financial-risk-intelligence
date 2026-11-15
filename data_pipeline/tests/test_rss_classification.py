from data_pipeline.ingest_rss import classify_event


def test_classifies_common_financial_event_candidates():
    assert classify_event("Company announces quarterly results", "") == "EARNINGS"
    assert classify_event("Regulator opens antitrust investigation", "") == "REGULATORY"
    assert classify_event("Board approves dividend payout", "") == "DIVIDEND"


def test_unmatched_article_is_not_promoted_to_event():
    assert classify_event("Company launches a new website", "New product page") is None
