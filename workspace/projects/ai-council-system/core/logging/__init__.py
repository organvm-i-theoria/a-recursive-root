"""
Logging System for AI Council

Comprehensive logging with structured output, performance tracking,
and debate-specific logging.
"""

from .logger import (
    LoggerManager,
    DebateLogger,
    PerformanceLogger,
    LogFormat,
    LogLevel,
    setup_logging,
    get_logger,
    get_debate_logger,
    get_performance_logger,
)

__all__ = [
    'LoggerManager',
    'DebateLogger',
    'PerformanceLogger',
    'LogFormat',
    'LogLevel',
    'setup_logging',
    'get_logger',
    'get_debate_logger',
    'get_performance_logger',
]
