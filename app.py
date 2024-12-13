import os
import time
import gc
import psutil
from datetime import datetime
from dotenv import load_dotenv
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from modules import manage
import yaml
from contextlib import contextmanager
from typing import Dict, Any, Optional
import signal
import weakref
from collections import deque
from dataclasses import dataclass
import json

def verify_environment():
    """Verify all required environment variables are set"""
    required_vars = {
        'AZURE_TABLES_CONNECTION_STRING': 'Azure Tables connection string',
        'TELEGRAM_BOT_TOKEN': 'Telegram bot token',
        'TELEGRAM_CHAT_ID': 'Telegram chat ID'
    }

    missing = []
    for var, description in required_vars.items():
        value = os.getenv(var)
        if not value:
            missing.append(f"{var} ({description})")
        else:
            # Log masked version of sensitive values
            masked = value[:4] + '*' * (len(value) - 8) + value[-4:] if len(value) > 8 else '****'
            logging.info(f"Found {var}: {masked}")

    if missing:
        raise EnvironmentError(
            "Missing required environment variables:\n" +
            "\n".join(f"- {var}" for var in missing)
        )

@dataclass
class JobMetrics:
    """Stores metrics for a single job run"""
    start_time: datetime
    end_time: Optional[datetime] = None
    memory_before: float = 0
    memory_after: float = 0
    memory_peak: float = 0
    success: bool = False
    error: Optional[str] = None

class JobStats:
    """Manages job statistics"""
    def __init__(self, maxlen: int = 100):
        self.metrics = deque(maxlen=maxlen)
        self.current_job: Optional[JobMetrics] = None

    def start_job(self) -> None:
        """Record job start metrics"""
        self.current_job = JobMetrics(
            start_time=datetime.now(),
            memory_before=self._get_memory_usage()
        )

    def end_job(self, success: bool, error: Optional[str] = None) -> None:
        """Record job end metrics"""
        if self.current_job:
            self.current_job.end_time = datetime.now()
            self.current_job.memory_after = self._get_memory_usage()
            self.current_job.success = success
            self.current_job.error = error
            self.metrics.append(self.current_job)
            self._log_metrics(self.current_job)
            self.current_job = None

    def update_peak_memory(self) -> None:
        """Update peak memory usage during job execution"""
        if self.current_job:
            self.current_job.memory_peak = max(
                self.current_job.memory_peak,
                self._get_memory_usage()
            )

    @staticmethod
    def _get_memory_usage() -> float:
        """Get current memory usage in MB"""
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024

    def _log_metrics(self, metrics: JobMetrics) -> None:
        """Log job metrics"""
        duration = (metrics.end_time - metrics.start_time).total_seconds() if metrics.end_time else 0
        memory_diff = metrics.memory_after - metrics.memory_before

        log_data = {
            "timestamp": metrics.start_time.isoformat(),
            "duration_seconds": duration,
            "memory_before_mb": round(metrics.memory_before, 2),
            "memory_after_mb": round(metrics.memory_after, 2),
            "memory_peak_mb": round(metrics.memory_peak, 2),
            "memory_diff_mb": round(memory_diff, 2),
            "success": metrics.success,
            "error": metrics.error
        }

        logging.info("Job Statistics: %s", json.dumps(log_data, indent=2))

class ConfigValidator:
    """Validates configuration values"""
    @staticmethod
    def validate_config(config: Dict[str, Any]) -> bool:
        required_fields = {
            'city': str,
            'minimum_bedrooms': (int, float, str),
            'max_price_in_euros': (int, float),
            'km_radius': (int, float),
            'scrape_interval_in_minutes': (int, float)
        }

        try:
            # Check all required fields exist
            for field, field_type in required_fields.items():
                if field not in config:
                    raise ValueError(f"Missing required field: {field}")

                # Convert string values to appropriate types
                if isinstance(field_type, tuple):
                    if not isinstance(config[field], field_type):
                        config[field] = float(config[field])
                elif not isinstance(config[field], field_type):
                    raise TypeError(f"Field {field} must be of type {field_type}")

            # Validate specific field constraints
            if not config['city'].strip():
                raise ValueError("City cannot be empty")

            if float(config['minimum_bedrooms']) <= 0:
                raise ValueError("Minimum bedrooms must be greater than 0")

            if float(config['max_price_in_euros']) <= 0:
                raise ValueError("Maximum price must be greater than 0")

            if float(config['km_radius']) < 0:
                raise ValueError("Radius cannot be negative")

            return True

        except Exception as e:
            logging.error(f"Config validation error: {str(e)}")
            raise ValueError(f"Invalid configuration: {str(e)}")

class SchedulerManager:
    """Manages the APScheduler with proper cleanup"""
    def __init__(self, config_manager: 'ConfigManager'):
        self.config_manager = config_manager
        self.scheduler = BlockingScheduler()
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.azure_table_connection_string = os.getenv('AZURE_TABLES_CONNECTION_STRING')
        self.job_stats = JobStats(maxlen=100)

        # Set up signal handlers
        signal.signal(signal.SIGINT, self._shutdown)
        signal.signal(signal.SIGTERM, self._shutdown)

        # Keep track of running jobs
        self._active_jobs = weakref.WeakSet()

    def run_job(self) -> None:
        """Execute the job with proper resource management"""
        self.job_stats.start_job()

        try:
            config = self.config_manager.get_config()

            # Validate config before running
            ConfigValidator.validate_config(config)

            # Create job context
            job_context = {
                'city': config["city"].lower(),
                'minimum_bedrooms': str(config["minimum_bedrooms"]),
                'max_price_in_euros': str(config["max_price_in_euros"]),
                'km_radius': str(config["km_radius"]),
                'bot_token': self.bot_token,
                'chat_id': self.chat_id,
                'azure_table_connection_string': self.azure_table_connection_string
            }

            # Monitor peak memory during execution
            self.job_stats.update_peak_memory()

            # Execute job
            manage.cronjob(**job_context)

            # Clear job context
            del job_context

            # Force garbage collection
            gc.collect()

            self.job_stats.end_job(success=True)

        except Exception as e:
            self.job_stats.end_job(success=False, error=str(e))
            self._cleanup()
            raise

    def start(self) -> None:
        """Start the scheduler with proper error handling"""
        try:
            # Read config
            config = self.config_manager.get_config()

            # Validate config before running
            ConfigValidator.validate_config(config)

            logging.info(f"Scraping pararius every {config['scrape_interval_in_minutes']} minute")

            # Initial job run
            self.run_job()
            time.sleep(10)

            # Schedule recurring job
            self.scheduler.add_job(
                self.run_job,
                'interval',
                minutes=config["scrape_interval_in_minutes"],
                max_instances=1,  # Prevent job overlapping
                coalesce=True     # Combine missed runs
            )

            self.scheduler.start()

        except (KeyboardInterrupt, SystemExit):
            self._shutdown()
        except Exception as e:
            logging.error(f"Scheduler error: {e}")
            self._shutdown()

    def _cleanup(self) -> None:
        """Clean up resources"""
        try:
            # Clear any remaining job references
            self._active_jobs.clear()

            # Force garbage collection
            gc.collect()

        except Exception as e:
            logging.error(f"Cleanup error: {e}")

    def _shutdown(self, signum=None, frame=None) -> None:
        """Graceful shutdown handler"""
        logging.info("Initiating graceful shutdown...")
        try:
            if self.scheduler.running:
                self.scheduler.shutdown(wait=False)
            self._cleanup()
            logging.info("Shutdown completed successfully.")
        except Exception as e:
            logging.error(f"Error during shutdown: {e}")
        finally:
            exit(0)

class ConfigManager:
    """Manages configuration with proper resource handling"""
    def __init__(self, path: str = "config.yml"):
        self.path = path
        self.config: Dict[str, Any] = {}
        self._load_config()

    def _load_config(self) -> None:
        try:
            with open(self.path, "r") as file:
                self.config = yaml.safe_load(file)
            # Validate config on load
            ConfigValidator.validate_config(self.config)
        except Exception as e:
            logging.error(f"Error loading config: {e}")
            raise

    def get_config(self) -> Dict[str, Any]:
        return self.config.copy()

@contextmanager
def create_scheduler() -> SchedulerManager:
    """Context manager for scheduler lifecycle"""
    config_manager = ConfigManager()
    scheduler_manager = SchedulerManager(config_manager)
    try:
        yield scheduler_manager
    finally:
        scheduler_manager._cleanup()

def main():
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('scheduler.log')
        ]
    )
    try:
        # Load environment variables
        load_dotenv()

        # Verify environment
        logging.info("Verifying environment variables...")
        verify_environment()

        # Run scheduler with context manager
        with create_scheduler() as scheduler:
            scheduler.start()

    except EnvironmentError as e:
        logging.error(f"Environment configuration error: {e}")
        exit(1)
    except Exception as e:
        logging.error(f"Startup error: {e}")
        exit(1)

if __name__ == "__main__":
    main()
