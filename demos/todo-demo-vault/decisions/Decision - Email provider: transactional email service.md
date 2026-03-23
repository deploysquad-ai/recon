---
belongs_to: '[[Module - Daily Digest]]'
governed_by:
- '[[Constraint - Email deliverability]]'
name: 'Email provider: transactional email service'
related_to: []
schema_version: 1
status: active
tags:
- project/focus
type: decision
---

## Context

The daily digest requires reliable, scheduled email delivery with strong deliverability to avoid spam filters.

## Decision

Use a dedicated transactional email provider (e.g. Resend, SendGrid, or Postmark) rather than sending email from application servers.

## Rationale

Transactional email providers manage IP reputation, SPF/DKIM/DMARC setup, bounce handling, and deliverability monitoring out of the box. This directly satisfies the Email Deliverability constraint without building infrastructure.

## Alternatives Considered

- Self-hosted SMTP: Full control but high operational overhead and poor deliverability reputation at start
- Marketing email tools (Mailchimp): Designed for bulk/newsletter, not transactional or personalized scheduling