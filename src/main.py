"""FastAPI application for Agent Hub.

This module provides a REST API endpoint for processing prompts.
"""

from __future__ import annotations

import logging

import structlog
from fastapi import FastAPI

from src.agents.factory import create_app_agent
from src.config import load_configuration
from src.k8s.manager import K8sManager
from src.library.fastapi.logging_middleware import logging_middleware
from src.logging_config import setup_logging
from src.routes.healthchecks import router as health_router
from src.routes.prompt import router as prompt_router

# Load configuration and setup logging
try:
    config = load_configuration()
    setup_logging(config.logging)
    logger = structlog.get_logger(__name__)
    logger.info("Configuration initialized")
    k8s_manager = K8sManager(config.k8s)
    logger.info("K8s Manager initialized")
    agent = create_app_agent(config)
    logger.info("Agent initialized with tools")
except Exception:
    # Fallback to standard logging if configuration fails
    logging.basicConfig(level=logging.INFO)
    fallback_logger = logging.getLogger(__name__)
    fallback_logger.exception("Failed to load configuration")
    raise

app: FastAPI = FastAPI(
    title="Agent Hub API",
    description="API for agent orchestration and prompt processing",
    version="1.0.0",
)

# Store global instances in app state for use in routes
app.state.agent = agent
app.state.k8s_manager = k8s_manager

# Register middleware
app.middleware("http")(logging_middleware)

# Register routers
app.include_router(health_router)
app.include_router(prompt_router)
