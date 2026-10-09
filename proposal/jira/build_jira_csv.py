#!/usr/bin/env python3
"""Build a Jira Cloud CSV import for the FYP sprint plan. 1 story point = 1 hour."""

import csv
from pathlib import Path

EPICS = [
    ("P0 Setup", "Applications in, repo and CI running, off-the-shelf detection stack working on one clip."),
    ("P1 Baseline and error model", "Measured accuracy of off-the-shelf positions, and an error model the rules engine can call."),
    ("P2 Rules and uncertainty", "Kick-frame detection, Law 11 engine listing every candidate, margins with error bars."),
    ("P3 Involvement", "What each offside-position attacker did after the kick. Stretch if the basic path is behind."),
    ("P4 Web application", "YouTube link or file in, analysis out. Comparison view and AWS are stretch inside this epic."),
    ("P5 Evaluation and dissertation", "Independent test cases, results, dissertation, demo."),
]

# summary, epic, sprint, hours, priority, labels, description
STORIES = [
    # S1 — 16h  (supervisor demo is the week-of-13-Oct checkpoint)
    ("Supervisor demo: off-the-shelf stack on one clip", "P0 Setup", "S1 Setup (12 Oct – 25 Oct)", 6, "Highest", "must-have off-the-shelf",
     "Due week of 13 Oct. Do not write any original code. Clone the Roboflow sports soccer example, run it on one football clip, and show player boxes plus a top-down radar. Open with: this is existing tooling I am using as-is; my project starts after this. Two minutes of video is enough. Log the commands."),
    ("Apply for SoccerNet data access", "P0 Setup", "S1 Setup (12 Oct – 25 Oct)", 3, "High", "must-have",
     "Apply in week one. Hugging Face NDA via soccer-net.org/data. If refused, write the fallback (open datasets + own footage) into the logbook the same week. Can slip a day if the supervisor demo is not yet running."),
    ("Submit ethics application", "P0 Setup", "S1 Setup (12 Oct – 25 Oct)", 4, "High", "must-have",
     "Cover the observer study and recording own footage on a local pitch. Apply early even if the study is stretch — ethics is the long pole. After the demo, not instead of it."),
    ("Create GitHub repo, branch protection and CI skeleton", "P0 Setup", "S1 Setup (12 Oct – 25 Oct)", 3, "High", "must-have",
     "Private or public repo, main protected, GitHub Actions running lint on an empty Python package. GitHub Projects board with these sprints mirrored as columns if Jira is delayed."),

    # S2 — 14h
    ("Detect players, keepers, referees and ball with football YOLO weights", "P0 Setup", "S2 Perception stack (26 Oct – 8 Nov)", 4, "High", "must-have off-the-shelf",
     "Ultralytics + Roboflow football-players-detection weights. One clip, boxes on screen. Do not train a new detector."),
    ("Keep player identities across frames with ByteTrack", "P0 Setup", "S2 Perception stack (26 Oct – 8 Nov)", 3, "High", "must-have off-the-shelf",
     "model.track(..., tracker='bytetrack.yaml') or the sports example tracker. Same person keeps an ID through the clip."),
    ("Map the camera view to a top-down pitch", "P0 Setup", "S2 Perception stack (26 Oct – 8 Nov)", 4, "High", "must-have off-the-shelf",
     "Roboflow sports pitch keypoints + ViewTransformer. Player positions in metres on a 105x68 pitch, not pixels."),
    ("Split teams by kit colour and export tracked positions as JSON", "P0 Setup", "S2 Perception stack (26 Oct – 8 Nov)", 3, "High", "must-have",
     "Done when one clip produces a JSON file of frame, track id, team, pitch x, pitch y. That JSON is the input to everything you write."),

    # S3 — 16h
    ("Obtain SoccerNet tracking/GSR data or lock in a fallback", "P1 Baseline and error model", "S3 Measure accuracy (9 Nov – 22 Nov)", 4, "Highest", "must-have",
     "Download Game State Reconstruction or tracking splits. If access is still pending, freeze the fallback dataset and do not wait."),
    ("Run the off-the-shelf pipeline on labelled clips", "P1 Baseline and error model", "S3 Measure accuracy (9 Nov – 22 Nov)", 6, "High", "must-have",
     "Batch the P0 stack over the labelled set. Save predicted pitch-space coordinates per player per frame."),
    ("Compare predicted positions to ground truth in metres", "P1 Baseline and error model", "S3 Measure accuracy (9 Nov – 22 Nov)", 6, "High", "must-have",
     "One number: mean (and spread of) position error in metres. This is basic goal B1. Plot error histogram."),

    # S4 — 18h
    ("Measure how position error changes with camera angle", "P1 Baseline and error model", "S4 Error factors (23 Nov – 6 Dec)", 8, "High", "must-have",
     "Stratify B1 by camera angle / zoom. Tight sideline vs flatter broadcast. Table, not just a sentence."),
    ("Measure how position error changes with crowding and occlusion", "P1 Baseline and error model", "S4 Error factors (23 Nov – 6 Dec)", 6, "High", "must-have",
     "Stratify B1 by how packed the box is and whether the relevant player is occluded."),
    ("Write up the measured accuracy figure", "P1 Baseline and error model", "S4 Error factors (23 Nov – 6 Dec)", 4, "High", "must-have",
     "Short note a supervisor can read: method, overall metres, the two stratifications, limits. This is B1 on paper."),

    # S5 — 16h
    ("Fit the error model", "P1 Baseline and error model", "S5 Error model (7 Dec – 20 Dec)", 8, "High", "must-have",
     "Turn the stratifications into a model: given camera/crowd/occlusion features, predicted position sigma in metres. Basic goal B2."),
    ("Expose the error model as a callable function", "P1 Baseline and error model", "S5 Error model (7 Dec – 20 Dec)", 4, "High", "must-have",
     "Pure Python, no YOLO import. Input: clip features and a player. Output: sigma in metres. Unit-tested on fixtures."),
    ("P1 supervisor report", "P1 Baseline and error model", "S5 Error model (7 Dec – 20 Dec)", 4, "Medium", "must-have",
     "Two to three pages: what you measured, the model, what you will not claim. Teaching ends 18 Dec — send before you leave."),

    # S6 — 8h (winter exams 5–16 Jan)
    ("Encode Law 11 as pure Python", "P2 Rules and uncertainty", "S6 Law 11 (4 Jan – 17 Jan)", 5, "High", "must-have",
     "Exam-week work, no GPU. Second-last defender including keeper, level-with-the-ball exception. No OpenCV/YOLO imports in this package."),
    ("Unit-test Law 11 on synthetic positions", "P2 Rules and uncertainty", "S6 Law 11 (4 Jan – 17 Jan)", 3, "High", "must-have",
     "Fixture files of attacker/defender coordinates with expected onside/offside. Include a keeper-as-second-last case."),

    # S7 — 20h
    ("Detect the frame the ball is kicked", "P2 Rules and uncertainty", "S7 Kick-frame (18 Jan – 31 Jan)", 10, "High", "must-have",
     "Heuristic from ball trajectory / contact. Output a frame index. Basic goal B3. Do not pretend this is centimetre-accurate."),
    ("Evaluate kick-frame error against manual labels", "P2 Rules and uncertainty", "S7 Kick-frame (18 Jan – 31 Jan)", 6, "High", "must-have",
     "Label ~20 clips by hand. Report mean and worst frame error. 25 fps means 40 ms a frame."),
    ("Measure how shifting the kick frame by 1–2 frames changes the margin", "P2 Rules and uncertainty", "S7 Kick-frame (18 Jan – 31 Jan)", 4, "High", "must-have",
     "This number is the reason the comparison view exists. Record it. You will show it in the demo."),

    # S8 — 22h
    ("Set the offside line from the frontmost legally playable body part", "P2 Rules and uncertainty", "S8 Enumeration (1 Feb – 14 Feb)", 8, "High", "must-have",
     "Use YOLO-pose keypoints. Not the bottom of the bounding box. Document which keypoints count under Law 11."),
    ("List every attacker beyond the offside line at the kick", "P2 Rules and uncertainty", "S8 Enumeration (1 Feb – 14 Feb)", 6, "Highest", "must-have",
     "The judged contribution. Not the scorer — everyone. Basic goal B4. Derby motivating case: Fernández must appear even if Haaland does not."),
    ("Integration tests for the rules engine on real clips", "P2 Rules and uncertainty", "S8 Enumeration (1 Feb – 14 Feb)", 8, "High", "must-have",
     "Synthetic fixtures plus at least five real clips with hand labels. pytest in CI."),

    # S9 — 20h
    ("Attach an error bar to each offside margin", "P2 Rules and uncertainty", "S9 Uncertainty (15 Feb – 28 Feb)", 8, "High", "must-have",
     "Call the P1 error model. Each candidate gets margin ± sigma. Basic goal B5."),
    ("Return too-close-to-call when the margin falls inside the error bar", "P2 Rules and uncertainty", "S9 Uncertainty (15 Feb – 28 Feb)", 4, "High", "must-have",
     "Three-way verdict: onside, offside, too close to call. No guessing inside the error bar."),
    ("CLI: clip in, JSON out", "P2 Rules and uncertainty", "S9 Uncertainty (15 Feb – 28 Feb)", 8, "High", "must-have",
     "One command: video path → kick frame, candidates, margins, verdicts. The website will wrap this. Done = B3+B4+B5 without a UI."),

    # S10 — 22h
    ("Track each offside candidate for about two seconds after the kick", "P3 Involvement", "S10 App + involvement (1 Mar – 14 Mar)", 8, "Medium", "stretch",
     "Reuse ByteTrack. Per candidate, a short trajectory after the kick frame."),
    ("Extract movement features for each candidate", "P3 Involvement", "S10 App + involvement (1 Mar – 14 Mar)", 8, "Medium", "stretch",
     "Speed, direction, distance to ball and to the goalkeeper. Enough to describe what they did."),
    ("React app shell with Vite and Tailwind", "P4 Web application", "S10 App + involvement (1 Mar – 14 Mar)", 6, "High", "must-have",
     "Empty site: paste-URL form stub, results route stub, comparison route stub. No backend yet."),

    # S11 — 15h (week before Easter; teaching stops 22 Mar)
    ("Write a short involvement description per candidate", "P3 Involvement", "S11 YouTube ingest (15 Mar – 21 Mar)", 7, "Medium", "stretch",
     "Plain sentence from the features, e.g. 'dived at the near post, did not touch the ball'."),
    ("YouTube URL plus timestamp ingest", "P4 Web application", "S11 YouTube ingest (15 Mar – 21 Mar)", 8, "Highest", "must-have",
     "Paste a URL and a rough timestamp. yt-dlp + ffmpeg pull only those seconds. Delete after analysis. Basic goal B6 input path."),

    # S12 — 40h (after Easter 5–18 Apr)
    ("Tell a passive offside player from one going for the ball", "P3 Involvement", "S12 Results + eval data (5 Apr – 18 Apr)", 8, "Low", "stretch",
     "Stretch S3. Only if P4 results page is already working. Rule or simple classifier on the features — not a new network if you can avoid it."),
    ("Attach involvement notes to the JSON output", "P3 Involvement", "S12 Results + eval data (5 Apr – 18 Apr)", 4, "Medium", "stretch",
     "CLI JSON includes the description (and the passive/active flag if that ticket landed)."),
    ("File upload fallback", "P4 Web application", "S12 Results + eval data (5 Apr – 18 Apr)", 4, "High", "must-have",
     "Same analysis path as YouTube. Needed for SoccerNet clips and for when a link fails."),
    ("Results page: kick frame, player list, margins, verdict", "P4 Web application", "S12 Results + eval data (5 Apr – 18 Apr)", 8, "Highest", "must-have",
     "This is the judged artefact. One incident on screen. Basic goal B6."),
    ("Assemble the KMI Panel and Mic'd Up test set", "P5 Evaluation and dissertation", "S12 Results + eval data (5 Apr – 18 Apr)", 6, "High", "must-have",
     "Independent labels. Do not use SoccerNet Offside labels as missed-offside truth. Include the 2026/27 derby as a worked example."),
    ("Record own footage on a local pitch with measured positions", "P5 Evaluation and dissertation", "S12 Results + eval data (5 Apr – 18 Apr)", 4, "Medium", "must-have",
     "Action camera or phone, tape measure, a few staged offside geometries. Cheapest accurate ground truth."),
    ("Run the observer study", "P5 Evaluation and dissertation", "S12 Results + eval data (5 Apr – 18 Apr)", 6, "Low", "stretch",
     "Stretch S6. Only if ethics is approved. Compare what people notice in a clip against what the system flags. Drop this first if April is slipping."),

    # S13 — 48h (submission fortnight; teaching ends 30 Apr)
    ("Wire the CLI pipeline to a backend job", "P4 Web application", "S13 Deploy + write-up (19 Apr – 2 May)", 8, "High", "must-have",
     "Form submit → job → JSON → results page. Can be local first; AWS ticket is separate."),
    ("Comparison view of two analyses side by side", "P4 Web application", "S13 Deploy + write-up (19 Apr – 2 May)", 8, "Medium", "stretch",
     "Stretch S1. Same clip, kick frame shifted by one or two frames, is the headline demo."),
    ("Deploy on AWS Lambda, API Gateway, DynamoDB and S3", "P4 Web application", "S13 Deploy + write-up (19 Apr – 2 May)", 10, "Medium", "stretch",
     "Stretch S2. Serverless so it stays in student credits. GPU stays on Kaggle/Colab."),
    ("CI/CD to deployment and measure delivery delay", "P4 Web application", "S13 Deploy + write-up (19 Apr – 2 May)", 4, "Medium", "stretch",
     "Push to main deploys. Record time from submit to result on screen."),
    ("Authentication and a short security note", "P4 Web application", "S13 Deploy + write-up (19 Apr – 2 May)", 4, "Low", "stretch",
     "Stretch S4. Cognito or similar if AWS landed; otherwise a written review of what you would lock down. Drop if behind."),
    ("Evaluation tables for the dissertation", "P5 Evaluation and dissertation", "S13 Deploy + write-up (19 Apr – 2 May)", 8, "Highest", "must-have",
     "SoccerNet position error, kick-frame error, rules-engine cases, KMI/Mic'd Up incidents. Figures you can paste into Word."),
    ("Compile the dissertation", "P5 Evaluation and dissertation", "S13 Deploy + write-up (19 Apr – 2 May)", 4, "Highest", "must-have",
     "Assemble chapters from the logbook and the P1/P2 write-ups. You should have been writing as you went — this is compile, not start."),
    ("Rehearse the demo", "P5 Evaluation and dissertation", "S13 Deploy + write-up (19 Apr – 2 May)", 2, "High", "must-have",
     "YouTube paste → player list. Comparison view if it exists. Derby clip as the story. Time it."),
]

SPRINTS = [
    ("S1 Setup (12 Oct – 25 Oct)", "12 Oct 2026", "25 Oct 2026", "P0", "Supervisor demo of existing tools; SoccerNet and ethics submitted."),
    ("S2 Perception stack (26 Oct – 8 Nov)", "26 Oct 2026", "8 Nov 2026", "P0", "YOLO + ByteTrack + homography on one clip. Includes reading week."),
    ("S3 Measure accuracy (9 Nov – 22 Nov)", "9 Nov 2026", "22 Nov 2026", "P1", "Overall position error in metres."),
    ("S4 Error factors (23 Nov – 6 Dec)", "23 Nov 2026", "6 Dec 2026", "P1", "Error vs camera angle, crowding, occlusion."),
    ("S5 Error model (7 Dec – 20 Dec)", "7 Dec 2026", "20 Dec 2026", "P1", "Callable error model. Teaching ends 18 Dec."),
    ("S6 Law 11 (4 Jan – 17 Jan)", "4 Jan 2027", "17 Jan 2027", "P2", "Light: exams 5–16 Jan. Law 11 in pure Python."),
    ("S7 Kick-frame (18 Jan – 31 Jan)", "18 Jan 2027", "31 Jan 2027", "P2", "Kick-frame detector and its error."),
    ("S8 Enumeration (1 Feb – 14 Feb)", "1 Feb 2027", "14 Feb 2027", "P2", "Every offside-position attacker, not just the scorer."),
    ("S9 Uncertainty (15 Feb – 28 Feb)", "15 Feb 2027", "28 Feb 2027", "P2", "Error bars, too close to call, CLI."),
    ("S10 App + involvement (1 Mar – 14 Mar)", "1 Mar 2027", "14 Mar 2027", "P3/P4", "App shell plus post-kick tracking."),
    ("S11 YouTube ingest (15 Mar – 21 Mar)", "15 Mar 2027", "21 Mar 2027", "P3/P4", "Short week. Easter starts 22 Mar. YouTube path working."),
    ("S12 Results + eval data (5 Apr – 18 Apr)", "5 Apr 2027", "18 Apr 2027", "P3/P4/P5", "Results page. Test-set footage. Heavy week."),
    ("S13 Deploy + write-up (19 Apr – 2 May)", "19 Apr 2027", "2 May 2027", "P4/P5", "Submission fortnight. Teaching ends 30 Apr."),
]


def desc(story):
    summary, epic, sprint, hours, priority, labels, body = story
    ac = {
        "Supervisor demo: off-the-shelf stack on one clip": "- Roboflow soccer example (or equivalent YOLO+radar) runs on one clip.\n- Output video or live window shown to supervisor.\n- Spoken line: this is not my contribution; it is the input my project will use.\n- Commands in the logbook. No original pipeline code.",
        "Apply for SoccerNet data access": "- Application submitted (or documented refusal) in the logbook.",
        "Submit ethics application": "- Form submitted; copy in the repo or OneNote.",
        "Create GitHub repo, branch protection and CI skeleton": "- Empty Python package lints green on push to main.",
        "Detect players, keepers, referees and ball with football YOLO weights": "- One clip with labelled boxes; no training run.",
        "Keep player identities across frames with ByteTrack": "- IDs stable through the clip except on full occlusions.",
        "Map the camera view to a top-down pitch": "- Player coordinates in metres on a standard pitch.",
        "Split teams by kit colour and export tracked positions as JSON": "- JSON schema documented; one clip exported.",
        "Obtain SoccerNet tracking/GSR data or lock in a fallback": "- Data on disk, or fallback named and justified.",
        "Run the off-the-shelf pipeline on labelled clips": "- Predictions saved for the whole labelled split.",
        "Compare predicted positions to ground truth in metres": "- Mean error and histogram in the logbook.",
        "Measure how position error changes with camera angle": "- Table of error by angle/zoom bin.",
        "Measure how position error changes with crowding and occlusion": "- Table of error by crowding/occlusion bin.",
        "Write up the measured accuracy figure": "- Note sent to supervisor.",
        "Fit the error model": "- Model predicts sigma; residuals checked.",
        "Expose the error model as a callable function": "- pytest covers at least four fixtures.",
        "P1 supervisor report": "- PDF or Word note in the repo.",
        "Encode Law 11 as pure Python": "- Package imports without ultralytics or cv2.",
        "Unit-test Law 11 on synthetic positions": "- Fixtures include keeper-as-second-last.",
        "Detect the frame the ball is kicked": "- Frame index returned for a clip.",
        "Evaluate kick-frame error against manual labels": "- Mean/worst frame error reported on ~20 clips.",
        "Measure how shifting the kick frame by 1–2 frames changes the margin": "- Table of margin vs frame offset.",
        "Set the offside line from the frontmost legally playable body part": "- Line uses a pose keypoint, not box bottom.",
        "List every attacker beyond the offside line at the kick": "- Multi-attacker fixture passes; scorer-only would fail it.",
        "Integration tests for the rules engine on real clips": "- CI runs pytest including at least five real clips.",
        "Attach an error bar to each offside margin": "- JSON includes margin and sigma per candidate.",
        "Return too-close-to-call when the margin falls inside the error bar": "- Three-way verdict in the JSON.",
        "CLI: clip in, JSON out": "- One command documented in the README.",
        "Track each offside candidate for about two seconds after the kick": "- Trajectory stored per candidate.",
        "Extract movement features for each candidate": "- Features in the JSON.",
        "React app shell with Vite and Tailwind": "- Three routes render without a backend.",
        "Write a short involvement description per candidate": "- Description string in the JSON.",
        "YouTube URL plus timestamp ingest": "- Short window downloaded, analysed, deleted.",
        "Tell a passive offside player from one going for the ball": "- Flag on each candidate, or ticket dropped with a logbook note.",
        "Attach involvement notes to the JSON output": "- CLI JSON includes involvement fields.",
        "File upload fallback": "- Uploaded file produces the same JSON shape as YouTube.",
        "Results page: kick frame, player list, margins, verdict": "- One incident visible end to end from an upload or link.",
        "Assemble the KMI Panel and Mic'd Up test set": "- Spreadsheet of incidents with independent labels and clip sources.",
        "Record own footage on a local pitch with measured positions": "- At least three staged geometries with taped distances.",
        "Run the observer study": "- Results table, or ticket cancelled if ethics/time missing.",
        "Wire the CLI pipeline to a backend job": "- UI submit produces a results page without hand-running CLI.",
        "Comparison view of two analyses side by side": "- Two kick frames, two verdicts, same clip.",
        "Deploy on AWS Lambda, API Gateway, DynamoDB and S3": "- Public URL, or ticket dropped with local-only demo noted.",
        "CI/CD to deployment and measure delivery delay": "- Delay figure in the dissertation, or N/A if AWS dropped.",
        "Authentication and a short security note": "- Page of risks and controls, even if auth is not built.",
        "Evaluation tables for the dissertation": "- Figures ready to paste.",
        "Compile the dissertation": "- Complete draft.",
        "Rehearse the demo": "- Timed run recorded in the logbook.",
    }[summary]
    return (
        f"{body}\n\n"
        f"Acceptance criteria:\n{ac}\n\n"
        f"Epic: {epic}\nSprint: {sprint}\nEstimate: {hours}h (1 story point = 1 hour)"
    )


def main():
    out = Path(__file__).with_name("jira_import.csv")
    hours = sum(s[3] for s in STORIES)
    assert hours == 275, hours
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "Summary", "Issue Type", "Description", "Epic Name", "Epic Link",
            "Sprint", "Priority", "Labels", "Story Points", "Original Estimate",
        ])
        for name, blurb in EPICS:
            w.writerow([name, "Epic", blurb, name, "", "", "High", "epic", "", ""])
        for s in STORIES:
            summary, epic, sprint, hrs, priority, labels, _ = s
            w.writerow([
                summary, "Story", desc(s), "", epic, sprint, priority,
                labels, hrs, f"{hrs}h",
            ])
    sprint_out = Path(__file__).with_name("sprints.csv")
    with sprint_out.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Sprint", "Start", "End", "Phase", "Goal", "Hours"])
        by = {}
        for s in STORIES:
            by[s[2]] = by.get(s[2], 0) + s[3]
        for name, start, end, phase, goal in SPRINTS:
            w.writerow([name, start, end, phase, goal, by[name]])
    print(f"Wrote {out} ({len(STORIES)} stories, {hours}h)")
    print(f"Wrote {sprint_out}")
    print("Hours by sprint:")
    for name, *_ in SPRINTS:
        print(f"  {by[name]:3d}h  {name}")


if __name__ == "__main__":
    main()
