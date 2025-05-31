import streamlit as st
from ui.main_interface import run_app
from core.config import setup_logging, clear_proxy_env_vars

if __name__ == "__main__":
    # Initial configurations like logging and proxy clearing are now in core.config
    # and typically run when core.config is imported.
    # If they need to be explicitly called, do it here.
    # setup_logging() # Already called at import of config
    # clear_proxy_env_vars() # Already called at import of config
    
    run_app()