import {
  CITY_GROUPS,
  CLASS_RANKINGS,
  DEGREES,
  FIELDS,
  INTERNSHIP_YEARS,
  LOCATIONS,
  SEMESTERS,
  UNIVERSITIES,
} from "../data/formOptions";

function Label({ children }) {
  return <label className="mb-2 block text-sm font-semibold text-brand-ink">{children}</label>;
}

export default function PersonalInfoSection({ fields, onFieldChange }) {
  return (
    <section className="panel">
      <h2 className="font-display text-2xl font-bold text-brand-ink">Section 1 — Personal Information</h2>
      <p className="mt-1 text-sm text-slate-600">
        Fill in your profile details exactly as they appear in your academic records.
      </p>

      <div className="mt-6 grid gap-4 sm:grid-cols-2">
        <div>
          <Label>Internship Year*</Label>
          <select
            className="w-full rounded-lg border border-slate-300 px-3 py-2"
            value={fields.internship_year}
            onChange={(event) => onFieldChange("internship_year", event.target.value)}
            required
          >
            {INTERNSHIP_YEARS.map((year) => (
              <option key={year} value={year}>
                {year}
              </option>
            ))}
          </select>
        </div>
        <div>
          <Label>Location*</Label>
          <select
            className="w-full rounded-lg border border-slate-300 px-3 py-2"
            value={fields.location}
            onChange={(event) => onFieldChange("location", event.target.value)}
            required
          >
            {LOCATIONS.map((location) => (
              <option key={location} value={location}>
                {location}
              </option>
            ))}
          </select>
        </div>

        <div>
          <Label>First Name*</Label>
          <input
            className="w-full rounded-lg border border-slate-300 px-3 py-2"
            value={fields.first_name}
            onChange={(event) => onFieldChange("first_name", event.target.value)}
            required
          />
        </div>
        <div>
          <Label>Last Name*</Label>
          <input
            className="w-full rounded-lg border border-slate-300 px-3 py-2"
            value={fields.last_name}
            onChange={(event) => onFieldChange("last_name", event.target.value)}
            required
          />
        </div>

        <div>
          <Label>Email*</Label>
          <input
            type="email"
            className="w-full rounded-lg border border-slate-300 px-3 py-2"
            value={fields.email}
            onChange={(event) => onFieldChange("email", event.target.value)}
            required
          />
        </div>
        <div>
          <Label>Phone*</Label>
          <input
            className="w-full rounded-lg border border-slate-300 px-3 py-2"
            placeholder="e.g. +923001234567"
            value={fields.phone}
            onChange={(event) => onFieldChange("phone", event.target.value)}
            required
          />
        </div>

        <div>
          <Label>City*</Label>
          <select
            className="w-full rounded-lg border border-slate-300 px-3 py-2"
            value={fields.city}
            onChange={(event) => onFieldChange("city", event.target.value)}
            required
          >
            <option value="">Select a city</option>
            {CITY_GROUPS.map((group) => (
              <optgroup key={group.province} label={group.province}>
                {group.cities.map((city) => (
                  <option key={`${group.province}-${city}`} value={city}>
                    {city}
                  </option>
                ))}
              </optgroup>
            ))}
          </select>
        </div>

        <div>
          <Label>University*</Label>
          <select
            className="w-full rounded-lg border border-slate-300 px-3 py-2"
            value={fields.university}
            onChange={(event) => onFieldChange("university", event.target.value)}
            required
          >
            <option value="">Select university</option>
            {UNIVERSITIES.map((university) => (
              <option key={university} value={university}>
                {university}
              </option>
            ))}
          </select>
        </div>

        {fields.university === "Other" && (
          <div className="sm:col-span-2">
            <Label>Other University*</Label>
            <input
              className="w-full rounded-lg border border-slate-300 px-3 py-2"
              value={fields.university_other}
              onChange={(event) => onFieldChange("university_other", event.target.value)}
              required
            />
          </div>
        )}

        <div>
          <Label>Degree*</Label>
          <select
            className="w-full rounded-lg border border-slate-300 px-3 py-2"
            value={fields.degree}
            onChange={(event) => onFieldChange("degree", event.target.value)}
            required
          >
            <option value="">Select degree</option>
            {DEGREES.map((degree) => (
              <option key={degree} value={degree}>
                {degree}
              </option>
            ))}
          </select>
        </div>
        <div>
          <Label>Major*</Label>
          <input
            className="w-full rounded-lg border border-slate-300 px-3 py-2"
            value={fields.major}
            onChange={(event) => onFieldChange("major", event.target.value)}
            required
          />
        </div>

        <div>
          <Label>CGPA*</Label>
          <input
            className="w-full rounded-lg border border-slate-300 px-3 py-2"
            placeholder="e.g. 3.40"
            value={fields.cgpa}
            onChange={(event) => onFieldChange("cgpa", event.target.value)}
            required
          />
        </div>
        <div>
          <Label>Current Semester*</Label>
          <select
            className="w-full rounded-lg border border-slate-300 px-3 py-2"
            value={fields.semester}
            onChange={(event) => onFieldChange("semester", event.target.value)}
            required
          >
            <option value="">Select semester</option>
            {SEMESTERS.map((semester) => (
              <option key={semester} value={semester}>
                {semester}
              </option>
            ))}
          </select>
        </div>

        <div>
          <Label>Class Ranking</Label>
          <select
            className="w-full rounded-lg border border-slate-300 px-3 py-2"
            value={fields.class_ranking}
            onChange={(event) => onFieldChange("class_ranking", event.target.value)}
          >
            <option value="">Select ranking</option>
            {CLASS_RANKINGS.map((ranking) => (
              <option key={ranking} value={ranking}>
                {ranking}
              </option>
            ))}
          </select>
        </div>

        {fields.class_ranking === "Others" && (
          <div>
            <Label>Other Ranking</Label>
            <input
              className="w-full rounded-lg border border-slate-300 px-3 py-2"
              value={fields.class_ranking_other}
              onChange={(event) => onFieldChange("class_ranking_other", event.target.value)}
            />
          </div>
        )}

        <div className={fields.class_ranking === "Others" ? "" : "sm:col-span-2"}>
          <Label>Field*</Label>
          <select
            className="w-full rounded-lg border border-slate-300 px-3 py-2"
            value={fields.field}
            onChange={(event) => onFieldChange("field", event.target.value)}
            required
          >
            <option value="">Select field</option>
            {FIELDS.map((field) => (
              <option key={field} value={field}>
                {field}
              </option>
            ))}
          </select>
        </div>
      </div>
    </section>
  );
}
