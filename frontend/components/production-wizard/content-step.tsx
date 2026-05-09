"use client";

import { useWizard } from "./wizard-state";

export function ContentStep() {
  const { data, setData } = useWizard();

  function update(partial: Partial<typeof data>) {
    setData((prev) => ({ ...prev, ...partial }));
  }

  const labelClasses = "block text-sm font-medium text-gray-700";
  const inputClasses =
    "block w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 placeholder:text-gray-400 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500";

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-gray-900">Production Content</h2>
        <p className="text-sm text-gray-500 mt-1">Provide the details for your new production.</p>
      </div>

      <div className="space-y-5">
        <div>
          <label htmlFor="title" className={labelClasses}>
            Title <span className="text-red-500">*</span>
          </label>
          <input
            id="title"
            type="text"
            required
            value={data.title}
            onChange={(e) => update({ title: e.target.value })}
            placeholder="Enter production title"
            className={`${inputClasses} mt-1`}
          />
        </div>

        <div>
          <label htmlFor="base_content" className={labelClasses}>
            Base Content
          </label>
          <textarea
            id="base_content"
            rows={5}
            value={data.base_content}
            onChange={(e) => update({ base_content: e.target.value })}
            placeholder="Enter the base content for the production..."
            className={`${inputClasses} mt-1 resize-y`}
          />
        </div>

        <div>
          <label htmlFor="editorial_context" className={labelClasses}>
            Editorial Context
          </label>
          <textarea
            id="editorial_context"
            rows={3}
            value={data.editorial_context}
            onChange={(e) => update({ editorial_context: e.target.value })}
            placeholder="Describe the editorial context, tone, and audience..."
            className={`${inputClasses} mt-1 resize-y`}
          />
        </div>

        <div>
          <label htmlFor="restrictions" className={labelClasses}>
            Restrictions
          </label>
          <input
            id="restrictions"
            type="text"
            value={data.restrictions}
            onChange={(e) => update({ restrictions: e.target.value })}
            placeholder="e.g., max 280 characters, no mentions of competitors"
            className={`${inputClasses} mt-1`}
          />
        </div>
      </div>
    </div>
  );
}
