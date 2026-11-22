#!/usr/bin/env bash
set -euo pipefail
gh api graphql -f query='query{viewer{contributionsCollection{contributionCalendar{totalContributions weeks{contributionDays{date contributionCount}}}}}}' > data/contributions.json
