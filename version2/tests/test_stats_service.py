from services.stats_service import load_stats_for_display


def test_load_stats_for_display(mock_supabase):
    client, table = mock_supabase
    table.select.return_value.execute.return_value.data = {
        "mean_norm": 1.23,
        "std_norm": 0.45,
    }

    stats = load_stats_for_display(client)
    assert stats["mean_norm"] == 1.23
