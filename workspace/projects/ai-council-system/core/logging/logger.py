"""
Comprehensive Logging System for AI Council

Provides structured logging with:
- Multiple output formats (JSON, text, colored console)
- Log levels and filtering
- Performance metrics
- Debate-specific logging
- Rotating file handlers
"""

import logging
import sys
import json
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from enum import Enum


class LogFormat(Enum):
    """Log output formats"""
    TEXT = "text"
    JSON = "json"
    COLORED = "colored"


class LogLevel(Enum):
    """Log levels"""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class ColoredFormatter(logging.Formatter):
    """Colored console output formatter"""

    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'       # Reset
    }

    def format(self, record):
        # Add color to level name
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = (
                f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"
            )

        # Format timestamp
        record.asctime = datetime.fromtimestamp(record.created).strftime(
            '%Y-%m-%d %H:%M:%S'
        )

        return super().format(record)


class JSONFormatter(logging.Formatter):
    """JSON output formatter"""

    def format(self, record):
        log_data = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }

        # Add extra fields
        if hasattr(record, 'debate_id'):
            log_data['debate_id'] = record.debate_id
        if hasattr(record, 'agent_id'):
            log_data['agent_id'] = record.agent_id
        if hasattr(record, 'duration'):
            log_data['duration'] = record.duration

        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)

        return json.dumps(log_data)


class DebateLogger:
    """
    Specialized logger for debate sessions

    Provides context-aware logging with debate and agent IDs
    """

    def __init__(self, logger: logging.Logger, debate_id: str):
        self.logger = logger
        self.debate_id = debate_id

    def _log(self, level: int, msg: str, agent_id: Optional[str] = None, **kwargs):
        """Internal log method with context"""
        extra = {
            'debate_id': self.debate_id,
        }
        if agent_id:
            extra['agent_id'] = agent_id

        extra.update(kwargs)
        self.logger.log(level, msg, extra=extra)

    def debug(self, msg: str, agent_id: Optional[str] = None, **kwargs):
        self._log(logging.DEBUG, msg, agent_id, **kwargs)

    def info(self, msg: str, agent_id: Optional[str] = None, **kwargs):
        self._log(logging.INFO, msg, agent_id, **kwargs)

    def warning(self, msg: str, agent_id: Optional[str] = None, **kwargs):
        self._log(logging.WARNING, msg, agent_id, **kwargs)

    def error(self, msg: str, agent_id: Optional[str] = None, **kwargs):
        self._log(logging.ERROR, msg, agent_id, **kwargs)

    def critical(self, msg: str, agent_id: Optional[str] = None, **kwargs):
        self._log(logging.CRITICAL, msg, agent_id, **kwargs)

    def log_agent_response(self, agent_id: str, response: str, duration: float):
        """Log agent response with timing"""
        self.info(
            f"Agent response generated",
            agent_id=agent_id,
            duration=duration,
            response_length=len(response)
        )

    def log_vote(self, agent_id: str, option: str, confidence: float):
        """Log agent vote"""
        self.info(
            f"Vote cast: {option}",
            agent_id=agent_id,
            option=option,
            confidence=confidence
        )

    def log_round_start(self, round_number: int):
        """Log debate round start"""
        self.info(f"Round {round_number} started", round=round_number)

    def log_round_end(self, round_number: int, duration: float):
        """Log debate round completion"""
        self.info(
            f"Round {round_number} completed",
            round=round_number,
            duration=duration
        )

    def log_debate_complete(self, duration: float, outcome: Dict[str, Any]):
        """Log debate completion"""
        self.info(
            "Debate completed",
            duration=duration,
            outcome=outcome
        )


class LoggerManager:
    """
    Central logging manager

    Sets up and configures all loggers for the application
    """

    def __init__(
        self,
        log_dir: str = "./logs",
        console_format: LogFormat = LogFormat.COLORED,
        file_format: LogFormat = LogFormat.JSON,
        console_level: LogLevel = LogLevel.INFO,
        file_level: LogLevel = LogLevel.DEBUG,
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5
    ):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.console_format = console_format
        self.file_format = file_format
        self.console_level = console_level
        self.file_level = file_level
        self.max_bytes = max_bytes
        self.backup_count = backup_count

        self._setup_root_logger()

    def _setup_root_logger(self):
        """Configure root logger"""
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)

        # Remove existing handlers
        root_logger.handlers.clear()

        # Add console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.console_level.value)
        console_handler.setFormatter(self._get_formatter(self.console_format))
        root_logger.addHandler(console_handler)

        # Add main file handler (rotating)
        main_log = self.log_dir / "ai_council.log"
        file_handler = RotatingFileHandler(
            main_log,
            maxBytes=self.max_bytes,
            backupCount=self.backup_count
        )
        file_handler.setLevel(self.file_level.value)
        file_handler.setFormatter(self._get_formatter(self.file_format))
        root_logger.addHandler(file_handler)

        # Add error file handler
        error_log = self.log_dir / "errors.log"
        error_handler = RotatingFileHandler(
            error_log,
            maxBytes=self.max_bytes,
            backupCount=self.backup_count
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(self._get_formatter(self.file_format))
        root_logger.addHandler(error_handler)

    def _get_formatter(self, format_type: LogFormat) -> logging.Formatter:
        """Get formatter for specified format"""
        if format_type == LogFormat.COLORED:
            return ColoredFormatter(
                '%(asctime)s | %(levelname)s | %(name)s | %(message)s'
            )
        elif format_type == LogFormat.JSON:
            return JSONFormatter()
        else:  # TEXT
            return logging.Formatter(
                '%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )

    def get_logger(self, name: str) -> logging.Logger:
        """Get named logger"""
        return logging.getLogger(name)

    def get_debate_logger(self, debate_id: str) -> DebateLogger:
        """Get debate-specific logger"""
        logger = logging.getLogger(f"debate.{debate_id}")

        # Add debate-specific file handler
        debate_log = self.log_dir / "debates" / f"{debate_id}.log"
        debate_log.parent.mkdir(parents=True, exist_ok=True)

        file_handler = RotatingFileHandler(
            debate_log,
            maxBytes=self.max_bytes,
            backupCount=2
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(self._get_formatter(self.file_format))
        logger.addHandler(file_handler)

        return DebateLogger(logger, debate_id)

    def get_component_logger(self, component: str) -> logging.Logger:
        """
        Get component-specific logger

        Components: agents, events, council, streaming, etc.
        """
        logger = logging.getLogger(component)

        # Add component-specific file handler
        component_log = self.log_dir / "components" / f"{component}.log"
        component_log.parent.mkdir(parents=True, exist_ok=True)

        file_handler = TimedRotatingFileHandler(
            component_log,
            when='midnight',
            interval=1,
            backupCount=7
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(self._get_formatter(self.file_format))
        logger.addHandler(file_handler)

        return logger

    def set_level(self, level: LogLevel, handler_type: str = "all"):
        """
        Change log level at runtime

        Args:
            level: New log level
            handler_type: "console", "file", or "all"
        """
        root_logger = logging.getLogger()

        for handler in root_logger.handlers:
            if handler_type == "all":
                handler.setLevel(level.value)
            elif handler_type == "console" and isinstance(handler, logging.StreamHandler):
                if not isinstance(handler, RotatingFileHandler):
                    handler.setLevel(level.value)
            elif handler_type == "file" and isinstance(handler, (RotatingFileHandler, TimedRotatingFileHandler)):
                handler.setLevel(level.value)


class PerformanceLogger:
    """Logger for performance metrics"""

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.metrics: Dict[str, list] = {}

    def log_duration(self, operation: str, duration: float, **kwargs):
        """Log operation duration"""
        if operation not in self.metrics:
            self.metrics[operation] = []

        self.metrics[operation].append(duration)

        self.logger.info(
            f"Performance: {operation}",
            extra={
                'operation': operation,
                'duration': duration,
                **kwargs
            }
        )

    def log_llm_call(
        self,
        provider: str,
        model: str,
        duration: float,
        tokens: int,
        cost: float = 0.0
    ):
        """Log LLM API call metrics"""
        self.log_duration(
            'llm_call',
            duration,
            provider=provider,
            model=model,
            tokens=tokens,
            cost=cost
        )

    def log_event_processing(self, count: int, duration: float):
        """Log event processing metrics"""
        self.log_duration(
            'event_processing',
            duration,
            event_count=count,
            rate=count / duration if duration > 0 else 0
        )

    def get_stats(self, operation: Optional[str] = None) -> Dict[str, Any]:
        """Get performance statistics"""
        if operation and operation in self.metrics:
            durations = self.metrics[operation]
            return {
                'operation': operation,
                'count': len(durations),
                'total': sum(durations),
                'avg': sum(durations) / len(durations),
                'min': min(durations),
                'max': max(durations),
            }

        # Return all stats
        return {
            op: self.get_stats(op)
            for op in self.metrics.keys()
        }


# Global logger instance
_logger_manager: Optional[LoggerManager] = None


def setup_logging(
    log_dir: str = "./logs",
    console_format: LogFormat = LogFormat.COLORED,
    file_format: LogFormat = LogFormat.JSON,
    console_level: LogLevel = LogLevel.INFO,
    file_level: LogLevel = LogLevel.DEBUG
) -> LoggerManager:
    """
    Setup global logging

    Should be called once at application startup
    """
    global _logger_manager
    _logger_manager = LoggerManager(
        log_dir=log_dir,
        console_format=console_format,
        file_format=file_format,
        console_level=console_level,
        file_level=file_level
    )
    return _logger_manager


def get_logger(name: str) -> logging.Logger:
    """Get named logger (convenience function)"""
    if _logger_manager:
        return _logger_manager.get_logger(name)
    return logging.getLogger(name)


def get_debate_logger(debate_id: str) -> DebateLogger:
    """Get debate logger (convenience function)"""
    if _logger_manager:
        return _logger_manager.get_debate_logger(debate_id)
    raise RuntimeError("Logging not initialized. Call setup_logging() first.")


def get_performance_logger(name: str) -> PerformanceLogger:
    """Get performance logger"""
    logger = get_logger(f"perf.{name}")
    return PerformanceLogger(logger)
