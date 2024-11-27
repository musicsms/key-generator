"""Configuration settings for the Key Generator application."""
import os
import logging
from logging.handlers import RotatingFileHandler

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(32)
    KEYS_DIR = os.path.abspath(os.environ.get('KEYS_DIR', 'keys'))
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    PROPAGATE_EXCEPTIONS = True

    # Logging configuration
    LOGGING_LEVEL = logging.INFO
    LOGGING_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOGGING_LOCATION = os.path.join(os.path.dirname(__file__), 'logs')
    
    @classmethod
    def configure_logging(cls, app):
        """Configure logging for the application."""
        # Ensure logs directory exists
        os.makedirs(cls.LOGGING_LOCATION, exist_ok=True)
        
        # Create a file handler
        log_file = os.path.join(cls.LOGGING_LOCATION, 'app.log')
        file_handler = RotatingFileHandler(
            log_file, 
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(cls.LOGGING_LEVEL)
        
        # Create a formatter
        formatter = logging.Formatter(cls.LOGGING_FORMAT)
        file_handler.setFormatter(formatter)
        
        # Add handler to the app's logger
        app.logger.addHandler(file_handler)
        app.logger.setLevel(cls.LOGGING_LEVEL)

class ProductionConfig(Config):
    """Production configuration."""
    ENV = 'production'
    DEBUG = False
    TESTING = False

class DevelopmentConfig(Config):
    """Development configuration."""
    ENV = 'development'
    DEBUG = True
    TESTING = False
    LOGGING_LEVEL = logging.DEBUG

class TestingConfig(Config):
    """Testing configuration."""
    ENV = 'testing'
    DEBUG = False
    TESTING = True
    WTF_CSRF_ENABLED = False

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': ProductionConfig
}
