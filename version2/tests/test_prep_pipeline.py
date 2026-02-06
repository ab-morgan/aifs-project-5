from unittest.mock import patch
from prep.prep_runner import run_prep


@patch("prep.prep_runner.compute_embeddings")
@patch("prep.prep_runner.compute_stats")
@patch("prep.prep_runner.verify_data")
def test_run_prep(mock_verify, mock_stats, mock_embed):
    run_prep()
    mock_verify.assert_called_once()
    mock_embed.assert_called_once()
    mock_stats.assert_called_once()
