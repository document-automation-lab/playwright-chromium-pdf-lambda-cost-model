#!/usr/bin/env python3
"""Playwright Chromium AWS Lambda PDF Cost Model."""
import argparse
import sys

def calculate_lambda_pdf(monthly_invocations, memory_mb=2048, avg_duration_sec=3.5):
    # AWS Lambda pricing (us-east-1 x86):
    # Memory: 2048 MB = $0.0000000333 per ms ($0.0000333 per second)
    # Execution cost
    exec_cost = monthly_invocations * (avg_duration_sec * 0.0000333)
    request_cost = (monthly_invocations / 1000000) * 0.20
    lambda_infra = exec_cost + request_cost

    # CloudWatch Logs & S3 storage for intermediate assets
    supporting_infra = 18.0

    # Maintenance: 3.5 hrs/mo managing Lambda layer sizes (Chromium > 50MB limit) & cold starts
    labor_cost = 3.5 * 65.0
    total_lambda_tco = lambda_infra + supporting_infra + labor_cost

    # Managed API alternative
    if monthly_invocations <= 3000:
        api_tier = "Basic ($19/mo)"
        api_cost = 19.0
    elif monthly_invocations <= 12000:
        api_tier = "Standard ($69/mo)"
        api_cost = 69.0
    else:
        api_tier = "Enterprise ($139/mo)"
        api_cost = 139.0

    savings = total_lambda_tco - api_cost
    return {
        "monthly_invocations": monthly_invocations,
        "lambda_infra": lambda_infra,
        "supporting_infra": supporting_infra,
        "labor_cost": labor_cost,
        "total_tco": total_lambda_tco,
        "api_tier": api_tier,
        "api_cost": api_cost,
        "savings": savings
    }

def main():
    parser = argparse.ArgumentParser(description="Playwright Chromium AWS Lambda PDF Cost Model")
    parser.add_argument("--invocations", type=int, default=10000, help="Monthly PDF rendering invocations (default: 10,000)")
    args = parser.parse_args()

    r = calculate_lambda_pdf(args.invocations)
    print("=" * 68)
    print(" Serverless AWS Lambda + Playwright PDF Infrastructure TCO")
    print("=" * 68)
    print(f" Monthly Invocations          : {r['monthly_invocations']:,} executions")
    print(f" Lambda Compute Charges       : ${r['lambda_infra']:.2f}/mo")
    print(f" Storage & Log Telemetry      : ${r['supporting_infra']:.2f}/mo")
    print(f" Layer Size & Ops Labor       : ${r['labor_cost']:.2f}/mo")
    print(f" Total Self-Hosted Lambda TCO : ${r['total_tco']:.2f}/mo")
    print("-" * 68)
    print(f" Managed REST API Tier        : {r['api_tier']}")
    print(f" Net Monthly Savings          : ${r['savings']:.2f}/mo ({(r['savings']/r['total_tco'])*100:.1f}%)")
    print("=" * 68)
    return 0

if __name__ == "__main__":
    sys.exit(main())
