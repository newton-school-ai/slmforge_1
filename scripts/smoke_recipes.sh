#!/usr/bin/env bash
# Smoke-test all four bundled recipes end-to-end.
# Used in CI (M10) and locally before tagging a release.

set -euo pipefail

for recipe in interview_coach feedback_summariser question_assistant iterative_editor; do
  echo "=== Smoke: $recipe ==="
  slmforge build --recipe "$recipe" --auto
done

echo "All recipes built. Run 'slmforge list' to see the build ids."
