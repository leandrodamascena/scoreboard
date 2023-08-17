import string
import pytest
import os
import boto3
import json
from typing import Any, Dict, List
from datetime import datetime
import random

from aws_lambda_powertools.utilities.parameters import get_parameter

@pytest.fixture
def stack_config():
    cfg = get_parameter(name=f"/service/scorecard/test/config")
    return json.loads(cfg)


@pytest.fixture
def scorecard_api_endpoint(stack_config: dict):
    return stack_config["ScoreEndpoint"]

@pytest.fixture
def scorecard_kinesis_stream(stack_config: dict):
    return stack_config["KinesisStream"]

@pytest.fixture
def scorecard_summarized_table(stack_config: dict):
    return stack_config["SummarizedTable"]

@pytest.fixture
def fake_player() -> List[Dict[str, Any]]:
    player: List[Dict[str, Any]] = [{
        "score": int(random.randint(0, 5)),
        "timestamp": str(datetime.now()),
        "player_name": f"TestIntegrationPowertools-{generate_random_string(10)}",
        "player_country": "Brazil",
        "player_level": "Level1",
        "player_os": "iOS"
    }]
    return player
    

def generate_random_string(length):
    characters = string.ascii_letters + string.digits  # Including both letters and digits
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string
