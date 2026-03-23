---
actors:
- '[[Persona - Overwhelmed Individual]]'
- '[[Persona - Team Member]]'
belongs_to: '[[Module - Daily Digest]]'
depends_on:
- '[[Module - Focus Engine]]'
epic: '[[Epic - Morning digest email]]'
governed_by:
- '[[Constraint - Email deliverability]]'
implements:
- '[[User Story - Receive morning email with top 3 priorities]]'
name: Digest email composer
related_to:
- '[[Feature - Digest scheduling]]'
schema_version: 1
status: draft
supports:
- '[[Goal - Deliver reliable daily digest]]'
- '[[Goal - Build daily focus habit]]'
tags:
- project/focus
target_version: '[[Version - v1.0]]'
type: feature
---

## Description

Generates personalized HTML email content for each user's morning digest. Queries the Focus Engine for the top 3 ranked tasks, formats them into a clean, mobile-optimized email template, and hands off to the email delivery service.

## Scope

In scope: top-3 task list, project labels, app deep link, unsubscribe link. Out of scope: images, custom branding, task due dates in email.