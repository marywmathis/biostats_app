import streamlit as st
import numpy as np
import pandas as pd

from tests.registry import REGISTRY, get_allowed_tests
from recommendations import recommend_test