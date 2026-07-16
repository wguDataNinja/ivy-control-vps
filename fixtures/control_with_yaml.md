---
repo_id: test-yaml
display_name: Test YAML Repo
lifecycle: production-active
admission: Gate 6
github_url: github.com/example/test-yaml
default_branch: main
github_visibility: PUBLIC
approved_sha: deadbeef1234567
vps_clone_state: /home/scraper/apps/test-yaml
runtime: Ivy VPS (scraper)
scheduler_writer: scheduler=active; writer=vps-writer
database: PostgreSQL test_yaml
health: present
archive: verified
hermes_scope: read-only
blocker: none
next_task: Monitor stability
gate: "6"
last_verified: 2026-07-15
---

# Test YAML Repo — Repository Control

Body text is ignored when YAML front matter is present.
