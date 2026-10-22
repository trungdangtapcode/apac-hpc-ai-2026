"""Reject changed assets before starting a GPU model worker."""
from pathlib import Path
import json
from asset_identity import verify_asset_identity
print(json.dumps(verify_asset_identity(Path(__file__).parent/'asset-verification.json', '/scratch/models/Qwen3-235B-A22B-Instruct-2507-FP8', '/scratch/enroot-images/sglang-harbor.sqsh'),indent=2))
