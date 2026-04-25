"""
seed.py — populate the OTC Engage database with realistic test data.

Usage (from the otc_engage/ directory):
    python manage.py shell < ../seed.py
  or
    python manage.py shell -c "exec(open('../seed.py').read())"
"""

import random
import uuid
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone

from account.models import Profile
from clubhouse.models import (
    Attendance, Club, Event, Location,
    Survey, SurveyQuestion, SurveyResponse,
)
from bulletin_board.models import Request, Reservation

User = get_user_model()

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_user(username, first, last, password="password123", is_staff=False):
    user, created = User.objects.get_or_create(
        username=username,
        defaults=dict(
            first_name=first,
            last_name=last,
            email=f"{username}@otc.edu",
            is_staff=is_staff,
        ),
    )
    if created:
        user.set_password(password)
        user.save()
    return user


def make_profile(user, role):
    profile, _ = Profile.objects.get_or_create(
        user=user,
        defaults=dict(
            otc_email=f"{user.username}@otc.edu",
            role=role,
            points=random.randint(0, 500),
        ),
    )
    return profile


# ---------------------------------------------------------------------------
# 1. Users & Profiles
# ---------------------------------------------------------------------------

print("Creating users and profiles...")

# Admin / Student Engagement staff
admin_user = make_user("admin", "Admin", "User", is_staff=True)
admin_profile = make_profile(admin_user, Profile.Role.ADMIN)

# Faculty advisors
advisor_users = [
    make_user("jsmith",   "Jane",   "Smith"),
    make_user("bwilson",  "Bob",    "Wilson"),
]
advisor_profiles = [make_profile(u, Profile.Role.ADVISOR) for u in advisor_users]

# Club officers
officer_users = [
    make_user("alice",   "Alice",   "Johnson"),
    make_user("charlie", "Charlie", "Brown"),
    make_user("diana",   "Diana",   "Prince"),
    make_user("ethan",   "Ethan",   "Hunt"),
]
officer_profiles = [make_profile(u, Profile.Role.LEAD) for u in officer_users]

# Regular students
student_names = [
    ("frank",   "Frank",   "Miller"),
    ("grace",   "Grace",   "Lee"),
    ("henry",   "Henry",   "Davis"),
    ("isla",    "Isla",    "Wilson"),
    ("jack",    "Jack",    "Taylor"),
    ("kate",    "Kate",    "Anderson"),
    ("liam",    "Liam",    "Thomas"),
    ("mia",     "Mia",     "Jackson"),
    ("noah",    "Noah",    "White"),
    ("olivia",  "Olivia",  "Harris"),
    ("peter",   "Peter",   "Martin"),
    ("quinn",   "Quinn",   "Garcia"),
]
student_users    = [make_user(*n) for n in student_names]
student_profiles = [make_profile(u, Profile.Role.STUDENT) for u in student_users]

all_student_profiles = officer_profiles + student_profiles

print(f"  {User.objects.count()} users ready.")


# ---------------------------------------------------------------------------
# 2. Locations
# ---------------------------------------------------------------------------

print("Creating locations...")

location_data = [
    ("ICW",  "101", "Main Lab"),
    ("ICW",  "202", None),
    ("IC",   "110", "Conference Room A"),
    ("IC",   "215", None),
    ("ICE",  "300", "Auditorium"),
    ("ITTC", "105", "Workshop"),
    ("PMC",  "201", None),
    ("LNC",  "102", "Study Hall"),
    ("GRAFF","104", "Seminar Room"),
]

locations = []
for building, room_num, room_name in location_data:
    loc, _ = Location.objects.get_or_create(
        building=building,
        room_num=room_num,
        defaults=dict(room_name=room_name),
    )
    locations.append(loc)

print(f"  {len(locations)} locations ready.")


# ---------------------------------------------------------------------------
# 3. Clubs
# ---------------------------------------------------------------------------

print("Creating clubs...")

club_data = [
    {
        "name":        "Robotics Club",
        "description": "Build, program, and compete with robots. Open to all skill levels.",
        "emoji":       "🤖",
        "approved":    True,
        "advisor_idx": 0,
        "officer_idxs": [0, 1],
        "member_idxs":  list(range(0, 8)),
    },
    {
        "name":        "Coding Club",
        "description": "Weekly hack sessions, project showcases, and guest speakers from the tech industry.",
        "emoji":       "💻",
        "approved":    True,
        "advisor_idx": 1,
        "officer_idxs": [2, 3],
        "member_idxs":  list(range(4, 12)),
    },
    {
        "name":        "Art & Design Society",
        "description": "Explore digital and traditional art, design thinking, and creative collaboration.",
        "emoji":       "🎨",
        "approved":    True,
        "advisor_idx": 0,
        "officer_idxs": [0, 2],
        "member_idxs":  list(range(2, 10)),
    },
    {
        "name":        "Haven",
        "description": "A safe, welcoming community for students to connect and support one another.",
        "emoji":       "🏡",
        "approved":    True,
        "advisor_idx": 1,
        "officer_idxs": [1, 3],
        "member_idxs":  list(range(0, 6)),
    },
    {
        "name":        "Entrepreneurship Club",
        "description": "Pitch ideas, build business plans, and network with local professionals.",
        "emoji":       "🚀",
        "approved":    False,   # pending approval — good for testing that flow
        "advisor_idx": 0,
        "officer_idxs": [3],
        "member_idxs":  list(range(6, 12)),
    },
]

clubs = []
for cd in club_data:
    club, _ = Club.objects.get_or_create(
        name=cd["name"],
        defaults=dict(
            description=cd["description"],
            emoji=cd["emoji"],
            approved=cd["approved"],
        ),
    )
    club.advisors.add(advisor_profiles[cd["advisor_idx"]])
    for i in cd["officer_idxs"]:
        club.officers.add(officer_profiles[i])
    for i in cd["member_idxs"]:
        club.members.add(all_student_profiles[i])
    clubs.append(club)

print(f"  {len(clubs)} clubs ready.")


# ---------------------------------------------------------------------------
# 4. Events
# ---------------------------------------------------------------------------

print("Creating events...")

now = timezone.now()

def future(days=0, hours=0):
    return now + timedelta(days=days, hours=hours)

def past(days=0, hours=0):
    return now - timedelta(days=days, hours=hours)


event_specs = [
    # Robotics Club events
    dict(title="Intro to Arduino",        club=clubs[0], status="PUBLISHED", loc=locations[5],
         start=future(3), end=future(3, 2),   points=15),
    dict(title="Robot Wars Scrimmage",    club=clubs[0], status="APPROVED",  loc=locations[4],
         start=future(10), end=future(10, 3), points=20),
    dict(title="End-of-Year Showcase",    club=clubs[0], status="DRAFT",     loc=None,
         start=future(30), end=future(30, 4), points=25),

    # Coding Club events
    dict(title="Hack Night #12",          club=clubs[1], status="PUBLISHED", loc=locations[0],
         start=future(1), end=future(1, 3),   points=10),
    dict(title="Guest Speaker: ML Ops",   club=clubs[1], status="SUBMITTED", loc=locations[2],
         start=future(7), end=future(7, 1),   points=10),
    dict(title="Hackathon Kickoff",       club=clubs[1], status="APPROVED",  loc=locations[4],
         start=future(14), end=future(14, 5), points=30),

    # Art & Design
    dict(title="Digital Illustration 101", club=clubs[2], status="PUBLISHED", loc=locations[7],
         start=future(2), end=future(2, 2),   points=10),
    dict(title="Portfolio Review Night",   club=clubs[2], status="DRAFT",     loc=None,
         start=future(21), end=future(21, 2), points=15),

    # Haven
    dict(title="Weekly Check-in",          club=clubs[3], status="PUBLISHED", loc=locations[3],
         start=future(2), end=future(2, 1),   points=5),
    dict(title="Mental Health Workshop",   club=clubs[3], status="APPROVED",  loc=locations[8],
         start=future(9), end=future(9, 2),   points=10),

    # Past events (for attendance/survey testing)
    dict(title="Robotics Orientation",     club=clubs[0], status="COMPLETED", loc=locations[5],
         start=past(14), end=past(13, 22),   points=10),
    dict(title="Hack Night #11",           club=clubs[1], status="COMPLETED", loc=locations[0],
         start=past(7),  end=past(6, 21),    points=10),
    dict(title="Intro to Watercolor",      club=clubs[2], status="COMPLETED", loc=locations[7],
         start=past(10), end=past(9, 22),    points=10),
    dict(title="Open Support Circle",      club=clubs[3], status="COMPLETED", loc=locations[3],
         start=past(5),  end=past(4, 23),    points=5),
]

events = []
for spec in event_specs:
    ev, _ = Event.objects.get_or_create(
        title=spec["title"],
        club=spec["club"],
        defaults=dict(
            status=spec["status"],
            start_time=spec["start"],
            end_time=spec["end"],
            location=spec["loc"],
            point_value=spec["points"],
        ),
    )
    events.append(ev)

print(f"  {len(events)} events ready.")


# ---------------------------------------------------------------------------
# 5. Attendance (past events only)
# ---------------------------------------------------------------------------

print("Creating attendance records...")

past_events = [e for e in events if e.start_time < now]

for ev in past_events:
    attendees = random.sample(student_users, k=random.randint(3, min(8, len(student_users))))
    for user in attendees:
        Attendance.objects.get_or_create(event=ev, user=user)

print(f"  Attendance records: {Attendance.objects.count()}")


# ---------------------------------------------------------------------------
# 6. Survey questions & responses (past/completed events)
# ---------------------------------------------------------------------------

print("Creating surveys...")

# Per-event question definitions: (prompt, type, order, required)
event_survey_specs = {
    "Robotics Orientation": {
        "questions": [
            ("How would you rate this event overall?",           "STARS", 0, True),
            ("Did you feel comfortable with the difficulty level?", "YESNO", 1, True),
            ("Would you recommend this event to a friend?",      "YESNO", 2, True),
            ("What did you enjoy most about the orientation?",   "TEXT",  3, False),
            ("What could we improve for next time?",             "TEXT",  4, False),
        ],
        "text_pools": {
            "What did you enjoy most about the orientation?": [
                "The hands-on Arduino demo was really engaging.",
                "I loved how welcoming everyone was — great community.",
                "Learning to wire up sensors was way easier than I expected.",
                "The officers explained everything really clearly.",
                "Getting to build something from scratch on day one was awesome.",
            ],
            "What could we improve for next time?": [
                "More time on the coding side would be great.",
                "Could use better lighting in the workshop.",
                "Maybe split into beginner and advanced tracks?",
                "I'd love printed reference sheets to take home.",
                "",
            ],
        },
        "star_weights": [1, 1, 2, 4, 4],   # skewed toward 3–5
        "yesno_weights": [[1, 4], [1, 5]],  # mostly yes
    },
    "Hack Night #11": {
        "questions": [
            ("How would you rate this hack night overall?",           "STARS", 0, True),
            ("Did you complete a project or make significant progress?", "YESNO", 1, True),
            ("Was the event long enough?",                             "YESNO", 2, False),
            ("What technologies did you work with tonight?",           "TEXT",  3, False),
            ("Any suggestions for future hack nights?",                "TEXT",  4, False),
        ],
        "text_pools": {
            "What technologies did you work with tonight?": [
                "Python and Flask — built a simple API.",
                "React + Tailwind, making a portfolio site.",
                "Django for the first time — it clicked!",
                "JavaScript and Chart.js for a data viz project.",
                "Just explored Git and GitHub workflows.",
            ],
            "Any suggestions for future hack nights?": [
                "More theme-based challenges would be fun.",
                "Having mentors walk around to help would be great.",
                "Please provide snacks next time!",
                "I'd love a mini demo session at the end.",
                "",
            ],
        },
        "star_weights": [1, 2, 3, 4, 3],
        "yesno_weights": [[2, 4], [1, 3]],
    },
    "Intro to Watercolor": {
        "questions": [
            ("How would you rate this session overall?",           "STARS", 0, True),
            ("Did you feel you had enough supplies and materials?", "YESNO", 1, True),
            ("Would you attend another art workshop like this?",    "YESNO", 2, True),
            ("What was your favorite part of the session?",        "TEXT",  3, False),
            ("Is there a specific art topic you'd like us to cover?", "TEXT", 4, False),
        ],
        "text_pools": {
            "What was your favorite part of the session?": [
                "Learning wet-on-wet blending techniques — so satisfying.",
                "The relaxed atmosphere made it easy to experiment.",
                "I finally understand color theory thanks to this.",
                "The instructor was patient and really encouraging.",
                "Seeing everyone's different interpretations of the same prompt.",
            ],
            "Is there a specific art topic you'd like us to cover?": [
                "Portrait drawing with pencils!",
                "Digital illustration basics — maybe Procreate?",
                "Acrylic pouring looks so fun.",
                "Zentangle or mindfulness doodling.",
                "",
            ],
        },
        "star_weights": [0, 1, 2, 5, 5],   # very positive
        "yesno_weights": [[1, 5], [0, 6]],
    },
    "Open Support Circle": {
        "questions": [
            ("How would you rate this week's circle overall?",            "STARS", 0, True),
            ("Did you feel safe and heard during today's session?",       "YESNO", 1, True),
            ("Would you encourage a fellow student to attend?",           "YESNO", 2, True),
            ("What made today's session valuable to you?",                "TEXT",  3, False),
            ("Is there a topic or resource you'd like us to address?",    "TEXT",  4, False),
        ],
        "text_pools": {
            "What made today's session valuable to you?": [
                "Knowing I'm not alone in what I'm going through.",
                "The guided breathing exercise really helped me reset.",
                "Open, judgment-free space — I needed that today.",
                "Hearing others' experiences made me feel understood.",
                "The check-in format was simple but really effective.",
            ],
            "Is there a topic or resource you'd like us to address?": [
                "Coping with exam stress.",
                "Time management and avoiding burnout.",
                "Resources for students dealing with housing insecurity.",
                "How to support a friend who's struggling.",
                "",
            ],
        },
        "star_weights": [0, 0, 1, 4, 6],   # heavily positive
        "yesno_weights": [[0, 6], [0, 6]],
    },
}

for ev in past_events:
    spec = event_survey_specs.get(ev.title)
    if not spec:
        continue

    for prompt, qtype, order, required in spec["questions"]:
        SurveyQuestion.objects.get_or_create(
            event=ev, prompt=prompt,
            defaults=dict(question_type=qtype, order=order, required=required),
        )

    questions   = list(ev.survey_questions.order_by("order"))
    yesno_qs    = [q for q in questions if q.question_type == "YESNO"]
    attendances = ev.attendees.select_related("user").all()

    for idx, attendance in enumerate(attendances):
        user = attendance.user
        survey, created = Survey.objects.get_or_create(
            event=ev, attendee=user,
            defaults=dict(bonus_points_awarded=True),
        )
        if not created:
            continue

        yesno_counter = 0
        for q in questions:
            if q.question_type == "STARS":
                weights = spec["star_weights"]
                answer  = random.choices(range(1, 6), weights=weights)[0]
                SurveyResponse.objects.get_or_create(
                    survey=survey, question=q,
                    defaults=dict(int_answer=answer),
                )
            elif q.question_type == "YESNO":
                w = spec["yesno_weights"][yesno_counter % len(spec["yesno_weights"])]
                answer = random.choices([0, 1], weights=w)[0]
                SurveyResponse.objects.get_or_create(
                    survey=survey, question=q,
                    defaults=dict(int_answer=answer),
                )
                yesno_counter += 1
            else:  # TEXT
                pool = spec["text_pools"].get(q.prompt, [""])
                SurveyResponse.objects.get_or_create(
                    survey=survey, question=q,
                    defaults=dict(text_answer=random.choice(pool)),
                )

print(f"  Surveys: {Survey.objects.count()}, Responses: {SurveyResponse.objects.count()}")


# ---------------------------------------------------------------------------
# 7. Requests (bulletin board)
# ---------------------------------------------------------------------------

print("Creating requests...")

request_specs = [
    dict(club=clubs[0], event=events[0],  type="IT",      notes="Need projector and HDMI adapter.",
         approval="O", due=future(2)),
    dict(club=clubs[0], event=events[1],  type="EVENT",   notes="Room booking for robot scrimmage.",
         approval="-", due=future(9)),
    dict(club=clubs[1], event=events[3],  type="IT",      notes="WiFi whitelist for 20 devices during hack night.",
         approval="O", due=future(1)),
    dict(club=clubs[1], event=events[5],  type="FINANCE", notes="Budget request: $200 for pizza and drinks.",
         approval="-", due=future(13)),
    dict(club=clubs[2], event=events[6],  type="CUSTODIAL", notes="Extra chairs and table setup needed.",
         approval="-", due=future(2)),
    dict(club=clubs[3], event=events[8],  type="SECURITY", notes="Keycard access to room 215 after hours.",
         approval="X", due=future(1)),
    dict(club=clubs[3], event=events[9],  type="EVENT",   notes="Approval for off-campus speaker visit.",
         approval="-", due=future(8)),
    dict(club=clubs[0], event=events[10], type="IT",      notes="Laptop loan request for 3 students.",
         approval="O", due=past(12), complete=True),
]

for spec in request_specs:
    Request.objects.get_or_create(
        club=spec["club"],
        notes=spec["notes"],
        defaults=dict(
            event=spec.get("event"),
            type=spec["type"],
            approval_status=spec.get("approval", "-"),
            due_date=spec["due"],
            complete=spec.get("complete", False),
        ),
    )

print(f"  Requests: {Request.objects.count()}")


# ---------------------------------------------------------------------------
# 8. Reservations
# ---------------------------------------------------------------------------

print("Creating reservations...")

reservation_specs = [
    dict(club=clubs[0], loc=locations[5], event=events[0],
         start=future(3),  end=future(3, 2),  approved=True),
    dict(club=clubs[1], loc=locations[0], event=events[3],
         start=future(1),  end=future(1, 3),  approved=True),
    dict(club=clubs[2], loc=locations[7], event=events[6],
         start=future(2),  end=future(2, 2),  approved=False),
    dict(club=clubs[3], loc=locations[3], event=events[8],
         start=future(2),  end=future(2, 1),  approved=True),
    dict(club=clubs[0], loc=locations[5], event=events[10],
         start=past(14),   end=past(14, -2),  approved=True),
    dict(club=clubs[1], loc=locations[0], event=events[11],
         start=past(7),    end=past(7, -2),   approved=True),
]

for spec in reservation_specs:
    Reservation.objects.get_or_create(
        club=spec["club"],
        event=spec["event"],
        defaults=dict(
            location=spec["loc"],
            start_time=spec["start"],
            end_time=spec["end"],
            approved=spec["approved"],
        ),
    )

print(f"  Reservations: {Reservation.objects.count()}")


# ---------------------------------------------------------------------------
# 9. Officer applicants
# ---------------------------------------------------------------------------

print("Adding officer applicants...")

# A couple of students applying to clubs they're members of but aren't officers of
clubs[0].officer_applicants.add(student_profiles[2], student_profiles[5])
clubs[1].officer_applicants.add(student_profiles[0], student_profiles[7])

print("  Done.")


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

print("\n✅ Seed complete!")
print(f"   Users:        {User.objects.count()}")
print(f"   Profiles:     {Profile.objects.count()}")
print(f"   Clubs:        {Club.objects.count()}")
print(f"   Locations:    {Location.objects.count()}")
print(f"   Events:       {Event.objects.count()}")
print(f"   Attendance:   {Attendance.objects.count()}")
print(f"   Surveys:      {Survey.objects.count()}")
print(f"   Requests:     {Request.objects.count()}")
print(f"   Reservations: {Reservation.objects.count()}")
print()
print("Default password for all accounts: password123")
print("Admin login: username=admin")