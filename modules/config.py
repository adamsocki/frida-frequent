from pathlib import Path
from typing import Optional, List, Dict, Any
import logging
import sys
import yaml
# import conf


def load_config(config_path: Path = Path("config.yaml")) -> Dict[str, Any]:

    logger = logging.getLogger('frida_freq')

    """Load configuration from YAML file"""
    if not config_path.exists():
        logger.error(f"Config file not found: {config_path}")
        logger.info("Copy config.example.yaml to config.yaml and edit")
        sys.exit(1)
    else:
        logger.info(f"Config file found: {config_path}")


    with open(config_path) as f:
        return yaml.safe_load(f)
