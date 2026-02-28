#!/bin/bash

# Script to manage branch protection for NewNepal-org repositories using GitHub Rulesets
# Usage: 
#   ./github-branch-protection.sh show
#   ./github-branch-protection.sh plan
#   ./github-branch-protection.sh enable <repo1> <repo2> ...
#   ./github-branch-protection.sh enable all

set -euo pipefail

ORG="NewNepal-org"

# Repos that have a test-and-lint CI job — these get required_status_checks
CI_REPOS=(
  "Jawafdehi"
  "NepalEntityService"
  "NepalEntityService-Tundikhel"
  "ngm"
  "org-admin-panel"
)

# Check if a repo has CI configured
has_ci() {
  local repo=$1
  for ci_repo in "${CI_REPOS[@]}"; do
    if [ "$ci_repo" = "$repo" ]; then
      return 0
    fi
  done
  return 1
}

# Function to show branch protection status
show_protection_status() {
  echo "Fetching repositories and their rulesets from $ORG..."
  echo ""
  printf "%-40s %-15s %-12s %s\n" "Repository" "Default Branch" "Protected" "Rulesets"
  printf "%-40s %-15s %-12s %s\n" "----------" "--------------" "---------" "--------"

  gh repo list $ORG \
    --limit 100 \
    --json name,defaultBranchRef \
    --jq '.[] | "\(.name):\(.defaultBranchRef.name)"' \
    | while IFS=: read -r repo branch; do
        # Check if rulesets exist (may fail for private repos)
        rulesets=$(gh api repos/$ORG/$repo/rulesets 2>/dev/null | jq -r 'if type == "array" then length else 0 end' || echo "0")
        
        if [ "$rulesets" -gt 0 ] 2>/dev/null; then
          protected="✓ Yes"
          ruleset_names=$(gh api repos/$ORG/$repo/rulesets 2>/dev/null | \
            jq -r 'if type == "array" then [.[].name] | join(", ") else "" end' | cut -c1-50 || echo "")
          printf "%-40s %-15s %-12s %s\n" "$repo" "$branch" "$protected" "$ruleset_names"
        else
          protected="✗ No"
          printf "%-40s %-15s %-12s %s\n" "$repo" "$branch" "$protected" "-"
        fi
      done

  echo ""
  echo "Done!"
}

# Delete all existing rulesets for a repository
delete_existing_rulesets() {
  local repo=$1
  
  local ruleset_ids
  ruleset_ids=$(gh api repos/$ORG/$repo/rulesets 2>/dev/null | jq -r 'if type == "array" then .[].id else empty end')
  
  if [ -z "$ruleset_ids" ]; then
    return
  fi
  
  for id in $ruleset_ids; do
    echo "  Deleting existing ruleset $id..."
    gh api --method DELETE repos/$ORG/$repo/rulesets/$id > /dev/null
  done
}

# Create Ruleset 1: Protect default branch (deletion + force push protection)
create_ruleset_1() {
  local repo=$1
  
  gh api \
    --method POST \
    repos/$ORG/$repo/rulesets \
    --input - > /dev/null <<EOF
{
  "name": "Protect default branch",
  "target": "branch",
  "enforcement": "active",
  "conditions": {
    "ref_name": {
      "include": ["~DEFAULT_BRANCH"],
      "exclude": []
    }
  },
  "bypass_actors": [
    {
      "actor_id": 5,
      "actor_type": "RepositoryRole",
      "bypass_mode": "always"
    }
  ],
  "rules": [
    {"type": "deletion"},
    {"type": "non_fast_forward"}
  ]
}
EOF
}

# Create Ruleset 2: Require PR for merging (with optional CI checks)
create_ruleset_2() {
  local repo=$1
  local with_ci=$2
  
  local rules
  if [ "$with_ci" = "true" ]; then
    rules='[
      {"type": "deletion"},
      {"type": "non_fast_forward"},
      {"type": "pull_request", "parameters": {
        "required_approving_review_count": 1,
        "dismiss_stale_reviews_on_push": false,
        "require_code_owner_review": false,
        "require_last_push_approval": false,
        "required_review_thread_resolution": true,
        "allowed_merge_methods": ["squash"]
      }},
      {"type": "required_status_checks", "parameters": {
        "strict_required_status_checks_policy": false,
        "do_not_enforce_on_create": false,
        "required_status_checks": [
          {"context": "test-and-lint"}
        ]
      }}
    ]'
  else
    rules='[
      {"type": "deletion"},
      {"type": "non_fast_forward"},
      {"type": "pull_request", "parameters": {
        "required_approving_review_count": 1,
        "dismiss_stale_reviews_on_push": false,
        "require_code_owner_review": false,
        "require_last_push_approval": false,
        "required_review_thread_resolution": true,
        "allowed_merge_methods": ["squash"]
      }}
    ]'
  fi

  gh api \
    --method POST \
    repos/$ORG/$repo/rulesets \
    --input - > /dev/null <<EOF
{
  "name": "Require PR for merging on default branch",
  "target": "branch",
  "enforcement": "active",
  "conditions": {
    "ref_name": {
      "include": ["~DEFAULT_BRANCH"],
      "exclude": []
    }
  },
  "bypass_actors": [
    {
      "actor_id": 5,
      "actor_type": "RepositoryRole",
      "bypass_mode": "always"
    }
  ],
  "rules": $rules
}
EOF
}

# Enable branch protection for a repository
enable_protection() {
  local repo=$1
  
  echo "[$repo]"
  
  # Check if repo is private (rulesets require GitHub Pro for private repos)
  local visibility
  visibility=$(gh repo view $ORG/$repo --json visibility --jq '.visibility')
  if [ "$visibility" = "PRIVATE" ]; then
    echo "  ⚠ Skipping — private repo (rulesets require GitHub Pro)"
    echo ""
    return
  fi
  
  # Delete existing rulesets
  delete_existing_rulesets "$repo"
  
  # Create Ruleset 1
  create_ruleset_1 "$repo"
  echo "  ✓ Ruleset 1: Protect default branch"
  
  # Create Ruleset 2 (with or without CI)
  if has_ci "$repo"; then
    create_ruleset_2 "$repo" "true"
    echo "  ✓ Ruleset 2: Require PR + CI (test-and-lint)"
  else
    create_ruleset_2 "$repo" "false"
    echo "  ✓ Ruleset 2: Require PR"
  fi
  
  echo ""
}

# Plan (dry-run) — show what would be applied
plan_protection() {
  echo "Plan: branch protection rulesets for $ORG"
  echo ""
  printf "%-40s %-20s %s\n" "Repository" "Ruleset 1" "Ruleset 2"
  printf "%-40s %-20s %s\n" "----------" "---------" "---------"
  
  gh repo list $ORG \
    --limit 100 \
    --json name \
    --jq '.[].name' \
    | sort \
    | while read -r repo; do
        if has_ci "$repo"; then
          printf "%-40s %-20s %s\n" "$repo" "protect branch" "PR + CI (test-and-lint)"
        else
          printf "%-40s %-20s %s\n" "$repo" "protect branch" "PR only"
        fi
      done
  
  echo ""
  echo "CI-enforced repos: ${CI_REPOS[*]}"
  echo ""
  echo "Run '$0 enable all' to apply."
}

# Main command handler
case "${1:-}" in
  show)
    show_protection_status
    ;;
  plan)
    plan_protection
    ;;
  enable)
    shift
    if [ $# -eq 0 ]; then
      echo "Error: Please specify repository names or 'all'"
      echo "Usage: $0 enable <repo1> <repo2> ... | all"
      exit 1
    fi
    
    if [ "$1" = "all" ]; then
      echo "Enabling branch protection for all repositories..."
      echo ""
      repos=$(gh repo list $ORG --limit 100 --json name --jq '.[].name')
      for repo in $repos; do
        enable_protection "$repo"
      done
    else
      for repo in "$@"; do
        enable_protection "$repo"
      done
    fi
    echo "Done!"
    ;;
  *)
    echo "Usage: $0 {show|plan|enable}"
    echo ""
    echo "Commands:"
    echo "  show                    Show branch protection status for all repos"
    echo "  plan                    Preview what protection would be applied"
    echo "  enable <repo1> <repo2>  Enable branch protection for specific repos"
    echo "  enable all              Enable branch protection for all repos"
    exit 1
    ;;
esac
