import argparse
import os
from dotenv import load_dotenv

load_dotenv()

from app import create_app  # noqa: E402
from app.seed import _seed  # noqa: E402

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--xlsx", required=True, help="Path to Case Study Data.xlsx")
    args = ap.parse_args()

    app = create_app()
    with app.app_context():
        if not os.path.exists(args.xlsx):
            raise SystemExit(f"XLSX not found: {args.xlsx}")
        _seed(args.xlsx)
        print("Seed completed")

if __name__ == "__main__":
    main()
