import pandas as pd
import numpy as np
import xgboost as xgb
import shap
from sqlalchemy import create_engine
from fastapi import FastAPI

print("✓ pandas", pd.__version__)
print("✓ xgboost", xgb.__version__)
print("✓ shap", shap.__version__)
print("✓ All libraries loaded — you're ready to start Phase 1")
