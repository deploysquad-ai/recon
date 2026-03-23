---
belongs_to: '[[Module - Task & Project Management]]'
governed_by:
- '[[Constraint - Mobile-first design]]'
name: 'Mobile delivery strategy: PWA over native apps'
related_to: []
schema_version: 1
status: active
tags:
- project/focus
type: decision
---

## Context

The app is mobile-first but building separate iOS and Android apps requires significant resources and App Store overhead for an early product.

## Decision

Ship as a Progressive Web App (PWA) with offline support, home screen installation, and push notification capability.

## Rationale

PWA delivers a native-like mobile experience with a single codebase, no App Store approval process, and instant updates. Covers the core use case for overwhelmed individuals on mobile without the distribution friction.

## Alternatives Considered

- Native iOS (Swift): Best UX but high cost, Apple review delays
- React Native: Cross-platform but still requires App Store distribution
- Mobile web only (no PWA): No offline, no home screen install — too limited