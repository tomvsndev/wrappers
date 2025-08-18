import os
from typing import Union, List, Any


def get_env_var(
        name: str,
        default: Union[str, int, float, bool],
        var_type: type,
        logger: object
) -> Union[str, int, float, bool]:
    """
    Safely get and convert environment variable with validation

    Args:
        name: Environment variable name
        default: Default value if not set
        var_type: Expected type (str, int, float, bool)
        logger: Logger instance for reporting

    Returns:
        Converted environment variable value
    """
    value = os.getenv(name)
    if value is None:
        logger.info(f"[get_env_var] Using default value for {name}: {default}")
        return default

    try:
        if var_type == bool:
            # Handle boolean values specially
            if value.lower() in ('true', '1', 't', 'y', 'yes'):
                return True
            elif value.lower() in ('false', '0', 'f', 'n', 'no'):
                return False
            else:
                raise ValueError(f"[get_env_var] Invalid boolean value: {value}")
        elif var_type == int:
            return int(value)
        elif var_type == float:
            return float(value)
        return var_type(value)
    except ValueError as e:
        logger.warning(f"[get_env_var] Invalid value for {name}={value} (expected {var_type.__name__}). Using default: {default}")
        return default


def validate_path(path: str, path_type: str, default: str, logger: object) -> str:
    """
    Validate that a path exists or create it if it's the tuning directory

    Args:
        path: Path to validate
        path_type: 'models' or 'tuning'
        default: Default path to use if validation fails
        logger: Logger instance

    Returns:
        Validated path
    """
    if path_type == 'models' and not os.path.exists(path):
        logger.error(f"[validate_path] Models directory {path} doesn't exist. Using default: {default}")
        os.makedirs(default, exist_ok=True)
        return default
    elif path_type == 'tuning':
        os.makedirs(path, exist_ok=True)
        return path
    return path


def validate_positive(value: Union[int, float], name: str, default: Union[int, float], logger: object) -> Union[
    int, float]:
    """Validate that a numeric value is positive"""
    if value <= 0:
        logger.warning(f"[validate_positive] {name} must be greater than 0. Using default: {default}")
        return default
    return value
def check_env_keys(required_keys:List[str],logger:object):
    enviro = os.environ
    missing_keys = []
    for key in required_keys:
        if key not in enviro.keys():
            missing_keys.append(key)
            logger.error(f'[check_env_keys] key : {key} doesnt exists in .env please add it before running this app.')
    return missing_keys
def load_config(logger: object,required_keys:List[str]) -> Any:
    """Load and validate all configuration from environment variables"""
    missing_keys =  check_env_keys(required_keys,logger)
    if missing_keys:
        return missing_keys

    config = {}

    # Path configurations
    config['models_directory'] = validate_path(
        os.getenv("MODELS_DIR", "./models"),
        'models',
        "./models",
        logger
    )

    config['tuning_directory'] = validate_path(
        os.getenv("TUNING_DIR", "./tuning"),
        'tuning',
        "./tuning",
        logger
    )

    # Numeric configurations with validation
    config['default_n_ctx'] = validate_positive(
        get_env_var("DEFAULT_N_CTX", 4096, int, logger),
        "DEFAULT_N_CTX",
        4096,
        logger
    )

    config['default_n_gpu_layers'] = get_env_var(
        "DEFAULT_N_GPU_LAYERS", -1, int, logger
    )
    if config['default_n_gpu_layers'] < -1:
        logger.warning("DEFAULT_N_GPU_LAYERS must be >= -1. Using default: -1")
        config['default_n_gpu_layers'] = -1

    config['default_n_threads'] = get_env_var(
        "DEFAULT_N_THREADS", None, int, logger
    )
    if config['default_n_threads'] is not None and config['default_n_threads'] <= 0:
        logger.warning("DEFAULT_N_THREADS must be > 0. Using default: None")
        config['default_n_threads'] = None

    config['target_tokens_per_second'] = validate_positive(
        get_env_var("TARGET_TOKENS_PER_SECOND", 30.0, float, logger),
        "TARGET_TOKENS_PER_SECOND",
        30.0,
        logger
    )

    config['max_tuning_time'] = validate_positive(
        get_env_var("MAX_TUNING_TIME_SECONDS", 300, int, logger),
        "MAX_TUNING_TIME_SECONDS",
        300,
        logger
    )

    config['min_context_size'] = validate_positive(
        get_env_var("MIN_CONTEXT_SIZE", 8000, int, logger),
        "MIN_CONTEXT_SIZE",
        8000,
        logger
    )

    # Boolean configurations
    config['use_mmap'] = get_env_var("USE_MMAP", True, bool, logger)
    config['use_mlock'] = get_env_var("USE_MLOCK", True, bool, logger)
    config['verbose_llama'] = get_env_var("VERBOSE", False, bool, logger)
    config['auto_tune_enabled'] = get_env_var("AUTO_TUNE_ENABLED", True, bool, logger)

    return config

