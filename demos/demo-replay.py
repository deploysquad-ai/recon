#!/usr/bin/env python3
"""Replay a scripted Claude /recon session with realistic streaming output."""
import sys, time, shutil

W = shutil.get_terminal_size((120, 40)).columns

RESET  = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
CYAN   = "\033[36m"
GREEN  = "\033[32m"
YELLOW = "\033[33m"
WHITE  = "\033[97m"
GRAY   = "\033[90m"

def stream(text, delay=0.018, color=""):
    for ch in text:
        sys.stdout.write(color + ch + RESET)
        sys.stdout.flush()
        time.sleep(delay)

def line(text="", delay=0.018, color="", pre_pause=0, post_pause=0.08):
    if pre_pause:
        time.sleep(pre_pause)
    stream(text, delay=delay, color=color)
    sys.stdout.write("\n")
    sys.stdout.flush()
    time.sleep(post_pause)

def pause(s):
    time.sleep(s)

def prompt(text, color=CYAN):
    sys.stdout.write(f"{BOLD}{color}❯ {RESET}")
    sys.stdout.flush()
    time.sleep(0.3)
    stream(text, delay=0.055, color=WHITE)
    sys.stdout.write("\n")
    sys.stdout.flush()
    time.sleep(0.5)

def label(tag, color):
    return f"{BOLD}{color}{tag}{RESET} "

# ── /recon ─────────────────────────────────────────────────────────────────────
prompt("/recon")
pause(1.2)

line()
stream(label("recon", CYAN), delay=0)
stream("I'm your graph authoring agent. Let's build your project knowledge graph.", delay=0.022, color=WHITE)
sys.stdout.write("\n")
pause(0.2)
stream(label("     ", CYAN), delay=0)
stream("What are you building?", delay=0.022, color=DIM)
sys.stdout.write("\n\n")
sys.stdout.flush()
pause(1.4)

# ── User input ─────────────────────────────────────────────────────────────────
prompt("I'm building a personal todo app. People feel overwhelmed by their task")
pause(0.1)
prompt("lists. You add tasks, group into projects, and the app nudges you to focus")
pause(0.1)
prompt("on one thing at a time. Mobile-first. Daily digest emails top 3 priorities.")
pause(0.1)
prompt("Eventually a team mode to share projects with coworkers.")
pause(1.8)

# ── Inference ──────────────────────────────────────────────────────────────────
stream(label("recon", CYAN), delay=0)
stream("Inferring project structure", delay=0.025, color=WHITE)
for _ in range(3):
    time.sleep(0.5)
    sys.stdout.write(".")
    sys.stdout.flush()
sys.stdout.write("\n\n")
sys.stdout.flush()
pause(0.8)

stream(label("     ", CYAN), delay=0)
stream("Drafted 42 nodes across 10 types:", delay=0.020, color=WHITE)
sys.stdout.write("\n\n")
sys.stdout.flush()
pause(0.3)

TABLE = [
    ("  Project    ", "Focus"),
    ("  Goals    4 ", "Reduce overwhelm · Focus habit · Daily digest · Team collab"),
    ("  Personas 3 ", "Overwhelmed Individual · Team Lead · Team Member"),
    ("  Constraints", "Mobile-first · Email deliverability · Team data isolation"),
    ("  Modules  4 ", "Task & Project Mgmt · Focus Engine · Daily Digest · Team"),
    ("  Decisions 3", "PWA over native · Email provider · Priority ranking"),
    ("  Stories  8 ", "Add task · Create project · Complete · Focus nudge · Digest…"),
    ("  Epics    4 ", "Core task experience · Focus & priority · Digest · Team"),
    ("  Features 9 ", "Task creation · Focus view · Nudge · Digest · Invite · Team…"),
    ("  Versions 3 ", "MVP  ·  v1.0  ·  v2.0"),
]

for col, val in TABLE:
    sys.stdout.write(f"  {BOLD}{CYAN}{col}{RESET}  {DIM}{val}{RESET}\n")
    sys.stdout.flush()
    time.sleep(0.12)

sys.stdout.write("\n")
sys.stdout.flush()
pause(0.8)

stream(label("     ", CYAN), delay=0)
stream("Confirm and write all 42 nodes? [y/n]", delay=0.022, color=WHITE)
sys.stdout.write("\n\n")
sys.stdout.flush()
pause(1.2)

# ── Confirm ────────────────────────────────────────────────────────────────────
prompt("y")
pause(0.6)

# ── Writing ────────────────────────────────────────────────────────────────────
stream(label("recon", CYAN), delay=0)
stream("Writing nodes to vault", delay=0.022, color=WHITE)
sys.stdout.write("\n\n")
sys.stdout.flush()
pause(0.3)

NODES = [
    "Project - Focus.md",
    "Goal - Reduce task overwhelm.md",
    "Goal - Build daily focus habit.md",
    "Goal - Deliver reliable daily digest.md",
    "Goal - Enable team collaboration.md",
    "Persona - Overwhelmed Individual.md",
    "Persona - Team Lead.md",
    "Persona - Team Member.md",
    "Constraint - Mobile-first design.md",
    "Constraint - Email deliverability.md",
    "Constraint - Team data isolation.md",
    "Module - Task & Project Management.md",
    "Module - Focus Engine.md",
    "Module - Daily Digest.md",
    "Module - Team Collaboration.md",
    "Decision - PWA over native apps.md",
    "Decision - Email provider: transactional service.md",
    "Decision - Priority ranking: user-defined with recency.md",
    "User Story - Add task to project.md",
    "User Story - Create and name a project.md",
    "User Story - Complete a task.md",
    "User Story - View single top-priority task.md",
    "User Story - Receive focus nudge when switching tasks.md",
    "User Story - Receive morning email with top 3 priorities.md",
    "User Story - Set digest delivery time.md",
    "User Story - Invite coworker to shared project.md",
    "Epic - Core task experience.md",
    "Epic - Focus and priority system.md",
    "Epic - Morning digest email.md",
    "Epic - Team project sharing.md",
    "Feature - Task creation form.md",
    "Feature - Project creation and task grouping.md",
    "Feature - Task completion.md",
    "Feature - Focus view.md",
    "Feature - Focus nudge.md",
    "Feature - Digest email composer.md",
    "Feature - Digest scheduling.md",
    "Feature - Project invitation flow.md",
    "Feature - Team task visibility.md",
    "Version - MVP.md",
    "Version - v1.0.md",
    "Version - v2.0.md",
]

for node in NODES:
    sys.stdout.write(f"  {GREEN}✓{RESET}  {DIM}{node}{RESET}\n")
    sys.stdout.flush()
    time.sleep(0.09)

sys.stdout.write("\n")
sys.stdout.flush()
pause(0.4)

stream(label("     ", CYAN), delay=0)
stream("42/42 nodes written. Index built.", delay=0.022, color=WHITE)
sys.stdout.write("\n")
sys.stdout.flush()
stream(label("     ", CYAN), delay=0)
stream("Open Graph View in Obsidian to explore your project. ↗", delay=0.022, color=DIM)
sys.stdout.write("\n\n")
sys.stdout.flush()
pause(3.0)
