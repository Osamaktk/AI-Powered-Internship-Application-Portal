const programOverview = [
  "Duration: 10 weeks",
  "Eligibility: Undergraduate and graduate students",
  "Format: Fully remote on Microsoft Teams (Fall 2025 details on SPS page)",
  "Goal: Build hands-on skills aligned with SPS career paths",
];

const programFeatures = [
  "Career Track Selection with mentor guidance",
  "Technology stack training and certification opportunities",
  "Academic-friendly schedule with flexible engagement",
];

const internshipPhases = [
  "Trainee: Foundational training on products and services",
  "Shadower: Observe client interactions and delivery workflows",
  "Apprentice: Contribute with teams on real assignments",
  "Full Time Intern: Transition path after performance and certifications",
];

const applicationProcess = [
  "Application: Submit your online form with resume and transcript",
  "Recorded Interview: Upload your short interview video",
  "Screening: Complete preliminary tasks/learning modules",
  "Offer: Selected applicants receive internship offers",
];

const areasOfInternship = [
  "Operations: Human Resource, Accounting, Legal & Compliance, Administration",
  "Technical: Cybersecurity, Cloud Computing, AI & Automation, Learning & Events",
  "Sales: Business Management, Sales, Marketing",
];

const whySps = [
  "Real-world experience on meaningful projects",
  "Learning and development with expert mentors",
  "Flexible program structure to support work-life balance",
  "Career launchpad with potential full-time pathway",
];

function Card({ title, items }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4">
      <h3 className="font-display text-lg font-semibold text-brand-ink">{title}</h3>
      <ul className="mt-3 space-y-2 text-sm text-slate-700">
        {items.map((item) => (
          <li key={item} className="flex gap-2">
            <span className="mt-1 h-1.5 w-1.5 flex-none rounded-full bg-brand-cyan" aria-hidden="true" />
            <span>{item}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default function SpsProgramInfoSection() {
  return (
    <section className="panel">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h2 className="font-display text-2xl font-bold text-brand-ink">
            SPS Internship Program - How It Works
          </h2>
          <p className="mt-1 text-sm text-slate-600">
            Information below is aligned with the official SPS Internship to Job Program page.
          </p>
        </div>
        <p className="rounded-full bg-brand-ink px-3 py-1 text-xs font-semibold uppercase tracking-wide text-white">
          Fall 2025 listing on SPS
        </p>
      </div>

      <div className="mt-4 rounded-xl border border-brand-mint/50 bg-brand-mint/15 p-4 text-sm text-brand-ink">
        The SPS page describes a 10-week internship experience with track selection, practical
        training, and mentorship. Students can progress through Trainee, Shadower, Apprentice,
        and Full Time Intern phases based on performance.
      </div>

      <div className="mt-5 grid gap-4 lg:grid-cols-2">
        <Card title="Program Overview" items={programOverview} />
        <Card title="Program Features" items={programFeatures} />
        <Card title="Application Process" items={applicationProcess} />
        <Card title="Progressive Internship Phases" items={internshipPhases} />
        <Card title="Areas of Internship" items={areasOfInternship} />
        <Card title="Why SPS" items={whySps} />
      </div>
    </section>
  );
}
